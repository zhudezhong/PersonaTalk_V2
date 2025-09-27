"""
模型服务基础抽象类
定义统一的模型服务接口，支持不同模型的实现
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str  # system, user, assistant
    content: str


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


class ChatResponse(BaseModel):
    """聊天响应模型"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, Any]] = None


class StreamChoice(BaseModel):
    """流式响应选择项"""
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class StreamResponse(BaseModel):
    """流式响应模型"""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]


class BaseModelService(ABC):
    """模型服务基础抽象类"""
    
    def __init__(self, api_key: str, base_url: str, model: str, **kwargs):
        """
        初始化模型服务
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def chat_completion(
        self, 
        request: ChatRequest
    ) -> ChatResponse:
        """
        非流式聊天完成
        
        Args:
            request: 聊天请求
            
        Returns:
            ChatResponse: 聊天响应
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否健康
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            Dict[str, Any]: 模型信息
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "config": self.config
        }
