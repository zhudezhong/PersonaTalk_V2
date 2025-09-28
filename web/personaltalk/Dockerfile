# 简单的 Node.js 构建方案
FROM node:20-alpine AS builder
WORKDIR /app

# 复制 package 文件并安装依赖
COPY package*.json ./
RUN npm install

# 复制源代码并构建
COPY . .
RUN npm run build

# 生产环境 - 使用静态文件服务
FROM node:20-alpine AS production
WORKDIR /app

# 安装 serve
RUN npm install -g serve

# 复制构建产物
COPY --from=builder /app/dist ./dist

# 暴露端口
EXPOSE 3000

# 启动服务
CMD ["serve", "-s", "dist", "-p", "3000"]

# 开发环境
FROM node:20-alpine AS development
WORKDIR /app

# 复制 package 文件并安装依赖
COPY package*.json ./
RUN npm install

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]