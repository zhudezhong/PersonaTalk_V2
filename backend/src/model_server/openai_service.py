"""
OpenAI 兼容的模型服务实现
支持 OpenAI API 格式的各种模型服务
"""
import json
import time
import uuid
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, AsyncGenerator
from src.model_server.base import BaseModelService, ChatRequest, ChatResponse, StreamResponse, StreamChoice


class OpenAIModelService(BaseModelService):
    """OpenAI 兼容的模型服务"""
    
    def __init__(self, api_key: str, base_url: str, model: str, **kwargs):
        """
        初始化 OpenAI 模型服务
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, base_url, model, **kwargs)
        self.timeout = kwargs.get('timeout', 30)
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = kwargs.get('retry_delay', 1)
    
    async def _make_request(
        self, 
        url: str, 
        payload: Dict[str, Any], 
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求
        
        Args:
            url: 请求URL
            payload: 请求载荷
            headers: 请求头
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"API请求失败: {response.status} - {error_text}")
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        raise Exception("请求失败，已达到最大重试次数")
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """
        非流式聊天完成
        
        Args:
            request: 聊天请求
            
        Returns:
            ChatResponse: 聊天响应
        """
        url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求载荷
        payload = {
            "model": request.model or self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "stream": False
        }
        
        # 添加可选参数
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            payload["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            payload["presence_penalty"] = request.presence_penalty
        
        try:
            response_data = await self._make_request(url, payload, headers)
            
            # 转换为标准响应格式
            return ChatResponse(
                id=response_data.get("id", str(uuid.uuid4())),
                created=response_data.get("created", int(time.time())),
                model=response_data.get("model", self.model),
                choices=response_data.get("choices", []),
                usage=response_data.get("usage")
            )
        except Exception as e:
            raise Exception(f"聊天完成失败: {str(e)}")
    
    async def chat_completion_stream(
        self, 
        request: ChatRequest
    ) -> AsyncGenerator[StreamResponse, None]:
        """
        流式聊天完成
        
        Args:
            request: 聊天请求
            
        Yields:
            StreamResponse: 流式响应
        """
        url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求载荷
        payload = {
            "model": request.model or self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "stream": True
        }
        
        # 添加可选参数
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            payload["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            payload["presence_penalty"] = request.presence_penalty
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"流式API请求失败: {response.status} - {error_text}")
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]  # 移除 'data: ' 前缀
                            if data == '[DONE]':
                                break
                            
                            try:
                                chunk_data = json.loads(data)
                                yield StreamResponse(
                                    id=chunk_data.get("id", str(uuid.uuid4())),
                                    created=chunk_data.get("created", int(time.time())),
                                    model=chunk_data.get("model", self.model),
                                    choices=[
                                        StreamChoice(
                                            index=choice.get("index", 0),
                                            delta=choice.get("delta", {}),
                                            finish_reason=choice.get("finish_reason")
                                        )
                                        for choice in chunk_data.get("choices", [])
                                    ]
                                )
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            raise Exception(f"流式聊天完成失败: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否健康
        """
        try:
            # 发送一个简单的测试请求
            test_request = ChatRequest(
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=1
            )
            await self.chat_completion(test_request)
            return True
        except Exception:
            return False

async def main():
    service = OpenAIModelService(
        api_key="",
        base_url="https://openai.qiniu.com/",
        model="deepseek-r1"
    )
    res1 = await service.chat_completion(ChatRequest(
        messages=[
            {"role": "user", "content": "hello, 你是谁？"}
        ],
        max_tokens=1
    ))
    # 非流式调用对话模型
    print("#" * 20, "非流式调用对话生成", "#" * 20)
    print(res1.choices[0]["message"]["reasoning_content"])

    print("#" * 20, "流式调用对话生成", "#" * 20)
    async for chunk in service.chat_completion_stream(ChatRequest(
        messages=[
            {"role": "user", "content": "hello, 你是谁？"}
        ],
        max_tokens=1
    )):
        print(chunk.choices[0].delta.get("reasoning_content", ""), end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
