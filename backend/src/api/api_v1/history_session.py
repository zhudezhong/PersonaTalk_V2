from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.api.deps import get_db
from src.crud.crud_history_session import (
    crud_history_session,
    HistorySessionCreate,
    HistorySessionUpdate,
    HistorySessionResponse
)
from src.model.history_session import HistorySession

router = APIRouter()


@router.post("/", response_model=HistorySessionResponse)
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
