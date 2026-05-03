"""
ZWF-20 打卡记录 Excel 解析器
============================
支持 xlsx / xls / csv 格式，自动推断列名并输出结构化 JSON。

Author: Tristan (技术架构官)
"""

import os
import re
import json
import logging
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

import openpyxl

logger = logging.getLogger("excel-parser")

# ----------------------------------------------------------------
#  列名映射模板
# ----------------------------------------------------------------
# key  = 用户文件中可能出现的列名（正则）
# value= 标准字段名
TEMPLATES = {
    "zwf20": {
        "columns": {
            "member_id|会员.*id|会员.*编号|用户.*id|员工.*号|工号|user.*id|userId|人员.*编号": "member_id",
            "name|姓名|名字|用户.*名|人员.*名": "name",
            "time|时间|打卡.*时间|日期|日期时间|punch.*time|record.*time|access.*time|log.*time": "punch_time",
            "verify.*mode|验证.*方式|验证.*模式|识别.*方式|verifyMode": "verify_mode",
            "in.*out|进出|进出.*方向|io.*mode|inOut|出入": "in_out",
            "temperature|体温|温度|temp|摄氏度": "temperature",
            "door.*mode|门禁.*方式|开锁|doorMode": "door_mode",
            "device.*id|设备.*编号|设备|deviceId|machine.*id": "device_id",
            "photo|照片|图片|image|logPhoto|face.*photo|人脸.*照片": "photo_base64",
        },
        "time_format": "%Y%m%d%H%M%S",  # 设备原生格式: 20260429083000
        "description": "ZWF-20 人脸设备导出格式",
    },
    "standard": {
        "columns": {
            "member_id|会员.*id|会员.*编号|用户.*id|员工.*号|工号|userId": "member_id",
            "name|姓名|名字": "name",
            "punch.*time|打卡.*时间|日期.*时间|record.*time|time|datetime": "punch_time",
            "verify.*mode|verify.*type|verifyMode": "verify_mode",
            "in.*out|in_out|inOut|direction|进出": "in_out",
            "temperature|temp|体温": "temperature",
        },
        "time_format": "%Y-%m-%d %H:%M:%S",
        "description": "通用标准格式",
    },
}


def get_template(name: str = "zwf20") -> dict:
    """获取命名模板"""
    tpl = TEMPLATES.get(name)
    if not tpl:
        raise ValueError(f"未知模板: {name}，可用: {list(TEMPLATES.keys())}")
    return tpl


def _match_column(header: str, column_map: dict) -> Optional[str]:
    """模糊匹配列名"""
    header_lower = header.strip().lower()
    for pattern, field in column_map.items():
        if re.search(pattern, header_lower, re.IGNORECASE):
            return field
    return None


def infer_column_mapping(headers: list[str], template_name: str = "zwf20") -> dict:
    """
    根据模板自动推断列映射
    返回 { 标准字段名: 原始列索引 }
    """
    tpl = get_template(template_name)
    mapping = {}  # raw_header -> standard_field
    for i, h in enumerate(headers):
        h = h.strip()
        if not h:
            continue
        field = _match_column(h, tpl["columns"])
        if field:
            if field in mapping.values():
                logger.warning("字段 '%s' 已映射，跳过重复列 '%s'", field, h)
            else:
                mapping[h] = field

    logger.info("列映射: %s", json.dumps(mapping, ensure_ascii=False, indent=2))
    return mapping


def normalize_time(value: Any, template_name: str = "zwf20") -> str:
    """
    将时间值规范化为 ISO8601 字符串
    支持多种输入形态：数字字符串、datetime 对象、Excel 序列号
    """
    tpl = get_template(template_name)
    fmt = tpl["time_format"]

    if isinstance(value, datetime):
        return value.strftime(fmt)
    if isinstance(value, (int, float)):
        # Excel 序列号 → datetime
        from datetime import timedelta
        base = datetime(1899, 12, 30)
        try:
            dt = base + timedelta(days=value)
            return dt.strftime(fmt)
        except Exception:
            pass

    s = str(value).strip()
    if not s:
        return ""

    # 已是指定格式
    try:
        datetime.strptime(s, fmt)
        return s
    except ValueError:
        pass

    # 尝试常见格式
    for candidate_fmt in [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y%m%d%H%M%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]:
        try:
            dt = datetime.strptime(s, candidate_fmt)
            return dt.strftime(fmt)
        except ValueError:
            continue

    # 保持原样
    return s


