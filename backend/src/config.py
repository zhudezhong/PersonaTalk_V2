from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库相关连接信息
    DATABASE_URL: str = ""
    
    # MySQL连接信息
    MYSQL_HOST: str = ""
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = ""
    
    # 异步数据库连接池配置
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False  # 是否打印SQL语句

    # 大模型相关配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = ""
    
    # 模型服务配置
    MODEL_SERVICE_TYPE: str = "qiniu"  # 默认使用七牛云
    MODEL_SERVICE_NAME: str = "default"  # 默认服务名称
    MODEL_TIMEOUT: int = 30  # 请求超时时间（秒）
    MODEL_MAX_RETRIES: int = 3  # 最大重试次数
    MODEL_RETRY_DELAY: int = 1  # 重试延迟（秒）
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # 如果没有设置DATABASE_URL，则使用MySQL配置
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    def get_model_config(self) -> dict:
        """获取模型服务配置"""
        return {
            "name": self.OPENAI_MODEL,
            "service_type": self.MODEL_SERVICE_TYPE,
            "service_name": self.MODEL_SERVICE_NAME,
            "api_key": self.OPENAI_API_KEY,
            "base_url": self.OPENAI_BASE_URL,
            "model": self.OPENAI_MODEL,
            "timeout": self.MODEL_TIMEOUT,
            "max_retries": self.MODEL_MAX_RETRIES,
            "retry_delay": self.MODEL_RETRY_DELAY
        }

settings: Settings = Settings(_env_file=".env")
