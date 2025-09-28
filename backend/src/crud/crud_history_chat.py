from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_
from pydantic import BaseModel, Field

from src.model.history_chat import HistoryChat, ChatRole
from src.crud.base import CRUDBase


def truncate_utf8_string(s: str, max_bytes: int = 65000) -> str:
    """
    截取字符串以确保在 UTF-8 编码下不超过指定的字节长度
    避免截断多字节字符（如中文）
    
    Args:
        s: 要截取的字符串
        max_bytes: 最大字节长度，默认 65000（略小于 MySQL TEXT 的 65535 限制）
        
    Returns:
        str: 截取后的字符串
    """
    if not s:
        return s
        
    encoded = s.encode('utf-8')
    if len(encoded) <= max_bytes:
        return s
        
    truncated = encoded[:max_bytes]
    while True:
        try:
            return truncated.decode('utf-8')
        except UnicodeDecodeError:
            truncated = truncated[:-1]


class HistoryChatCreate(BaseModel):
    """创建聊天记录的请求模型"""
    session_id: str = Field(description="会话ID")
    role: ChatRole = Field(description="角色")
    content: str = Field(description="对话内容")
class HistoryChatResponse(BaseModel):
    """历史聊天记录响应模型"""
    id: str
    session_id: str
    role: str
    content: str
    created_at: str
    updated_at: str

class HistoryChatUpdate(BaseModel):
    pass


class CRUDHistoryChat(CRUDBase[HistoryChat, HistoryChatCreate, HistoryChatUpdate]):
    """历史聊天记录CRUD操作类"""
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: HistoryChatCreate
    ) -> HistoryChat:
        """
        创建新的历史聊天记录
        
        Args:
            db: 数据库会话
            obj_in: 创建数据
            
        Returns:
            HistoryChat: 创建的历史聊天记录对象
        """
        # 截取内容以确保不超过 MySQL TEXT 类型限制
        original_length = len(obj_in.content.encode('utf-8')) if obj_in.content else 0
        truncated_content = truncate_utf8_string(obj_in.content)
        truncated_length = len(truncated_content.encode('utf-8')) if truncated_content else 0
        
        # 如果内容被截取，记录日志
        if original_length > truncated_length:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"聊天内容被截取: 原始长度 {original_length} 字节 -> 截取后 {truncated_length} 字节")
        
        db_obj = HistoryChat(
            session_id=obj_in.session_id,
            role=obj_in.role,
            content=truncated_content
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_session_id(
        self, 
        db: AsyncSession, 
        *, 
        session_id: str,
        limit: Optional[int] = None
    ) -> List[HistoryChat]:
        """
        根据会话ID获取历史聊天记录
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            limit: 限制返回的记录数
            
        Returns:
            List[HistoryChat]: 历史聊天记录列表
        """
        query = select(HistoryChat).where(
            HistoryChat.session_id == session_id
        ).order_by(HistoryChat.created_at.asc())
        
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_by_session_id(
        self, 
        db: AsyncSession, 
        *, 
        session_id: str
    ) -> int:
        """
        统计会话的聊天记录数量
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            int: 聊天记录数量
        """
        from sqlalchemy import func
        
        result = await db.execute(
            select(func.count(HistoryChat.id)).where(
                HistoryChat.session_id == session_id
            )
        )
        return result.scalar() or 0
    
    async def delete_by_session_id(
        self, 
        db: AsyncSession, 
        *, 
        session_id: str
    ) -> int:
        """
        删除会话的所有聊天记录
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            int: 删除的记录数
        """
        result = await db.execute(
            select(HistoryChat).where(HistoryChat.session_id == session_id)
        )
        chats = result.scalars().all()
        
        for chat in chats:
            await db.delete(chat)
        
        await db.commit()
        return len(chats)


# 创建CRUD实例
crud_history_chat = CRUDHistoryChat(HistoryChat)

async def main():
    from src.api.deps import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        await crud_history_chat.create(session, obj_in=HistoryChatCreate(session_id="1", role=ChatRole.USER, content="H" * 65535))
        chats = await crud_history_chat.get_by_session_id(session, session_id="1")
        print(chats)
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())