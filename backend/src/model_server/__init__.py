"""
模型服务模块
提供统一的模型服务接口，支持多种模型服务的切换
"""

from .base import BaseModelService, ChatRequest, ChatResponse, StreamResponse, ChatMessage
from .openai_service import OpenAIModelService
from .factory import ModelServiceFactory, ModelServiceManager, model_service_manager
from .deps import get_model_service, get_model_service_manager, init_model_service, ModelService, ModelServiceManagerDep
from .tts_service import tts_service
__all__ = [
    "BaseModelService",
    "ChatRequest", 
    "ChatResponse",
    "StreamResponse",
    "ChatMessage",
    "OpenAIModelService",
    "ModelServiceFactory",
    "ModelServiceManager", 
    "model_service_manager",
    "get_model_service",
    "get_model_service_manager", 
    "init_model_service",
    "ModelService",
    "ModelServiceManagerDep",
    "tts_service"
]
