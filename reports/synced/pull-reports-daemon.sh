#!/bin/bash
# ============================================================
# ZWISERFIT AI报告同步 — 创始人端拉取脚本
# ============================================================
# 部署位置：创始人 WSL2 任意目录（建议 ~/zwiserfit-sync/）
# 启动方式：./pull-reports-daemon.sh
# 
# 工作原理：
#   利用 Tailscale 稳定 IP（100.99.243.119）拉取 VM 端报告
#   Tailscale IP 不受 WSL2 重启影响，永久稳定
#   每 10 秒拉取一次，近实时同步
# ============================================================

REMOTE_HOST="agentuser@100.99.243.119"
REMOTE_DIR="/home/agentuser/.openclaw/workspace/reports/synced/"
LOCAL_DIR="/mnt/c/Users/suzannemok/Desktop/ZWISERFIT/AIreports/"
LOCK_FILE="/tmp/zwiserfit-sync.lock"
LOG_FILE="/tmp/zwiserfit-sync.log"
INTERVAL=10

# ----- 首次运行检查 -----
if [ ! -d "$LOCAL_DIR" ]; then
    echo "[$(date)] 创建本地目录: $LOCAL_DIR"
    mkdir -p "$LOCAL_DIR"
fi

# ----- 单实例锁 -----
if [ -f "$LOCK_FILE" ]; then
    OLD_PID=$(cat "$LOCK_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "[$(date)] 同步守护进程已在运行 (PID: $OLD_PID)，退出。"
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE; exit" INT TERM EXIT

# ----- 日志函数 -----
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🟢 报告同步守护进程启动"
log "  远程: $REMOTE_HOST:$REMOTE_DIR"
log "  本地: $LOCAL_DIR"
log "  轮询间隔: ${INTERVAL}秒"

# ----- 主循环 -----
FAIL_COUNT=0
while true; do
    # rsync 拉取（排除隐藏文件）
    rsync -avz \
        --exclude='.*' \
        --exclude='*.tmp' \
        --exclude='*.swp' \
        -e "ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no" \
        "${REMOTE_HOST}:${REMOTE_DIR}" \
        "$LOCAL_DIR" 2>&1 | while IFS= read -r line; do
        # 只记录实际传输的文件
        if echo "$line" | grep -qvE '(sending|receiving|total|speedup|^$|^\./)'; then
            log "  📥 $line"
        fi
    done
    
    RSYNC_EXIT=$?
    if [ $RSYNC_EXIT -eq 0 ]; then
        FAIL_COUNT=0
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        if [ $FAIL_COUNT -eq 1 ]; then
            log "⚠️ 同步失败 (退出码: $RSYNC_EXIT)，将在下次重试"
        fi
        if [ $FAIL_COUNT -ge 6 ]; then
            log "🔴 连续 ${FAIL_COUNT} 次同步失败，请检查网络连接"
        fi
    fi
    
    sleep $INTERVAL
done
