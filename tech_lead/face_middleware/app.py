#!/usr/bin/env python3
"""
人脸设备 HTTP 协议中间件（Flask）
==================================
协议：BS HTTP API (可见光终端客户端通信协议)
功能：
  1. 解析设备心跳 (receive_cmd) → 返回 ERROR_NO_CMD
  2. 下发 GET_LOG_DATA 指令拉取打卡记录
  3. 解析打卡记录 Base64 编码数据（logPhoto）
  4. 结构化数据暂存至数据库

Author: Tristan (技术架构官)
"""

import os
import json
import hashlib
import base64
import logging
import traceback
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import unquote

import requests
from flask import Flask, request, jsonify, make_response, Response

# ── 日志配置 ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("face_middleware")

# ── 配置 ─────────────────────────────────────────────────────────
class Config:
    # 服务器监听
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))

    # 设备验证密钥（厂商提供）
    DEVICE_SECRET = os.getenv("DEVICE_SECRET", "default_secret_key_change_me")

    # 日志拉取时间范围（默认最近 7 天）
    LOG_DAYS_BACK = int(os.getenv("LOG_DAYS_BACK", "7"))

    # 数据库配置 (Tencent MySQL / PostgreSQL)
    DB_ENABLED = os.getenv("DB_ENABLED", "true").lower() == "true"
    DB_TYPE = os.getenv("DB_TYPE", "mysql")  # mysql / postgresql / sqlite
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "face_device")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))

    # 照片存储
    PHOTO_DIR = os.getenv("PHOTO_DIR", "./photos")
    SAVE_PHOTOS = os.getenv("SAVE_PHOTOS", "true").lower() == "true"

    # 设备指令缓存目录（待下发指令）
    CMD_DIR = os.getenv("CMD_DIR", "./pending_cmds")

    # 推送服务
    PUSH_ENABLED = os.getenv("PUSH_ENABLED", "true").lower() == "true"


# ── Flask 应用 ──────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

# ── 设备指令队列 ────────────────────────────────────────────────
# 数据结构：{dev_id: [{"trans_id":..., "cmd_code":..., "cmd_param":...}, ...]}
pending_commands = {}

# ── 工具函数 ─────────────────────────────────────────────────────

def verify_token(dev_id: str, token: str) -> bool:
    """验证设备 token: MD5(dev_id + secret)"""
    expected = hashlib.md5(
        (dev_id + Config.DEVICE_SECRET).encode()
    ).hexdigest().upper()
    return token == expected


def build_http_header_response(headers: dict) -> str:
    """构建 HTTP header 文本（用于辅助调试/日志）"""
    lines = []
    for k, v in headers.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines)


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def parse_device_time(time_str: str) -> datetime:
    """解析设备时间字段
    格式: "201910010645" 或 "20191001064500"
    """
    try:
        if len(time_str) == 12:
            return datetime.strptime(time_str, "%Y%m%d%H%M")
        elif len(time_str) == 14:
            return datetime.strptime(time_str, "%Y%m%d%H%M%S")
    except ValueError:
        pass
    return datetime.now()


def safe_base64_decode(data: str) -> bytes:
    """安全 Base64 解码，自动补齐 padding"""
    if not data:
        return b""
    # 补 padding
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    try:
        return base64.b64decode(data)
    except Exception:
        return b""


def save_photo(dev_id: str, user_id: str, timestamp: str, photo_b64: str) -> str | None:
    """保存打卡照片到本地"""
    if not Config.SAVE_PHOTOS or not photo_b64:
        return None
    ensure_dir(Config.PHOTO_DIR)
    # 文件名: {dev_id}_{user_id}_{timestamp}.jpg
    safe_ts = timestamp.replace(":", "").replace(" ", "_")
    filename = f"{dev_id}_{user_id}_{safe_ts}.jpg"
    filepath = os.path.join(Config.PHOTO_DIR, filename)
    try:
        data = safe_base64_decode(photo_b64)
        if data:
            with open(filepath, "wb") as f:
                f.write(data)
            logger.info(f"照片已保存: {filepath} ({len(data)} bytes)")
            return filepath
    except Exception as e:
        logger.warning(f"保存照片失败 {filename}: {e}")
    return None


