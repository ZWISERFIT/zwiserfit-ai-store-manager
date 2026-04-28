"""
ZWF-20 门禁设备心跳中间件
========================
腾讯云 Flask 部署
接收设备心跳，实现 receive_cmd 与 ERROR_NO_CMD 应答
"""

import os
import json
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 设备注册表（生产环境应使用持久存储）
DEVICE_REGISTRY: dict[str, dict] = {}

# 日志
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger("device-pipeline")

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 设备注册
# ---------------------------------------------------------------------------
def register_device(device_id: str) -> dict:
    """注册或更新设备信息"""
    now = datetime.now(timezone.utc).isoformat()
    if device_id not in DEVICE_REGISTRY:
        DEVICE_REGISTRY[device_id] = {
            "device_id": device_id,
            "first_seen": now,
            "last_heartbeat": now,
            "status": "online",
            "heartbeat_count": 0,
        }
    DEVICE_REGISTRY[device_id]["last_heartbeat"] = now
    DEVICE_REGISTRY[device_id]["heartbeat_count"] += 1
    DEVICE_REGISTRY[device_id]["status"] = "online"
    return DEVICE_REGISTRY[device_id]

# ---------------------------------------------------------------------------
# API 路由
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "device-pipeline",
        "devices_online": len(DEVICE_REGISTRY),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/v1/heartbeat", methods=["POST"])
def heartbeat():
    """
    接收设备心跳
    ---
    请求体:
        device_id: str  设备唯一标识
        timestamp: str  ISO8601 时间戳
        status: str     设备状态
        firmware: str   固件版本（可选）
    """
    data = request.get_json(silent=True)
    if not data or "device_id" not in data:
        return jsonify({"code": 2002, "message": "缺少 device_id"}), 400

    device_id = data["device_id"]
    register_device(device_id)
    logger.info("设备心跳: %s | 状态: %s", device_id, data.get("status", "unknown"))

    return jsonify({
        "code": 0,
        "message": "ok",
        "data": {
            "device_id": device_id,
            "heartbeat_interval_s": 30,
            "server_time": datetime.now(timezone.utc).isoformat(),
        },
    })


@app.route("/api/v1/receive_cmd", methods=["POST"])
def receive_cmd():
    """
    接收设备命令请求
    返回 ERROR_NO_CMD —— 当前无待执行命令
    ---
    请求体:
        device_id: str  设备标识
        cmd_type: str   请求的命令类型
        cmd_id: str     命令请求ID（可选）
    """
    data = request.get_json(silent=True)
    if not data or "device_id" not in data:
        return jsonify({"code": 2002, "message": "缺少 device_id"}), 400

    device_id = data["device_id"]
    cmd_type = data.get("cmd_type", "unknown")
    cmd_id = data.get("cmd_id", "")

    # 检查设备是否已注册
    if device_id not in DEVICE_REGISTRY:
        return jsonify({"code": 2001, "message": "设备未注册"}), 404

    logger.info("命令请求: %s | 类型: %s | cmd_id: %s", device_id, cmd_type, cmd_id)

    # ERROR_NO_CMD: 当前无待执行命令
    return jsonify({
        "code": 0,
        "message": "ok",
        "data": {
            "cmd": None,
            "error_no_cmd": True,
            "error_code": "ERROR_NO_CMD",
            "error_description": "当前无待执行命令",
            "next_poll_interval_s": 30,
            "device_id": device_id,
        },
    })


@app.route("/api/v1/devices", methods=["GET"])
def list_devices():
    """列出所有已注册设备"""
    return jsonify({
        "code": 0,
        "data": {
            "total": len(DEVICE_REGISTRY),
            "devices": list(DEVICE_REGISTRY.values()),
        },
    })

# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("启动设备管道中间件: %s:%d", HOST, PORT)
    app.run(host=HOST, port=PORT, debug=DEBUG)