def parse_excel(file_path: str,
                template_name: str = "zwf20",
                sheet_name: Optional[str] = None,
                header_row: int = 1,
                skip_rows: int = 0) -> list[dict]:
    """
    解析 Excel 文件并返回结构化记录列表。

    参数
    ----
    file_path : str
        .xlsx / .xls / .csv 文件路径
    template_name : str
        字段映射模板名（默认 zwf20）
    sheet_name : str | None
        指定 sheet（xlsx），None 用第一个
    header_row : int
        表头所在行（1-indexed）
    skip_rows : int
        表头下方跳过的行数
    """
    fp = Path(file_path)
    if not fp.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    ext = fp.suffix.lower()
    if ext == ".csv":
        return _parse_csv(fp, template_name, header_row, skip_rows)
    elif ext in (".xlsx", ".xls"):
        return _parse_xlsx(fp, template_name, sheet_name, header_row, skip_rows)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")


def _parse_xlsx(file_path: Path,
                template_name: str,
                sheet_name: Optional[str],
                header_row: int,
                skip_rows: int) -> list[dict]:
    """解析 .xlsx / .xls"""
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    sheet = wb[sheet_name] if sheet_name else wb.active
    rows_iter = sheet.iter_rows(values_only=True)

    # 读取表头
    current_row = 0
    headers = []
    for _ in range(header_row):
        try:
            headers = [str(c) if c is not None else "" for c in next(rows_iter)]
            current_row += 1
        except StopIteration:
            break

    # 跳过指定行
    for _ in range(skip_rows):
        try:
            next(rows_iter)
            current_row += 1
        except StopIteration:
            break

    # 构建列映射
    mapping = infer_column_mapping(headers, template_name)
    reverse_map = {v: k for k, v in mapping.items()}  # field -> raw_header

    records = []
    for row in rows_iter:
        row_values = ["" if v is None else v for v in row]
        if not any(row_values):
            continue

        record = {}
        for std_field, raw_header in reverse_map.items():
            idx = headers.index(raw_header) if raw_header in headers else -1
            if 0 <= idx < len(row_values):
                val = row_values[idx]
                if std_field == "punch_time":
                    val = normalize_time(val, template_name)
                elif std_field == "temperature":
                    try:
                        val = float(val) if val else 0.0
                    except (ValueError, TypeError):
                        val = 0.0
                record[std_field] = val

        if record.get("member_id"):
            records.append(record)

    wb.close()
    logger.info("解析完成: %s → %d 条记录", file_path.name, len(records))
    return records


def _parse_csv(file_path: Path,
               template_name: str,
               header_row: int,
               skip_rows: int) -> list[dict]:
    """解析 .csv"""
    import csv
    records = []
    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        # Skip to header row
        for _ in range(header_row - 1):
            try:
                next(reader)
            except StopIteration:
                break

        try:
            headers = next(reader)
        except StopIteration:
            return records

        for _ in range(skip_rows):
            try:
                next(reader)
            except StopIteration:
                break

        mapping = infer_column_mapping(headers, template_name)
        reverse_map = {v: k for k, v in mapping.items()}

        for row in reader:
            if not any(row):
                continue
            record = {}
            for std_field, raw_header in reverse_map.items():
                idx = headers.index(raw_header) if raw_header in headers else -1
                if 0 <= idx < len(row):
                    val = row[idx]
                    if std_field == "punch_time":
                        val = normalize_time(val, template_name)
                    elif std_field == "temperature":
                        try:
                            val = float(val) if val else 0.0
                        except (ValueError, TypeError):
                            val = 0.0
                    record[std_field] = val
            if record.get("member_id"):
                records.append(record)

    logger.info("CSV 解析完成: %s → %d 条记录", file_path.name, len(records))
    return records


# ----------------------------------------------------------------
#  快捷入口（Python 直接调用）
# ----------------------------------------------------------------

def parse_to_json(file_path: str,
                  template_name: str = "zwf20",
                  output_dir: Optional[str] = None) -> dict:
    """
    解析文件并返回结构化结果字典。

    结果结构:
    {
        "file": "xxx.xlsx",
        "parsed_at": "2026-04-30T00:00:00",
        "template": "zwf20",
        "total": 10,
        "records": [ {...}, ... ],
        "errors": []
    }
    """
    try:
        records = parse_excel(file_path, template_name)
        result = {
            "file": os.path.basename(file_path),
            "parsed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "template": template_name,
            "total": len(records),
            "records": records,
            "errors": [],
        }
    except Exception as e:
        logger.exception("解析失败")
        result = {
            "file": os.path.basename(file_path),
            "parsed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "template": template_name,
            "total": 0,
            "records": [],
            "errors": [str(e)],
        }

    # 可选：写出 JSON 到同目录
    if output_dir:
        out_path = Path(output_dir) / f"{Path(file_path).stem}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info("JSON 已写入: %s", out_path)
        result["_json_output"] = str(out_path)

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys
    if len(sys.argv) < 2:
        print("用法: python parser.py <file.xlsx> [template_name]")
        sys.exit(1)
    result = parse_to_json(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "zwf20")
    print(json.dumps(result, ensure_ascii=False, indent=2))
