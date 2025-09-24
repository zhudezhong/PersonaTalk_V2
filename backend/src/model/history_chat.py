from enum import Enum
from sqlmodel import SQLModel, Field
from .base import BaseModelMixin


class ChatRole(str, Enum):
    """聊天角色枚举"""
    USER = "user"  # 用户
    ASSISTANT = "assistant"  # 大模型/助手


class HistoryChat(SQLModel, BaseModelMixin, table=True):
    """
    历史聊天记录数据库表模型
    
    字段说明:
    - id: 聊天记录唯一标识符
    - session_id: 会话ID，关联到HistorySession
    - role: 角色（用户或大模型）
    - content: 对话内容
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __tablename__ = "history_chat"
    
    session_id: str = Field(description="会话ID，关联到HistorySession")
    role: ChatRole = Field(description="角色（用户或大模型）")
    content: str = Field(default="", description="对话内容")
