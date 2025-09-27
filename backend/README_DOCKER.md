# PersonaTalk Backend Docker 部署指南

本指南帮助您快速启动 PersonaTalk Backend 的本地测试环境。

## 🚀 一键启动

### 快速开始

```bash
# 一键启动测试环境（推荐）
./start.sh

# 或手动启动
docker compose up --build -d
```

启动后访问：
- **API 服务**: http://localhost:8888
- **API 文档**: http://localhost:8888/docs
- **健康检查**: http://localhost:8888/api/v1/chat/health

### 停止环境

```bash
# 一键停止
./stop.sh

# 或手动停止
docker compose down
```

## 📋 环境配置

### 默认配置

| 服务 | 端口 | 用户名 | 密码 | 说明 |
|------|------|--------|------|------|
| Backend API | 8888 | - | - | 主服务 |
| MySQL | 3306 | personatalk | personatalk123 | 数据库 |
| Redis | 6379 | - | - | 缓存（可选） |

### 自定义配置

1. 复制环境配置文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，修改以下关键配置：
```env
# 模型服务配置（必须）
OPENAI_API_KEY=your_actual_api_key
OPENAI_BASE_URL=https://your_model_service_url
OPENAI_MODEL=your_model_name

# 数据库配置（可选，默认使用内置 MySQL）
MYSQL_HOST=mysql
MYSQL_PASSWORD=your_password
```

3. 重启服务使配置生效：
```bash
docker compose restart
```

## 🛠️ 开发模式

当前配置已启用开发模式特性：

- ✅ **代码热重载**: 修改代码后自动重启
- ✅ **日志输出**: 实时查看应用日志
- ✅ **调试模式**: 包含详细错误信息
- ✅ **数据持久化**: 数据库数据保存在 Docker 卷中

### 查看日志

```bash
# 查看后端服务日志
docker compose logs -f personatalk-backend

# 查看数据库日志
docker compose logs -f mysql

# 查看所有服务日志
docker compose logs -f
```

### 服务管理

```bash
# 查看服务状态
docker compose ps

# 重启特定服务
docker compose restart personatalk-backend

# 进入容器调试
docker compose exec personatalk-backend bash
```

## 🧪 测试 API

### 健康检查

```bash
curl http://localhost:8888/api/v1/chat/health
```

### 获取模型列表

```bash
curl http://localhost:8888/api/v1/chat/models
```

### 测试聊天接口

```bash
curl -X POST "http://localhost:8888/api/v1/chat/text_chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "system_prompt": "You are a helpful assistant."
  }'
```

### 测试流式聊天

```bash
curl -X POST "http://localhost:8888/api/v1/chat/text_chat_stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "system_prompt": "You are a helpful assistant."
  }'
```

## 📊 数据库管理

### 连接数据库

```bash
# 使用 Docker 容器连接
docker compose exec mysql mysql -u personatalk -p personatalk_db

# 或使用外部工具连接
# 主机: localhost:3306
# 用户: personatalk
# 密码: personatalk123
# 数据库: personatalk_db
```

### 备份数据

```bash
# 备份数据库
docker compose exec mysql mysqldump -u personatalk -p personatalk_db > backup.sql

# 恢复数据库
docker compose exec -T mysql mysql -u personatalk -p personatalk_db < backup.sql
```

## 🔧 故障排除

### 常见问题

1. **端口占用**
```bash
# 检查端口占用
lsof -i :8888
# 修改 docker-compose.yml 中的端口映射
```

2. **数据库连接失败**
```bash
# 检查数据库容器状态
docker compose ps mysql
# 查看数据库日志
docker compose logs mysql
```

3. **模型服务调用失败**
- 检查 `.env` 文件中的 `OPENAI_API_KEY` 配置
- 确认网络连接正常
- 查看应用日志了解具体错误

### 清理和重置

```bash
# 完全清理（删除所有数据）
docker compose down -v --rmi local

# 重新构建
docker compose up --build -d
```

## 📁 项目结构

```
backend/
├── Dockerfile              # Docker 镜像构建文件
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore           # Docker 构建忽略文件
├── start.sh                # 一键启动脚本
├── stop.sh                 # 一键停止脚本
├── .env.example            # 环境配置示例
├── docker/
│   └── mysql/
│       └── init.sql        # MySQL 初始化脚本
├── logs/                   # 应用日志目录
└── src/                    # 应用源码
```

## 🚀 生产部署

当前配置针对开发和测试环境，生产部署时建议：

1. **移除开发特性**:
   - 关闭代码热重载
   - 移除调试模式
   - 使用生产级数据库

2. **安全配置**:
   - 使用强密码
   - 配置防火墙
   - 启用 HTTPS

3. **性能优化**:
   - 调整数据库连接池
   - 配置负载均衡
   - 启用缓存

更多生产部署建议，请参考官方文档。
