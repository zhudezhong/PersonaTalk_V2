#!/bin/bash

# PersonaTalk Backend 一键启动脚本
# 用于快速启动本地测试环境

set -e

echo "🚀 启动 PersonaTalk Backend 测试环境..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否可用
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装或不可用，请确保 Docker Desktop 正常运行"
    exit 1
fi

# 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建 .env 配置文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p docker/mysql

# 停止可能存在的旧容器
echo "🛑 停止旧容器..."
docker compose down 2>/dev/null || true

# 清理可能存在的孤立容器
echo "🧹 清理孤立容器..."
docker compose down --remove-orphans 2>/dev/null || true

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker compose ps

# 等待健康检查通过
echo "🏥 等待健康检查通过..."
for i in {1..30}; do
    if curl -s http://localhost:8888/api/v1/chat/health > /dev/null 2>&1; then
        echo "✅ 健康检查通过！"
        break
    fi
    echo "⏳ 等待服务启动... ($i/30)"
    sleep 2
done

# 显示服务信息
echo ""
echo "🎉 PersonaTalk Backend 测试环境启动成功！"
echo ""
echo "📋 服务信息："
echo "  - Backend API: http://localhost:8888"
echo "  - 健康检查: http://localhost:8888/api/v1/chat/health"
echo "  - 模型列表: http://localhost:8888/api/v1/chat/models"
echo "  - API 文档: http://localhost:8888/docs"
echo "  - MySQL: localhost:3306 (用户: personatalk, 密码: personatalk123)"
echo "  - Redis: localhost:6379"
echo ""
echo "📖 常用命令："
echo "  - 查看日志: docker compose logs -f personatalk-backend"
echo "  - 停止服务: docker compose down"
echo "  - 重启服务: docker compose restart"
echo "  - 查看状态: docker compose ps"
echo ""
echo "🔧 如需修改配置，请编辑 .env 文件后重启服务"
