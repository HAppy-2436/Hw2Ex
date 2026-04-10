#!/bin/bash
# 创建数据目录
mkdir -p data/uploads data/backups data/cache

# 启动服务
docker-compose up -d

# 检查健康状态
sleep 5
curl -f http://localhost:5000/api/health
