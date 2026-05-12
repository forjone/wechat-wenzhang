#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/superfa/superfa-ai-agent}"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
WECHAT_ACCOUNT="${WECHAT_ACCOUNT:-cjfai}"
ITEM_LIMIT="${ITEM_LIMIT:-10}"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

RUN_DATE="$(date +%F)"
SOURCE_DATE="$(date -d yesterday +%F)"
LOG_FILE="$LOG_DIR/daily-${RUN_DATE}.log"

{
  echo "[$(date '+%F %T')] start generate-daily source_date=${SOURCE_DATE} account=${WECHAT_ACCOUNT}"
  env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
    NO_PROXY='*' no_proxy='*' \
    "$PYTHON_BIN" -m app.main generate-daily \
      --date "$SOURCE_DATE" \
      --create-draft \
      --items "$ITEM_LIMIT" \
      --wechat-account "$WECHAT_ACCOUNT" \
      --no-fallback
  echo "[$(date '+%F %T')] done generate-daily source_date=${SOURCE_DATE} account=${WECHAT_ACCOUNT}"
} >> "$LOG_FILE" 2>&1
