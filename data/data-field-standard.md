# ZWF-20 门禁数据采集字段标准草案

> 版本: v0.1-draft
> 起草人: Ethan（effect_lead）
> 日期: 2026-04-28
> 状态: 草案，待评审

---

## 1. 概述

本标准定义 ZWF-20 门禁设备在数据采集管道中的字段格式和规范。所有设备上报数据及中间件处理数据须遵循本标准。

## 2. 顶层字段结构

```
{
  "schema_version": "0.1",
  "device_id":    "<string>",       # 设备唯一标识
  "timestamp":    "<ISO8601>",      # 数据生成时间
  "event_type":   "<enum>",         # 事件类型
  "payload":      "<object>",       # 事件负载
  "signature":    "<string>"        # 数据签名（可选）
}
```

## 3. 字段定义

### 3.1 schema_version

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 是 |
| 格式 | semver |
| 示例 | "0.1" |
| 说明 | 本标准版本号 |

### 3.2 device_id

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 是 |
| 格式 | ZWF-20-{3位序号} |
| 示例 | "ZWF-20-001" |
| 说明 | 每个设备出厂时分配的唯⼀标识 |

### 3.3 timestamp

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 是 |
| 格式 | ISO 8601，含时区 |
| 示例 | "2026-04-28T16:30:00+08:00" |
| 说明 | 事件发生的精确时间 |

### 3.4 event_type

| 属性 | 值 |
|------|-----|
| 类型 | string (enum) |
| 必填 | 是 |
| 可选值 | "heartbeat", "door_open", "door_close", "alarm", "error", "cmd_response" |

### 3.5 payload

根据 event_type 不同，payload 结构不同。

#### 3.5.1 heartbeat 负载

```json
{
  "status":       "<enum: online|offline|maintenance>",
  "firmware":     "<string>",
  "uptime_s":     "<integer>",
  "battery_pct":  "<integer: 0-100>",
  "temperature_c": "<float>"
}
```

#### 3.5.2 door_open / door_close 负载

```json
{
  "door_id":      "<string>",
  "method":       "<enum: card|fingerprint|password|remote|manual>",
  "user_id":      "<string>",       # 开门用户标识（如适用）
  "duration_ms":  "<integer>"       # 开门持续时间
}
```

#### 3.5.3 alarm 负载

```json
{
  "alarm_type":   "<enum: forced_open|tamper|low_battery|network_down>",
  "severity":     "<enum: info|warning|critical>",
  "detail":       "<string>"
}
```

#### 3.5.4 error 负载

```json
{
  "error_code":   "<string>",
  "error_msg":    "<string>",
  "component":    "<string>"
}
```

#### 3.5.5 cmd_response 负载

```json
{
  "cmd_id":       "<string>",
  "cmd_status":   "<enum: received|executing|success|failed>",
  "result":       "<object>"
}
```

## 4. 应答字段标准

### 4.1 标准应答

```json
{
  "code":         "<integer: 0=成功, >0=错误>",
  "message":      "<string>",
  "data":         "<object>"
}
```

### 4.2 错误码表格

| code | 名称 | 说明 |
|------|------|------|
| 0 | OK | 成功 |
| 1001 | ERROR_NO_CMD | 无待执行命令 |
| 2001 | DEVICE_NOT_REGISTERED | 设备未注册 |
| 2002 | INVALID_SIGNATURE | 签名验证失败 |
| 2003 | MALFORMED_REQUEST | 请求格式错误 |
| 3001 | INTERNAL_ERROR | 服务内部错误 |

## 5. 数据流规范

```
设备 → [心跳/事件] → 中间件 → [格式化数据] → 存储层
设备 ← [命令/应答] ← 中间件
```

- 设备每 30 秒发送一次心跳
- 设备每次上报后轮询 receive_cmd
- 无命令时应答 ERROR_NO_CMD
- 所有数据落盘须使用 UTF-8 编码
- 时间戳强制使用 ISO 8601 + 时区

## 6. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v0.1 | 2026-04-28 | 初始草案 |
