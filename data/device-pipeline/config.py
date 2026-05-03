#!/usr/bin/env python3
"""
设备管道中间件配置
==================
所有配置集中管理，支持环境变量覆盖。
设备注册表 device_registry 在此维护。
"""

import os
from typing import Optional


# ── 服务器配置 ─────────────────────────────────────────
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ── 设备密钥 ─────────────────────────────────────────
DEVICE_SECRET = os.getenv("DEVICE_SECRET", "")

# ── 路径配置 ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_PATH = os.getenv("MAPPING_PATH", "/home/agentuser/shared/member-device-mapping.json")
PHOTO_DIR = os.getenv("PHOTO_DIR", "/home/agentuser/shared/photos")
SAVE_PHOTOS = os.getenv("SAVE_PHOTOS", "true").lower() == "true"
STANDARDIZED_DIR = os.path.join(BASE_DIR, "output")
PENDING_FILE = os.path.join(BASE_DIR, "pending_unclaimed.json")
MOMO_NOTIFY_FILE = os.path.join(BASE_DIR, "momo_notifications.json")

# ── 数据库配置 ─────────────────────────────────────────
DB_ENABLED = os.getenv("DB_ENABLED", "true").lower() == "true"
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "device_pipeline")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")


# ── 设备注册表 ─────────────────────────────────────────
# 在此注册设备型号 → 适配器的映射
# 新增适配器时，修改此字典即可
DEVICE_REGISTRY = {
    "zwf-20":    "adapters.BSProtocolAdapter",
    "zwf-30":    "adapters.BSProtocolAdapter",
    "bs-100":    "adapters.BSProtocolAdapter",
    "bs-200":    "adapters.BSProtocolAdapter",
}
DEVICE_DEFAULT_ADAPTER = "adapters.BSProtocolAdapter"


def get_adapter_path(device_model: str) -> str:
    """根据设备型号获取适配器类路径"""
    key = device_model.strip().lower()
    return DEVICE_REGISTRY.get(key, DEVICE_DEFAULT_ADAPTER)


# ── 输出路径初始化 ─────────────────────────────────────

def ensure_dirs():
    """确保所有输出目录存在"""
    for d in [PHOTO_DIR, STANDARDIZED_DIR]:
        os.makedirs(d, exist_ok=True)
