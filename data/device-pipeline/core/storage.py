#!/usr/bin/env python3
"""
存储层 (Storage)
================
职责：
- 打卡记录持久化（SQLite / MySQL / PostgreSQL）
- 设备心跳状态记录
- 照片文件保存

未来切换存储引擎（如 PostgreSQL / ClickHouse），只改此模块。
"""

import json
import os
import base64
import logging
from datetime import datetime
from typing import Optional

from config import (
    DB_ENABLED, DB_TYPE, DB_HOST, DB_PORT, DB_NAME,
    DB_USER, DB_PASS, PHOTO_DIR, SAVE_PHOTOS,
)

logger = logging.getLogger("device-pipeline.storage")


# ── 照片保存 ─────────────────────────────────────────

def save_photo(dev_id: str, user_id: str, timestamp: str, photo_b64: str) -> Optional[str]:
    """保存 Base64 照片到本地文件"""
    if not SAVE_PHOTOS or not photo_b64:
        return None

    os.makedirs(PHOTO_DIR, exist_ok=True)
    safe_ts = timestamp.replace(":", "").replace(" ", "_")
    filename = f"{dev_id}_{user_id}_{safe_ts}.jpg"
    filepath = os.path.join(PHOTO_DIR, filename)

    try:
        data = _safe_base64_decode(photo_b64)
        if data:
            with open(filepath, "wb") as f:
                f.write(data)
            logger.info("照片已保存: %s (%d bytes)", filepath, len(data))
            return filepath
    except Exception as e:
        logger.warning("保存照片失败 %s: %s", filename, e)
    return None


def _safe_base64_decode(data: str) -> bytes:
    """安全 Base64 解码"""
    if not data:
        return b""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    try:
        return base64.b64decode(data)
    except Exception:
        return b""


# ── 数据库连接管理 ─────────────────────────────────────

def _get_conn():
    if not DB_ENABLED:
        return None
    if DB_TYPE == "sqlite":
        import sqlite3
        db_path = DB_NAME if DB_NAME.endswith(".db") else f"{DB_NAME}.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    elif DB_TYPE == "mysql":
        import pymysql
        return pymysql.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER,
            password=DB_PASS, database=DB_NAME, charset="utf8mb4",
        )
    elif DB_TYPE == "postgresql":
        import psycopg2
        return psycopg2.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER,
            password=DB_PASS, dbname=DB_NAME,
        )
    return None


def _param_style() -> str:
    """返回当前数据库的参数占位符风格"""
    if DB_TYPE == "sqlite":
        return "?"
    return "%s"


# ── 建表 ──────────────────────────────────────────────

