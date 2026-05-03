# ZWISERFIT AIreports · 创始人报告验收目录

> **创建时间：** 2026-05-02 23:17 CST  
> **创建人：** Tristan（技术架构官）  
> **VM端路径：** `/home/agentuser/.openclaw/workspace/data/ZWISERFIT/AIreports/`  
> **创始端路径：** `/Users/suzannemok/Desktop/ZWISERFIT/AIreports/`

---

## 📋 目录用途

此目录是**创始人直观验收所有 AI 生成正式报告的唯一通道**。

收录范围：
- 审计报告（Stella 每日/专项审计）
- 环境基线报告（Tristan 环境比对）
- 故障修复报告（任何 Agent 的修复后总结）
- SOP 文档（新增或更新的标准操作流程）
- 系统健康检查报告（Stella 每日 08:00）
- 其他经创始人或 Shuyu 指定的正式报告

## 📝 文件命名规范

```
[日期]-[报告类型]-[生成者].md
```

**示例：**
- `20260504-环境基线验收报告-Stella.md`
- `20260503-每日审计报告-Stella.md`
- `20260502-故障修复报告-Momo.md`
- `20260502-系统健康检查报告-Stella.md`

## 🔄 同步机制

VM 端报告目录与创始端目录通过以下方式同步：

```bash
# 创始人从 WSL2 执行（拉取所有报告到本地桌面）
scp agentuser@82.156.224.176:/home/agentuser/.openclaw/workspace/data/ZWISERFIT/AIreports/*.md /Users/suzannemok/Desktop/ZWISERFIT/AIreports/
```

建议设置 cron 或 watch 自动同步。

## ⚠️ 铁律

所有 AI 生成报告，在提交的同时必须备份至此目录。任何报告缺失均视为未提交。
