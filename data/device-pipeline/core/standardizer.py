#!/usr/bin/env python3
"""
标准化数据生成器 (Standardizer)
================================
将 RecordPayload + 会员信息 → 统一 ZWF-20 格式 JSON 记录。
此格式是数据资产化的核心输出，所有设备适配器的数据最终都汇聚于此。

资产化字段说明：
  punch_standard_{YYYYMMDD}.jsonl   →  每日标准化打卡记录
  字段设计兼顾数据分析（Ethan）和管理报表（Shuyu）
"""

import json
import os
import logging
from datetime import datetime

from config import STANDARDIZED_DIR

logger = logging.getLogger("device-pipeline.standardizer")

# 标准化版本号 — 字段结构变更时递增
STANDARD_VERSION = "v2.0"


def standardize(record: dict, member_id: str, member_info: dict) -> dict:
    """将打卡记录 + 会员信息合并为标准化 JSON

    Args:
        record: RecordPayload 或字典形式的打卡数据
        member_id: 会员编号 (MEMBER_XXX)
        member_info: 会员资料字典

    Returns:
        dict: 标准化记录（见下方字段说明）
    """
    standardized = {
        # ═══ 身份标识 ═══
        "member_id": member_id,
        "member_name": member_info.get("name", ""),

        # ═══ 设备来源 ═══
        "device_id": record.get("device_id", ""),
        "device_user_id": record.get("device_user_id", "")
                        or record.get("userId", ""),
        "adapter": record.get("adapter_name", ""),

        # ═══ 打卡事件 ═══
        "punch_time": record.get("punch_time", "")
                      or record.get("time", ""),
        "verify_mode": record.get("verify_mode", "")
                       or record.get("verifyMode", ""),
        "in_out": record.get("in_out", "")
                  or record.get("inOut", ""),

        # ═══ 环境数据 ═══
        "temperature": float(record.get("temperature", 0.0)),
        "door_mode": record.get("door_mode", "")
                     or record.get("doorMode", ""),

        # ═══ 媒体 ═══
        "photo_path": record.get("photo_path", "")
                      or record.get("_photo_path", ""),

        # ═══ 会员画像（资产摘要）═══
        "member_summary": {
            "phone": str(member_info.get("phone", "")),
            "gender": str(member_info.get("gender", "")),
            "total_amount": member_info.get("total_amount", 0),
            "purchase_count": member_info.get("purchase_count", 0),
            "member_level": str(member_info.get("member_level", "")),
        },

        # ═══ 元数据 ═══
        "standard_version": STANDARD_VERSION,
        "generated_at": datetime.now().isoformat(),
    }

    return standardized


def append_to_jsonl(record: dict) -> str:
    """将一条标准化记录追加到当天的 JSONL 文件

    Returns:
        str: 写入的文件路径
    """
    os.makedirs(STANDARDIZED_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(STANDARDIZED_DIR, f"punch_standard_{date_str}.jsonl")

    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return output_file


def query_by_date(date_str: str) -> list:
    """按日期查询标准化记录"""
    filepath = os.path.join(STANDARDIZED_DIR, f"punch_standard_{date_str}.jsonl")
    if not os.path.exists(filepath):
        return []

    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
