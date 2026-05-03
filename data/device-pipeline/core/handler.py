#!/usr/bin/env python3
"""
管道处理器 (Pipeline Handler)
=============================
编排层：将设备请求 → 适配器解析 → 会员映射 → 标准化 → 持久化
是整个设备管道的核心业务流程编排器。

职责：
1. 根据设备型号选择对应适配器
2. 调用适配器解析请求为 RecordPayload
3. 通过 MemberMapper 匹配会员身份
4. 通过 Standardizer 生成标准化 JSON
5. 通过 Storage 持久化到 DB 和文件
6. 未匹配记录加入待认领队列
"""

import logging
from typing import Optional

# 核心模块
from member_mapper import MemberMapper
from core import standardizer as std
from core import storage as store

# 适配器
from adapters import BaseAdapter, BSProtocolAdapter
from config import DEVICE_SECRET, get_adapter_path

logger = logging.getLogger("device-pipeline.handler")


class PipelineHandler:
    """设备管道编排处理器"""

    def __init__(self):
        self.mapper = MemberMapper()
        self._adapter_cache = {}  # dev_model → adapter instance

    # ── 适配器管理 ────────────────────────────────────

    def get_adapter(self, device_model: str) -> BaseAdapter:
        """根据设备型号获取适配器实例（带缓存）"""
        model_key = device_model.strip().lower() if device_model else "__default__"
        if model_key not in self._adapter_cache:
            adapter_path = get_adapter_path(device_model)
            if "BSProtocolAdapter" in adapter_path:
                self._adapter_cache[model_key] = BSProtocolAdapter(DEVICE_SECRET)
            # ── 未来新增适配器在此扩展 ──
            # elif "BrandXAdapter" in adapter_path:
            #     self._adapter_cache[model_key] = BrandXAdapter(...)
            # elif "BrandYAdapter" in adapter_path:
            #     self._adapter_cache[model_key] = BrandYAdapter(...)
            else:
                self._adapter_cache[model_key] = BSProtocolAdapter(DEVICE_SECRET)

        return self._adapter_cache[model_key]

    def register_adapter(self, model_key: str, adapter: BaseAdapter):
        """手动注册适配器实例（测试/扩展用）"""
        self._adapter_cache[model_key.strip().lower()] = adapter

    # ── 核心流程 ──────────────────────────────────────

    def process_punch_record(self, adapter: BaseAdapter,
                             record_payload) -> dict:
        """处理一条打卡记录：匹配 → 标准化 → 持久化

        Args:
            adapter: 使用的适配器
            record_payload: RecordPayload 实例或字典

        Returns:
            {
                "matched": True/False,
                "member_id": "MEMBER_001" 或 None,
                "standardized": dict 或 None,
                "pending_key": "device_uid_time" 或 None,
            }
        """
        # 转为字典（兼容 RecordPayload 和 raw dict）
        if hasattr(record_payload, 'to_standard_dict'):
            record = record_payload.to_standard_dict()
            record['raw_data'] = getattr(record_payload, 'raw_data', {})
        else:
            record = dict(record_payload)

        dev_id = record.get("device_id", "")
        user_id = record.get("device_user_id", "") or record.get("userId", "")

        # 1. 保存照片
        photo_path = None
        photo_b64 = record.get("photo_base64", "") or record.get("logPhoto", "")
        if photo_b64:
            punch_time = record.get("punch_time", "") or record.get("time", "")
            photo_path = store.save_photo(dev_id, user_id, punch_time, photo_b64)
        record["_photo_path"] = photo_path or ""

        # 2. 持久化原始记录到 DB
        store.store_log(dev_id, record, photo_path or "")

        # 3. 会员匹配
        member_id = self.mapper.lookup(user_id)

        result = {
            "matched": False,
            "member_id": None,
            "standardized": None,
            "pending_key": None,
        }

        if member_id:
            # 已匹配 → 生成标准化数据
            member_info = self.mapper.get_member_info(member_id)
            if member_info:
                std_record = std.standardize(record, member_id, member_info)
                std.append_to_jsonl(std_record)
                result["matched"] = True
                result["member_id"] = member_id
                result["standardized"] = std_record
                logger.info("✅ 匹配: userId=%s → %s (%s)",
                            user_id, member_id, member_info.get("name", ""))
        else:
            # 未匹配 → 加入待认领
            pending_record = {**record, "device_id": dev_id}
            pending_list = self.mapper.add_pending(pending_record)
            result["pending_key"] = f"{dev_id}_{user_id}_{record.get('punch_time', '')}"
            logger.info("⚠️ 未匹配: userId=%s | 已加入待认领", user_id)

        return result

    def process_log_batch(self, adapter: BaseAdapter,
                          body: dict, headers: dict) -> dict:
        """批量处理 GET_LOG_DATA 结果（多条打卡记录）

        Args:
            adapter: 使用的适配器
            body: 请求 body
            headers: 请求 headers

        Returns:
            统计结果
        """
        logs = body.get("logs", [])
        if isinstance(logs, str):
            import json as _json
            logs = _json.loads(logs)

        stats = {
            "total": len(logs),
            "matched": 0,
            "unmatched": 0,
            "errors": 0,
        }

        for entry in logs:
            try:
                # 构造合租 payload（伪装为请求体之一条log）
                fake_body = {**body, **entry}
                record_payload = adapter.parse_request(fake_body, headers)
                result = self.process_punch_record(adapter, record_payload)
                if result["matched"]:
                    stats["matched"] += 1
                else:
                    stats["unmatched"] += 1
            except Exception as e:
                logger.error("处理批量记录失败: %s", e)
                stats["errors"] += 1

        # 如有未匹配，生成 Momo 通知
        if stats["unmatched"] > 0:
            pending = self.mapper.get_pending()
            if pending:
                logger.info("待认领总量: %d 条", len(pending))

        return stats

    def process_realtime_punch(self, adapter: BaseAdapter,
                               body: dict, headers: dict) -> dict:
        """处理单条实时打卡推送"""
        record_payload = adapter.parse_request(body, headers)
        return self.process_punch_record(adapter, record_payload)

    def reload_mapping(self):
        """重载会员映射表"""
        self.mapper.load_mapping()
        logger.info("会员映射已重载: %d 位会员, %d 位已绑定",
                    len(self.mapper.member_data),
                    len(self.mapper.device_to_member))
