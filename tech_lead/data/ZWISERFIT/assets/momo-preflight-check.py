#!/usr/bin/env python3
"""
============================================================================
Momo 防脑补前置检查器 v1.0 (Anti-Confabulation Pre-Flight Checker)
============================================================================
Web5 MVP 核心技术落地 — Layer 1: DT (Digital Twin) 边界执行
ZWISERFIT · Tristan 技术架构官 · 2026-05-05
Shuyu 指令 #2026-0505-Momo-AntiConfab

功能:
  在 Momo 生成任何汇报/输出之前，自动拦截并检查内容中是否包含
  被标记为 INACTIVE、TEST-ONLY、DEPRECATED 的数据引用。
  如有违规 → 拦截输出，返回错误码和修正指引。
  如通过 → 放行，附加数据来源置信度标签。

使用:
  python3 momo-preflight-check.py <input_file_or_stdin>
  echo "汇报内容..." | python3 momo-preflight-check.py --stdin
============================================================================
"""

import sys
import os
import re
import json
import hashlib
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))

# ══════════════════════════════════════════════════════
# Momo 数字孪生能力档案 — 数据断点与标记
# ══════════════════════════════════════════════════════

DIGITAL_TWIN_ARCHIVE = {
    "agent": "Momo·实体门店数字孪生运营操作系统",
    "version": "2.0",
    "last_updated": "2026-05-05T20:30:00+08:00",
    "maintainer": "Tristan (tech_lead)",
    
    "data_gaps": {
        "GAP-001": {
            "capability": "人脸机打卡数据采集",
            "status": "INACTIVE",
            "severity": "CRITICAL",
            "reason": "人脸识别终端物理连接未建立，API 未对接",
            "blocked_since": "2026-05-01",
            "expected_resolution": "Tristan Issue #infra-iot-001",
            "alternative": "使用小白店长手动登记的到店签到表",
            "forbidden_patterns": [
                r"人脸机.*打卡",
                r"刷脸.*签到",
                r"人脸识别.*到店",
                r"face.*check.*in",
                r"面部识别.*考勤",
            ]
        },
        "GAP-002": {
            "capability": "会员映射表 (member-device-mapping)",
            "status": "TEST-ONLY",
            "severity": "WARNING",
            "reason": "映射表基于 Excel 历史数据生成，未与实时人脸机数据库交叉验证",
            "blocked_since": "2026-05-01",
            "expected_resolution": "IoT 数据管道打通后进行交叉验证",
            "alternative": "仅用于开发/测试环境的数据格式验证，不可用于业务报告",
            "forbidden_patterns": [
                r"会员映射表.*显示",
                r"member.device.mapping.*数据",
                r"根据.*映射表",
            ]
        },
        "GAP-003": {
            "capability": "旧版 Excel 营业额汇总 (智爱动营业额汇总2026.xlsx)",
            "status": "DEPRECATED",
            "severity": "CRITICAL",
            "reason": "数据截止于 2026-04，不包含 5月实时数据，已不再更新",
            "blocked_since": "2026-05-02",
            "expected_resolution": "永久弃用，由实时数据管道替代",
            "alternative": "使用小白店长每日上报的最新经营数据",
            "forbidden_patterns": [
                r"营业额汇总.*Excel",
                r"智爱动营业额汇总",
                r"2026.*Excel.*数据",
                r"根据.*Excel.*统计",
                r"旧.*Excel.*显示",
            ]
        },
        "GAP-004": {
            "capability": "实时客流量自动统计",
            "status": "INACTIVE",
            "severity": "WARNING",
            "reason": "门店未安装客流量计数器/红外传感器，无法自动统计",
            "blocked_since": "2026-05-01",
            "expected_resolution": "IoT 硬件采购与安装 (待创始人决策)",
            "alternative": "小白店长每日手动计数并上报",
            "forbidden_patterns": [
                r"自动统计.*客流",
                r"传感器.*到店人数",
                r"系统自动.*统计.*人数",
                r"红外.*计数.*客流",
            ]
        },
    },
    
    "data_classification": {
        "L1_REALTIME": {
            "label": "实时实测数据",
            "description": "由物理设备实时采集、未经人工加工的数据",
            "allowed_in_reports": True,
            "requires_citation": True,
            "examples": ["小白店长每日上报的到店人数", "企微收银记录"]
        },
        "L2_VERIFIED": {
            "label": "已验证历史数据",
            "description": "过去采集并经过人工/Stella 审计确认的数据",
            "allowed_in_reports": True,
            "requires_citation": True,
            "examples": ["已完成审计的上月营业额", "Stella 验证过的会员增长趋势"]
        },
        "L3_TEST": {
            "label": "测试/推算数据",
            "description": "基于历史数据推算、测试环境模拟的数据",
            "allowed_in_reports": False,
            "requires_citation": True,
            "must_label": "TEST-ONLY",
            "examples": ["会员映射表数据", "基于 Excel 的汇总推算"]
        },
        "L4_FORBIDDEN": {
            "label": "禁止引用数据",
            "description": "已弃用、未连接、或明确标注 INACTIVE/DEPRECATED 的数据源",
            "allowed_in_reports": False,
            "examples": ["人脸机打卡数据", "旧 Excel 汇总", "传感器自动计数"]
        }
    },
    
    "red_line_rules": [
        "禁止在任何面向 Shuyu 或外部渠道的汇报中引用 INACTIVE 状态的数据",
        "TEST-ONLY 数据仅限内部开发调试使用，输出时必须附加 [TEST-ONLY] 标签",
        "DEPRECATED 数据源在任何情况下不得作为实时业务数据引用",
        "数据通路未完全打通前，禁止生成未标注数据来源的汇总型报告",
        "每次汇报必须标注每条数据属于 L1~L4 哪一级，以及具体来源",
    ]
}

