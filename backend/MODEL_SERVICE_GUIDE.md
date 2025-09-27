# 模型服务使用指南

## 概述

本项目已集成可扩展的模型服务模块，支持多种模型服务的统一接口和切换。

## 文件结构

```
src/model_server/
├── __init__.py          # 模块导出
├── base.py              # 基础抽象类
├── openai_service.py    # OpenAI 兼容服务实现
├── factory.py           # 模型服务工厂和管理器
├── deps.py              # FastAPI 依赖注入
├── example.py           # 使用示例
└── README.md            # 详细文档
```

## 快速开始

### 1. 安装依赖

```bash
poetry install
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# 模型服务配置
MODEL_SERVICE_TYPE=qiniu
MODEL_SERVICE_NAME=default
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://openai.qiniu.com
OPENAI_MODEL=deepseek-r1
MODEL_TIMEOUT=30
MODEL_MAX_RETRIES=3
MODEL_RETRY_DELAY=1
```

### 3. 启动服务

```bash
poetry run start
```

### 4. 测试 API

访问 `http://localhost:8000/docs` 查看 API 文档。

## API 端点

### 聊天完成

```bash
POST /api/v1/chat/completions
```

请求示例：

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 100
}
```

### 流式聊天

```bash
POST /api/v1/chat/completions/stream
```

### 模型列表

```bash
GET /api/v1/chat/models
```

### 健康检查

```bash
GET /api/v1/chat/health
```

## 代码使用示例

### 基础使用

```python
from src.model_server import model_service_manager, ChatRequest, ChatMessage

# 创建聊天请求
request = ChatRequest(
    messages=[
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Hello!")
    ]
)

# 发送请求
service = model_service_manager.get_service()
response = await service.chat_completion(request)
print(response.choices[0]['message']['content'])
```

### 流式响应

```python
async for chunk in service.chat_completion_stream(request):
    if chunk.choices[0].delta.get("content"):
        print(chunk.choices[0].delta["content"], end="", flush=True)
```

### 多服务管理

```python
# 添加多个服务
model_service_manager.add_service(
    name="qiniu",
    service_type="qiniu",
    api_key="qiniu-key",
    base_url="https://openai.qiniu.com",
    model="deepseek-r1"
)

# 切换服务
model_service_manager.set_default_service("qiniu")
```

## 支持的模型服务

- **qiniu**: 七牛云 (OpenAI 兼容)
- **deepseek**: DeepSeek (OpenAI 兼容)
- **openai**: OpenAI API

## 扩展新的模型服务

1. 继承 `BaseModelService` 类
2. 实现必要的方法
3. 在 `ModelServiceFactory` 中注册

```python
class CustomModelService(BaseModelService):
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        # 实现逻辑
        pass
    
    async def chat_completion_stream(self, request: ChatRequest):
        # 实现流式逻辑
        pass
    
    async def health_check(self) -> bool:
        # 实现健康检查
        pass

# 注册服务
ModelServiceFactory.register_service("custom", CustomModelService)
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

## 注意事项

1. 确保 API 密钥正确配置
2. 检查网络连接和防火墙设置
3. 注意 API 调用频率限制
4. 生产环境中建议设置合适的超时和重试参数

## 故障排除

### 常见问题

1. **导入错误**: 确保已安装 `aiohttp` 依赖
2. **连接超时**: 检查网络连接和 API 地址
3. **认证失败**: 验证 API 密钥是否正确
4. **模型不存在**: 确认模型名称是否正确

### 调试方法

1. 查看应用日志
2. 使用健康检查端点
3. 测试简单的聊天请求
4. 检查网络连接
