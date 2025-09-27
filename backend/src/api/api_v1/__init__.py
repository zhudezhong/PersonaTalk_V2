from fastapi import APIRouter
from src.api.api_v1 import history_session
from src.api.api_v1 import chat

api_router = APIRouter()

# 包含历史会话路由
api_router.include_router(
    history_session.router, 
    prefix="/sessions", 
    tags=["历史会话"]
)

# 包含聊天路由
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["对话相关接口"]
)