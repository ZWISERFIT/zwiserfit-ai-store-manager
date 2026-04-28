# 门禁设备数据采集管道 - Flask 中间件

## 概述

腾讯云 Flask 中间件，负责接收门禁设备心跳，实现命令接收与应答机制。

## 架构

```
门禁设备 (ZWF-20) → HTTP/JSON → Flask 中间件 (腾讯云)
                                        ↓
                                receive_cmd 接口
                                        ↓
                              ERROR_NO_CMD 应答
```

## 部署

```bash
pip install flask gunicorn
python app.py
# 或生产部署
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API 接口

### 设备心跳

```
POST /api/v1/heartbeat
Content-Type: application/json

{
  "device_id": "ZWF-20-001",
  "timestamp": "2026-04-28T16:30:00+08:00",
  "status": "online",
  "firmware": "v2.1.3"
}
```

### 命令接收

```
POST /api/v1/receive_cmd
Content-Type: application/json

{
  "device_id": "ZWF-20-001",
  "cmd_type": "query_status",
  "cmd_id": "cmd_20260428_001"
}
```

### 应答格式

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "cmd": null,
    "error_no_cmd": true
  }
}
```

## 状态码

| code | 说明 |
|------|------|
| 0 | 正常应答 |
| 1001 | ERROR_NO_CMD — 无待执行命令 |
| 2001 | 设备未注册 |
| 2002 | 签名验证失败 |
