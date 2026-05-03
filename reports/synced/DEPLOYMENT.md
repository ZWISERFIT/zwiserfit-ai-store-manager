# ZWISERFIT AI报告实时同步 — 部署说明

> **部署日期：** 2026-05-03  
> **部署人：** Shuyu（执行总指挥）  
> **Tristan 审核：** 待确认  
> **此文件将作为首次自动同步的测试文件**

---

## 一、方案概述

```
┌──────────────────────────┐         ┌──────────────────────────┐
│   VM 端 (腾讯云服务器)     │         │   创始人端 (WSL2)          │
│                          │         │                          │
│  reports/synced/         │  rsync  │  /mnt/c/Users/           │
│  ├─ *.md                 │ ◄────── │  suzannemok/Desktop/     │
│  ├─ .sync-watcher.sh     │  pull   │  ZWISERFIT/AIreports/    │
│  └─ .sync-manifest.json  │  via    │                          │
│                          │Tailscale│  pull-reports-daemon.sh  │
│  inotifywait 监视        │         │  每10秒拉取               │
│  记录所有变更事件         │         │                          │
└──────────────────────────┘         └──────────────────────────┘
```

**核心设计：**
- 传输层：Tailscale 稳定 IP（`100.99.243.119`），WSL2 重启不影响
- 同步方式：创始人端 rsync 拉取（pull），无需服务器直连创始人机器
- 实时性：10 秒轮询间隔，近实时同步
- 可靠性：systemd 自动重启 + 单实例锁 + 失败重试

## 二、VM 端部署清单

| 组件 | 路径 | 状态 |
|------|------|------|
| 报告源目录 | `/home/agentuser/.openclaw/workspace/reports/synced/` | ✅ 已创建 |
| 文件监视器 | `reports/synced/.sync-watcher.sh` | ✅ 已部署 |
| systemd 服务 | `ai-report-sync-watcher.service` | ✅ 已启用（auto-start） |
| 同步清单 | `reports/synced/.sync-manifest.json` | 自动生成 |
| 拉取脚本 | `reports/synced/pull-reports-daemon.sh` | ✅ 待创始人部署 |
| 部署说明 | `reports/synced/DEPLOYMENT.md` | 本文件 |

**VM 端服务验证：**
```bash
systemctl status ai-report-sync-watcher.service
tail -f ~/.openclaw/workspace/reports/synced/.sync-events.log
```

## 三、创始人端部署步骤（一次性）

### 步骤 1：创建本地目录
```powershell
# 在 Windows PowerShell 中执行
mkdir C:\Users\suzannemok\Desktop\ZWISERFIT\AIreports
```

### 步骤 2：确保 Tailscale SSH 已配置
在 WSL2 中确认可以无密码 SSH 到 VM：
```bash
ssh agentuser@100.99.243.119
```
如需要密码，先设置 SSH Key：
```bash
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
ssh-copy-id agentuser@100.99.243.119
```

### 步骤 3：获取拉取脚本
```bash
# 在 WSL2 中执行
scp agentuser@100.99.243.119:/home/agentuser/.openclaw/workspace/reports/synced/pull-reports-daemon.sh ~/
chmod +x ~/pull-reports-daemon.sh
```

### 步骤 4：启动同步守护进程
```bash
# 前台运行（测试用）
~/pull-reports-daemon.sh

# 后台运行（生产用）
nohup ~/pull-reports-daemon.sh > /dev/null 2>&1 &
```

### 步骤 5：设置 WSL2 开机自启（可选）
在 WSL2 的 `~/.bashrc` 或 `~/.profile` 中添加：
```bash
# ZWISERFIT 报告自动同步
~/pull-reports-daemon.sh &
```

## 四、WSL2 IP 变化问题 — 已彻底解决

Tailscale 分配给每台设备的 IP 是永久稳定的：
- VM 服务器：`100.99.243.119`（永不变）
- 创始人笔记本：`100.96.110.58`（永不变）

rsync 使用 Tailscale IP 通信，与 WSL2 的本地 IP 完全无关。即使 WSL2 重启 100 次，同步通道始终畅通。

## 五、验证方法

### VM 端创建测试报告：
```bash
echo "## 测试报告 - $(date)" > ~/.openclaw/workspace/reports/synced/test-$(date +%s).md
```

### 创始人端检查：
```bash
ls -la /mnt/c/Users/suzannemok/Desktop/ZWISERFIT/AIreports/
```
10 秒内应出现测试文件。

## 六、故障排查

| 现象 | 检查项 | 命令 |
|------|--------|------|
| 文件不出现 | Tailscale 连通性 | `tailscale ping 100.99.243.119` |
| 文件不出现 | SSH 可达性 | `ssh agentuser@100.99.243.119 echo ok` |
| 文件不出现 | 守护进程状态 | `cat /tmp/zwiserfit-sync.log` |
| VM 端未监视 | 服务状态 | `systemctl status ai-report-sync-watcher` |

## 七、军规

1. 所有 AI 正式报告必须存入 `reports/synced/` 目录
2. 报告文件名格式：`YYYY-MM-DD-标题.md`
3. 此同步通道为创始人验收产出的唯一入口，必须保持 100% 可用
4. 发现同步中断，Tristan 和 Shuyu 需在 5 分钟内响应

---

*此文件是 ZWISERFIT AI军团报告同步系统的组成部分。*
*生成时间：2026-05-03 00:20 CST*