def ensure_tables():
    """自动建表"""
    if not DB_ENABLED:
        logger.warning("数据库未启用，跳过建表")
        return

    conn = _get_conn()
    if not conn:
        return

    try:
        if DB_TYPE == "sqlite":
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
        elif DB_TYPE in ("mysql", "postgresql"):
            with conn.cursor() as cur:
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
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS device_info (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        device_id VARCHAR(24) UNIQUE NOT NULL,
                        device_model VARCHAR(16) DEFAULT '',
                        last_heartbeat TIMESTAMP NULL,
                        extra_info JSON DEFAULT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            conn.commit()
        logger.info("数据库表已就绪 (%s)", DB_TYPE)
    except Exception as e:
        logger.error("建表失败: %s", e)
    finally:
        conn.close()


# ── 打卡记录 CRUD ─────────────────────────────────────

def store_log(dev_id: str, record: dict, photo_path: str = ""):
    """写入一条打卡记录到数据库"""
    if not DB_ENABLED:
        return

    conn = _get_conn()
    if not conn:
        return

    try:
        user_id = record.get("device_user_id", "") or record.get("userId", "")
        punch_time = record.get("punch_time", "") or record.get("time", "")
        verify_mode = record.get("verify_mode", "") or record.get("verifyMode", "")
        io_mode = record.get("io_mode", 0) or record.get("ioMode", 0)
        in_out = record.get("in_out", "") or record.get("inOut", "")
        door_mode = record.get("door_mode", "") or record.get("doorMode", "")
        temperature = record.get("temperature", 0.0)
        photo_b64 = record.get("photo_base64", "") or record.get("logPhoto", "")

        if DB_TYPE == "sqlite":
            conn.execute("""
                INSERT INTO face_logs
                (device_id, user_id, punch_time, verify_mode, io_mode,
                 in_out, door_mode, temperature, photo_base64, photo_path, raw_data)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                dev_id, user_id, punch_time, verify_mode, io_mode,
                in_out, door_mode, temperature, photo_b64, photo_path,
                json.dumps(record, ensure_ascii=False),
            ))
        else:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO face_logs
                    (device_id, user_id, punch_time, verify_mode, io_mode,
                     in_out, door_mode, temperature, photo_base64, photo_path, raw_data)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    dev_id, user_id, punch_time, verify_mode, io_mode,
                    in_out, door_mode, temperature, photo_b64, photo_path,
                    json.dumps(record, ensure_ascii=False),
                ))
        conn.commit()
    except Exception as e:
        logger.error("DB 写入失败: %s", e)
    finally:
        conn.close()


def update_heartbeat(dev_id: str, dev_model: str = ""):
    """记录设备心跳时间"""
    if not DB_ENABLED:
        return
    conn = _get_conn()
    if not conn:
        return
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if DB_TYPE == "sqlite":
            conn.execute("""
                INSERT INTO device_info (device_id, device_model, last_heartbeat)
                VALUES (?,?,?)
                ON CONFLICT(device_id) DO UPDATE SET
                    device_model=excluded.device_model,
                    last_heartbeat=excluded.last_heartbeat
            """, (dev_id, dev_model, now))
        else:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO device_info (device_id, device_model, last_heartbeat)
                    VALUES (%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        device_model=VALUES(device_model),
                        last_heartbeat=VALUES(last_heartbeat)
                """, (dev_id, dev_model, now))
        conn.commit()
    except Exception as e:
        logger.warning("DB 心跳更新失败: %s", e)
    finally:
        conn.close()


def query_logs(device_id: str = "", user_id: str = "",
               limit: int = 50, offset: int = 0) -> dict:
    """查询打卡记录"""
    if not DB_ENABLED:
        return {"total": 0, "records": []}

    conn = _get_conn()
    if not conn:
        return {"total": 0, "records": []}

    try:
        conditions = []
        params = []
        if device_id:
            conditions.append("device_id=?")
            params.append(device_id)
        if user_id:
            conditions.append("user_id=?")
            params.append(user_id)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        if DB_TYPE == "sqlite":
            total_row = conn.execute(
                f"SELECT COUNT(*) as c FROM face_logs {where}", params
            ).fetchone()
            total = total_row[0] if total_row else 0
            rows = conn.execute(
                f"SELECT * FROM face_logs {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
        else:
            import pymysql
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(
                    f"SELECT COUNT(*) as c FROM face_logs {where}",
                    params
                )
                total = cur.fetchone()["c"]
                cur.execute(
                    f"SELECT * FROM face_logs {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                    params + [limit, offset]
                )
                rows = cur.fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "records": [dict(r) if not isinstance(r, dict) else r for r in rows],
        }
    finally:
        conn.close()


def list_devices() -> list:
    """列出已注册设备"""
    if not DB_ENABLED:
        return []
    conn = _get_conn()
    if not conn:
        return []
    try:
        if DB_TYPE == "sqlite":
            rows = conn.execute(
                "SELECT * FROM device_info ORDER BY last_heartbeat DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        else:
            import pymysql
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(
                    "SELECT * FROM device_info ORDER BY last_heartbeat DESC"
                )
                return cur.fetchall()
    finally:
        conn.close()
