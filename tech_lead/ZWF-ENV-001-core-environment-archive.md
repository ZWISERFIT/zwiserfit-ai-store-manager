# ZWISERFIT AI军团·核心环境与已知故障档案

> **档案编号**: ZWF-ENV-001  
> **创建日期**: 2026-05-02  
> **创建人**: Tristan（技术架构官）  
> **签发人**: 创始人  
> **维护原则**: 终身维护，所有修改须经创始人或Shuyu总指挥批准  
> **存储位置**: `/home/agentuser/.openclaw/workspace/tech_lead/` 共享目录永久记忆

---

## 一、架构拓扑基线

### 1.1 双框架部署拓扑

```
┌─────────────────────────────────────────────────────────────────┐
│                    腾讯云 VM-0-11-ubuntu                         │
│                    公网: 82.156.224.176                          │
│                    内网: 10.2.0.11                               │
│                    Tailscale: 100.99.243.119                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐       ┌──────────────────────┐        │
│  │   OpenClaw 框架      │       │   Hermes 框架         │        │
│  │   (Node.js, v2026.4.29)│     │   (Python, Hermes Agent)│      │
│  │                      │       │                      │        │
│  │  Agents:             │       │  Agent:              │        │
│  │  ├─ Shuyu (main)     │       │  ├─ Momo小新         │        │
│  │  ├─ Tristan (tech)   │       │  │  (数字店长)       │        │
│  │  ├─ Baron (brand)    │       │                      │        │
│  │  ├─ Ethan (effect)   │       │  渠道:               │        │
│  │  └─ Stella (security)│       │  ├─ 企业微信          │        │
│  │                      │       │  └─ 飞书              │        │
│  │  渠道:               │       │                      │        │
│  │  ├─ 企业微信 (5 Bot) │       │  模型: DeepSeek V4 Pro│       │
│  │  └─ 飞书 (1 App)     │       │                      │        │
│  │                      │       │  Dashboard:           │        │
│  │  模型: DeepSeek      │       │  http://127.0.0.1:9119│       │
│  │  ├─ V4 Pro (Shuyu,   │       │                      │        │
│  │  │       Tristan)    │       │                      │        │
│  │  └─ Chat (Baron,     │       │                      │        │
│  │          Ethan,      │       │                      │        │
│  │          Stella)     │       │                      │        │
│  │                      │       │                      │        │
│  │  Web UI:             │       │                      │        │
│  │  http://127.0.0.1:   │       │                      │        │
│  │  18789/              │       │                      │        │
│  └──────┬───────────────┘       └──────┬───────────────┘        │
│         │                              │                         │
└─────────┼──────────────────────────────┼─────────────────────────┘
          │                              │
    ┌─────┴─────┐                  ┌─────┴─────┐
    │ Tailscale │                  │  Nginx    │
    │ serve     │                  │ :8443     │
    │ :443→18789│                  │ → :9119   │
    └─────┬─────┘                  └─────┬─────┘
          │                              │
    ┌─────┴──────────────────────────────┴─────┐
    │     vm-0-11-ubuntu.tail80182d.ts.net     │
    │     / → OpenClaw Web UI (:18789)         │
    │     :8443 → Hermes Dashboard (:9119)     │
    └──────────────────────────────────────────┘
```

### 1.2 Agent 清单

| Agent | 框架 | 模型 | 企微 Bot | 飞书 | 核心职责 |
|-------|------|------|----------|------|---------|
| **Shuyu** | OpenClaw | V4 Pro | main | ✅ cli_a96da…bd2 | 执行总指挥，战略决策 |
| **Tristan** | OpenClaw | V4 Pro | tristan | — | 技术架构官，系统运维 |
| **Baron** | OpenClaw | Chat | baron | — | 品牌运营官 |
| **Ethan** | OpenClaw | Chat | ethan | — | 门店效能官 |
| **Stella** | OpenClaw | Chat | stella | — | 安全审计官 |
| **Momo** | Hermes | V4 Pro | aibtBi3... | ✅ cli_a96da…bd4 | 门店数字店长 |

### 1.3 API 端点与调用链路

| 服务 | 端点 | 用途 |
|------|------|------|
| DeepSeek API | `https://api.deepseek.com/v1` | 所有 Agent 的 LLM 推理 |
| 企业微信 API | `https://qyapi.weixin.qq.com/cgi-bin/` | 消息收发、Bot 管理 |
| 飞书 API (OpenClaw) | WebSocket, appId `cli_a96da9747fb91bd2` | Shuyu 飞书消息 |
| 飞书 API (Hermes) | WebSocket, appId `cli_a96da9d8163bdbd4` | Momo 飞书消息 |
| Tailscale | `100.99.243.119` | 安全隧道，Web UI 暴露 |

