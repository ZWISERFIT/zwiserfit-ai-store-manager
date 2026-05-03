#!/bin/bash
# ════════════════════════════════════════════════════════════════
# ZWF-20 Dashboard SSH Tunnel - 一键安装脚本
# 
# 功能：在 WSL2 上安装并配置 autossh，实现 SSH 隧道自动重连
# 效果：电脑锁屏后隧道断开 → autossh 自动重连（≤50秒）
#      解锁后直接刷新 http://localhost:9119 即可使用
# 
# 使用方法：
#   从腾讯云服务器拉取并执行：
#     curl -s http://82.156.224.176:9099/setup_tunnel.sh | bash
#
#   或者复制到本地执行：
#     bash setup_tunnel.sh
# ════════════════════════════════════════════════════════════════

set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   🚀 ZWF-20 Dashboard 隧道 · 一键安装                   ║"
echo "║   安装完成后，锁屏自动重连，无需任何手动操作              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# ── 第1步：检查 autossh ─────────────────────────────────────

echo -e "${YELLOW}[1/5]${NC} 检查 autossh..."

if command -v autossh &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} autossh 已安装 ($(autossh -V 2>&1))"
else
    echo "  → 正在安装 autossh..."
    sudo apt update -qq && sudo apt install -y autossh
    echo -e "  ${GREEN}✓${NC} autossh 安装完成"
fi

# ── 第2步：检查 SSH 密钥 ─────────────────────────────────────

echo ""
echo -e "${YELLOW}[2/5]${NC} 检查 SSH 密钥配置..."

SSH_KEY=""
for key in ~/.ssh/id_ed25519 ~/.ssh/id_rsa ~/.ssh/id_ecdsa; do
    if [ -f "$key" ]; then
        SSH_KEY="$key"
        break
    fi
done

if [ -n "$SSH_KEY" ]; then
    echo -e "  ${GREEN}✓${NC} SSH 密钥已存在: $SSH_KEY"
else
    echo "  → 正在生成 SSH 密钥..."
    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -q
    SSH_KEY=~/.ssh/id_ed25519
    echo -e "  ${GREEN}✓${NC} SSH 密钥已生成: $SSH_KEY"
fi

# ── 第3步：测试免密登录，配置密钥 ────────────────────────────

echo ""
echo -e "${YELLOW}[3/5]${NC} 验证服务器免密登录..."

REMOTE_USER="agentuser"
REMOTE_HOST="82.156.224.176"

if ssh -o BatchMode=yes -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" "echo OK" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} 免密登录已配置（可自动连接服务器）"
else
    echo -e "  ${YELLOW}→ 需要配置 SSH 公钥到服务器。${NC}"
    echo -e "  ${YELLOW}→ 请在提示时输入服务器密码（一次即可）。${NC}"
    echo ""
    
    # 复制公钥到服务器
    ssh-copy-id -i "${SSH_KEY}.pub" "${REMOTE_USER}@${REMOTE_HOST}"
    
    echo ""
    # 再次验证
    if ssh -o BatchMode=yes -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" "echo OK" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} 免密登录配置成功 ✅"
    else
        echo -e "  ${RED}✗${NC} 免密登录配置失败。请手动运行："
        echo -e "    ${YELLOW}ssh-copy-id ${REMOTE_USER}@${REMOTE_HOST}${NC}"
        echo -e "    然后重新执行本脚本。"
        exit 1
    fi
fi

# ── 第4步：创建 systemd 服务 ────────────────────────────────

echo ""
echo -e "${YELLOW}[4/5]${NC} 创建 systemd 隧道服务..."

LOCAL_USER=$(whoami)

sudo tee /etc/systemd/system/zwf20-tunnel.service > /dev/null << EOF
[Unit]
Description=ZWF-20 Dashboard SSH Tunnel (autossh)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${LOCAL_USER}
ExecStart=/usr/bin/autossh -M 0 \
  -o "ServerAliveInterval=15" \
  -o "ServerAliveCountMax=3" \
  -o "ExitOnForwardFailure=yes" \
  -o "TCPKeepAlive=yes" \
  -o "ConnectTimeout=10" \
  -o "StrictHostKeyChecking=no" \
  -N -L 9119:127.0.0.1:9119 ${REMOTE_USER}@${REMOTE_HOST}
ExecStop=/usr/bin/fuser -k 9119/tcp
Restart=always
RestartSec=5
StartLimitInterval=0

[Install]
WantedBy=multi-user.target
EOF

echo -e "  ${GREEN}✓${NC} 服务文件已创建"
sudo systemctl daemon-reload

# ── 第5步：启动并验证 ──────────────────────────────────────

echo ""
echo -e "${YELLOW}[5/5]${NC} 启动服务并验证..."

sudo systemctl enable zwf20-tunnel.service
sudo systemctl start zwf20-tunnel.service

echo "  → 等待隧道建立..."
sleep 5

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   📊 验证结果                                            ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# 验证服务状态
if sudo systemctl is-active --quiet zwf20-tunnel.service; then
    echo -e "  ${GREEN}✓${NC} 系统服务: active (running)"
else
    echo -e "  ${RED}✗${NC} 系统服务: 未运行"
fi

# 验证端口
if ss -tlnp | grep -q 9119; then
    echo -e "  ${GREEN}✓${NC} 端口 9119: 已监听"
else
    echo -e "  ${RED}✗${NC} 端口 9119: 未监听"
fi

# 验证 Dashboard HTTP
if curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:9119 | grep -q 200; then
    echo -e "  ${GREEN}✓${NC} Dashboard: HTTP 200 ✅"
else
    echo -e "  ${RED}✗${NC} Dashboard: 不可访问"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   ✅ 安装完成！                                          ║"
echo "║                                                          ║"
echo "║   现在可以关闭本终端，以后开浏览器直接访问：               ║"
echo "║     http://localhost:9119                                ║"
echo "║                                                          ║"
echo "║   即使锁屏/重启，隧道也会自动恢复。                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# ── 附：运维命令备忘 ─────────────────────────────────────────

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  运维命令备忘"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  查看状态:  sudo systemctl status zwf20-tunnel.service"
echo "  查看日志:  sudo journalctl -u zwf20-tunnel.service -f"
echo "  重启服务:  sudo systemctl restart zwf20-tunnel.service"
echo "  停止服务:  sudo systemctl stop zwf20-tunnel.service"
echo "  卸载服务:  sudo systemctl disable --now zwf20-tunnel.service"
echo "              sudo rm /etc/systemd/system/zwf20-tunnel.service"
echo "              sudo systemctl daemon-reload"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
