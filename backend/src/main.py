import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.api_v1 import api_router
from src.api.deps import create_tables, close_db_connections, health_check
from src.config import settings
from src.model_server import init_model_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时创建数据库表
    - 关闭时清理数据库连接
    """
    # 启动时执行
    logger.info("应用启动中...")
    try:
        # 检查数据库连接
        from src.api.deps import check_db_connection
        if await check_db_connection():
            logger.info("数据库连接正常")
            # 只在需要时创建表
            await create_tables()
            logger.info("数据库表检查/创建完成")
        else:
            logger.error("数据库连接失败")
            raise Exception("数据库连接失败")
        
        # 初始化模型服务
        init_model_service()
        logger.info("模型服务初始化完成")
        
    except Exception as e:
        logger.error(f"应用初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭中...")
    try:
        await close_db_connections()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")


# 创建FastAPI应用实例
app = FastAPI(
    title="PersonaTalk API",
    description="个人对话系统API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Starlette HTTP异常处理器"""
    logger.error(f"Starlette HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.error(f"请求验证异常: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "请求参数验证失败",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "服务器内部错误",
            "status_code": 500,
            "path": str(request.url)
        }
    )


# 健康检查端点
@app.get("/health")
async def health():
    """健康检查端点"""
    try:
        db_health = await health_check()
        return {
            "status": "healthy",
            "database": db_health,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "version": "1.0.0"
            }
        )


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "PersonaTalk API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# 包含API路由
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8888,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )