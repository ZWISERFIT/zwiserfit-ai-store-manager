#!/usr/bin/env python3
"""
ZWF-20 设备管道中间件 — 统一入口
=================================
Flask Web 服务，提供：
  1. 设备协议入口 POST /        → 适配器路由
  2. 统一数据 API /api/v1/…     → 标准化数据接口
  3. 管理接口 /api/v1/…/admin   → 映射/待认领管理

架构：
  app.py (入口) → handler.py (编排) → adapters/* (设备协议)
                                     → member_mapper.py (映射)
                                     → core/standardizer.py (标准化)
                                     → core/storage.py (持久化)

新增设备品牌流程（无需修改 app.py）：
  1. 在 adapters/ 下新建 BrandXAdapter（继承 BaseAdapter）
  2. 在 config.py 的 DEVICE_REGISTRY 中添加映射
  3. 重启服务

Author: Tristan (技术架构官)
"""

import os
import json
import logging
from datetime import datetime, timezone

from flask import Flask, request, jsonify

from config import (
    HOST, PORT, DEBUG, STANDARDIZED_DIR, ensure_dirs,
)
from core import PipelineHandler, standardizer as std, storage as store
from adapters import BSProtocolAdapter

# ── 初始化 ─────────────────────────────────────────
ensure_dirs()
store.ensure_tables()

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] device-pipeline: %(message)s",
)
logger = logging.getLogger("device-pipeline")

app = Flask(__name__)
handler = PipelineHandler()

# ── 设备指令队列 ──────────────────────────────────
pending_commands: dict[str, list[dict]] = {}
_cmd_trans_map: dict[str, str] = {}


# ================================================================
#  一、设备协议入口（POST /）
# ================================================================

@app.route("/", methods=["POST"])
def device_entry():
    """通用设备请求入口，自动路由到对应适配器

    流程：
      1. 提取设备型号，选择适配器
      2. 验证 Token
      3. 判断请求类型（心跳/打卡/门状态/注册数据）
      4. 调用对应处理逻辑
    """
    body_parsed = _parse_body(request)
    headers = _get_headers(request)

    dev_id = headers.get("dev_id") or body_parsed.get("dev_id", "")
    dev_model = headers.get("dev_model") or body_parsed.get("dev_model", "")

    # 选择适配器
    adapter = handler.get_adapter(dev_model)
    adapter_info = adapter.get_info()
    logger.info("← %s | dev=%s model=%s adapter=%s",
                _get_request_code(body_parsed), dev_id, dev_model, adapter_info.name)

    # Token 验证
    req_token = (body_parsed.get("token", "") or headers.get("token", "") or "")
    if dev_id and not adapter.verify_token(dev_id, req_token):
        logger.warning("Token 验证失败: dev_id=%s", dev_id)
        return _build_response(*adapter.build_error_response(403))

    # 请求分类
    classify = adapter.classify_request(body_parsed, headers)

    try:
        if classify == "heartbeat":
            return _handle_heartbeat(dev_id, dev_model, adapter, body_parsed, headers)
        elif classify == "punch_realtime":
            return _handle_punch_realtime(adapter, body_parsed, headers)
        elif classify == "cmd_result":
            return _handle_cmd_result(adapter, body_parsed, headers)
        elif classify == "door_status":
            return _handle_door_status(dev_id, body_parsed)
        elif classify == "enroll_data":
            return _handle_enroll_data(dev_id, body_parsed)
        else:
            logger.warning("未知请求类型: %s", classify)
            return _build_response(*adapter.build_error_response(400))
    except Exception as e:
        logger.error("设备请求处理异常: %s", e, exc_info=True)
        return _build_response(*adapter.build_error_response(500))


def _handle_heartbeat(dev_id, dev_model, adapter, body, headers):
    """设备心跳：记录在线状态，返回待执行指令"""
    device_time = body.get("time", "")
    logger.info("心跳 | dev=%s time=%s", dev_id, device_time)

    store.update_heartbeat(dev_id, dev_model)

    # 检查指令队列
    if dev_id in pending_commands and pending_commands[dev_id]:
        cmd = pending_commands[dev_id].pop(0)
        logger.info("下发指令 | dev=%s | %s", dev_id, cmd.get("cmd_code"))
        return _build_response(*adapter.build_cmd_response(cmd))

    return _build_response(*adapter.build_no_cmd_response())


def _handle_punch_realtime(adapter, body, headers):
    """实时打卡推送"""
    logger.info("实时打卡 | dev=%s", adapter.extract_device_id(body, headers))
    result = handler.process_realtime_punch(adapter, body, headers)
    logger.info("  结果: matched=%s", result.get("matched"))
    return _build_response(*adapter.build_ack_response({}))