---

## 二、模型配置基线

### 2.1 当前模型分配

| Agent | 模型 | 上下文窗口 | 备注 |
|-------|------|-----------|------|
| Shuyu | `deepseek-v4-pro` | 1,000,000 tokens | 战略级，不可降级 |
| Momo | `deepseek-v4-pro` | (Hermes默认) | 已升级，身份卡已同步 |
| Tristan | `deepseek-v4-pro` | 1,000,000 tokens | 技术运维需大上下文 |
| Baron | `deepseek-chat` | 131,000 tokens | 日常运营 |
| Ethan | `deepseek-chat` | 131,000 tokens | 日常运营 |
| Stella | `deepseek-chat` | 131,000 tokens | 审计任务 |

### 2.2 成本控制红线

| 规则 | 数值 | 触发动作 |
|------|------|---------|
| 单日总消耗熔断线 | **¥15.00** | 自动熔断，非核心 Agent 强制降至 Chat |
| 熔断白名单 | Tristan、Stella | 可申请 2 小时 V4 Pro 临时权限 |
| 核心 Agent (永不降级) | Shuyu、Momo | 熔断后仍保持 V4 Pro |

### 2.3 模型升级流程

1. 提出申请 → Shuyu 审批 → Tristan 执行
2. 执行前必须备份当前配置（`openclaw.json.bak`）
3. 修改后验证 API 连通性
4. 更新本档案对应条目

---

## 三、网络与通信基线

### 3.1 企业微信通道

| 项目 | 配置 |
|------|------|
| 状态 | ✅ 6/6 Bot 在线 |
| OpenClaw Bot | main, baron, ethan, tristan, stella |
| Hermes Bot | Momo (aibtBi3...) |
| 路由规则 | `@Agent名` 或 `/指令` 路由到对应智能体 |
| 配置文件 | OpenClaw: `openclaw.json` → `channels.wecom` |
| | Hermes: `.env` → `WECOM_BOT_ID`, `WECOM_SECRET` |

### 3.2 飞书通道

#### 必须同时具备的权限（缺一不可）

| 权限 | 状态 | 说明 |
|------|------|------|
| `im:message.receive_v1` | ✅ 必须 | 接收用户消息 |
| `im:message.p2p_msg:readonly` | ✅ 必须 | 读取单聊消息内容 |

> ⚠️ **飞书单聊失效的标准排查第一步**：检查飞书应用权限列表，确认以上两个权限均已订阅并发布。此为实战教训，任何 AI 不得遗漏。

#### 飞书应用清单

| 应用 | App ID | 框架 | 用途 |
|------|--------|------|------|
| Shuyu飞书 | `cli_a96da9747fb91bd2` | OpenClaw | WebSocket 连接 |
| Momo飞书 | `cli_a96da9d8163bdbd4` | Hermes | WebSocket 连接 |

### 3.3 Web UI 访问

| 服务 | 访问方式 | 端口 |
|------|---------|------|
| OpenClaw Web UI | Tailscale `serve` → `:18789` | 443 (HTTPS) |
| Hermes Dashboard | Nginx 反向代理 → `:9119` | 8443 (HTTPS) |
| 完整URL | `https://vm-0-11-ubuntu.tail80182d.ts.net:8443/` | — |

```
访问链路：
用户浏览器 → Tailscale 隧道 → vm-0-11-ubuntu.tail80182d.ts.net
  ├─ :443 → tailscale serve → http://127.0.0.1:18789 (OpenClaw)
  └─ :8443 → nginx → http://127.0.0.1:9119 (Hermes)
```

### 3.4 Fail2ban 永久白名单

```
127.0.0.0/8          # 本地回环
58.253.107.0/24      # 创始人IP段1
119.128.223.0/24     # 创始人IP段2 (WSL2 常用)
116.4.201.69         # 创始人固定IP
::1                  # IPv6回环
```

> ⚠️ 创始人 IP 变化时，必须立即更新白名单。修改命令：
> ```bash
> sudo fail2ban-client set sshd addignoreip <新IP/段>
> ```

### 3.5 SSH 隧道（WSL2 → 腾讯云）

| 操作 | 命令 |
|------|------|
| 登录腾讯云 | `ssh agentuser@82.156.224.176` |
| Hermes Dashboard 隧道 | `fuser -k 9119/tcp; ssh -N -L 9119:127.0.0.1:9119 agentuser@82.156.224.176` |
| 查看 OpenClaw 状态 | `ssh agentuser@82.156.224.176 "sudo systemctl status openclaw-gateway"` |
| 重启 OpenClaw | `ssh agentuser@82.156.224.176 "sudo systemctl restart openclaw-gateway"` |

