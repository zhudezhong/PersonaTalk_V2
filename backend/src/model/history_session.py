from sqlmodel import SQLModel, Field
from .base import BaseModelMixin


class HistorySession(SQLModel, BaseModelMixin, table=True):
    """
    历史聊天会话数据库表模型
    
    字段说明:
    - id: 会话唯一标识符
    - created_at: 创建时间
    - updated_at: 更新时间
    - username: 用户名
    - session_name: 会话名称
    - is_deleted: 状态（是否删除）
    """
    __tablename__ = "history_session"
    
    username: str = Field(default="", max_length=100, description="用户名")
    session_name: str = Field(default="", max_length=200, description="会话名称")
    is_deleted: bool = Field(default=False, description="状态（是否删除）")