def _handle_cmd_result(adapter, body, headers):
    """指令执行结果（包含 GET_LOG_DATA 打卡数据回传）"""
    trans_id = str(body.get("trans_id", "") or "")
    cmd_return_code = str(body.get("cmd_return_code", "") or "")
    package_id = body.get("packageId")

    logger.info("指令结果 | trans=%s return=%s package=%s",
                trans_id, cmd_return_code, package_id)

    # 判断是否为 GET_LOG_DATA 结果
    is_log_result = (package_id is not None or "logs" in body)

    if is_log_result:
        stats = handler.process_log_batch(adapter, body, headers)
        logger.info("  批量处理: total=%d matched=%d unmatched=%d errors=%d",
                    stats["total"], stats["matched"], stats["unmatched"], stats["errors"])

    return _build_response(*adapter.build_ack_response({}))


def _handle_door_status(dev_id, body):
    """门状态推送"""
    door_status = body.get("doorStatus", "")
    logger.info("门状态 | dev=%s status=%s", dev_id, door_status)
    return _build_response(*(BSProtocolAdapter().build_ack_response({})))


def _handle_enroll_data(dev_id, body):
    """注册数据推送"""
    logger.info("注册数据 | dev=%s", dev_id)
    return _build_response(*(BSProtocolAdapter().build_ack_response({})))


# ================================================================
#  二、指令管理（下发 GET_LOG_DATA 等指令）
# ================================================================

def queue_get_log_data(dev_id: str, begin_time: str = "", end_time: str = ""):
    """向设备指令队列添加 GET_LOG_DATA"""
    if dev_id not in pending_commands:
        pending_commands[dev_id] = []

    trans_id = int(datetime.now().timestamp() * 1000) % 100000
    _cmd_trans_map[f"{dev_id}_{trans_id}"] = "GET_LOG_DATA"

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
    logger.info("指令已入队: GET_LOG_DATA | dev=%s | trans=%s", dev_id, trans_id)
    return trans_id


# ================================================================
#  三、统一数据 API（供 Ethan、Shuyu、Stella 调用）
# ================================================================

@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "device-pipeline",
        "version": "3.0",
        "adapters": [handler.get_adapter(m).get_info().name
                     for m in ["zwf-20"]],
        "db_enabled": store.DB_ENABLED if hasattr(store, 'DB_ENABLED') else True,
        "db_type": "sqlite",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ── 3.1 标准化数据查询（Ethan 用） ──────────────────

@app.route("/api/v1/standardized", methods=["GET"])
def get_standardized():
    """获取标准化打卡数据"""
    date_str = request.args.get("date", "")
    if not date_str:
        date_str = datetime.now().strftime("%Y%m%d")

    records = std.query_by_date(date_str)
    return jsonify({
        "code": 0,
        "data": {
            "date": date_str,
            "total": len(records),
            "records": records,
            "standard_version": "v2.0",
        }
    })


# ── 3.2 原始打卡记录查询（Shuyu / Stella 用） ──────

@app.route("/api/v1/logs", methods=["GET"])
def query_logs():
    """查询原始打卡记录"""
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    device_id = request.args.get("device_id", "")
    user_id = request.args.get("user_id", "")
    result = store.query_logs(device_id, user_id, limit, offset)
    return jsonify({"code": 0, "data": result})


# ── 3.3 设备列表 ──────────────────────────────────

@app.route("/api/v1/devices", methods=["GET"])
def list_devices():
    """列出已注册设备"""
    devices = store.list_devices()
    fallback = [{"device_id": k, "adapter": "auto", "pending_cmds": len(v)}
                for k, v in pending_commands.items()]
    return jsonify({
        "code": 0,
        "data": {
            "total": len(devices) or len(fallback),
            "devices": devices or fallback,
        }
    })


# ================================================================
#  四、会员映射管理 API
# ================================================================

@app.route("/api/v1/mapping/reload", methods=["POST"])
def reload_mapping():
    """重载会员映射表"""
    handler.reload_mapping()
    return jsonify({
        "code": 0,
        "message": "ok",
        "data": {
            "total_members": len(handler.mapper.member_data),
            "bound_members": len(handler.mapper.device_to_member),
        }
    })


@app.route("/api/v1/mapping/register", methods=["POST"])
def register_mapping():
    """注册设备 userId → 会员编号 映射"""
    data = request.get_json(silent=True) or {}
    device_user_id = data.get("device_user_id", "")
    member_id = data.get("member_id", "")
    updated_by = data.get("updated_by", "api")

    if not device_user_id or not member_id:
        return jsonify({"code": 2002, "message": "缺少 device_user_id 或 member_id"}), 400

    success, msg = handler.mapper.register_mapping(
        device_user_id, member_id, updated_by
    )
    return jsonify({"code": 0 if success else 2003, "message": msg})


