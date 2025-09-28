# PersonaTalk
An AI-powered roleplay chat platform that lets users interact with their favorite characters through text and real-time voice conversations. Built with LLMs, speech recognition, and TTS technologies.

# PersonaTalk Backend

> 一个基于 FastAPI 的智能对话系统后端服务，支持角色扮演聊天和文字转语音功能

## 📋 目录

- [项目概述](#项目概述)
- [技术架构](#技术架构)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [部署指南](#部署指南)
- [开发指南](#开发指南)

## 🎯 项目概述

PersonaTalk Backend 是一个现代化的智能对话系统后端服务，专为角色扮演聊天场景设计。系统集成了大语言模型和文字转语音（TTS）服务，为用户提供沉浸式的对话体验。

### 主要特性

- 🤖 **智能对话**: 基于大语言模型的角色扮演对话
- 🎭 **角色定制**: 支持自定义角色提示词和音色
- 🔊 **语音合成**: 集成 TTS 服务，支持多种音色
- 📚 **会话管理**: 完整的聊天历史和会话管理
- 🚀 **高性能**: 基于 FastAPI 的异步架构
- 📖 **自动文档**: 自动生成交互式 API 文档

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用      │    │   API Gateway   │    │   Load Balancer │
│   (Web/Mobile)  │◄──►│   (FastAPI)     │◄──►│   (Nginx)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  业务逻辑层      │
                       │  (API Routes)   │
                       └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │  数据访问层  │ │  模型服务层  │ │  外部服务层  │
        │   (CRUD)    │ │ (LLM/TTS)   │ │ (OpenAI)    │
        └─────────────┘ └─────────────┘ └─────────────┘
                │               │               │
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   MySQL     │ │  七牛云AI   │ │  七牛云TTS  │
        │  Database   │ │   Service   │ │   Service   │
        └─────────────┘ └─────────────┘ └─────────────┘
```

### 核心组件

1. **API 层**: FastAPI 路由和中间件
2. **业务逻辑层**: 聊天、会话管理、TTS 处理
3. **数据访问层**: SQLModel ORM 和 CRUD 操作
4. **模型服务层**: 大语言模型和 TTS 服务集成
5. **数据存储层**: MySQL 数据库

## 🚀 核心功能

### 1. 智能对话系统
- **角色扮演**: 支持自定义角色提示词
- **上下文记忆**: 维护对话历史和上下文
- **流式响应**: 支持实时流式对话
- **多轮对话**: 完整的会话管理

### 2. 语音合成服务
- **多音色支持**: 集成多种音色类型
- **实时转换**: 文字实时转语音
- **格式支持**: 支持 MP3 等音频格式
- **参数调节**: 支持语速、音色等参数调节

### 3. 会话管理
- **会话创建**: 自动创建和管理对话会话
- **历史记录**: 完整的聊天历史存储
- **会话搜索**: 支持会话内容搜索
- **数据持久化**: 可靠的数据库存储

## 🛠️ 技术栈

### 后端框架
- **FastAPI**: 现代、高性能的 Web 框架
- **Uvicorn**: ASGI 服务器
- **Pydantic**: 数据验证和序列化

### 数据库
- **MySQL**: 主数据库
- **SQLModel**: 现代 ORM 框架
- **aiomysql**: 异步 MySQL 驱动

### AI 服务
- **OpenAI API**: 大语言模型服务
- **七牛云 AI**: 国内 AI 服务提供商
- **TTS 服务**: 文字转语音服务

### 开发工具
- **Poetry**: 依赖管理和打包
- **Pytest**: 单元测试框架
- **Black**: 代码格式化
- **MyPy**: 类型检查

## 📁 项目结构

```
backend/
├── README.md                    # 项目文档
├── pyproject.toml              # Poetry 配置
├── docker-compose.yml          # Docker 编排
├── Dockerfile                  # Docker 镜像
├── start.sh                    # 启动脚本
├── stop.sh                     # 停止脚本
├── logs/                       # 日志目录
├── docker/                     # Docker 配置
│   └── mysql/                  # MySQL 配置
└── src/                        # 源代码
    ├── main.py                 # 应用入口
    ├── config.py               # 配置管理
    ├── api/                    # API 层
    │   ├── __init__.py
    │   ├── deps.py             # 依赖注入
    │   ├── error.py            # 错误处理
    │   └── api_v1/             # API v1
    │       ├── __init__.py
    │       ├── chat.py         # 聊天接口
    │       └── history_session.py # 会话管理
    ├── model/                  # 数据模型
    │   ├── __init__.py
    │   ├── base.py             # 基础模型
    │   ├── history_chat.py     # 聊天记录模型
    │   └── history_session.py  # 会话模型
    ├── crud/                   # 数据访问层
    │   ├── __init__.py
    │   ├── base.py             # 基础 CRUD
    │   ├── crud_history_chat.py # 聊天 CRUD
    │   └── crud_history_session.py # 会话 CRUD
    ├── model_server/           # 模型服务层
    │   ├── __init__.py
    │   ├── base.py             # 基础服务
    │   ├── deps.py             # 服务依赖
    │   ├── factory.py          # 服务工厂
    │   ├── openai_service.py   # OpenAI 服务
    │   ├── tts_service.py      # TTS 服务
    │   └── README.md           # 服务文档
    └── test/                   # 测试代码
        ├── __init__.py
        └── test_deps.py        # 依赖测试
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- Poetry (推荐) 或 pip

### 1. 克隆项目

```bash
git clone <repository-url>
cd PersonaTalk/backend
```

### 2. 安装依赖

```bash
# 使用 Poetry (推荐)
poetry install

# 或使用 pip
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=personatalk

# AI 服务配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://openai.qiniu.com
OPENAI_MODEL=your_model_name

# TTS 配置
TTS_MODEL=tts
```

### 4. 启动服务

```bash
# 使用 Poetry
poetry run start

# 或直接运行
uvicorn src.main:app --reload --host 0.0.0.0 --port 8888
```

### 5. 访问服务

- **API 文档**: http://localhost:8888/docs
- **健康检查**: http://localhost:8888/health

## 📚 API 文档

### 核心接口

#### 1. 聊天接口

**POST** `/api/v1/chat/text_chat`

```json
{
  "session_id": "session_123",
  "message": "你好，请介绍一下自己",
  "voice_type": "qiniu_zh_female_wwxkjx"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "聊天完成",
  "data": {
    "session_id": "session_123",
    "response": "你好！我是...",
    "audio_data": "base64编码的音频数据",
    "voice_type": "qiniu_zh_female_wwxkjx"
  }
}
```

#### 2. 文字转语音

**POST** `/api/v1/chat/text_to_speech`

```json
{
  "text": "你好，世界！",
  "voice_type": "qiniu_zh_female_wwxkjx",
  "encoding": "mp3",
  "speed_ratio": 1.0
}
```

#### 3. 获取音色列表

**GET** `/api/v1/chat/voice_list`

#### 4. 会话管理

- **GET** `/api/v1/history_session/history_session` - 获取会话列表
- **GET** `/api/v1/history_session/{session_id}/chats` - 获取聊天记录
- **PUT** `/api/v1/history_session/{session_id}` - 更新会话
- **DELETE** `/api/v1/history_session/{session_id}` - 删除会话

### 完整 API 文档

访问 http://localhost:8888/docs 查看完整的交互式 API 文档。

## ⚙️ 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `MYSQL_HOST` | MySQL 主机地址 | - | ✅ |
| `MYSQL_PORT` | MySQL 端口 | 3306 | ❌ |
| `MYSQL_USER` | MySQL 用户名 | - | ✅ |
| `MYSQL_PASSWORD` | MySQL 密码 | - | ✅ |
| `MYSQL_DATABASE` | 数据库名 | - | ✅ |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - | ✅ |
| `OPENAI_BASE_URL` | API 基础 URL | https://openai.qiniu.com | ❌ |
| `OPENAI_MODEL` | 模型名称 | - | ✅ |
| `TTS_MODEL` | TTS 模型 | tts | ❌ |

### 数据库配置

```python
# 连接池配置
DB_POOL_SIZE = 10          # 连接池大小
DB_MAX_OVERFLOW = 20       # 最大溢出连接
DB_POOL_TIMEOUT = 30       # 连接超时时间
DB_POOL_RECYCLE = 3600     # 连接回收时间
DB_ECHO = False            # 是否打印 SQL
```

## 🐳 部署指南

### Docker 部署

1. **构建镜像**:
```bash
docker build -t personatalk-backend .
```

2. **使用 Docker Compose**:
```bash
docker-compose up -d
```

3. **查看日志**:
```bash
docker-compose logs -f
```

### 生产环境部署

1. **使用 Nginx 反向代理**
2. **配置 SSL 证书**
3. **设置环境变量**
4. **配置日志轮转**
5. **设置监控和告警**

## 👨‍💻 开发指南

### 代码规范

- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 使用 **MyPy** 进行类型检查
- 使用 **Flake8** 进行代码检查

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行测试并生成覆盖率报告
poetry run pytest --cov=src

# 运行特定测试文件
poetry run pytest src/test/test_deps.py
```

### 代码格式化

```bash
# 格式化代码
poetry run black src/
poetry run isort src/

# 类型检查
poetry run mypy src/
```

### 添加新功能

1. **创建数据模型** (`src/model/`)
2. **实现 CRUD 操作** (`src/crud/`)
3. **添加 API 接口** (`src/api/api_v1/`)
4. **编写测试用例** (`src/test/`)
5. **更新文档**

## 📊 性能优化

### 数据库优化
- 使用连接池管理数据库连接
- 添加适当的数据库索引
- 使用异步数据库操作

### API 优化
- 使用异步处理提高并发性能
- 实现请求缓存机制
- 添加请求限流和熔断

### 监控和日志
- 集成 Prometheus 监控
- 使用结构化日志
- 添加性能指标收集

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目维护者: 朱德中 宗灵恩 滕柳明
- 项目链接: [https://github.com/MECREATOR/PersonaTalk](https://github.com/MECREATOR/PersonaTalk)

DEMO：通过网盘分享的文件：
链接: https://pan.baidu.com/s/1XHNRl5IJnnDi6WCEr6ZyDA 提取码: 1x4y 复制这段内容后打开百度网盘手机App，操作更方便哦

---

**PersonaTalk Backend** - 让 AI 对话更有趣！ 🚀
