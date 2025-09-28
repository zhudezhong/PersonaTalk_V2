#!/bin/bash

# PersonaTalk 项目启动脚本（简化版）
# 只包含 MySQL、Backend、Web 和 Nginx 服务

set -e

echo "🚀 启动 PersonaTalk 项目..."

# 检查 Docker 和 Docker Compose 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 停止可能存在的容器
echo "🛑 停止现有容器..."
docker-compose down --remove-orphans

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "✅ PersonaTalk 项目启动完成！"
echo ""
echo "📋 服务访问信息："
echo "   🌐 前端应用: http://localhost (端口 80)"
echo "   🌐 备用端口: http://localhost:8003"
echo "   🔧 后端 API: http://localhost/api"
echo "   🎵 音频服务: http://localhost/audio"
echo "   🗄️  MySQL: localhost:3306"
echo ""
echo "📊 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo "🔄 重启服务: docker-compose restart"
echo ""

# 检查服务健康状态
echo "🏥 检查服务健康状态..."
sleep 5

# 检查 Nginx
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Nginx 代理服务正常"
else
    echo "❌ Nginx 代理服务异常"
fi

echo ""
echo "🎉 所有服务已启动，请访问 http://localhost 开始使用！"
echo "💡 提示: 如果需要修改配置，请查看 docker-compose.yml 文件"
