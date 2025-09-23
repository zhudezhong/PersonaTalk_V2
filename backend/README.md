# PersonaTalk Backend

## 技术栈

本项目采用 **FastAPI** 作为后端Web框架，FastAPI是一个现代、快速（高性能）的Web框架，用于构建基于Python的API。主要特点包括：

- **高性能**: 基于Starlette和Pydantic，性能可与NodeJS和Go媲美
- **自动文档生成**: 自动生成交互式API文档（Swagger UI）
- **类型提示支持**: 基于Python 3.6+的类型提示，提供更好的开发体验
- **异步支持**: 原生支持异步编程，适合高并发场景
- **数据验证**: 基于Pydantic的自动数据验证和序列化

## 项目结构

```
backend/
├── README.md                 # 项目说明文档
└── src/                     # 源代码目录
    ├── main.py              # 应用程序入口点
    ├── config.py            # 配置文件
    ├── api/                 # API相关模块
    │   ├── __init__.py      # API模块初始化
    │   ├── deps.py          # 依赖注入
    │   ├── error.py         # 错误处理
    │   └── api_v1/          # API v1版本
    │       └── __init__.py  # API v1初始化
    ├── model/               # 数据模型
    │   ├── __init__.py      # 模型模块初始化
    │   ├── history_chat.py  # 聊天历史模型
    │   └── history_session.py # 会话历史模型
    └── model_server/        # 模型服务器
        └── __init__.py      # 模型服务器初始化
```

## 目录说明

- **src/main.py**: 应用程序的主入口文件，负责启动FastAPI应用
- **src/config.py**: 项目配置文件，包含数据库连接、API密钥等配置信息
- **src/api/**: API相关功能模块
  - **deps.py**: 依赖注入，提供数据库连接、认证等依赖
  - **error.py**: 全局错误处理机制
  - **api_v1/**: API v1版本的路由和端点
- **src/model/**: 数据模型定义
  - **history_chat.py**: 聊天记录相关的数据模型
  - **history_session.py**: 会话记录相关的数据模型
- **src/model_server/**: 模型服务器相关功能，用于与AI模型进行交互
