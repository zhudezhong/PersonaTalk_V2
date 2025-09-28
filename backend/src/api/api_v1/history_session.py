from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field

from src.api.api_v1.chat import ApiResponse, ResponseCode
from src.crud.crud_history_chat import crud_history_chat
from src.model.history_chat import HistoryChat, ChatRole
from src.api.deps import get_db
from src.crud.crud_history_session import (
    crud_history_session,
    HistorySessionCreate,
    HistorySessionUpdate,
    HistorySessionResponse
)
from src.model.history_session import HistorySession

router = APIRouter()

# 聊天记录响应数据模型
class ChatRecordResponse(BaseModel):
    """聊天记录响应数据模型"""
    id: str = Field(description="聊天记录ID")
    session_id: str = Field(description="会话ID")
    role: ChatRole = Field(description="角色（用户或系统）")
    content: str = Field(description="对话内容")
    created_at: str = Field(description="创建时间")
    updated_at: str = Field(description="更新时间")

# 聊天记录列表响应数据模型
class ChatHistoryResponseData(BaseModel):
    """聊天历史响应数据模型"""
    session_id: str = Field(description="会话ID")
    total_count: int = Field(description="总记录数")
    chat_records: List[ChatRecordResponse] = Field(description="聊天记录列表")


@router.post("/", response_model=HistorySessionResponse, deprecated=True)
async def create_history_session(
    *,
    db: AsyncSession = Depends(get_db),
    session_in: HistorySessionCreate
) -> HistorySession:
    """
    创建新的历史会话
    
    Args:
        db: 数据库会话
        session_in: 会话创建数据
        
    Returns:
        HistorySession: 创建的历史会话
    """
    session = await crud_history_session.create(db=db, obj_in=session_in)
    return session


@router.get("/history_session", response_model=List[HistorySessionResponse])
async def get_history_session(
    *,
    db: AsyncSession = Depends(get_db),
    username: Optional[str] = Query(default="admin", description="用户名"),
    page: int = Query(0, ge=0, description="跳过的记录数"),
    page_size: int = Query(20, ge=1, le=1000, description="限制返回的记录数"),
) -> List[HistorySession]:
    """
    根据用户名获取历史会话列表
    
    Args:
        db: 数据库会话
        username: 用户名
        page: 页码
        page_size: 每页记录数
        
    Returns:
        List[HistorySession]: 历史会话列表
    """
    sessions = await crud_history_session.get_multi(db=db, username=username, page=page, page_size=page_size)
    return sessions

@router.get("/{session_id}/chats", response_model=ApiResponse[ChatHistoryResponseData])
async def get_history_chat_by_session_id(
    *,
    db: AsyncSession = Depends(get_db),
    session_id: str,
) -> ApiResponse[ChatHistoryResponseData]:
    """
    根据会话ID获取历史聊天记录
    
    Args:
        db: 数据库会话
        session_id: 会话ID
        
    Returns:
        ApiResponse[ChatHistoryResponseData]: 包含聊天记录的响应数据
        
    Raises:
        HTTPException: 会话不存在时抛出404错误
    """
    try:
        # 验证会话是否存在
        session = await crud_history_session.get(db=db, id=session_id)
        if not session:
            return ApiResponse(
                code=ResponseCode.NOT_FOUND, 
                message=f"会话 {session_id} 不存在"
            )
        
        # 获取聊天记录
        chats = await crud_history_chat.get_by_session_id(db=db, session_id=session_id)
        
        # 转换为响应数据模型
        chat_records = []
        for chat in chats:
            chat_record = ChatRecordResponse(
                id=chat.id,
                session_id=chat.session_id,
                role=chat.role,
                content=chat.content,
                created_at=chat.created_at.isoformat() if chat.created_at else "",
                updated_at=chat.updated_at.isoformat() if chat.updated_at else ""
            )
            chat_records.append(chat_record)
        
        # 构建响应数据
        response_data = ChatHistoryResponseData(
            session_id=session_id,
            total_count=len(chat_records),
            chat_records=chat_records
        )
        
        return ApiResponse(
            code=ResponseCode.SUCCESS,
            data=response_data, 
            message=f"成功获取会话 {session_id} 的聊天记录，共 {len(chat_records)} 条"
        )
        
    except Exception as e:
        return ApiResponse(
            code=ResponseCode.INTERNAL_ERROR,
            message=f"获取聊天记录失败: {str(e)}"
        )


@router.delete("/{session_id}", response_model=HistorySessionResponse)
async def delete_history_session(
    *,
    db: AsyncSession = Depends(get_db),
    session_id: str,
) -> HistorySession:
    """
    删除历史会话
    
    Args:
        db: 数据库会话
        session_id: 会话ID
        hard_delete: 是否硬删除（默认软删除）
        
    Returns:
        HistorySession: 删除的历史会话
        
    Raises:
        HTTPException: 会话不存在时抛出404错误
    """
    session = await crud_history_session.soft_delete(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="历史会话不存在")
    
    return session


@router.get("/search", response_model=List[HistorySessionResponse])
async def search_history_session(
    *,
    db: AsyncSession = Depends(get_db),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(0, ge=0, description="跳过的记录数"),
    page_size: int = Query(20, ge=1, le=1000, description="限制返回的记录数"),
) -> List[HistorySession]:
    sessions = await crud_history_session.search_sessions(db=db, keyword=keyword, page=page, page_size=page_size)
    return sessions