# ══════════════════════════════════════════════════════
# 检查引擎
# ══════════════════════════════════════════════════════

class MomoPreFlightChecker:
    def __init__(self, archive=DIGITAL_TWIN_ARCHIVE):
        self.archive = archive
        self.violations = []
        self.warnings = []
        self.passed = True
        self.content_hash = None
        
    def _is_self_report(self, text: str, match_start: int, gap_id: str) -> bool:
        """检查是否是自我标注（如 '⚠️ INACTIVE (GAP-001)'），而非伪装真实数据"""
        # 检查前后30字符内是否有自我标注标记
        context = text[max(0, match_start-30):match_start+30]
        self_report_markers = [
            'INACTIVE', 'GAP-', '⚠️', '未连接', '未开通', '不可用',
            '数据收集中', '待对接', '状态:', 'STATUS:', '管道'
        ]
        return any(marker in context for marker in self_report_markers)
    
    def check_content(self, text: str) -> dict:
        """对 Momo 的输出内容执行全量前置检查"""
        self.violations = []
        self.warnings = []
        self.passed = True
        
        # 计算内容哈希用于存证
        self.content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        # 逐条检查每个 GAP 的禁止模式
        for gap_id, gap in self.archive["data_gaps"].items():
            for pattern in gap["forbidden_patterns"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # 跳过自我标注（如 "⚠️ INACTIVE"）
                    if self._is_self_report(text, match.start(), gap_id):
                        continue
                    
                    context_start = max(0, match.start() - 40)
                    context_end = min(len(text), match.end() + 40)
                    context = text[context_start:context_end].replace('\n', ' ')
                    
                    violation = {
                        "gap_id": gap_id,
                        "status": gap["status"],
                        "severity": gap["severity"],
                        "capability": gap["capability"],
                        "matched_pattern": pattern,
                        "matched_text": match.group(),
                        "context": f"...{context}...",
                        "position": match.start(),
                        "alternative": gap["alternative"],
                    }
                    
                    if gap["severity"] == "CRITICAL":
                        self.violations.append(violation)
                        self.passed = False
                    else:
                        self.warnings.append(violation)
        
        # 检查数据来源标注
        has_l1_citation = bool(re.search(r'L1[_\s]*(实测|实时|REALTIME)', text))
        has_source_citation = bool(re.search(r'(数据来源|数据由|上报|来源:|source:)', text))
        
        return {
            "timestamp_cst": datetime.now(CST).isoformat(),
            "content_hash_sha256": self.content_hash,
            "passed": self.passed,
            "violations_count": len(self.violations),
            "warnings_count": len(self.warnings),
            "violations": self.violations,
            "warnings": self.warnings,
            "metadata": {
                "has_l1_citation": has_l1_citation,
                "has_source_citation": has_source_citation,
                "data_integrity_score": self._calculate_score(has_l1_citation, has_source_citation),
            }
        }
    
    def _calculate_score(self, has_l1: bool, has_source: bool) -> str:
        if self.passed and has_l1 and has_source:
            return "A (可信)"
        elif self.passed and (has_l1 or has_source):
            return "B (基本可信)"
        elif self.passed:
            return "C (需补充来源标注)"
        elif len(self.violations) <= 2:
            return "D (存在违规，需修正)"
        else:
            return "F (严重违规，禁止输出)"
    
    def format_report(self, result: dict) -> str:
        """生成人类可读的检查报告"""
        lines = []
        lines.append("=" * 72)
        lines.append("  Momo 防脑补前置检查报告 (Anti-Confabulation Pre-Flight)")
        lines.append("  ZWISERFIT Web5 MVP · Layer 1: DT Boundary Enforcement")
        lines.append("=" * 72)
        lines.append(f"  时间: {result['timestamp_cst']}")
        lines.append(f"  内容哈希: {result['content_hash_sha256']}")
        lines.append(f"  数据完整性评分: {result['metadata']['data_integrity_score']}")
        lines.append(f"  来源标注: L1={result['metadata']['has_l1_citation']} 来源={result['metadata']['has_source_citation']}")
        lines.append("")
        
        if result["passed"]:
            lines.append("  ✅ 检查通过 — 未发现禁止数据引用")
            lines.append("  📤 允许输出至目标渠道")
        else:
            lines.append(f"  ❌ 检查未通过 — 发现 {result['violations_count']} 条违规")
            lines.append("  🚫 输出已被拦截，请修正后重新提交")
            lines.append("")
            lines.append("  --- 违规详情 ---")
            for i, v in enumerate(result["violations"], 1):
                lines.append(f"  [{i}] GAP: {v['gap_id']} | 状态: {v['status']} | 严重: {v['severity']}")
                lines.append(f"      能力: {v['capability']}")
                lines.append(f"      匹配: \"{v['matched_text']}\"")
                lines.append(f"      上下文: {v['context']}")
                lines.append(f"      替代方案: {v['alternative']}")
                lines.append("")
        
        if result["warnings"]:
            lines.append("  --- 警告 (非致命) ---")
            for i, w in enumerate(result["warnings"], 1):
                lines.append(f"  ⚠️  [{w['gap_id']}] {w['capability']}: \"{w['matched_text']}\"")
            lines.append("")
        
        lines.append("  --- 修正指引 ---")
        lines.append("  1. 移除所有引用 INACTIVE/DEPRECATED 数据的语句")
        lines.append("  2. 使用小白店长手动上报的实时数据替代")
        lines.append("  3. 为每条数据标注 L1~L4 级别和具体来源")
        lines.append("  4. 若确实无实时数据可用，标注「数据收集中」而非推算")
        lines.append("")
        lines.append("  红线规则 (Red Line Rules):")
        for i, rule in enumerate(self.archive["red_line_rules"], 1):
            lines.append(f"  {i}. {rule}")
        lines.append("")
        lines.append("=" * 72)
        
        return "\n".join(lines)


def main():
    # 读取输入
    if len(sys.argv) > 1 and sys.argv[1] == "--stdin":
        text = sys.stdin.read()
        source = "stdin"
    elif len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"Error: 文件不存在: {filepath}", file=sys.stderr)
            sys.exit(2)
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        source = filepath
    else:
        # 默认从 stdin 读取
        text = sys.stdin.read()
        source = "stdin"
    
    if not text.strip():
        print("Error: 空输入", file=sys.stderr)
        sys.exit(2)
    
    # 执行检查
    checker = MomoPreFlightChecker()
    result = checker.check_content(text)
    
    # 输出报告
    report = checker.format_report(result)
    print(report)
    
    # 同时输出 JSON (用于自动化流水线)
    json_path = os.environ.get("MOMO_CHECK_JSON_OUT", "")
    if json_path:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 退出码: 0=通过, 1=违规拦截
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
