# 模型服务模块

这个模块提供了一个统一的模型服务接口，支持多种模型服务的切换，包括 OpenAI、DeepSeek、七牛云等。

## 特性

- 🚀 **统一接口**: 所有模型服务都使用相同的接口
- 🔄 **易于切换**: 通过配置文件即可切换不同的模型服务
- 📦 **可扩展**: 支持添加新的模型服务类型
- 🔧 **配置灵活**: 支持超时、重试等配置
- 📊 **流式支持**: 支持流式和非流式响应
- 🏥 **健康检查**: 内置健康检查功能

## 快速开始

### 1. 配置环境变量

在 `.env` 文件中配置模型服务参数：

```env
# 模型服务配置
MODEL_SERVICE_TYPE=qiniu
MODEL_SERVICE_NAME=default
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://openai.qiniu.com
OPENAI_MODEL=deepseek-r1
MODEL_TIMEOUT=30
MODEL_MAX_RETRIES=3
MODEL_RETRY_DELAY=1
```

### 2. 基础使用

```python
from src.model_server import model_service_manager, ChatRequest, ChatMessage
from src.config import settings

# 从配置创建服务
config = settings.get_model_config()
service = model_service_manager.add_service(
    name=config["service_name"],
    service_type=config["service_type"],
    api_key=config["api_key"],
    base_url=config["base_url"],
    model=config["model"]
)

# 创建聊天请求
request = ChatRequest(
    messages=[
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Hello!")
    ]
)

# 发送请求
response = await service.chat_completion(request)
print(response.choices[0]['message']['content'])
```

### 3. 流式响应

```python
# 创建流式请求
request = ChatRequest(
    messages=[
        ChatMessage(role="user", content="Write a poem")
    ],
    stream=True
)

# 流式响应
async for chunk in service.chat_completion_stream(request):
    if chunk.choices[0].delta.get("content"):
        print(chunk.choices[0].delta["content"], end="", flush=True)
```

## 支持的模型服务

### 当前支持的服务类型

- `openai`: OpenAI API
- `deepseek`: DeepSeek API (OpenAI 兼容)
- `qiniu`: 七牛云 API (OpenAI 兼容)

### 添加新的模型服务

1. 继承 `BaseModelService` 类
2. 实现必要的方法
3. 在 `ModelServiceFactory` 中注册

```python
from .base import BaseModelService

class CustomModelService(BaseModelService):
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        # 实现非流式聊天
        pass
    
    async def chat_completion_stream(self, request: ChatRequest):
        # 实现流式聊天
        pass
    
    async def health_check(self) -> bool:
        # 实现健康检查
        pass

# 注册服务
ModelServiceFactory.register_service("custom", CustomModelService)
```

## 多服务管理

```python
# 添加多个服务
model_service_manager.add_service(
    name="qiniu",
    service_type="qiniu",
    api_key="qiniu-key",
    base_url="https://openai.qiniu.com",
    model="deepseek-r1"
)

model_service_manager.add_service(
    name="openai",
    service_type="openai", 
    api_key="openai-key",
    base_url="https://api.openai.com",
    model="gpt-3.5-turbo"
)

# 切换默认服务
model_service_manager.set_default_service("openai")

# 使用特定服务
service = model_service_manager.get_service("qiniu")
```

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `MODEL_SERVICE_TYPE` | 服务类型 | `qiniu` |
| `MODEL_SERVICE_NAME` | 服务名称 | `default` |
| `OPENAI_API_KEY` | API密钥 | - |
| `OPENAI_BASE_URL` | API基础URL | - |
| `OPENAI_MODEL` | 模型名称 | - |
| `MODEL_TIMEOUT` | 请求超时时间(秒) | `30` |
| `MODEL_MAX_RETRIES` | 最大重试次数 | `3` |
| `MODEL_RETRY_DELAY` | 重试延迟(秒) | `1` |

## 错误处理

所有方法都会抛出异常，建议使用 try-catch 进行错误处理：

```python
try:
    response = await service.chat_completion(request)
except Exception as e:
    print(f"请求失败: {e}")
```

## 示例

查看 `example.py` 文件获取完整的使用示例。

## 依赖

- `aiohttp`: 异步 HTTP 客户端
- `pydantic`: 数据验证
- `pydantic-settings`: 配置管理
