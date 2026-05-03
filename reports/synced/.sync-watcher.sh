#!/bin/bash
# ============================================================
# ZWISERFIT AI报告同步 — 服务端文件监视器
# 职责：监视报告目录，记录变更事件，触发同步标记
# 部署位置：VM端 ~/.openclaw/workspace/reports/
# 启动方式：systemd 服务 ai-report-sync-watcher.service
# ============================================================

WATCH_DIR="/home/agentuser/.openclaw/workspace/reports/synced"
MANIFEST_FILE="${WATCH_DIR}/.sync-manifest.json"
LOG_FILE="/home/agentuser/.openclaw/workspace/reports/synced/.sync-events.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🟢 同步监视器启动，监视目录: $WATCH_DIR"

# 确保 manifest 初始存在
if [ ! -f "$MANIFEST_FILE" ]; then
    echo '{"lastSync":"","files":[]}' > "$MANIFEST_FILE"
fi

inotifywait -m -r \
    --exclude '(\.sync-|\.swp|\.tmp|~$)' \
    -e create -e modify -e moved_to -e close_write \
    --format '%w%f|%e|%T' \
    --timefmt '%Y-%m-%dT%H:%M:%S' \
    "$WATCH_DIR" | while IFS='|' read -r filepath event time; do
    
    filename=$(basename "$filepath")
    
    # 跳过隐藏文件和 manifest 自身
    [[ "$filename" == .* ]] && continue
    
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # 更新 manifest
    python3 -c "
import json, os
manifest_path = '$MANIFEST_FILE'
try:
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
except:
    manifest = {'lastSync': '', 'files': []}

manifest['lastSync'] = '$timestamp'

existing = [f for f in manifest['files'] if f['name'] == '$filename']
if existing:
    existing[0]['mtime'] = '$timestamp'
    existing[0]['event'] = '$event'
else:
    manifest['files'].append({
        'name': '$filename',
        'mtime': '$timestamp',
        'event': '$event',
        'size': os.path.getsize('$filepath') if os.path.exists('$filepath') else 0
    })

# 只保留最近 50 条
manifest['files'] = manifest['files'][-50:]

with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
"
    
    log "📄 $event → $filename"
done
