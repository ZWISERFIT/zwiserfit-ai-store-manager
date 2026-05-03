#!/bin/bash
# ZWISERFIT AIreports 同步脚本
# 用途：将VM端报告同步至创始人本地桌面
# 执行方式：在创始人 WSL2 终端运行此脚本
# 创建人：Tristan（技术架构官）
# 创建时间：2026-05-02

VM_USER="agentuser"
VM_HOST="82.156.224.176"
VM_REPORTS="/home/agentuser/.openclaw/workspace/data/ZWISERFIT/AIreports/"
LOCAL_REPORTS="/Users/suzannemok/Desktop/ZWISERFIT/AIreports/"

# 确保本地目录存在
mkdir -p "$LOCAL_REPORTS"

# 同步报告文件
echo "📥 正在从 VM 同步报告到本地..."
scp "${VM_USER}@${VM_HOST}:${VM_REPORTS}*.md" "$LOCAL_REPORTS" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 同步完成。报告已写入：$LOCAL_REPORTS"
    ls -la "$LOCAL_REPORTS"
else
    echo "❌ 同步失败。请确认 SSH 连接到 VM 正常。"
    exit 1
fi