@app.route("/api/v1/mapping/info", methods=["GET"])
def mapping_info():
    """查看映射统计"""
    maps = {
        dev_id: {
            "member_id": mid,
            "name": handler.mapper.member_data.get(mid, {}).get("name", ""),
        }
        for dev_id, mid in handler.mapper.device_to_member.items()
    }
    return jsonify({
        "code": 0,
        "data": {
            "total_members": len(handler.mapper.member_data),
            "bound_count": len(handler.mapper.device_to_member),
            "unbound_count": len(handler.mapper.member_data) - len(handler.mapper.device_to_member),
            "maps": maps,
        }
    })


# ================================================================
#  五、待认领 & Momo 通知 API
# ================================================================

@app.route("/api/v1/pending", methods=["GET"])
def get_pending():
    """查看待认领列表"""
    pending = handler.mapper.get_pending()
    return jsonify({
        "code": 0,
        "data": {
            "total": len(pending),
            "records": pending,
        }
    })


@app.route("/api/v1/pending/claim", methods=["POST"])
def claim_pending():
    """认领一条待认领记录"""
    data = request.get_json(silent=True) or {}
    device_user_id = data.get("device_user_id", "")
    member_id = data.get("member_id", "")
    match_key = data.get("match_key", "")
    updated_by = data.get("updated_by", "momo")

    if not device_user_id or not member_id:
        return jsonify({"code": 2002, "message": "缺少 device_user_id 或 member_id"}), 400

    success, msg = handler.mapper.register_mapping(
        device_user_id, member_id, updated_by
    )
    if not success:
        return jsonify({"code": 2003, "message": msg}), 400

    # 重跑待认领记录（标准化未匹配的历史记录）
    pending = handler.mapper.get_pending()
    replayed = 0
    for r in pending:
        if r.get("userId") == device_user_id:
            member_info = handler.mapper.get_member_info(member_id)
            if member_info:
                std_record = std.standardize(r, member_id, member_info)
                std.append_to_jsonl(std_record)
                replayed += 1

    # 清理已处理的待认领
    to_clear = [r["_match_key"] for r in pending
                if r.get("userId") == device_user_id]
    if to_clear:
        handler.mapper.clear_pending(to_clear)

    return jsonify({
        "code": 0,
        "message": "ok",
        "data": {
            "mapping": f"{device_user_id} → {member_id}",
            "replay_count": replayed,
        }
    })


@app.route("/api/v1/pending/notify-momo", methods=["POST"])
def notify_momo():
    """生成 Momo 通知"""
    notification = handler.mapper.notify_momo()
    if notification:
        return jsonify({"code": 0, "message": "notification sent", "data": notification})
    return jsonify({"code": 0, "message": "no pending records", "data": None})


# ================================================================
#  六、指令下发 API
# ================================================================

@app.route("/api/v1/trigger_get_log", methods=["POST", "GET"])
def trigger_get_log():
    """触发 GET_LOG_DATA 指令下发"""
    if request.method == "GET":
        dev_id = request.args.get("dev_id", "")
    else:
        data = request.get_json(silent=True) or {}
        dev_id = data.get("dev_id", "")

    if not dev_id:
        return jsonify({"code": 2002, "message": "缺少 dev_id"}), 400

    trans_id = queue_get_log_data(dev_id)
    return jsonify({"code": 0, "message": "ok", "data": {"trans_id": trans_id}})


# ================================================================
#  工具函数
# ================================================================

def _parse_body(request_obj) -> dict:
    """解析请求 body"""
    if request_obj.data:
        try:
            return json.loads(request_obj.data)
        except Exception:
            try:
                return request_obj.get_json(silent=True) or {}
            except Exception:
                return {}
    return {}


def _get_headers(request_obj) -> dict:
    """提取请求 headers（小写 key，便于统一处理）"""
    result = {}
    for k, v in request_obj.headers.items():
        result[k.lower()] = v
    return result


def _get_request_code(body: dict) -> str:
    return body.get("request_code", "-")


def _build_response(body: str, status: int, headers: dict) -> tuple:
    """构建标准响应"""
    resp_headers = {
        "Content-Type": "application/octet-stream",
    }
    resp_headers.update(headers)
    return body, status, resp_headers


# ================================================================
#  入口
# ================================================================

if __name__ == "__main__":
    logger.info("⚡ 设备管道中间件 v3.0 启动: %s:%d", HOST, PORT)
    logger.info("   适配器: %s", "BSProtocolAdapter (zwf-20/bs-100/bs-200)")
    logger.info("   数据目录: output/, photos/")
    logger.info("   会员映射: %d 位", len(handler.mapper.member_data))
    app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)
