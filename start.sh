#!/bin/bash

# 启动后端服务
cd api && uvicorn app:app --host 0.0.0.0 --port 8000 &

# 启动前端服务
cd ../web && npm run start