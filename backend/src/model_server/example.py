"""
模型服务使用示例
演示如何使用模型服务进行聊天对话
"""
import asyncio
from typing import List
from src.model_server.factory import model_service_manager
from src.model_server.base import ChatRequest, ChatMessage
from src.config import settings


async def example_basic_chat():
    """基础聊天示例"""
    print("=== 基础聊天示例 ===")
    
    # 从配置创建模型服务
    config = settings.get_model_config()
    service = model_service_manager.add_service(
        name=config["service_name"],
        service_type=config["service_type"],
        api_key=config["api_key"],
        base_url=config["base_url"],
        model=config["model"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
        retry_delay=config["retry_delay"]
    )
    
    # 创建聊天请求
    request = ChatRequest(
        messages=[
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello! How are you today?")
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    try:
        # 发送请求
        response = await service.chat_completion(request)
        print(f"模型: {response.model}")
        print(f"响应: {response.choices[0]['message']['content']}")
        if response.usage:
            print(f"Token使用: {response.usage}")
    except Exception as e:
        print(f"请求失败: {e}")


async def example_stream_chat():
    """流式聊天示例"""
    print("\n=== 流式聊天示例 ===")
    
    # 获取服务
    service = model_service_manager.get_service()
    
    # 创建流式聊天请求
    request = ChatRequest(
        messages=[
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="请写一首关于春天的短诗")
        ],
        temperature=0.8,
        max_tokens=200,
        stream=True
    )
    
    try:
        print("流式响应:")
        async for chunk in service.chat_completion_stream(request):
            if chunk.choices[0].delta.get("content"):
                print(chunk.choices[0].delta["content"], end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"流式请求失败: {e}")


async def example_multi_service():
    """多服务示例"""
    print("\n=== 多服务示例 ===")
    
    # 添加多个服务
    # 七牛云服务
    qiniu_service = model_service_manager.add_service(
        name="qiniu",
        service_type="qiniu",
        api_key="your-qiniu-api-key",
        base_url="https://openai.qiniu.com",
        model="deepseek-r1"
    )
    
    # OpenAI 服务（示例）
    openai_service = model_service_manager.add_service(
        name="openai",
        service_type="openai",
        api_key="your-openai-api-key",
        base_url="https://api.openai.com",
        model="gpt-3.5-turbo"
    )
    
    # 列出所有服务
    services = model_service_manager.list_services()
    print("可用服务:")
    for name, info in services.items():
        print(f"  - {name}: {info['info']['model']} (默认: {info['is_default']})")
    
    # 使用特定服务
    request = ChatRequest(
        messages=[
            ChatMessage(role="user", content="What is 2+2?")
        ],
        max_tokens=50
    )
    
    try:
        # 使用七牛云服务
        response = await qiniu_service.chat_completion(request)
        print(f"\n七牛云响应: {response.choices[0]['message']['content']}")
        
        # 切换到 OpenAI 服务
        model_service_manager.set_default_service("openai")
        openai_response = await model_service_manager.get_service().chat_completion(request)
        print(f"OpenAI响应: {openai_response.choices[0]['message']['content']}")
        
    except Exception as e:
        print(f"多服务请求失败: {e}")


async def example_health_check():
    """健康检查示例"""
    print("\n=== 健康检查示例 ===")
    
    service = model_service_manager.get_service()
    
    try:
        is_healthy = await service.health_check()
        print(f"服务健康状态: {'健康' if is_healthy else '不健康'}")
    except Exception as e:
        print(f"健康检查失败: {e}")


async def main():
    """主函数"""
    print("模型服务使用示例")
    print("=" * 50)
    
    # 运行示例
    await example_basic_chat()
    await example_stream_chat()
    await example_multi_service()
    await example_health_check()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
