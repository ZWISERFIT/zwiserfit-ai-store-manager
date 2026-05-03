#!/usr/bin/env python3
"""
BS 通讯协议适配器（云开门管家 / ZWF-20 系列设备）
==============================================
实现了 BS 通讯协议的 HTTP/JSON 版本，涵盖：
- 3.2.1 设备心跳（ReceiveCmd）：上报设备信息，轮询指令
- 3.2.7 打卡数据回传（SendCmdResult）：GET_LOG_DATA 结果
- 4.1 实时打卡推送（RealtimeGlog）：设备主动推送
- 4.2 实时门状态推送（RealtimeDoorStatus）
- 4.3 实时注册数据推送（RealtimeEnrollData）

协议文档参考：BS_通讯协议.pdf（SDK 2.0）
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Optional

from .base import BaseAdapter, AdapterInfo, RecordPayload, AdapterError

logger = logging.getLogger("device-pipeline.adapters.bs_protocol")


class BSProtocolAdapter(BaseAdapter):
    """BS 通讯协议适配器"""

    # ── 协议常量 ───────────────────────────────────────
    REQUEST_CODES = {
        "receive_cmd":        "heartbeat",        # 3.2.1 设备心跳
        "send_cmd_result":    "cmd_result",       # 2.7/2.8 指令结果
        "realtime_glog":      "punch_realtime",   # 4.1 实时打卡
        "realtime_door_status": "door_status",    # 4.2 门状态
        "realtime_enroll_data": "enroll_data",    # 4.3 注册数据
    }

    VERIFY_MODE_MAP = {
        "0": "password",
        "1": "fingerprint",
        "2": "card",
        "3": "face",
        "4": "multi_mode",
        "5": "face_and_fingerprint",
        "6": "face_and_card",
        "7": "face_and_password",
        "":  "unknown",
        "FACE_D_100": "face",       # 人脸识别模式标识
    }

    def __init__(self, device_secret: str = ""):
        self.device_secret = device_secret

    # ── 元信息 ─────────────────────────────────────────

    def get_info(self) -> AdapterInfo:
        return AdapterInfo(
            name="BSProtocolAdapter",
            protocol="BS HTTP/JSON",
            manufacturer="云开门管家 / BS",
            version="2.0",
            supported_models=["ZWF-20", "ZWF-30", "BS-100", "BS-200"],
        )

    # ── 设备标识提取 ──────────────────────────────────

    def extract_device_id(self, body: dict, headers: dict) -> str:
        return self._extract_field("dev_id", body, headers)

    def extract_device_model(self, body: dict, headers: dict) -> str:
        return self._extract_field("dev_model", body, headers)

    # ── 请求分类 ──────────────────────────────────────

    def classify_request(self, body: dict, headers: dict) -> str:
        """判断请求类型: heartbeat / cmd_result / punch_realtime / door_status / enroll_data / unknown

        兼容多种请求码格式:
          - snake_case:  receive_cmd, send_cmd_result, realtime_glog
          - PascalCase:  ReceiveCmd, SendCmdResult, RealtimeGlog
        """
        raw_code = self._extract_field("request_code", body, headers).strip()

        # 先尝试精确匹配
        lower_code = raw_code.lower()
        result = self.REQUEST_CODES.get(lower_code)
        if result:
            return result

        # 尝试将 PascalCase 转为 snake_case
        import re
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', raw_code).lower()
        result = self.REQUEST_CODES.get(snake)
        if result:
            return result

        return "unknown"

    # ── 核心：解析请求 → RecordPayload ────────────────

    def parse_request(self, body: dict, headers: dict) -> RecordPayload:
        classify = self.classify_request(body, headers)

        if classify in ("punch_realtime",):
            return self._parse_realtime_punch(body, headers)

        # cmd_result 可能是打卡数据回传（GET_LOG_DATA 结果）
        if classify == "cmd_result":
            cmd_return_code = str(body.get("cmd_return_code", "") or "")
            package_id = body.get("packageId")

            # packageId 存在说明是 GET_LOG_DATA 的数据分包
            if package_id is not None or "logs" in body:
                return self._parse_log_result(body, headers)

        # 其他类型（心跳、门状态、注册数据、非打卡指令结果）不产生活动记录
        raise AdapterError(f"请求类型 '{classify}' 不产生活动记录")

    def _parse_realtime_punch(self, body: dict, headers: dict) -> RecordPayload:
        """解析 4.1 实时打卡推送"""
        dev_id = self.extract_device_id(body, headers)
        verify_mode_raw = str(body.get("verifyMode", "") or "")

        return RecordPayload(
            device_id=dev_id,
            device_user_id=str(body.get("userId", "")),
            punch_time=str(body.get("time", "")),
            verify_mode=self.VERIFY_MODE_MAP.get(verify_mode_raw, verify_mode_raw),
            io_mode=int(body.get("ioMode", 0)),
            in_out=str(body.get("inOut", "")),
            door_mode=str(body.get("doorMode", "")),
            temperature=float(body.get("temperature", 0.0)),
            photo_base64=str(body.get("logPhoto", "")),
            adapter_name=self.get_info().name,
            raw_data=body,
        )

    def _parse_log_result(self, body: dict, headers: dict) -> RecordPayload:
        """解析 3.2.7 GET_LOG_DATA 结果中的第一条记录

        注意：一个响应可能包含多条记录。本解析器每次处理一条。
        外部循环调用 BSPipelineHandler 处理每一条。
        """
        logs = body.get("logs", [])
        if not logs:
            raise AdapterError("GET_LOG_DATA 结果中无打卡记录")

        # 取第一条（外部应逐条调用）
        entry = logs[0] if isinstance(logs, list) else logs
        if isinstance(entry, str):
            entry = json.loads(entry)

        dev_id = self.extract_device_id(body, headers)
        verify_mode_raw = str(entry.get("verifyMode", "") or "")

        return RecordPayload(
            device_id=dev_id,
            device_user_id=str(entry.get("userId", "")),
            punch_time=str(entry.get("time", "")),
            verify_mode=self.VERIFY_MODE_MAP.get(verify_mode_raw, verify_mode_raw),
            io_mode=int(entry.get("ioMode", 0)),
            in_out=str(entry.get("inOut", "")),
            door_mode=str(entry.get("doorMode", "")),
            temperature=float(entry.get("temperature", 0.0)),
            photo_base64=str(entry.get("logPhoto", "")),
            adapter_name=self.get_info().name,
            raw_data=entry,
            extra={
                "all_log_count": body.get("allLogCount", 0),
                "package_id": body.get("packageId"),
                "trans_id": str(body.get("trans_id", "") or ""),
            },
        )

    # ── 生成设备响应 ──────────────────────────────────

    def build_ack_response(self, record: RecordPayload) -> tuple:
        """标准打卡接收确认响应"""
        return "", 200, {
            "response_code": "OK",
            "Content-Type": "application/octet-stream",
        }

    def build_no_cmd_response(self) -> tuple:
        """无指令响应（心跳轮询时返回）"""
        return "", 200, {
            "response_code": "ERROR_NO_CMD",
            "trans_id": "",
            "cmd_code": "",
            "Content-Type": "application/octet-stream",
        }

    def build_cmd_response(self, cmd: dict) -> tuple:
        """指令下发响应（心跳回复时返回待执行指令）"""
        body = json.dumps(cmd.get("cmd_param", {}))
        return body, 200, {
            "response_code": "OK",
            "trans_id": str(cmd.get("trans_id", "")),
            "cmd_code": cmd.get("cmd_code", ""),
            "Content-Type": "application/octet-stream",
        }

    def build_error_response(self, status_code: int = 400) -> tuple:
        return "", status_code, {
            "response_code": "ERROR",
            "Content-Type": "application/octet-stream",
        }

    # ── Token 验证 ─────────────────────────────────────

    def verify_token(self, dev_id: str, token: str) -> bool:
        """MD5(dev_id + secret) 验签"""
        if not self.device_secret:
            return True  # 未配置密钥时跳过验证
        expected = hashlib.md5(
            (dev_id + self.device_secret).encode()
        ).hexdigest().upper()
        return token == expected

    # ── 工具 ─────────────────────────────────────────

    @staticmethod
    def _extract_field(name: str, body: dict, headers: dict) -> str:
        """从 body（优先）和 headers 提取字段"""
        val = body.get(name, "")
        if val:
            return str(val)
        for variant in [name, name.replace("_", "-"), name.replace("_", "-").title(), name.upper()]:
            val = headers.get(variant, "")
            if val:
                return str(val)
        return ""
