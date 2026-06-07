#!/usr/bin/env bash
set -eou pipefail
FAILED=0
failed_checks=()

pass() { printf " PASS: %s\n" "$1"; }
fail() { printf " FAIL: %s\n" "$1"; failed_checks+=("$1"); FAILED=1;}

# 1. Check if required tools are installed
printf "\n── Checking required tools ──\n"
for tool in git python3 node curl; do
    command -v "$tool" > /dev/null 2>&1 && pass "$tool is installed" || { fail "$tool is not installed"; true; }
done

# 2. Check if Repository is properly cloned
printf "\n── Checking repository files ──\n"
for file in README.md .git/config; do
    [ -f "$file" ] && pass "$file exists" || fail "$file is missing"
done

# 3. Check basic connectivity (GitHub API)
printf "\n── Checking GitHub API connectivity ──\n"
curl -sf --max-time 3 https://api.github.com > /dev/null 2>&1 \
    && pass "GitHub API is reachable" \
    || fail "GitHub API is unreachable"

# Summary
printf "\n────────────────────────────────\n"
if [ "$FAILED" -eq 0 ]; then
    printf " All checks passed.\n"
    exit 0
else
    printf "\n The following checks failed:\n"
    for check in "${failed_checks[@]}"; do
        printf " - %s\n" "$check"
    done
    exit 1
fi

# printf is used to make the script compatible across macOS and Linux.