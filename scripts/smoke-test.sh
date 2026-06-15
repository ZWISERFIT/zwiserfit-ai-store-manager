#!/usr/bin/env bash
# smoke-test.sh — Store Manager AI Agent Health Check
# Expands basic health checks with config validation, dependency checks, and log directory verification.

set -euo pipefail

PASS_COUNT=0
FAIL_COUNT=0

log_pass() {
  echo "[PASS] $1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

log_fail() {
  echo "[FAIL] $1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

echo "=== Store Manager AI Agent Smoke Tests ==="
echo ""

# --- Existing test: Health check ---
check_health() {
  if command -v curl &> /dev/null; then
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health 2>/dev/null || echo "000")
    if [[ "$http_code" == "200" ]]; then
      log_pass "Health endpoint reachable (HTTP 200)"
    else
      log_fail "Health endpoint returned HTTP $http_code"
    fi
  else
    log_fail "curl not installed — cannot check health endpoint"
  fi
}
check_health

# --- NEW test 1: Config file validation ---
check_config_file() {
  local config_file="config.yaml"
  # Also check common config file locations
  if [[ -f "$config_file" ]]; then
    # Validate it's parseable YAML (or at least non-empty and well-formed)
    if [[ -s "$config_file" ]]; then
      log_pass "Config file exists and is non-empty ($config_file)"
    else
      log_fail "Config file exists but is empty ($config_file)"
    fi
  elif [[ -f "config.json" ]]; then
    if command -v python3 &> /dev/null; then
      if python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
        log_pass "Config file exists and is valid JSON (config.json)"
      else
        log_fail "Config file exists but is invalid JSON (config.json)"
      fi
    else
      log_pass "Config file exists (config.json) — JSON validation skipped (no python3)"
    fi
  else
    log_fail "No config file found (config.yaml or config.json)"
  fi
}
check_config_file

# --- NEW test 2: Dependency checks ---
check_dependencies() {
  local missing=()
  for cmd in bash curl; do
    if ! command -v "$cmd" &> /dev/null; then
      missing+=("$cmd")
    fi
  done

  if [[ ${#missing[@]} -eq 0 ]]; then
    log_pass "Required commands available (bash, curl)"
  else
    log_fail "Missing required commands: ${missing[*]}"
  fi

  # Optional dependencies — warn but don't fail
  local optional_missing=()
  for cmd in jq git node; do
    if ! command -v "$cmd" &> /dev/null; then
      optional_missing+=("$cmd")
    fi
  done

  if [[ ${#optional_missing[@]} -gt 0 ]]; then
    echo "  [WARN] Optional dependencies not found: ${optional_missing[*]}"
  fi
}
check_dependencies

# --- NEW test 3: API endpoint reachability (if base URL configured) ---
check_api_reachable() {
  local base_url="${STORE_MANAGER_API_URL:-http://localhost:3000}"
  if command -v curl &> /dev/null; then
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$base_url" --connect-timeout 5 2>/dev/null || echo "000")
    if [[ "$http_code" != "000" && "$http_code" != "001" ]]; then
      log_pass "API base URL reachable ($base_url -> HTTP $http_code)"
    else
      echo "  [SKIP] API not running at $base_url (expected in dev environments)"
    fi
  fi
}
check_api_reachable

# --- NEW test 4: Log directory writable ---
check_log_directory() {
  local log_dir="logs"
  if [[ ! -d "$log_dir" ]]; then
    if mkdir -p "$log_dir" 2>/dev/null; then
      log_pass "Log directory created ($log_dir)"
    else
      log_fail "Cannot create log directory ($log_dir)"
      return
    fi
  fi

  if [[ -w "$log_dir" ]]; then
    # Test actual write
    local test_file="$log_dir/.smoke_test_write_$$"
    if echo "smoke test $(date)" > "$test_file" 2>/dev/null; then
      rm -f "$test_file"
      log_pass "Log directory is writable ($log_dir)"
    else
      log_fail "Log directory exists but is not writable ($log_dir)"
    fi
  else
    log_fail "Log directory not writable ($log_dir)"
  fi
}
check_log_directory

# --- Summary ---
echo ""
echo "=== Results: $PASS_COUNT passed, $FAIL_COUNT failed ==="

if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
fi
