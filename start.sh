# start.sh
#!/bin/bash
set -euo pipefail

# 启动后端服务
PORT="${PORT:-8000}"
if [ -d "api" ]; then
  cd api
  uvicorn app:app --host 0.0.0.0 --port "$PORT" &
  cd ..
fi

# 启动前端服务
if [ -d "web" ]; then
  cd web
  npm run start
fi