def ensure_db_table():
    """确保数据库表存在（自动建表）"""
    if not Config.DB_ENABLED:
        return None

    if Config.DB_TYPE == "sqlite":
        import sqlite3
        db_path = Config.DB_NAME if Config.DB_NAME.endswith(".db") else f"{Config.DB_NAME}.db"
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS face_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                punch_time TEXT NOT NULL,
                verify_mode TEXT DEFAULT '',
                io_mode INTEGER DEFAULT 0,
                in_out TEXT DEFAULT '',
                door_mode TEXT DEFAULT '',
                temperature REAL DEFAULT 0.0,
                photo_base64 TEXT DEFAULT '',
                photo_path TEXT DEFAULT '',
                raw_data TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS device_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                device_model TEXT DEFAULT '',
                last_heartbeat TIMESTAMP,
                extra_info TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        logger.info(f"SQLite 数据库初始化完成: {db_path}")
        return db_path

    try:
        if Config.DB_TYPE == "mysql":
            import pymysql
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                database=Config.DB_NAME,
                charset="utf8mb4",
            )
        elif Config.DB_TYPE == "postgresql":
            import psycopg2
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                dbname=Config.DB_NAME,
            )
        else:
            return None

        with conn.cursor() as cur:
            # 打卡记录表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS face_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(24) NOT NULL,
                    user_id VARCHAR(64) NOT NULL,
                    punch_time VARCHAR(20) NOT NULL,
                    verify_mode VARCHAR(32) DEFAULT '',
                    io_mode INT DEFAULT 0,
                    in_out VARCHAR(8) DEFAULT '',
                    door_mode VARCHAR(32) DEFAULT '',
                    temperature DECIMAL(4,1) DEFAULT 0.0,
                    photo_base64 MEDIUMTEXT DEFAULT NULL,
                    photo_path VARCHAR(255) DEFAULT '',
                    raw_data JSON DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS device_info (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(24) UNIQUE NOT NULL,
                    device_model VARCHAR(16) DEFAULT '',
                    last_heartbeat TIMESTAMP NULL,
                    extra_info JSON DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        conn.close()
        logger.info(f"数据库连接成功: {Config.DB_TYPE}://{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        return True
    except ImportError as e:
        logger.warning(f"数据库驱动未安装: {e}，将使用 SQLite 降级")
        Config.DB_TYPE = "sqlite"
        return ensure_db_table()
    except Exception as e:
        logger.warning(f"数据库连接失败，将降级为无数据库模式: {e}")
        Config.DB_ENABLED = False
        return None


def store_log_to_db(dev_id: str, log_entry: dict):
    """将打卡记录存入数据库"""
    if not Config.DB_ENABLED:
        return

    try:
        if Config.DB_TYPE == "sqlite":
            import sqlite3
            db_path = Config.DB_NAME if Config.DB_NAME.endswith(".db") else f"{Config.DB_NAME}.db"
            conn = sqlite3.connect(db_path)
            conn.execute(
                """INSERT INTO face_logs 
                   (device_id, user_id, punch_time, verify_mode, io_mode, in_out, 
                    door_mode, temperature, photo_base64, photo_path, raw_data)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    dev_id,
                    log_entry.get("userId", ""),
                    log_entry.get("time", ""),
                    log_entry.get("verifyMode", ""),
                    log_entry.get("ioMode", 0),
                    log_entry.get("inOut", ""),
                    log_entry.get("doorMode", ""),
                    log_entry.get("temperature", 0.0),
                    log_entry.get("logPhoto", ""),
                    log_entry.get("_photo_path", ""),
                    json.dumps(log_entry),
                ),
            )
            conn.commit()
            conn.close()
        elif Config.DB_TYPE in ("mysql", "postgresql"):
            import pymysql
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                database=Config.DB_NAME,
                charset="utf8mb4",
            )
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO face_logs 
                       (device_id, user_id, punch_time, verify_mode, io_mode, in_out,
                        door_mode, temperature, photo_base64, photo_path, raw_data)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        dev_id,
                        log_entry.get("userId", ""),
                        log_entry.get("time", ""),
                        log_entry.get("verifyMode", ""),
                        log_entry.get("ioMode", 0),
                        log_entry.get("inOut", ""),
                        log_entry.get("doorMode", ""),
                        log_entry.get("temperature", 0.0),
                        log_entry.get("logPhoto", ""),
                        log_entry.get("_photo_path", ""),
                        json.dumps(log_entry, ensure_ascii=False),
                    ),
                )
            conn.commit()
            conn.close()
    except Exception as e:
        logger.error(f"写入数据库失败: {e}")


def update_device_heartbeat(dev_id: str, dev_model: str = ""):
    """更新设备心跳时间"""
    if not Config.DB_ENABLED:
        return
    try:
        if Config.DB_TYPE == "sqlite":
            import sqlite3
            db_path = Config.DB_NAME if Config.DB_NAME.endswith(".db") else f"{Config.DB_NAME}.db"
            conn = sqlite3.connect(db_path)
            conn.execute(
                """INSERT INTO device_info (device_id, device_model, last_heartbeat)
                   VALUES (?,?, CURRENT_TIMESTAMP)
                   ON CONFLICT(device_id) DO UPDATE SET
                   device_model=excluded.device_model, last_heartbeat=CURRENT_TIMESTAMP""",
                (dev_id, dev_model),
            )
            conn.commit()
            conn.close()
        elif Config.DB_TYPE == "mysql":
            import pymysql
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                database=Config.DB_NAME,
                charset="utf8mb4",
            )
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO device_info (device_id, device_model, last_heartbeat)
                       VALUES (%s, %s, NOW())
                       ON DUPLICATE KEY UPDATE
                       device_model=%s, last_heartbeat=NOW()""",
                    (dev_id, dev_model, dev_model),
                )
            conn.commit()
            conn.close()
        elif Config.DB_TYPE == "postgresql":
            import psycopg2
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                dbname=Config.DB_NAME,
            )
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO device_info (device_id, device_model, last_heartbeat)
                       VALUES (%s, %s, NOW())
                       ON CONFLICT(device_id) DO UPDATE SET
                       device_model=%s, last_heartbeat=NOW()""",
                    (dev_id, dev_model, dev_model),
                )
            conn.commit()
            conn.close()
    except Exception as e:
        logger.warning(f"更新设备心跳失败: {e}")


# ── 主路由：设备请求入口 ──────────────────────────────────────

@app.route("/", methods=["POST"])
@app.route("/api/device", methods=["POST"])
def device_endpoint():
    """
    设备 HTTP 请求入口。
    协议说明（见协议 2.2/2.5）：
    - 所有请求为 HTTP POST
    - HTTP Header 中包含 request_code, dev_id, dev_model, token 等字段
    - HTTP Body 为 JSON 格式，二进制数据用 Base64 编码
    """
    # ── 提取 HTTP 头部字段 ──
    # 注意：设备发送的 header 名称包含下划线（如 request_code, dev_id），
    # WSGI 规范（PEP 3333）要求过滤下划线 header（安全原因）。
    # 解决方案：
    #   1. 生产环境在 nginx 中设置 underscores_in_headers on;
    #   2. 或设备配置时将 header 名改为连字符格式（如 Request-Code）
    #   3. 此处同时接受 Body 中的 _header 字段作为备选
    #
    # 优先级：HTTP Header > Body._headers > 请求参数
    def _get_header(name: str) -> str:
        """从多个来源读取 header 值"""
        # 尝试 HTTP headers（连字符格式，WSGI 兼容）
        hdr_name = name.replace("_", "-")
        hdr_title = "-".join(w.capitalize() for w in hdr_name.split("-"))
        for variant in [name, hdr_name, hdr_title, hdr_name.upper()]:
            val = request.headers.get(variant, "")
            if val:
                return val
        return ""

    request_code = _get_header("request_code").strip().lower()
    dev_id = _get_header("dev_id")
    dev_model = _get_header("dev_model")
    token = _get_header("token")

    # 解析 Body
    # 协议规定 Content-Type 为 application/octet-stream，但 Body 是 JSON。
    # Flask 的 get_json() 默认只解析标准 JSON Content-Type，需强制解析。
    body = {}
    if request.data:
        try:
            body = json.loads(request.data)
        except Exception:
            # 兜底：尝试 get_json（如果 Content-Type 被正确设置）
            try:
                body = request.get_json(silent=True) or {}
            except Exception:
                pass

    # 如果 header 未命中，尝试从 Body 中读取（兼容设备直接 POST 的情况）
    if not request_code:
        request_code = (body.get("request_code") or "").strip().lower()
    if not dev_id:
        dev_id = body.get("dev_id") or ""
    if not dev_model:
        dev_model = body.get("dev_model") or ""
    if not token:
        token = body.get("token") or ""

    logger.info(
        f"收到设备请求 | request_code={request_code} | "
        f"dev_id={dev_id} | dev_model={dev_model}"
    )

    # ── Token 验证 ──
    if dev_id and not verify_token(dev_id, token):
        logger.warning(f"Token 验证失败: dev_id={dev_id}, token={token}")
        return make_response(
            "Authentication Failed", 403,
            {"response_code": "ERROR", "Content-Type": "application/octet-stream"}
        )

    # ── 路由请求类型 ──
    if request_code == "receive_cmd":
        return handle_receive_cmd(dev_id, dev_model, body, token)
    elif request_code == "send_cmd_result":
        return handle_send_cmd_result(dev_id, request.headers, body)
    elif request_code == "realtime_glog":
        return handle_realtime_glog(dev_id, body)
    elif request_code == "realtime_door_status":
        return handle_realtime_door_status(dev_id, body)
    elif request_code == "realtime_enroll_data":
        return handle_realtime_enroll_data(dev_id, body)
    else:
        logger.warning(f"未知请求代码: {request_code}")
        return make_response(
            json.dumps({"error": f"unknown request_code: {request_code}"}),
            400,
            {"response_code": "ERROR", "Content-Type": "application/octet-stream"}
        )


# ═══════════════════════════════════════════════════════════════════
#  1. 设备心跳处理 (receive_cmd)
# ═══════════════════════════════════════════════════════════════════

def handle_receive_cmd(dev_id: str, dev_model: str, body: dict, token: str):
    """
    处理设备心跳请求（协议 3.2.1）
    设备每隔一定时间发送 receive_cmd 查询是否有待执行指令。
    若无指令，返回 ERROR_NO_CMD。
    若有指令（如 GET_LOG_DATA），在应答 Header 中附带指令信息。
    """
    # 记录心跳
    update_device_heartbeat(dev_id, dev_model)

    device_time = body.get("time", "")
    logger.info(f"设备心跳 | dev_id={dev_id} | time={device_time}")

    # 检查是否有待下发的指令
    cmds = pending_commands.get(dev_id, [])
    if cmds:
        cmd = cmds.pop(0)  # FIFO
        trans_id = cmd.get("trans_id", "")
        cmd_code = cmd.get("cmd_code", "")
        cmd_param = cmd.get("cmd_param", {})

        logger.info(f"下发指令 | dev_id={dev_id} | trans_id={trans_id} | cmd_code={cmd_code}")

        resp = make_response(json.dumps(cmd_param))
        resp.headers["response_code"] = "OK"
        resp.headers["trans_id"] = str(trans_id)
        resp.headers["cmd_code"] = cmd_code
        resp.headers["Content-Type"] = "application/octet-stream"
        return resp

    # 无指令，返回 ERROR_NO_CMD（协议 3.2.1）
    resp = make_response("")
    resp.headers["response_code"] = "ERROR_NO_CMD"
    resp.headers["trans_id"] = ""
    resp.headers["cmd_code"] = ""
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp


# ═══════════════════════════════════════════════════════════════════
#  2. 设备执行结果处理 (send_cmd_result)
# ═══════════════════════════════════════════════════════════════════

def _get_body_or_header(body: dict, name: str, default="") -> str:
    """从 body 或 headers 中取值（兼容 WSGI 过滤下划线 header）"""
    val = body.get(name, default)
    if val:
        return val
    for variant in [name, name.replace("_", "-"), name.replace("_", "-").title(), name.upper()]:
        val = request.headers.get(variant, "")
        if val:
            return val
    return default


def handle_send_cmd_result(dev_id: str, headers: dict, body: dict):
    """
    处理设备回传的指令执行结果（协议 2.7/2.8）
    当设备执行完指令（如 GET_LOG_DATA），将结果通过 send_cmd_result 回传。
    """
    trans_id = _get_body_or_header(body, "trans_id")
    cmd_return_code = _get_body_or_header(body, "cmd_return_code")
    package_id = body.get("packageId", None)

    logger.info(
        f"指令执行结果 | dev_id={dev_id} | trans_id={trans_id} | "
        f"cmd_return_code={cmd_return_code} | packageId={package_id}"
    )

    # 处理 GET_LOG_DATA 结果
    if trans_id and trans_id.isdigit():
        cmd_type = _get_cmd_type_by_trans_id(dev_id, trans_id)
        if cmd_type == "GET_LOG_DATA":
            process_log_data(dev_id, body)

    # 返回确认（协议 2.8）
    resp = make_response("")
    resp.headers["response_code"] = "OK"
    resp.headers["trans_id"] = str(trans_id)
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp


# ═══════════════════════════════════════════════════════════════════
#  3. GET_LOG_DATA 指令拉取 & 解析
# ═══════════════════════════════════════════════════════════════════

def queue_get_log_data(dev_id: str, begin_time: str = "", end_time: str = ""):
    """
    向设备队列中添加 GET_LOG_DATA 指令。
    设备下次心跳时会将指令下发并执行。
    """
    if dev_id not in pending_commands:
        pending_commands[dev_id] = []

    # 用当前时间戳生成 trans_id
    trans_id = int(datetime.now().timestamp() * 1000) % 100000

    # 记录 trans_id → cmd_type 映射
    if not hasattr(app, "_cmd_trans_map"):
        app._cmd_trans_map = {}
    app._cmd_trans_map[f"{dev_id}_{trans_id}"] = "GET_LOG_DATA"

    pending_commands[dev_id].append({
        "trans_id": trans_id,
        "cmd_code": "GET_LOG_DATA",
        "cmd_param": {
            "newLog": 0,
            "beginTime": begin_time,
            "endTime": end_time,
            "clearMark": 0,
        },
    })

    logger.info(f"已加入 GET_LOG_DATA 指令队列 | dev_id={dev_id} | trans_id={trans_id}")
    return trans_id


def _get_cmd_type_by_trans_id(dev_id: str, trans_id: str) -> str:
    """根据 trans_id 查找指令类型"""
    if hasattr(app, "_cmd_trans_map"):
        return app._cmd_trans_map.get(f"{dev_id}_{trans_id}", "")
    return ""


def process_log_data(dev_id: str, body: dict):
    """
    解析 GET_LOG_DATA 的返回数据（协议 3.2.7）
    设备应答 body 格式：
    {
        "packageId": 0,
        "allLogCount": 26,
        "logsCount": 26,
        "logs": [{
            "userId": "1",
            "time": "yyyyMMddHHmmss",
            "verifyMode": "Card+Face",
            "ioMode": 1,
            "inOut": "In",
            "doorMode": "hand_open",
            "temperature": 37.1,
            "logPhoto": "Base64"
        }, ...]
    }
    """
    all_log_count = body.get("allLogCount", 0)
    logs_count = body.get("logsCount", 0)
    logs = body.get("logs", [])

    logger.info(
        f"解析打卡数据 | dev_id={dev_id} | "
        f"allLogCount={all_log_count} | logsCount={logs_count}"
    )

    saved_count = 0
    for log_entry in logs:
        # 提取结构化字段
        user_id = log_entry.get("userId", "")
        punch_time = log_entry.get("time", "")
        verify_mode = log_entry.get("verifyMode", "")
        io_mode = log_entry.get("ioMode", 0)
        in_out = log_entry.get("inOut", "")
        door_mode = log_entry.get("doorMode", "")
        temperature = log_entry.get("temperature", 0.0)
        photo_b64 = log_entry.get("logPhoto", "")

        # 解析照片 Base64
        photo_path = save_photo(dev_id, user_id, punch_time, photo_b64)
        log_entry["_photo_path"] = photo_path or ""

        # 记录日志
        logger.info(
            f"  打卡记录 | user={user_id} | time={punch_time} | "
            f"verify={verify_mode} | temp={temperature} | "
            f"hasPhoto={'yes' if photo_b64 else 'no'}"
        )

        # 存入数据库
        store_log_to_db(dev_id, log_entry)
        saved_count += 1

    logger.info(f"本次同步: 共处理 {saved_count} 条打卡记录")

    # 如果还有更多分包（packageId > 0），等待设备下次回传
    if body.get("packageId", 0) > 0:
        logger.info(f"还有分包数据待接收: packageId={body['packageId']}")


# ═══════════════════════════════════════════════════════════════════
#  4. 实时打卡记录推送处理 (realtime_glog)
# ═══════════════════════════════════════════════════════════════════

def handle_realtime_glog(dev_id: str, body: dict):
    """
    处理实时打卡记录推送（协议 4.1）
    当设备有新记录产生时，主动推送到服务器。
    """
    logger.info(f"实时打卡推送 | dev_id={dev_id}")

    # 解析并处理
    process_log_data(dev_id, {"logs": [body], "allLogCount": 1, "logsCount": 1})

    # 确认接收
    resp = make_response("")
    resp.headers["response_code"] = "OK"
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp


# ═══════════════════════════════════════════════════════════════════
#  5. 其他实时推送处理
# ═══════════════════════════════════════════════════════════════════

def handle_realtime_door_status(dev_id: str, body: dict):
    """处理实时门状态推送（协议 4.2）"""
    door_status = body.get("doorStatus", "")
    logger.info(f"实时门状态 | dev_id={dev_id} | status={door_status}")
    resp = make_response("")
    resp.headers["response_code"] = "OK"
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp


def handle_realtime_enroll_data(dev_id: str, body: dict):
    """处理实时登记数据推送（协议 4.3）"""
    user_id = body.get("userId", "")
    logger.info(f"实时登记数据 | dev_id={dev_id} | user_id={user_id}")
    resp = make_response("")
    resp.headers["response_code"] = "OK"
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp


# ═══════════════════════════════════════════════════════════════════
#  管理接口
# ═══════════════════════════════════════════════════════════════════

@app.route("/admin/trigger_get_log", methods=["POST"])
def admin_trigger_get_log():
    """
    管理接口：触发 GET_LOG_DATA 指令下发。
    请求体 JSON:
    {
        "dev_id": "设备ID",
        "begin_time": "20250401",   // 可选
        "end_time": "20250429"      // 可选
    }
    """
    data = request.get_json(silent=True) or {}
    dev_id = data.get("dev_id", "")
    if not dev_id:
        return jsonify({"error": "dev_id required"}), 400

    begin_time = data.get("begin_time", "")
    end_time = data.get("end_time", "")
    trans_id = queue_get_log_data(dev_id, begin_time, end_time)

    return jsonify({
        "status": "queued",
        "dev_id": dev_id,
        "trans_id": trans_id,
        "message": f"GET_LOG_DATA 指令已加入对 {dev_id} 的队列，下次心跳时将下发"
    })


@app.route("/admin/status", methods=["GET"])
def admin_status():
    """管理接口：查看服务器状态"""
    return jsonify({
        "status": "running",
        "pending_commands": {
            dev_id: len(cmds) for dev_id, cmds in pending_commands.items()
        },
        "device_count": len(pending_commands),
        "db_enabled": Config.DB_ENABLED,
        "db_type": Config.DB_TYPE,
    })


@app.route("/admin/logs", methods=["GET"])
def admin_query_logs():
    """管理接口：查询已存储的打卡记录（最近 100 条）"""
    dev_id = request.args.get("dev_id", "")
    limit = min(int(request.args.get("limit", "100")), 500)

    if not Config.DB_ENABLED:
        return jsonify({"error": "database not enabled"}), 503

    try:
        if Config.DB_TYPE == "sqlite":
            import sqlite3
            db_path = Config.DB_NAME if Config.DB_NAME.endswith(".db") else f"{Config.DB_NAME}.db"
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            if dev_id:
                rows = conn.execute(
                    "SELECT * FROM face_logs WHERE device_id=? ORDER BY created_at DESC LIMIT ?",
                    (dev_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM face_logs ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            conn.close()
            records = [dict(r) for r in rows]
        elif Config.DB_TYPE == "mysql":
            import pymysql
            conn = pymysql.connect(
                host=Config.DB_HOST, port=Config.DB_PORT,
                user=Config.DB_USER, password=Config.DB_PASS,
                database=Config.DB_NAME, charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            with conn.cursor() as cur:
                if dev_id:
                    cur.execute(
                        "SELECT * FROM face_logs WHERE device_id=%s ORDER BY created_at DESC LIMIT %s",
                        (dev_id, limit),
                    )
                else:
                    cur.execute(
                        "SELECT * FROM face_logs ORDER BY created_at DESC LIMIT %s",
                        (limit,),
                    )
                records = cur.fetchall()
            conn.close()
        else:
            records = []

        # 忽略照片 base64 数据以减小响应
        for r in records:
            if isinstance(r.get("photo_base64"), str) and len(r["photo_base64"]) > 100:
                r["photo_base64"] = f"(base64, {len(r['photo_base64'])} chars)"

        return jsonify({"total": len(records), "records": records})

    except Exception as e:
        logger.error(f"查询记录失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(Exception)
def handle_error(e):
    """全局异常处理"""
    logger.error(f"未处理异常: {traceback.format_exc()}")
    resp = make_response(json.dumps({"error": "Internal Server Error"}))
    resp.headers["response_code"] = "ERROR"
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp, 500


# ═══════════════════════════════════════════════════════════════════
#  启动入口
# ═══════════════════════════════════════════════════════════════════

def main():
    logger.info("=" * 60)
    logger.info("人脸设备 HTTP 协议中间件启动中...")
    logger.info(f"PID: {os.getpid()}")
    logger.info(f"监听: {Config.HOST}:{Config.PORT}")
    logger.info(f"数据库: {'启用 (' + Config.DB_TYPE + ')' if Config.DB_ENABLED else '禁用'}")
    logger.info(f"照片存储: {Config.PHOTO_DIR}")
    logger.info("=" * 60)

    # 初始化数据库
    ensure_db_table()

    # 创建必要目录
    ensure_dir(Config.PHOTO_DIR)
    ensure_dir(Config.CMD_DIR)

    # 以 gunicorn 或 Flask 开发服务器方式运行
    use_gunicorn = os.getenv("USE_GUNICORN", "false").lower() == "true"
    if use_gunicorn:
        # 由 gunicorn 命令启动，此处只导入 app
        return app
    else:
        app.run(host=Config.HOST, port=Config.PORT, debug=False)


if __name__ == "__main__":
    main()
