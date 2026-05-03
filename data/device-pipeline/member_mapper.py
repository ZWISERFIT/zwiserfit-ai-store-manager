#!/usr/bin/env python3
"""
会员-设备映射模块
=================
职责：设备 userId → 会员编号 映射、标准化JSON生成、未匹配待认领管理
Author: Tristan (技术架构官)
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger("device-pipeline.mapper")

# 路径配置
MAPPING_PATH = "/home/agentuser/shared/member-device-mapping.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STANDARDIZED_DIR = os.path.join(BASE_DIR, "output")
PENDING_FILE = os.path.join(BASE_DIR, "pending_unclaimed.json")
MOMO_NOTIFY_FILE = os.path.join(BASE_DIR, "momo_notifications.json")


class MemberMapper:
    """会员映射管理器"""

    def __init__(self):
        self.member_data = {}       # member_id → 会员完整信息
        self.device_to_member = {}  # device_user_id → member_id
        self.load_mapping()

    def load_mapping(self):
        """加载会员映射表，构建 device_user_id → member_id 反向索引"""
        try:
            with open(MAPPING_PATH, 'r') as f:
                data = json.load(f)

            self.member_data = data
            self.device_to_member = {}
            for member_id, info in data.items():
                dev_id = info.get("device_id")
                if dev_id:
                    self.device_to_member[str(dev_id)] = member_id

            logger.info(
                "会员映射加载完成: %d 位会员, %d 位已绑定设备",
                len(self.member_data), len(self.device_to_member)
            )
        except Exception as e:
            logger.error("会员映射加载失败: %s", e)
            self.member_data = {}
            self.device_to_member = {}

    def lookup(self, device_user_id: str):
        """通过设备 userId 查找会员编号"""
        return self.device_to_member.get(str(device_user_id))

    def get_member_info(self, member_id: str):
        """获取会员详细信息"""
        return self.member_data.get(member_id)

    def register_mapping(self, device_user_id: str, member_id: str, updated_by: str = "admin"):
        """注册/更新设备用户ID与会员编号的映射"""
        if member_id not in self.member_data:
            return False, f"会员编号 {member_id} 不存在"

        # 更新内存
        self.device_to_member[str(device_user_id)] = member_id
        self.member_data[member_id]["device_id"] = str(device_user_id)

        # 持久化到文件
        try:
            with open(MAPPING_PATH, 'w') as f:
                json.dump(self.member_data, f, ensure_ascii=False, indent=2)
            logger.info("映射已持久化: device_user=%s -> member=%s (by=%s)",
                        device_user_id, member_id, updated_by)
            return True, "ok"
        except Exception as e:
            logger.error("映射持久化失败: %s", e)
            return True, "已写入内存但持久化到文件失败"

    def add_pending(self, record: dict):
        """添加未匹配记录到待认领列表"""
        os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)

        pending = []
        if os.path.exists(PENDING_FILE):
            try:
                with open(PENDING_FILE, 'r') as f:
                    pending = json.load(f)
            except Exception:
                pending = []

        # 按 userId + time 去重
        key = f"{record.get('device_id', '')}_{record.get('userId', '')}_{record.get('time', '')}"
        exists = any(
            f"{r.get('device_id', '')}_{r.get('userId', '')}_{r.get('time', '')}" == key
            for r in pending
        )

        if not exists:
            pending.append({
                **record,
                "_unmatched_since": datetime.now().isoformat(),
                "_match_key": key,
            })
            with open(PENDING_FILE, 'w') as f:
                json.dump(pending, f, ensure_ascii=False, indent=2, default=str)
            logger.info("未匹配记录已加入待认领: userId=%s | time=%s",
                        record.get("userId"), record.get("time"))

        return pending

    def get_pending(self) -> list:
        """获取待认领列表"""
        if os.path.exists(PENDING_FILE):
            try:
                with open(PENDING_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def clear_pending(self, match_keys: list = None):
        """清除待认领记录（认领后调用）"""
        if not os.path.exists(PENDING_FILE):
            return True
        try:
            if match_keys:
                pending = self.get_pending()
                remaining = [r for r in pending
                             if r.get("_match_key") not in match_keys]
                with open(PENDING_FILE, 'w') as f:
                    json.dump(remaining, f, ensure_ascii=False, indent=2)
            else:
                with open(PENDING_FILE, 'w') as f:
                    json.dump([], f)
            return True
        except Exception as e:
            logger.error("清除待认领失败: %s", e)
            return False

    def save_standardized(self, record: dict, member_id: str, member_info: dict) -> dict:
        """生成标准化 JSON 数据供 Ethan 分析"""
        os.makedirs(STANDARDIZED_DIR, exist_ok=True)

        standardized = {
            "member_id": member_id,
            "member_name": member_info.get("name", ""),
            "device_id": record.get("device_id", ""),
            "device_user_id": record.get("userId", ""),
            "punch_time": record.get("time", ""),
            "verify_mode": record.get("verifyMode", ""),
            "in_out": record.get("inOut", ""),
            "temperature": record.get("temperature", 0.0),
            "door_mode": record.get("doorMode", ""),
            "photo_path": record.get("_photo_path", ""),
            "member_summary": {
                "phone": member_info.get("phone", ""),
                "gender": member_info.get("gender", ""),
                "total_amount": member_info.get("total_amount", 0),
                "purchase_count": member_info.get("purchase_count", 0),
            },
            "standard_version": "v1.0",
            "generated_at": datetime.now().isoformat(),
        }

        # 按日期分文件
        date_str = datetime.now().strftime("%Y%m%d")
        output_file = os.path.join(STANDARDIZED_DIR, f"punch_standard_{date_str}.jsonl")

        # JSONL 格式，每行一条记录
        with open(output_file, 'a') as f:
            f.write(json.dumps(standardized, ensure_ascii=False) + "\n")

        logger.info("标准化数据已生成: member=%s | time=%s", member_id, record.get("time"))
        return standardized

    def notify_momo(self):
        """生成 Momo 待认领通知"""
        pending = self.get_pending()
        if not pending:
            logger.info("无待认领记录，跳过 Momo 通知")
            return None

        os.makedirs(os.path.dirname(MOMO_NOTIFY_FILE), exist_ok=True)

        notification = {
            "type": "pending_claim_alert",
            "timestamp": datetime.now().isoformat(),
            "pending_count": len(pending),
            "message": f"🚨 有 {len(pending)} 条打卡记录无法匹配会员，需要人工认领",
            "pending_summary": [
                {
                    "device_id": r.get("device_id"),
                    "user_id": r.get("userId"),
                    "punch_time": r.get("time"),
                    "unmatched_since": r.get("_unmatched_since"),
                }
                for r in pending
            ],
            "resolved": False,
        }

        alerts = []
        if os.path.exists(MOMO_NOTIFY_FILE):
            try:
                with open(MOMO_NOTIFY_FILE, 'r') as f:
                    alerts = json.load(f)
            except Exception:
                alerts = []

        alerts.append(notification)
        with open(MOMO_NOTIFY_FILE, 'w') as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2)

        logger.info("Momo 通知已生成: %d 条待处理", len(pending))
        return notification
