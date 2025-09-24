# Dockerfile

# 第一步：设置基础环境
FROM node:22-alpine AS base
WORKDIR /app

# 先复制 package.json 和 package-lock.json
COPY package*.json ./


# 阶段一：生产环境构建
FROM base AS production
RUN npm ci --only=production && npm cache clean --force


# 阶段二：开发环境构建
FROM base AS development
RUN npm ci  # 安装所有依赖
# 或者 RUN npm install（仅当你想允许更新 lock 文件时）

# 然后继续复制源码、启动命令等...
COPY . .
CMD ["npm", "run", "dev"]