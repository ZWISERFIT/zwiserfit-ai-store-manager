---
name: wecom-self-healing
description: 企业微信通道异常自愈技能。当发现企微通道异常时，自主执行诊断、重启和上报流程。技能包含日志查看、错误识别、服务重启和错误汇报。
metadata:
  {
    "openclaw": { "emoji": "⚡" },
  }
---

# 企业微信通道自愈技能

> **核心身份确认**：我是Shuyu（舒妤），智爱动集团商业总指挥，创始人莫淑瑜的数字分身。负责维护企业微信通道的正常运行，确保与Momo小新等子AI的通信畅通。

## 何时使用本技能

当以下条件**任一**满足时触发本技能：
1. 发送企业微信消息时收到连接错误或超时
2. 调用wecom_mcp工具时返回权限错误或连接失败
3. 用户报告企业微信通道异常
4. 定期心跳检查发现通道不可用
5. 检测到"pairing required"、"unauthorized"、"bootstrap token invalid"等关键词错误

### 持久规则（2026-04-20生效 | 2026-04-25修订：遵守铁律一禁止自重启）
当发现企微通道异常时，必须立即执行以下自愈流程：
1. 查看最新日志定位错误
2. 若发现"pairing required"等关键词，记录完整错误日志
3. 向创始人汇报错误详情，请创始人手动重启网关
4. 将处理过程和结果记录到持久记忆

## 自愈流程

### 1. 诊断阶段：查看最新日志

**执行命令**：
```bash
journalctl --user -u openclaw-gateway -n 20
```

**分析要点**：
- 检查最近20条日志记录
- 识别错误关键词：
  - `pairing required` - 配对要求
  - `unauthorized` - 未授权
  - `bootstrap token invalid` - 引导令牌无效
  - `bootstrap token expired` - 引导令牌过期
  - `gateway.bind` - 网关绑定错误
  - `gateway.remote.url` - 远程URL错误
  - `Tailscale` - Tailscale相关错误
  - `plugins.entries.device-pair.config.publicUrl` - 插件配置错误

### 2. 处理阶段：根据错误类型采取措施

#### 场景A：发现"pairing required"等配对相关错误
**⚠️ 注意：遵守铁律一，不自已重启**

**执行流程**：
1. 收集完整错误日志：`journalctl --user -u openclaw-gateway -n 40`
2. 在回复中输出错误摘要
3. **请求创始人手动重启网关**，提示语：
   > "检测到配对错误，请创始人手动执行：`systemctl --user restart openclaw-gateway`"
4. 可向创始人提供验证建议：重启后过30秒，检查 `systemctl --user status openclaw-gateway` 确认服务活跃

#### 场景B：创始人手动重启后问题依旧存在
**上报流程**：
1. **收集完整错误信息**：
   ```bash
   journalctl --user -u openclaw-gateway --since "10 minutes ago" > /tmp/openclaw-gateway-error.log
   ```
2. **向创始人汇报**：
   - 清晰描述问题现象
   - 附上关键错误日志片段
   - 说明已尝试的修复措施
   - 请求进一步指示

#### 场景C：其他类型错误
**分类处理**：
- **权限错误**：检查tools.alsoAllow配置，执行wecom-preflight检查
- **网络错误**：检查网络连接，验证Tailscale状态
- **配置错误**：检查OpenClaw配置文件

### 3. 验证阶段：确认通道恢复

**验证步骤**：
1. **检查服务状态**：
   ```bash
   systemctl --user status openclaw-gateway | grep -E "(active|running|failed)"
   ```
2. **测试基本功能**：
   ```bash
   wecom_mcp list contact 2>&1 | head -5
   ```
3. **记录恢复时间**：
   - 记录问题发生时间
   - 记录修复完成时间
   - 计算宕机时长

### 4. 记录阶段：更新持久记忆

**记录要求**：
1. **更新MEMORY.md**：
   - 添加自愈事件记录
   - 记录错误类型和解决方案
   - 更新服务稳定性统计
2. **记录到每日内存文件**：
   ```bash
   echo "## 企业微信通道自愈记录" >> /home/agentuser/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
   echo "- 时间: $(date '+%Y-%m-%d %H:%M:%S')" >> /home/agentuser/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
   echo "- 问题: [具体问题描述]" >> /home/agentuser/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
   echo "- 措施: [执行的自愈措施]" >> /home/agentuser/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
   echo "- 结果: [修复结果]" >> /home/agentuser/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
   ```

## 错误处理矩阵

| 错误现象 | 可能原因 | 立即措施 | 后备措施 |
| "pairing required" | 设备配对过期 | 收集日志 → 请创始人手动重启 | 重新配对流程 |
| "unauthorized" | 权限令牌失效 | 收集日志 → 请创始人手动重启 | 检查token配置 |
| 连接超时 | 网络问题/Tailscale | 检查网络状态 | 请创始人手动排查Tailscale |
| 工具不可用 | tools.alsoAllow缺失 | 执行wecom-preflight | 手动配置权限 |
| 服务未运行 | gateway进程崩溃 | 提示创始人手动重启 | 收集崩溃日志供分析 |

## 预防性维护

### 定期检查
- **每日检查**：在heartbeat中检查gateway服务状态
- **每周检查**：验证wecom_mcp所有品类工具可用性
- **每月检查**：审查错误日志，识别模式性问题

### 监控指标
1. **服务可用性**：gateway服务运行时间
2. **通道响应时间**：wecom_mcp调用平均延迟
3. **错误频率**：各类错误发生次数
4. **自愈成功率**：自动修复成功比例

## 注意事项

1. **安全边界**：重启gateway服务会短暂中断所有连接，需评估影响
2. **权限范围**：仅操作user级别systemctl服务，不涉及系统级服务
3. **数据保护**：错误日志可能包含敏感信息，分享时需脱敏处理
4. **上报时机**：连续修复失败3次后必须立即上报创始人
5. **记录完整**：所有自愈操作必须有完整记录，便于审计追踪

## 示例场景

### 场景一：配对过期错误
**错误信息**：`Error: pairing required for device connection`

**自愈流程**：
1. 执行`journalctl --user -u openclaw-gateway -n 20`确认错误
2. 收集完整错误日志
3. 向创始人汇报错误详情，**请创始人手动重启**：`systemctl --user restart openclaw-gateway`
4. 记录到MEMORY.md

### 场景二：权限令牌失效
**错误信息**：`Error: unauthorized access to wecom API`

**自愈流程**：
1. 检查日志确认错误类型
2. 收集完整错误日志
3. 向创始人汇报并**请创始人手动重启**：`systemctl --user restart openclaw-gateway`
4. 执行wecom-preflight检查工具权限
5. 如问题持续，收集完整日志上报创始人

---

**最后更新**：2026-04-25（遵守铁律一，移除自动重启）  
**技能维护者**：Shuyu总指挥