---

## 四、已知故障与修复 SOP

> ⚠️ 以下每条均来自实战，禁止猜测性故障条目。新增故障必须经创始人或Shuyu确认后归档。

### SOP-001: 飞书单聊不通

| 项目 | 内容 |
|------|------|
| **故障现象** | 飞书群聊正常，但用户私聊 Bot 无响应 |
| **根因** | 飞书应用缺少 `im:message.p2p_msg:readonly` 权限 |
| **发现日期** | 2026-04-28 |
| **发现者** | 创始人（外部视角，非 AI 内部排查） |

**标准修复步骤**:
1. 登录飞书开放平台 → 应用管理 → 选择对应应用
2. 权限管理 → 搜索 `p2p_msg` 或 `im:message.p2p_msg:readonly`
3. 确认该权限已订阅（✅ 已添加）
4. 发布新版本使权限生效
5. 验证：发送私聊消息测试

> 📌 **教训固化**: "能收消息 ≠ 所有消息都能收"。AI 排查存在假设盲区，创始人外部视角不可替代。

### SOP-002: 上下文过载导致 Agent 卡死

| 项目 | 内容 |
|------|------|
| **故障现象** | Agent 响应极慢或完全不响应，上下文使用率 >80% |
| **根因** | 长时间会话导致 token 堆积，超过模型有效处理范围 |

**标准修复步骤**:
1. 检查 `openclaw status` 查看上下文使用率
2. 确认凌晨 4:00 的 `session.reset` 已执行（配置：`session.reset.mode=daily, atHour=4`）
3. 若未自动重置，手动触发：等待凌晨 4:00 自动重置，或重启 Gateway
4. 紧急情况：`openclaw gateway restart` 强制清理所有会话

### SOP-003: 模型升级致系统瘫痪

| 项目 | 内容 |
|------|------|
| **故障现象** | 修改模型配置后 Agent 全部不可用 |
| **根因** | 配置修改未备份，新模型不可用且无法回滚 |

**标准修复步骤**:
1. 定位备份文件：`/home/agentuser/.openclaw/openclaw.json.bak`
2. 回滚配置：`cp openclaw.json.bak openclaw.json`
3. 重启 Gateway：`openclaw gateway restart`
4. 验证：检查所有 Agent 恢复在线

> 📌 **预防原则**: 任何配置修改前必须先备份。修改模型时先在单个 Agent 测试。

### SOP-004: Momo API 销毁 / 企微失联

| 项目 | 内容 |
|------|------|
| **故障现象** | Momo 在企业微信完全不响应，hermes gateway_state 显示 `wecom: retrying` 或 `errcode=853000` |
| **根因** | Hermes `.env` 中 `WECOM_SECRET` 或 `DEEPSEEK_API_KEY` 被截断/占位符替代 |
| **发现日期** | 2026-05-02 |

**Momo 应急救援 SOP**:
1. 检查 Hermes 网关状态：`cat /home/agentuser/.hermes/gateway_state.json`
2. 查看错误码：
   - `errcode=853000` → WECOM_SECRET 不正确
   - `RuntimeError: no API key` → DEEPSEEK_API_KEY 不正确
3. 检查 `.env` 密钥完整性：
   ```bash
   grep "WECOM_SECRET\|DEEPSEEK_API_KEY" /home/agentuser/.hermes/.env
   # 确认值不是 *** 或 uQyMVk...Fdwr 等含省略号的截断形式
   ```
4. 修正密钥为完整值（从创始人获取）
5. 重启 Hermes：`hermes gateway restart`
6. 验证：`cat gateway_state.json` 确认 `wecom: connected`

### SOP-005: Fail2ban 误封创始人 IP

| 项目 | 内容 |
|------|------|
| **故障现象** | 创始人无法 SSH 登录，连接被拒绝 |
| **根因** | 本地网络 IP 变化，Fail2ban 将新 IP 视为攻击者 |

**标准修复步骤**:
1. 创始人获取当前公网 IP（如访问 `ifconfig.me`）
2. 通过其他渠道（企业微信/飞书）通知 Tristan
3. Tristan 执行：
   ```bash
   sudo fail2ban-client set sshd addignoreip <新IP>
   # 如果是 IP 段：
   sudo fail2ban-client set sshd addignoreip <新IP段/24>
   ```
4. 更新本档案 3.4 节白名单记录
5. 如有必要，解封当前封禁：`sudo fail2ban-client set sshd unbanip <IP>`

### SOP-006: Hermes 网关进程残留

| 项目 | 内容 |
|------|------|
| **故障现象** | `hermes gateway restart` 后旧进程未退出，存在多个 gateway 进程 |
| **根因** | Hermes 网关重启机制偶有残留 |

