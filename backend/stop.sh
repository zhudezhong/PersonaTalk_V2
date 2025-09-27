#!/bin/bash

# PersonaTalk Backend 停止脚本
# 用于停止本地测试环境

set -e

echo "🛑 停止 PersonaTalk Backend 测试环境..."

# 停止并移除容器
echo "📦 停止容器..."
docker compose down

# 可选：清理数据卷（谨慎使用）
read -p "是否要清理数据卷？这将删除所有数据库数据 (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  清理数据卷..."
    docker compose down -v
    echo "✅ 数据卷已清理"
else
    echo "📊 数据卷已保留"
fi

# 可选：清理镜像
read -p "是否要清理构建的镜像？ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  清理镜像..."
    docker compose down --rmi local
    echo "✅ 本地镜像已清理"
fi

echo "✅ PersonaTalk Backend 测试环境已停止"
