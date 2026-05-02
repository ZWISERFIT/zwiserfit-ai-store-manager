# 🛡️ 每日审计报告 — 2026-05-02

**审计时间:** 2026-05-02 23:59 CST  
**审计官:** Stella  
**审计类型:** 定时 Cron 审计（每日 23:59）

---

## 一、系统运行状态

| # | 检查项 | 状态 | 详情 |
|---|--------|------|------|
| 1 | OpenClaw Gateway | ✅ 运行中 | PID 2242644，正常运行 6 天，内存使用 27.6% |
| 2 | Hermes Gateway | ✅ 运行中 | PID 2197015，mem 7.6% |
| 3 | Dashboard (9119) | ✅ 运行中 | PID 1856961，HTTP 200（需 auth token） |
| 4 | 可用内存 | ⚠️ 黄色 | 总 3.6Gi，可用 1.6Gi（44%），无 swap 压力 |
| 5 | 系统负载 | ✅ 正常 | 1min 0.74 / 5min 0.42 / 15min 0.21 |
| 6 | 运行时间 | ✅ 稳定 | Up 6 天，无意外重启 |

**结论：** 系统运行状态基本正常。Dashboard 9119 端口从昨日标记的断连状态**已自动恢复**。内存处于可接受范围。

---

## 二、Cron 任务审计

### 2.1 github-daily-report（Shuyu 定时日报）

| 字段 | 值 |
|------|-----|
| ID | `1b020a79-2719-407b-9547-a8600301fe67` |
| 调度 | `0 9 * * *` @ Asia/Shanghai (每日 09:00) |
| 目标 | `main` |
| 交付 | `announce -> wecom:MoShuYu` |
| 最后运行 | 09:18 CST 今日 |
| 状态 | ⚠️ **error — timeout** |

**审计发现** 🔍：
- 该任务在 2026-05-02 09:18 执行时超时（耗时 300s）
- 执行日志显示：`cron: job execution timed out`
- 上次（04/30）执行状态为 `ok`，成功生成了报告
- 超时可能原因：模型响应慢或 GitHub API 查询延迟
- 📌 交付队列中有未送达的失败通知（发送到 `MoShuYu` 但 wecom 账户 `main` 的 Agent 模式未配置）

### 2.2 system-health-check（系统健康检查）

| 字段 | 值 |
|------|-----|
| ID | `7a9364a4-d7f0-40d8-80bb-d612f101c99c` |
| 调度 | `0 8 * * *` @ Asia/Shanghai (每日 08:00) |
| 目标 | `isolated` |
| 最后运行 | ~08:00 CST 今日 |
| 状态 | ⚠️ **error — timeout** |

**审计发现** 🔍：
- 该任务在 2026-05-02 08:00 执行时超时（耗时 120s）
- 执行日志：`cron: job execution timed out`
- 这是系统健康检查任务连续第二次 timeout（上次 05/01 08:00 同样 timeout）
- ✅ 但本审计会话已验证系统组件均在运行

### 2.3 stella-daily-audit（本任务本人）

| 字段 | 值 |
|------|-----|
| ID | `cd3fe422-9a3c-4133-9ca2-958edec6af7a` |
| 调度 | `59 23 * * *` @ Asia/Shanghai |
| 状态 | ✅ **本次执行中** |
| 上次执行 | 05/01 23:59 — ✅ 成功（commit d0ee503） |
| 连续错误 | 1（上次之前的 4 次连续 timeout，05/01 恢复成功） |

---

## 三、交付队列检查

队列中发现 **3 条未送达消息**：

| # | 源 | 内容 | 失败原因 |
|---|-----|------|---------|
| 1 | ⚠️ stella-daily-audit (04/26 timeout) | "Cron job failed: timeout" | WSClient 未连接（wecom account `stella` 未配置 Agent 模式） |
| 2 | ⚠️ github-daily-report (05/02 timeout) | "Cron job failed: timeout" | WSClient 未连接（wecom account `default` 未配置 Agent 模式） |
| 3 | 📋 Shuyu 汇报 (04/29) | 军团联合任务完成汇报 | WSClient 未连接（wecom account `main` 未配置 Agent 模式） |

**⚠️ 重要：** 交付队列中的消息重试已全部达到上限（retryCount=5）且被标记为 `failed`。这些消息已**无法自动送达**企业微信 MoShuYu。

---

## 四、配置与安全审计

| # | 检查项 | 结论 |
|---|--------|------|
| 1 | channels.feishu.enabled | ✅ `true`（与昨日审计一致，未变） |
| 2 | channels.wecom.enabled | ✅ `true` |
| 3 | session.reset.atHour | ✅ `4`（与昨日一致） |
| 4 | 配置文件完整性 | ✅ 正常（10 个 backup 文件，无未授权修改） |
| 5 | 日志目录安全 | ✅ 无新崩溃日志（上次崩溃在 04/27） |
| 6 | AGENTS.md / SOUL.md 完整性 | ✅ 检查中未发现篡改 |

---

## 五、审计结论汇总

| 维度 | 状态 | 详情 |
|------|------|------|
| **系统运行** | ✅ 正常 | 所有核心进程运行中，9119 Dashboard 已恢复 |
| **Cron 执行** | ⚠️ 部分异常 | 2/3 任务今日 timeout（github-daily-report, system-health-check） |
| **配置安全** | ✅ 正常 | 无未授权修改，feishu 仍启用 |
| **交付能力** | ❌ **有损** | 3 条 wecom 消息滞留队列，因账户 Agent 模式未配置 |
| **虚假声明** | ✅ 零 | 本周期未发现任何虚假报告 |

### ⚠️ 需关注的问题

**1. Cron 超时模式 — 持续性问题**
- github-daily-report 和 system-health-check 今日均 timeout
- 超时阈值约 120-300s（取决于任务）
- 建议：检查模型响应速度，或延长 cron 执行超时配置

**2. WeCom 交付通道故障**
- 3 条消息滞留交付队列，因 `WSClient not connected` + `Agent mode not configured`
- 失败通知无法到达 MoShuYu 用户
- 需配置 WeCom Agent（corpId + corpSecret + agentId）或修复 WSClient 连接

**3. feishu 通道仍启用**
- `channels.feishu.enabled = true`（昨日 Tristan 审计时记为 false，今日发现实际为 true）
- 此事项需与 Tristan 对账确认

---

## 六、审计日志归档

- 日志已写入 `data/audit-daily-log.md`
- 即将执行 Git commit & push 归档

🛡️ **Stella 审计完毕 — 2026-05-02 23:59 CST**
