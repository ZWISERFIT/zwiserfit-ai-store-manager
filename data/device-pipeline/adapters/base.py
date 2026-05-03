#!/usr/bin/env python3
"""
设备适配器基类 - 所有品牌适配器必须实现的接口
===============================================
新增品牌适配器只需继承 BaseAdapter 并实现以下方法：
  - parse_request(body, headers)  → 统一的 RecordPayload
  - build_response(ack_type, ...) → 设备对应格式的 HTTP 响应
  - device_id(request)            → 从请求中提取设备标识
  - device_model()                → 设备型号字符串

配置注册：
  在 device_registry.yaml 或 config.py 中注册设备型号→适配器的映射
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class RecordPayload:
    """标准化打卡记录负载（适配器输出，标准器输入）

    所有适配器将设备私有协议解析为本格式后，交给 Standardizer 处理。
    字段设计包含 ZWF-20 协议常用字段，品牌特定字段放在 extra 中。
    """
    # 核心字段（必须）
    device_id: str                          # 设备ID，如 ZWF20-001
    device_user_id: str                     # 设备端用户ID，如 "1", "1002"
    punch_time: str                         # 打卡时间，格式 "YYYY-MM-DD HH:MM:SS"
    verify_mode: str = ""                   # 验证方式: face/fingerprint/card/password/...

    # 门状态字段（可选）
    io_mode: int = 0                        # I/O 模式（BS协议用）
    in_out: str = ""                        # 出入方向: in/out
    door_mode: str = ""                     # 门控模式
    temperature: float = 0.0                # 体温

    # 媒体字段（可选）
    photo_base64: str = ""                  # 抓拍照片（Base64）
    photo_path: str = ""                    # 本地保存路径（处理后填充）

    # 品牌私有数据（原样保留，不影响标准化）
    extra: dict = field(default_factory=dict)

    # 来源信息（框架填充）
    adapter_name: str = ""                  # 适配器名称
    raw_data: dict = field(default_factory=dict)  # 原始请求数据

    def to_standard_dict(self) -> dict:
        """转为基础字典（不包含 extra/raw_data）"""
        return {k: v for k, v in asdict(self).items()
                if k not in ("extra", "raw_data")}


@dataclass
class AdapterInfo:
    """适配器元信息"""
    name: str                               # 适配器名称
    protocol: str                           # 协议名: "BS/HTTP", "MQTT", "WebSocket"...
    manufacturer: str                       # 设备厂商
    version: str = "1.0"                    # 适配器版本
    supported_models: list = field(default_factory=list)  # 支持的设备型号列表


class BaseAdapter(ABC):
    """设备适配器基类"""

    @abstractmethod
    def get_info(self) -> AdapterInfo:
        """返回适配器元信息"""
        ...

    @abstractmethod
    def parse_request(self, body: dict, headers: dict) -> RecordPayload:
        """将设备私有协议请求解析为统一的 RecordPayload

        Args:
            body: 请求 body（已 JSON 解析）
            headers: 请求 headers（原始字典）

        Returns:
            RecordPayload: 标准化打卡记录

        Raises:
            AdapterError: 解析失败时抛出
        """
        ...

    @abstractmethod
    def build_ack_response(self, record: RecordPayload) -> tuple:
        """生成设备期望的 HTTP 确认响应

        Returns:
            (body_str, status_code, headers_dict)
        """
        ...

    @abstractmethod
    def extract_device_id(self, body: dict, headers: dict) -> str:
        """从请求中提取设备唯一标识"""
        ...

    @abstractmethod
    def extract_device_model(self, body: dict, headers: dict) -> str:
        """从请求中提取设备型号"""
        ...

    def heartbeat(self, body: dict, headers: dict) -> tuple:
        """处理设备心跳（可选覆写）

        默认返回无指令响应。如需在心跳中添加指令下发逻辑，覆写此方法。

        Returns:
            (body_str, status_code, headers_dict)
        """
        return "", 200, {}


class AdapterError(Exception):
    """适配器处理错误"""
    pass