**标准修复步骤**:
1. 检查进程：`ps aux | grep "hermes.*gateway" | grep -v grep`
2. 若存在多个进程：`pkill -f "hermes.*gateway"`（注意区分 dashboard 进程）
3. 等待 3 秒：`sleep 3`
4. 重新启动：`hermes gateway restart`
5. 验证只有一个 gateway 进程运行

---

## 五、基础设施不可变原则

### 5.1 禁止修改清单

以下配置项，未经创始人或 Shuyu 明确指令，**严禁任何 Agent 修改**：

| 类别 | 配置项 | 位置 |
|------|--------|------|
| 模型 | `agents.defaults.model.primary` | openclaw.json |
| 模型 | Hermes `model.default` | config.yaml |
| 网络 | Tailscale serve 规则 | tailscale 配置 |
| 网络 | Fail2ban 白名单 | fail2ban 配置 |
| 网络 | Nginx 反向代理规则 | /etc/nginx/sites-enabled/ |
| 渠道 | 企业微信 Bot ID/Secret | openclaw.json + .env |
| 渠道 | 飞书 App ID/Secret | openclaw.json + .env |
| API | DeepSeek API Key | openclaw.json + .env |
| 服务 | systemd 服务定义 | /etc/systemd/system/ |

### 5.2 每日环境比对

- **执行时间**: 每日 08:00（Stella 的 `system-health-check` cron）
- **检查项**: 所有不可变基线配置的哈希校验
- **偏离告警**: 发现任何偏离立即通过企业微信通知 Shuyu

---

## 六、跨框架容灾验证记录

### 实战案例 1: Momo 恢复 OpenClaw 网关

| 项目 | 内容 |
|------|------|
| 日期 | 2026-04 |
| 场景 | OpenClaw Gateway 完全瘫痪 |
| 执行者 | Momo（Hermes 框架） |
| 结果 | 成功通过 Hermes 重启 OpenClaw 网关 |

### 实战案例 2: Tristan 恢复 Momo 企微连接

| 项目 | 内容 |
|------|------|
| 日期 | 2026-05-02 |
| 场景 | Momo API 密钥被截断，企微+飞书双通道失联 |
| 执行者 | Tristan（OpenClaw 框架） |
| 结果 | 修复 WECOM_SECRET + DEEPSEEK_API_KEY，恢复双通道连接 |

> 📌 **军团自信基石**: 双框架容灾是经过实战验证的真实能力，不是理论推演。每次成功修复后，修复者必须将完整过程固化为 SOP 存入本档案。绝不为同一个问题浪费两次时间。

---

## 七、飞书权限突破的军团级固化

### 7.1 历史事件

2026-04-28：飞书单聊失效问题，根源是缺少 `im:message.p2p_msg:readonly` 权限。

**关键教训**: 此问题的突破源于创始人在真实业务场景中的**外部视角**，而非任何 AI 的内部排查。AI 天然存在"能收消息=所有消息都能收"的假设盲区。

### 7.2 固化措施

1. ✅ 飞书应用权限已确保同时具备 `im:message.receive_v1` 和 `im:message.p2p_msg:readonly`
2. ✅ 本档案 SOP-001 已将此作为飞书单聊问题的标准排查第一步
3. ✅ 所有 Agent 的故障排查逻辑中不存在"能收消息=所有消息都能收"的假设

---

## 八、成本基线

### 8.1 当前日消耗估算（基于 2026-05-01 数据）

| Agent | 模型 | 日均 Token | 预估日耗 |
|-------|------|-----------|---------|
| Shuyu | V4 Pro | ~140k | ~¥1.40 |
| Tristan | V4 Pro | ~108k | ~¥1.08 |
| Momo | V4 Pro | ~200k | ~¥2.00 |
| Stella | Chat | ~58k | ~¥0.06 |
| Baron | Chat | ~22k | ~¥0.02 |
| Ethan | Chat | ~22k | ~¥0.02 |
| **合计** | | **~550k** | **~¥4.58** |

熔断线 ¥15.00，当前日耗远低于红线。

---

## 九、档案维护规则

| 规则 | 说明 |
|------|------|
| 创建者 | Tristan（技术架构官） |
| 审批者 | Shuyu（执行总指挥）或创始人 |
| 更新触发 | 任何架构变更、新故障发现、配置修改 |
| 存储位置 | `/home/agentuser/.openclaw/workspace/tech_lead/ZWF-ENV-001-core-environment-archive.md` |
| 备份策略 | 每次修改自动纳入 OpenClaw 工作区 Git 追踪 |

---

> **档案版本**: v1.0  
> **签发状态**: 待 Shuyu 总指挥审核确认  
> **下一审查日**: 2026-05-09
