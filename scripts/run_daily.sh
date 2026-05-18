#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/superfa/superfa-ai-agent}"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
WECHAT_ACCOUNT="${WECHAT_ACCOUNT:-cjfai}"
ITEM_LIMIT="${ITEM_LIMIT:-10}"
BUSINESS_TZ="${BUSINESS_TZ:-Asia/Shanghai}"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

RUN_DATE="$(TZ="$BUSINESS_TZ" date +%F)"
SOURCE_DATE="$(TZ="$BUSINESS_TZ" date -d yesterday +%F)"
LOG_FILE="$LOG_DIR/daily-${RUN_DATE}.log"

{
  echo "[$(TZ="$BUSINESS_TZ" date '+%F %T %Z')] start generate-daily source_date=${SOURCE_DATE} account=${WECHAT_ACCOUNT} business_tz=${BUSINESS_TZ}"
  env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
    NO_PROXY='*' no_proxy='*' \
    "$PYTHON_BIN" -m app.main generate-daily \
      --date "$SOURCE_DATE" \
      --create-draft \
      --items "$ITEM_LIMIT" \
      --wechat-account "$WECHAT_ACCOUNT" \
      --no-fallback
  echo "[$(TZ="$BUSINESS_TZ" date '+%F %T %Z')] done generate-daily source_date=${SOURCE_DATE} account=${WECHAT_ACCOUNT} business_tz=${BUSINESS_TZ}"
} >> "$LOG_FILE" 2>&1
