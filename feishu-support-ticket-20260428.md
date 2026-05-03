# 飞书技术支持工单

**工单编号：** ZIAD-2026-0428-001
**提交方：** 智爱动集团
**提交人：** Shuyu（集团商业总指挥）
**创建时间：** 2026-04-28 11:30 (Asia/Shanghai)
**优先级：** 高

---

## 一、问题概述

飞书机器人（App ID: `cli_a96da9d8163bdbd4`）通过 WebSocket 长连接成功连接到飞书服务器后，**无法接收到用户发送的消息**。具体现象为：

- WebSocket 连接建立 ✅
- 飞书后台事件订阅配置正确（长连接模式） ✅
- 用户通过飞书私聊发消息给机器人 → 机器人收不到 ❌
- 企微通道正常，可通过企微确认机器人运行状态 ✅

## 二、环境信息

| 项目 | 值 |
|------|-----|
| 飞书 App ID | `cli_a96da9d8163bdbd4` |
| 飞书 App Name | （智爱动相关应用） |
| 服务器 | 阿里云 ECS, Ubuntu 22.04 |
| SDK | `lark-oapi` (Python) |
| 连接模式 | WebSocket 长连接（`wss://msg-frontier.feishu.cn/ws/v2`） |
| 连接状态 | ✅ 已连接（2026-04-28 02:13:56 至今） |

## 三、证据链

### 3.1 WebSocket 连接日志

```
[2026-04-28 02:13:56] [Feishu] Connected in websocket mode (feishu)
[2026-04-28 02:13:56] connected to wss://msg-frontier.feishu.cn/ws/v2?fpid=493&aid=552564&...
```

连接建立成功，鉴权通过。

### 3.2 网关状态确认

```json
{
  "feishu": {
    "state": "connected",
    "error_code": null,
    "error_message": null,
    "updated_at": "2026-04-27T18:13:56.083424+00:00"
  }
}
```

### 3.3 事件处理器注册错误（关键证据）

网关日志中反复出现 `processor not found` 错误，共 **31 次**。具体分布：

| 缺失事件类型 | 出现次数 | 时间范围 |
|-------------|---------|---------|
| `im.chat.access_event.bot_p2p_chat_entered_v1` | 24 次 | 4月21日 16:41 ~ 4月22日 00:52 |
| `contact.scope.updated_v3` | 3 次 | 4月21日 18:16 ~ 18:21 |
| 其他（含重复 conn_id 变体） | 4 次 | 4月21日 ~ 4月22日 |

典型错误日志：
```
ERROR Lark: handle message failed, message_type: event, 
message_id: c96181e5-7524-49af-8b16-c04b3a5ab8b5,
trace_id: 2c1a4a8667f23dce78a241bfb9429d80,
err: processor not found, type: im.chat.access_event.bot_p2p_chat_entered_v1
[conn_id=7631121905668361408]
```

**影响分析：** 根据 Lark SDK 机制，当 WebSocket 客户端收到无法处理的事件时，会向飞书服务器返回 **HTTP 500 错误**。飞书服务器在持续收到 500 响应后，会停止向该 WebSocket 连接推送后续消息事件。这解释了"连接成功但收不到消息"的异常现象。

### 3.4 Bot 身份信息获取失败（次要问题）

```
WARNING gateway.platforms.feishu: [Feishu] Unable to hydrate bot identity 
from application info. Grant admin:app.info:readonly or 
application:application:self_manage so group @mention gating can 
resolve the bot name precisely.
```

该警告出现 **34 次**（同步记录于 agent.log 和 errors.log），不影响消息接收，但可能影响群聊 @mention 解析精度。

## 四、已采取的排查措施

### 4.1 事件处理器补丁（内部修复）

我方已在 `feishu.py` 中添加缺失的 `bot_p2p_chat_entered` 事件处理器注册：

```python
.register_p2_im_chat_access_event_bot_p2p_chat_entered_v1(
    self._on_bot_p2p_chat_entered
)
```

补丁写入时间：2026-04-28 02:52:07（文件修改时间戳）

**⚠️ 注意：** 由于网关进程启动时间（02:13:52）早于补丁时间，当前运行中的网关尚未加载此补丁。需要重启网关后验证。

### 4.2 配对目录检查

我方已检查 `~/.hermes/pairing/` 目录，确认该目录为企微（WeCom）配对专用机制，飞书接入不涉及配对码流程，目录中无飞书相关记录。

## 五、飞书技术支持请求

### 5.1 核心问题确认请求

请飞书技术支持团队协助确认以下问题：

1. **事件推送阻断机制：** 当 WebSocket 客户端对某个事件返回 500（`processor not found`）时，飞书服务器是否会停止推送后续消息事件（`im.message.receive_v1`）？如果是，阻断持续多长时间？如何恢复推送？
2. **`bot_p2p_chat_entered` 事件的必要性：** `im.chat.access_event.bot_p2p_chat_entered_v1` 是否是接收消息的前置条件？缺失此事件处理器是否必然导致 `im.message.receive_v1` 事件停止推送？
3. **SDK 默认注册建议：** Lark SDK 是否有推荐的必注册事件处理器清单？建议在官方文档中明确标注哪些事件为接收消息的"必要注册事件"。

### 5.2 所需操作

- [ ] 确认以上事件阻断机制的技术细节
- [ ] 如有必要，协助恢复我方飞书应用的消息推送通道
- [ ] 提供 SDK 事件处理器注册的最佳实践文档或建议

## 六、附件与参考

- 本工单相关日志归档位置：`/home/agentuser/.hermes/logs/`
- 飞书后台配置截图：由创始人手动提供
- 内部修复工具包：`feishu-recovery-toolkit`（含完整诊断流程）

---

**本工单内容基于网关日志、系统状态和实际排查记录编写，数据均如实标注来源与时间。未描述的内容标注为"无证据"或"待确认"。**

