"""
聊天 API 端点
演示如何使用模型服务进行聊天对话
"""
from typing import Annotated, List, Optional, Generic, TypeVar
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.crud_history_chat import crud_history_chat
from src.model_server.deps import get_model_service
from src.model_server import BaseModelService, ChatRequest, ChatMessage, ChatResponse
from src.crud.crud_history_session import HistorySessionCreate, crud_history_session
from src.api.deps import get_db
from src.crud.crud_history_chat import HistoryChatCreate
from src.model.history_chat import ChatRole

import json
import time
from typing import Generic, TypeVar, Any
from enum import Enum

router = APIRouter()


class ChatRequestModel(BaseModel):
    """聊天请求模型"""
    session_id: Optional[str] = Field(None, description="会话ID，如果不存在则创建新会话")
    message: str = Field(description="用户消息")
    system_prompt: str = Field("You are a helpful assistant.", description="系统提示词")

# 添加响应状态码枚举
class ResponseCode(int, Enum):
    """响应状态码枚举"""
    SUCCESS = 200          # 成功
    BAD_REQUEST = 400      # 请求参数错误
    UNAUTHORIZED = 401     # 未授权
    FORBIDDEN = 403        # 禁止访问
    NOT_FOUND = 404        # 资源不存在
    INTERNAL_ERROR = 500   # 服务器内部错误
    SERVICE_ERROR = 502    # 外部服务错误

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """统一的API响应模型"""
    code: int = Field(description="响应状态码")
    message: str = Field(description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

# 聊天响应模型
class ChatResponseData(BaseModel):
    """聊天响应数据模型"""
    session_id: str
    response: str

# 流式聊天响应
class StreamChatResponseData(BaseModel):
    """流式聊天响应数据模型"""
    session_id: str
    content: str
    message_id: str


@router.post("/text_chat", response_model=ApiResponse[ChatResponseData])
async def chat_completions(
    request: ChatRequestModel,
    model_service: Annotated[BaseModelService, Depends(get_model_service)],
    db: AsyncSession = Depends(get_db),
):
    """
    聊天完成端点
    
    Args:
        request: 聊天请求
        model_service: 模型服务依赖注入
        db: 数据库会话
        
    Returns:
        ApiResponse[ChatResponseData]: 统一格式的聊天响应
    """
    try:
        # 1. 处理会话
        session_id = request.session_id
        if session_id:
            # 检查会话是否存在
            session = await crud_history_session.get_by_id(db, id=session_id)
            if not session:
                # 会话不存在，创建新会话
                session_id = None
        
        if not session_id:
            # 创建新会话
            session_name = request.message or "新对话..."
            session_create = HistorySessionCreate(
                session_name=session_name
            )
            session = await crud_history_session.create(db, obj_in=session_create)
            session_id = session.id
        
        # 2. 获取历史聊天记录        
        history_chats = await crud_history_chat.get_by_session_id(
            db, 
            session_id=session_id, 
        )
        
        # 3. 构建消息列表
        messages = []
        
        # 添加系统提示词
        if request.system_prompt:
            messages.append(ChatMessage(role=ChatRole.SYSTEM.value, content=request.system_prompt))
        
        # 添加历史记录（按时间顺序）
        for chat in history_chats:
            messages.append(ChatMessage(role=chat.role.value, content=chat.content))
        
        # 添加当前用户消息
        messages.append(ChatMessage(role=ChatRole.USER.value, content=request.message))
        
        # 4. 保存用户消息到数据库
        user_chat_create = HistoryChatCreate(
            session_id=session_id,
            role=ChatRole.USER,
            content=request.message
        )
        await crud_history_chat.create(db, obj_in=user_chat_create)
        
        # 5. 创建聊天请求
        chat_request = ChatRequest(
            messages=messages,
            temperature=0.7,
            max_tokens=4096
        )
        
        # 6. 发送请求到模型服务
        response = await model_service.chat_completion(chat_request)
        
        # 7. 保存助手回复到数据库
        assistant_content = response.choices[0]['message']['content']
        assistant_chat_create = HistoryChatCreate(
            session_id=session_id,
            role=ChatRole.SYSTEM,
            content=assistant_content
        )
        await crud_history_chat.create(db, obj_in=assistant_chat_create)
        
        # 8. 返回统一格式的结果  
        response_data = ChatResponseData(
            session_id=session_id,
            response=assistant_content
        )
        
        return ApiResponse(
            code=ResponseCode.SUCCESS,
            message="聊天完成",
            data=response_data
        )
        
    except Exception as e:
        return ApiResponse(
            code=ResponseCode.SERVICE_ERROR,
            message=f"聊天请求失败: {str(e)}",
            data=None
        )


@router.post("/text_chat_stream")
async def chat_completions_stream(
    request: ChatRequestModel,
    model_service: Annotated[BaseModelService, Depends(get_model_service)],
    db: AsyncSession = Depends(get_db),
):
    """
    流式聊天完成端点
    
    Args:
        request: 聊天请求
        model_service: 模型服务依赖注入
        db: 数据库会话
        
    Returns:
        StreamingResponse: 流式响应
    """
    async def generate_response():
        try:
            # 1. 处理会话
            session_id = request.session_id
            if session_id:
                # 检查会话是否存在
                session = await crud_history_session.get_by_id(db, id=session_id)
                if not session:
                    # 会话不存在，创建新会话
                    session_id = None
            
            if not session_id:
                # 创建新会话
                session_name = request.message or "新对话..."
                session_create = HistorySessionCreate(
                    session_name=session_name
                )
                session = await crud_history_session.create(db, obj_in=session_create)
                session_id = session.id
            
            # 2. 获取历史聊天记录        
            history_chats = await crud_history_chat.get_by_session_id(
                db, 
                session_id=session_id, 
            )
            
            # 3. 构建消息列表
            messages = []
            
            # 添加系统提示词
            if request.system_prompt:
                messages.append(ChatMessage(role=ChatRole.SYSTEM.value, content=request.system_prompt))
            
            # 添加历史记录（按时间顺序）
            for chat in history_chats:
                messages.append(ChatMessage(role=chat.role.value, content=chat.content))
            
            # 添加当前用户消息
            messages.append(ChatMessage(role=ChatRole.USER.value, content=request.message))
            
            # 4. 保存用户消息到数据库
            user_chat_create = HistoryChatCreate(
                session_id=session_id,
                role=ChatRole.USER,
                content=request.message
            )
            await crud_history_chat.create(db, obj_in=user_chat_create)
            
            # 5. 创建聊天请求
            chat_request = ChatRequest(
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                stream=True
            )
            
            # 6. 发送流式请求到模型服务
            assistant_content = ""
            message_id = ""
            model_name = ""
            
            async for chunk in model_service.chat_completion_stream(chat_request):
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    content = delta.get('content', '')
                    if content:
                        assistant_content += content
                    
                    # 保存 message_id 和 model 信息
                    if not message_id:
                        message_id = chunk.id
                    if not model_name:
                        model_name = chunk.model
                    
                    # 构建统一格式的流式响应
                    stream_data = StreamChatResponseData(
                        session_id=session_id,
                        content=content,
                        message_id=chunk.id
                    )
                    
                    api_response = ApiResponse(
                        code=ResponseCode.SUCCESS,
                        message="流式数据",
                        data=stream_data
                    )
                    
                    yield f"data: {json.dumps(api_response.model_dump(), ensure_ascii=False)}\n\n"
                    
                    # 如果对话结束，保存完整的助手回复到数据库
                    if chunk.choices[0].finish_reason:
                        assistant_chat_create = HistoryChatCreate(
                            session_id=session_id,
                            role=ChatRole.SYSTEM,
                            content=assistant_content
                        )
                        await crud_history_chat.create(db, obj_in=assistant_chat_create)
                        
                        # 发送结束信号
                        final_data = StreamChatResponseData(
                            session_id=session_id,
                            content="",
                            message_id=message_id
                        )
                        
                        final_response = ApiResponse(
                            code=ResponseCode.SUCCESS,
                            message="对话完成",
                            data=final_data
                        )
                        
                        yield f"data: {json.dumps(final_response.model_dump(), ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"
                        break
                        
        except Exception as e:
            error_response = ApiResponse(
                code=ResponseCode.SERVICE_ERROR,
                message=f"流式聊天请求失败: {str(e)}",
                data=None
            )
            yield f"data: {json.dumps(error_response.model_dump(), ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


# 修改其他端点使用统一响应格式
@router.get("/models", response_model=ApiResponse[List[dict]])
async def list_models(model_service: Annotated[BaseModelService, Depends(get_model_service)]):
    """
    列出可用模型
    
    Args:
        model_service: 模型服务依赖注入
        
    Returns:
        ApiResponse[List[dict]]: 统一格式的模型信息响应
    """
    try:
        model_info = model_service.get_model_info()
        models_data = [
            {
                "id": model_info["model"],
                "object": "model",
                "created": 0,
                "owned_by": "personatalk"
            }
        ]
        return ApiResponse(
            code=ResponseCode.SUCCESS,
            message="获取模型列表成功",
            data=models_data
        )
    except Exception as e:
        return ApiResponse(
            code=ResponseCode.SERVICE_ERROR,
            message=f"获取模型信息失败: {str(e)}",
            data=None
        )

@router.get("/health", response_model=ApiResponse[dict])
async def health_check(model_service: Annotated[BaseModelService, Depends(get_model_service)]):
    """
    模型服务健康检查
    
    Args:
        model_service: 模型服务依赖注入
        
    Returns:
        ApiResponse[dict]: 统一格式的健康状态响应
    """
    try:
        is_healthy = await model_service.health_check()
        health_data = {
            "status": "healthy" if is_healthy else "unhealthy",
            "model": model_service.get_model_info()["model"]
        }
        return ApiResponse(
            code=ResponseCode.SUCCESS,
            message="健康检查完成",
            data=health_data
        )
    except Exception as e:
        return ApiResponse(
            code=ResponseCode.SERVICE_ERROR,
            message="健康检查失败",
            data={
                "status": "unhealthy",
                "error": str(e)
            }
        )
