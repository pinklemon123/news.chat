#!/bin/bash
set -euo pipefail

# 启动后端服务
PORT="${PORT:-8000}"
API_DIR="news-suite/api"
LEGACY_API_DIR="api"

if [ -d "$API_DIR" ]; then
  (
    cd "$API_DIR"
    uvicorn app:app --host 0.0.0.0 --port "$PORT" &
  )
elif [ -d "$LEGACY_API_DIR" ]; then
  (
    cd "$LEGACY_API_DIR"
    uvicorn app:app --host 0.0.0.0 --port "$PORT" &
  )
fi

# 启动前端服务
WEB_DIR="news-suite/web"
LEGACY_WEB_DIR="web"

if [ -d "$WEB_DIR" ]; then
  cd "$WEB_DIR"
  npm run start
elif [ -d "$LEGACY_WEB_DIR" ]; then
  cd "$LEGACY_WEB_DIR"
  npm run start
fi
