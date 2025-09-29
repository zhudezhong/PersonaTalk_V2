#!/bin/bash

# PersonaTalk 项目一键启动脚本
# 包含 MySQL、Backend、Web 和 Nginx 服务的完整启动流程

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info "启动 PersonaTalk 项目..."

# 检查是否在正确的目录
if [[ ! -f "docker-compose.yml" ]]; then
    print_error "未找到 docker-compose.yml 文件，请确保在 deploy 目录下运行此脚本"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    print_error "Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

# 检查 Docker 和 Docker Compose 是否安装
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查必要的文件
required_files=("nginx/nginx.conf" "db/init.sql" "../backend/Dockerfile" "../web/personaltalk/Dockerfile")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        print_error "缺少必要文件: $file"
        exit 1
    fi
done

# 停止可能存在的容器
print_info "停止现有容器..."
docker-compose down --remove-orphans 2>/dev/null || true

# 清理旧的镜像和网络（可选）
print_info "清理 Docker 资源..."
docker system prune -f &> /dev/null || true

# 拉取镜像并构建启动服务
print_info "拉取镜像、构建并启动服务..."
print_info "这可能需要几分钟时间（首次运行会下载镜像）..."

if docker-compose up --build -d --pull always; then
    print_success "服务启动成功"
else
    print_error "服务启动失败"
    print_info "查看错误日志: docker-compose logs"
    exit 1
fi

# 等待服务初始化
print_info "等待服务初始化..."
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""

# 检查服务状态
print_info "检查服务状态..."
docker-compose ps

# 等待数据库初始化完成
print_info "等待数据库初始化..."
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec mysql-8.0 mysqladmin ping -h localhost -u root -proot123 &> /dev/null; then
        print_success "数据库已就绪"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
    if [ $((attempt % 10)) -eq 0 ]; then
        print_info "等待数据库启动... ($attempt/$max_attempts)"
    fi
done

if [ $attempt -eq $max_attempts ]; then
    print_error "数据库启动超时"
    exit 1
fi

# 检查后端服务（通过 Nginx 代理）
print_info "等待后端服务启动..."
backend_ready=false
for i in {1..30}; do
    # 通过 Nginx 代理检查后端服务
    if curl -f http://localhost/api/health &> /dev/null || docker exec backend curl -f http://localhost:8888/health &> /dev/null 2>&1; then
        print_success "后端服务已就绪"
        backend_ready=true
        break
    fi
    sleep 2
    if [ $((i % 5)) -eq 0 ]; then
        print_info "等待后端服务... ($i/30)"
    fi
done

# 检查前端服务
print_info "等待前端服务启动..."
web_ready=false
for i in {1..20}; do
    if curl -f http://localhost:3000 &> /dev/null; then
        print_success "前端服务已就绪"
        web_ready=true
        break
    fi
    sleep 2
    if [ $((i % 5)) -eq 0 ]; then
        print_info "等待前端服务... ($i/20)"
    fi
done

# 检查 Nginx 代理
print_info "检查 Nginx 代理服务..."
nginx_ready=false
for i in {1..10}; do
    if curl -f http://localhost &> /dev/null; then
        print_success "Nginx 代理服务正常"
        nginx_ready=true
        break
    fi
    sleep 2
done

# 显示启动结果
echo ""
echo "=========================================="
if [ "$backend_ready" = true ] && [ "$web_ready" = true ] && [ "$nginx_ready" = true ]; then
    print_success "PersonaTalk 项目启动完成！"
else
    print_warning "部分服务可能未完全就绪，请检查日志"
fi
echo "=========================================="
echo ""

# 显示访问信息
echo -e "${BLUE}📋 服务访问信息：${NC}"
echo "   🌐 完整应用: http://localhost (推荐)"
echo "   🌐 备用端口: http://localhost:8003"
echo "   🔧 后端 API: http://localhost/api (统一通过 Nginx 代理)"
echo "   💾 数据库:   localhost:6036 (用户: personatalk)"
echo ""
echo -e "${BLUE}🐳 Docker 管理命令：${NC}"
echo "   📊 查看日志: docker-compose logs -f [服务名]"
echo "   🛑 停止服务: docker-compose down"
echo "   🔄 重启服务: docker-compose restart [服务名]"
echo "   📈 查看状态: docker-compose ps"
echo ""

# 显示各服务状态
echo -e "${BLUE}🔍 服务状态检查：${NC}"
if [ "$nginx_ready" = true ]; then
    print_success "Nginx 代理: ✓ 正常"
else
    print_error "Nginx 代理: ✗ 异常"
fi

if [ "$backend_ready" = true ]; then
    print_success "后端服务: ✓ 正常"
else
    print_error "后端服务: ✗ 异常"
fi

if [ "$web_ready" = true ]; then
    print_success "前端服务: ✓ 正常"
else
    print_error "前端服务: ✗ 异常"
fi

print_success "数据库: ✓ 正常"

echo ""
if [ "$nginx_ready" = true ]; then
    echo -e "${GREEN}🎉 所有服务已启动，请访问 ${BLUE}http://localhost${GREEN} 开始使用！${NC}"
    
    # 尝试自动打开浏览器
    if command -v open &> /dev/null; then
        read -p "是否自动打开浏览器？ (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "正在打开浏览器..."
            open http://localhost
        fi
    fi
else
    print_warning "请检查服务状态，可能需要等待几分钟后再访问"
fi

echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "   - 如果服务无法访问，请等待1-2分钟后重试"
echo "   - 查看详细日志: docker-compose logs -f"
echo "   - 修改配置请查看 docker-compose.yml 文件"
echo ""
