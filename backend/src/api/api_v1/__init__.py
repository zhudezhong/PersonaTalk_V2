from fastapi import APIRouter
from . import history_session

api_router = APIRouter()

# 包含历史会话路由
api_router.include_router(
    history_session.router, 
    prefix="/sessions", 
    tags=["历史会话"]
)
