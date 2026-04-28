# 🚪 门禁数据采集管道

## 概述

AI 军团首次物理世界数据采集任务。构建 ZWF-20 门禁设备数据采集管道，从心跳接入到标准化存储，完成从代码到硬件的闭环。

**关联里程碑：** 千城万店 · 数据基础设施

---

## 子任务

### [Tristan] Flask 中间件开发 ✅

- [x] 创建 `data/device-pipeline/app.py` — Flask 中间件
  - `/api/v1/heartbeat` — 设备心跳接收
  - `/api/v1/receive_cmd` — 命令接收 / ERROR_NO_CMD 应答
  - `/health` — 健康检查
  - `/api/v1/devices` — 设备列表查询
- [x] 编写 `data/device-pipeline/README.md` — 部署文档
- [x] 代码已提交至 `data/device-pipeline/`
- [ ] **待部署：** 上传至腾讯云服务器并运行

### [Ethan] 数据字段标准 ✅

- [x] 创建 `data/data-field-standard.md` — ZWF-20 字段标准草案
  - 顶层字段结构
  - 字段类型/格式/必填性
  - 各事件类型 payload 规范
  - 错误码表格
  - 数据流规范

### [Baron] 品牌传播素材 ✅

- [x] 创建 `brand_lead/data-pipeline-brand-content.md`
  - 标题方案
  - 传播话术（长文 + 短文案）
  - 可视化建议
  - 渠道与时间线

### [Stella] 独立审计 ⏳

- [ ] 待 Tristan 和 Ethan 交付物就位后审计
- [ ] 验证代码是否真实部署
- [ ] 验证标准文档是否真实提交
- [ ] 审计报告写入 `data/audit-daily-log.md`

---

## 技术信息

| 项目 | 值 |
|------|-----|
| 中间件框架 | Flask |
| 部署目标 | 腾讯云 |
| 设备协议 | ZWF-20 · HTTP/JSON |
| 标准版本 | v0.1-draft |
| 代码位置 | `data/device-pipeline/` |

## 后续步骤

1. 部署 Flask 中间件至腾讯云
2. 配置 ZWF-20 设备对接 IP
3. 接收首条真实心跳数据
4. 数据管道压力测试
5. 审计与复盘
