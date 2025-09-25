# start.sh
#!/bin/bash
set -euo pipefail

PORT="${PORT:-8000}"

# 如果存在 api 目录就进入，否则留在当前目录
[ -d "api" ] && cd api

# 这里的 app:app 改成你的实际模块与应用对象
exec uvicorn app:app --host 0.0.0.0 --port "$PORT"
