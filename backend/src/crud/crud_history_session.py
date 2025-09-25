from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_
from pydantic import BaseModel, Field

from src.model.history_session import HistorySession
from src.crud.base import CRUDBase


class HistorySessionCreate(BaseModel):
    """创建历史会话的请求模型"""
    username: str = Field(default="admin", description="用户名")
    session_name: str


class HistorySessionUpdate(BaseModel):
    """更新历史会话的请求模型"""
    session_name: Optional[str] = None
    is_deleted: Optional[bool] = None


class HistorySessionResponse(BaseModel):
    """历史会话响应模型"""
    id: str
    username: str
    session_name: str
    is_deleted: bool
    created_at: str
    updated_at: str


class CRUDHistorySession(CRUDBase[HistorySession, HistorySessionCreate, HistorySessionUpdate]):
    """历史会话CRUD操作类"""
    
    def __init__(self):
        super().__init__(HistorySession)
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: HistorySessionCreate
    ) -> HistorySession:
        """
        创建新的历史会话
        
        Args:
            db: 数据库会话
            obj_in: 创建数据
            
        Returns:
            HistorySession: 创建的历史会话对象
        """
        db_obj = HistorySession(
            username=obj_in.username,
            session_name=obj_in.session_name,
            is_deleted=False
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_id(
        self, 
        db: AsyncSession, 
        *, 
        id: str
    ) -> Optional[HistorySession]:
        """
        根据ID获取历史会话
        
        Args:
            db: 数据库会话
            id: 会话ID
            
        Returns:
            Optional[HistorySession]: 历史会话对象或None
        """
        result = await db.execute(
            select(HistorySession).where(
                and_(
                    HistorySession.id == id,
                    HistorySession.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 0, 
        page_size: int = 20,
        username: Optional[str] = "admin"
    ) -> List[HistorySession]:
        """
        获取历史会话列表
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页记录数
            username: 用户名过滤（可选）
            
        Returns:
            List[HistorySession]: 历史会话列表
        """
        query = select(HistorySession).where(HistorySession.is_deleted == False)
        
        if username:
            query = query.where(HistorySession.username == username)
        
        query = query.offset(page * page_size).limit(page_size).order_by(HistorySession.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_username(
        self, 
        db: AsyncSession, 
        *, 
        username: str
    ) -> List[HistorySession]:
        """
        根据用户名获取历史会话列表
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            List[HistorySession]: 该用户的历史会话列表
        """
        result = await db.execute(
            select(HistorySession).where(
                and_(
                    HistorySession.username == username,
                    HistorySession.is_deleted == False
                )
            ).order_by(HistorySession.created_at.desc())
        )
        return result.scalars().all()
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: HistorySession, 
        obj_in: Union[HistorySessionUpdate, Dict[str, Any]]
    ) -> HistorySession:
        """
        更新历史会话
        
        Args:
            db: 数据库会话
            db_obj: 数据库中的对象
            obj_in: 更新数据
            
        Returns:
            HistorySession: 更新后的历史会话对象
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def soft_delete(
        self, 
        db: AsyncSession, 
        *, 
        id: str
    ) -> Optional[HistorySession]:
        """
        软删除历史会话（标记为已删除）
        
        Args:
            db: 数据库会话
            id: 会话ID
            
        Returns:
            Optional[HistorySession]: 删除的历史会话对象或None
        """
        db_obj = await self.get_by_id(db, id=id)
        if not db_obj:
            return None
        
        db_obj.is_deleted = True
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def search_sessions(
        self, 
        db: AsyncSession, 
        *, 
        keyword: Optional[str] = None,
        page: int = 0,
        page_size: int = 20
    ) -> List[HistorySession]:
        """
        搜索历史会话
        
        Args:
            db: 数据库会话
            username: 用户名
            keyword: 搜索关键词（在会话名称中搜索）
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            List[HistorySession]: 搜索结果列表
        """
        query = select(HistorySession).where(
            HistorySession.is_deleted == False
        )
        
        if keyword:
            query = query.where(
                HistorySession.session_name.contains(keyword)
            )
        
        query = query.offset(page * page_size).limit(page_size).order_by(HistorySession.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_by_username(
        self, 
        db: AsyncSession, 
        *, 
        username: str
    ) -> int:
        """
        统计用户的历史会话数量
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            int: 会话数量
        """
        from sqlalchemy import func
        
        result = await db.execute(
            select(func.count(HistorySession.id)).where(
                and_(
                    HistorySession.username == username,
                    HistorySession.is_deleted == False
                )
            )
        )
        return result.scalar() or 0


# 创建CRUD实例
crud_history_session = CRUDHistorySession()