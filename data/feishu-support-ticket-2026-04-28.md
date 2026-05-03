# 飞书技术支持工单

**提交日期：** 2026-04-28
**提交人：** 智爱动集团（Shuyu 应用运维）

---

## 1. 应用信息

| 项目 | 内容 |
|------|------|
| 应用名称 | Shuyu |
| App ID | cli_a96da9747fb91bd2 |
| 开发模式 | 自建应用（Self-Build） |
| 平台 | 飞书（Feishu.cn） |
| 服务器端框架 | OpenClaw 2026.4.24 + @larksuiteoapi/node-sdk v1.61.1 |

## 2. 已完成的配置确认 ✅

以下配置均已确认正确：

### 2.1 应用发布
- 应用已发布到企业
- Bot 激活状态：正常（`activate_status: 2`）

### 2.2 权限配置
- API 凭证已验证通过（tenant_access_token 获取成功 ✅）
- Bot 信息返回正常

### 2.3 事件订阅
- **订阅方式：** 已设为「使用长连接接收事件/回调」
- **已添加事件：**
  - `im.message.receive_v1` ★（核心问题事件）
  - `im.message.message_read_v1`
  - `im.chat.member.bot.added_v1`
  - `im.chat.member.bot.deleted_v1`
  - `im.message.reaction.created_v1`
  - `im.message.reaction.deleted_v1`
  - `drive.notice.comment_add_v1`
  - `application.bot.menu_v6`
  - `card.action.trigger`

### 2.4 服务器端配置
- WebSocket 长连接已建立 ✅
- `im.message.receive_v1` 事件处理器已通过 `EventDispatcher.register()` 注册 ✅（Lark SDK 标准注册方式）
- 事件分发器（EventDispatcher）已正确传入 WSClient ✅
- 单进程运行，无多实例冲突

## 3. 问题描述 ❌

**现象：** 用户向 Bot 发送私聊消息后，Bot 无任何响应。

**服务器日志关键证据：**

```
2026-04-28T01:58:52.937Z [INFO] feishu[default]: starting feishu[default] (mode: websocket)
2026-04-28T01:58:52.975Z [INFO] feishu[default]: bot open_id resolved: ou_76b2aceb08583b19f3b199fa19683efb
2026-04-28T01:58:53.078Z [INFO] feishu[default]: starting WebSocket connection...
2026-04-28T01:58:53.085Z [INFO] feishu[default]: WebSocket client started
```

**WebSocket 连接已成功建立，但未出现过以下任一日志：**
- `feishu[default]: received message from ...`
- `im.message.receive_v1`
- 任何 `im.` 开头的事件处理记录

**WARNING（每次连接均出现，来源为 Lark SDK 内部 WSClient）：**
```
[ws] receive events or callbacks through persistent connection
only available in self-build & Feishu app.
```

## 4. 已排除的原因

| 可能原因 | 排查结果 |
|---------|---------|
| 凭证无效 | ✅ 已验证，token 正常 |
| WebSocket 未连接 | ✅ 已连接（WebSocket client started） |
| 事件处理器未注册 | ✅ 已通过 EventDispatcher.register() 注册 |
| 应用未发布 | ✅ 已发布且激活 |
| 订阅方式错误 | ✅ 已设为「长连接」 |
| 事件未添加 | ✅ im.message.receive_v1 已添加 |
| 权限不足 | ⚠️ 待飞书核实（im:message 权限授予情况） |
| 多实例冲突 | ✅ 单进程运行 |
| 防火墙/代理 | ✅ 服务器可正常访问飞书 API |
| 域名配置 | ✅ 使用默认 feishu.cn 域名 |

## 5. 请求事项

请飞书技术支持协助排查以下方面：

1. **平台端事件推送状态：** 确认飞书平台是否已向该应用的 WebSocket 长连接推送 `im.message.receive_v1` 事件？如未推送，请告知原因。
2. **事件路由核查：** 该应用的事件是否被路由到 WebSocket 连接？是否存在向其他目标（如 webhook URL）推送的记录？
3. **应用类型检查：** 自建应用的 WebSocket 长连接事件接收是否有特殊限制或额外配置要求？
4. **权限核查：** 确认 `im:message` 相关权限是否已正确授予该应用，发送消息的用户是否在应用可见范围内。
5. **日志级别：** 如可能，请提供平台侧该应用的事件推送日志，以便对照排查。

## 6. 附：服务器端连接数据

- 服务器 IP：82.156.224.176（中国境内）
- 网关 PID：489789
- SDK 版本：@larksuiteoapi/node-sdk ^1.61.1
- OpenClaw 版本：2026.4.24
- Node.js 版本：22.22.2
- 操作系统：Ubuntu Linux (6.8.0-101-generic x64)
- 企业已授权：是
- 应用已被管理员添加至可用范围：是
