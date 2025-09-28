# PersonaTalk 部署指南

PersonaTalk 是一个基于 AI 的角色扮演对话应用，支持文本聊天和语音合成功能。

## 🏗️ 架构概览

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Nginx    │ -> │     Web     │    │   Backend   │ -> │    MySQL    │
│  (反向代理)  │    │  (Vue前端)   │    │ (FastAPI)   │    │   (数据库)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🚀 快速启动

### 前置要求
- Docker >= 20.10
- Docker Compose >= 2.0

### 一键启动
```bash
# 进入部署目录
cd deploy

# 启动所有服务
chmod +x start.sh
./start.sh
```

### 手动启动
```bash
# 进入部署目录
cd deploy

# 构建并启动服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 🔧 服务配置

### 环境变量
在 `docker-compose.yml` 中可以配置以下环境变量：

```yaml
# 数据库配置
MYSQL_DATABASE=personatalk
MYSQL_USER=personatalk
MYSQL_PASSWORD=personatalk123

# AI 模型配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://openai.qiniu.com/v1
OPENAI_MODEL=gpt-3.5-turbo
TTS_MODEL=tts
```

### 端口映射
- **80**: Nginx 主端口（前端应用）
- **8003**: Nginx 备用端口
- **3306**: MySQL 数据库
- **8888**: 后端 API（容器内部）
- **3000**: 前端服务（容器内部）

## 📁 目录结构

```
deploy/
├── docker-compose.yml    # Docker Compose 配置
├── start.sh             # 启动脚本
├── nginx/
│   └── nginx.conf       # Nginx 配置
└── db/
    └── init.sql         # 数据库初始化脚本
```

## 🌐 访问地址

启动成功后，可以通过以下地址访问：

- **前端应用**: http://localhost
- **备用端口**: http://localhost:8003
- **后端 API**: http://localhost/api
- **音频服务**: http://localhost/audio

## 📊 监控和调试

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f web
docker-compose logs -f nginx
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec mysql mysql -u personatalk -p
```

## 🛠️ 常见问题

### 1. 端口冲突
如果 80 端口被占用，可以修改 `docker-compose.yml` 中的端口映射：
```yaml
nginx:
  ports:
    - "8080:80"  # 改为 8080 端口
    - "8003:8003"
```

### 2. 数据库连接失败
确保 MySQL 服务已正常启动并通过健康检查：
```bash
docker-compose logs mysql
```

### 3. 前端页面加载失败
检查 Web 服务是否正常构建：
```bash
docker-compose logs web
```

## 🔄 重启和停止

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

## 📝 数据持久化

- **MySQL 数据**: 存储在 `mysql_data` 数据卷中
- **音频文件**: 存储在 `audio_files` 数据卷中

数据会在容器重启后保持，除非手动删除数据卷。

## 🔐 安全建议

1. 修改默认的数据库密码
2. 在生产环境中使用 HTTPS
3. 限制数据库访问权限
4. 定期备份数据

## 📞 技术支持

如遇问题，请检查：
1. Docker 和 Docker Compose 版本
2. 端口是否被占用
3. 服务日志中的错误信息
4. 网络连接是否正常
