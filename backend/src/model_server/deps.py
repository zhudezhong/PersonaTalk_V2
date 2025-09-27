"""
模型服务依赖注入
提供模型服务的依赖注入功能
"""
from typing import Annotated
from fastapi import Depends
from src.model_server.factory import model_service_manager, ModelServiceManager
from src.model_server.base import BaseModelService
from src.config import settings


def get_model_service_manager() -> ModelServiceManager:
    """
    获取模型服务管理器
    
    Returns:
        ModelServiceManager: 模型服务管理器实例
    """
    return model_service_manager


def get_model_service(
    manager: Annotated[ModelServiceManager, Depends(get_model_service_manager)]
) -> BaseModelService:
    """
    获取默认模型服务
    
    Args:
        manager: 模型服务管理器
        
    Returns:
        BaseModelService: 模型服务实例
    """
    return manager.get_service()


def init_model_service():
    """
    初始化模型服务
    从配置文件创建默认模型服务
    """
    config = settings.get_model_config()
    
    # 检查是否已经存在同名服务
    if config["service_name"] not in model_service_manager._services:
        model_service_manager.add_service(
            name=config["service_name"],
            service_type=config["service_type"],
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=config["model"],
            timeout=config["timeout"],
            max_retries=config["max_retries"],
            retry_delay=config["retry_delay"]
        )
        print(f"模型服务已初始化: {config['service_name']} ({config['service_type']})")
    else:
        print(f"模型服务已存在: {config['service_name']}")


# 类型别名，用于依赖注入
ModelService = Annotated[BaseModelService, Depends(get_model_service)]
ModelServiceManagerDep = Annotated[ModelServiceManager, Depends(get_model_service_manager)]
# manager = get_model_service_manager()
# service = get_model_service(manager)
# print(service.get_model_info())