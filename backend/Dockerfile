# 使用官方 Python 3.11 slim 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN pip install poetry==1.6.1

# 配置 Poetry：不创建虚拟环境（因为已经在容器中）
RUN poetry config virtualenvs.create false

# 复制 Poetry 配置文件
COPY pyproject.toml poetry.lock* ./

# 创建 src 目录结构（Poetry 需要）
RUN mkdir -p src

# 复制应用代码
COPY . .

# 安装 Python 依赖（包含开发依赖以便测试）
RUN poetry install --no-interaction --no-ansi

# 创建 logs 目录
RUN mkdir -p /app/logs

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口 8888
EXPOSE 8888

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8888/api/v1/chat/health || exit 1

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8888", "--reload"]
