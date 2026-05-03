#!/bin/bash
# Start Hermes Dashboard (port 9119 on 127.0.0.1)
# To be accessed via SSH tunnel: ssh -N -L 9119:127.0.0.1:9119 agentuser@82.156.224.176

cd /home/agentuser/.hermes/hermes-agent

# Kill any existing dashboard process on 9119
fuser -k 9119/tcp 2>/dev/null
sleep 1

# Start dashboard in background
nohup venv/bin/python -c "
import sys
sys.path.insert(0, '/home/agentuser/.hermes/hermes-agent')
import uvicorn
from hermes_cli.web_server import app
uvicorn.run(app, host='127.0.0.1', port=9119, log_level='warning')
" > /tmp/hermes_dashboard.log 2>&1 &

DASHBOARD_PID=$!
echo "Dashboard PID: $DASHBOARD_PID"

# Wait for it to start
sleep 3

# Verify
if ss -tlnp | grep -q 9119; then
    echo "✓ Hermes Dashboard running on http://127.0.0.1:9119"
    curl -s http://127.0.0.1:9119/api/status | python3 -m json.tool 2>&1 | head -5
else
    echo "✗ Dashboard failed to start"
    cat /tmp/hermes_dashboard.log
    exit 1
fi
