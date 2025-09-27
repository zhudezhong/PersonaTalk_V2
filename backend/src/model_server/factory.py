"""
模型服务工厂类
用于创建和管理不同的模型服务实例
"""
from typing import Dict, Any, Optional, Type
from .base import BaseModelService, ChatRequest, ChatResponse, StreamResponse
from .openai_service import OpenAIModelService


class ModelServiceFactory:
    """模型服务工厂类"""
    
    # 注册的模型服务类型
    _services: Dict[str, Type[BaseModelService]] = {
        "openai": OpenAIModelService,
        "deepseek": OpenAIModelService,  # DeepSeek 使用 OpenAI 兼容的 API
        "qiniu": OpenAIModelService,     # 七牛云使用 OpenAI 兼容的 API
    }
    
    @classmethod
    def register_service(cls, name: str, service_class: Type[BaseModelService]):
        """
        注册新的模型服务类型
        
        Args:
            name: 服务名称
            service_class: 服务类
        """
        cls._services[name] = service_class
    
    @classmethod
    def create_service(
        self, 
        service_type: str, 
        api_key: str, 
        base_url: str, 
        model: str, 
        **kwargs
    ) -> BaseModelService:
        """
        创建模型服务实例
        
        Args:
            service_type: 服务类型 (openai, deepseek, qiniu 等)
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            **kwargs: 其他配置参数
            
        Returns:
            BaseModelService: 模型服务实例
            
        Raises:
            ValueError: 不支持的服务类型
        """
        if service_type not in self._services:
            raise ValueError(f"不支持的服务类型: {service_type}. 支持的类型: {list(self._services.keys())}")
        
        service_class = self._services[service_type]
        return service_class(api_key=api_key, base_url=base_url, model=model, **kwargs)
    
    @classmethod
    def get_supported_services(cls) -> list:
        """
        获取支持的服务类型列表
        
        Returns:
            list: 支持的服务类型列表
        """
        return list(cls._services.keys())


class ModelServiceManager:
    """模型服务管理器"""
    
    def __init__(self):
        self._services: Dict[str, BaseModelService] = {}
        self._default_service: Optional[str] = None
    
    def add_service(
        self, 
        name: str, 
        service_type: str, 
        api_key: str, 
        base_url: str, 
        model: str, 
        **kwargs
    ) -> BaseModelService:
        """
        添加模型服务
        
        Args:
            name: 服务名称
            service_type: 服务类型
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            **kwargs: 其他配置参数
            
        Returns:
            BaseModelService: 创建的模型服务实例
        """
        service = ModelServiceFactory.create_service(
            service_type=service_type,
            api_key=api_key,
            base_url=base_url,
            model=model,
            **kwargs
        )
        self._services[name] = service
        
        # 如果这是第一个服务，设为默认服务
        if self._default_service is None:
            self._default_service = name
        
        return service
    
    def get_service(self, name: Optional[str] = None) -> BaseModelService:
        """
        获取模型服务实例
        
        Args:
            name: 服务名称，如果为 None 则返回默认服务
            
        Returns:
            BaseModelService: 模型服务实例
            
        Raises:
            ValueError: 服务不存在
        """
        if name is None:
            name = self._default_service
        
        if name not in self._services:
            raise ValueError(f"服务不存在: {name}")
        
        return self._services[name]
    
    def set_default_service(self, name: str):
        """
        设置默认服务
        
        Args:
            name: 服务名称
            
        Raises:
            ValueError: 服务不存在
        """
        if name not in self._services:
            raise ValueError(f"服务不存在: {name}")
        self._default_service = name
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有服务信息
        
        Returns:
            Dict[str, Dict[str, Any]]: 服务信息字典
        """
        return {
            name: {
                "info": service.get_model_info(),
                "is_default": name == self._default_service
            }
            for name, service in self._services.items()
        }
    
    def remove_service(self, name: str) -> bool:
        """
        移除服务
        
        Args:
            name: 服务名称
            
        Returns:
            bool: 是否成功移除
        """
        if name in self._services:
            del self._services[name]
            
            # 如果移除的是默认服务，重新设置默认服务
            if name == self._default_service:
                self._default_service = next(iter(self._services.keys())) if self._services else None
            
            return True
        return False


# 全局模型服务管理器实例
model_service_manager = ModelServiceManager()
