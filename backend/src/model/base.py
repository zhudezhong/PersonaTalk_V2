import uuid
from datetime import datetime
from sqlmodel import Field
from zoneinfo import ZoneInfo


def get_current_time():
    """获取当前时间（东八区）"""
    return datetime.now(ZoneInfo("UTC"))


class IDMixin:
    """ID字段Mixin"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="唯一标识符"
    )


class DateTimeMixin:
    """时间字段Mixin"""
    created_at: datetime = Field(
        default_factory=get_current_time,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_current_time,
        description="更新时间"
    )


class BaseModelMixin(IDMixin, DateTimeMixin):
    """基础模型Mixin，包含ID和时间字段"""
    pass
