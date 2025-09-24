from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from ..config import settings
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 创建异步数据库引擎
engine: AsyncEngine = create_async_engine(
    settings.get_database_url(),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,  # 连接前测试连接是否有效
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_tables():
    """创建数据库表"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话的依赖注入函数
    
    Yields:
        AsyncSession: 异步SQLAlchemy数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"数据库操作错误: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


def get_engine() -> AsyncEngine:
    """
    获取异步数据库引擎
    
    Returns:
        AsyncEngine: 异步SQLAlchemy数据库引擎
    """
    return engine


async def close_db_connections():
    """关闭所有数据库连接"""
    try:
        await engine.dispose()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")


async def check_db_connection() -> bool:
    """
    检查数据库连接是否正常
    
    Returns:
        bool: 连接是否正常
    """
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("数据库连接正常")
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False


# 数据库健康检查
async def health_check() -> dict:
    """
    数据库健康检查
    
    Returns:
        dict: 健康状态信息
    """
    try:
        is_connected = await check_db_connection()
        pool_status = {
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
        }
        
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "connected": is_connected,
            "pool_status": pool_status
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e)
        }