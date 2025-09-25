# PersonalTalk 前端项目

## 项目介绍
PersonalTalk 前端项目基于 Vite 构建，使用 Docker 实现开发环境标准化，确保团队成员使用一致的依赖和配置。


## 环境准备
### 必要工具
1. **Docker Desktop**  
   下载地址：[Docker 官网](https://www.docker.com/products/docker-desktop/)  
   安装后启动 Docker 服务（状态栏显示 Docker 图标即启动成功）。

## 快速开始

# 进入前端项目目录


### 2. 拉取 Docker 开发镜像
使用统一的开发镜像，无需本地安装 Node.js 环境：# 拉取镜像（首次拉取可能较慢，耐心等待）
docker pull heyanyisuxiyanqing/personaltalk-frontend:dev

### 3. 启动开发环境
#### 方式 1：使用命令行启动（推荐）# 启动容器（端口映射+代码实时同步）
docker run -it --rm \
-p 5173:5173 \
-v $(pwd):/app \
heyanyisuxiyanqing/personaltalk-frontend:dev- 参数说明：
- `-p 5173:5173`：本地 5173 端口映射到容器内服务端口
- `-v $(pwd):/app`：本地代码目录同步到容器，修改代码实时生效
- `--rm`：容器停止后自动清理，不占用空间


#### 方式 2：使用 Docker Compose（简化操作）
1. 在项目根目录（`web/personaltalk`）创建 `docker-compose.yml`，内容如下：
   ```yaml
   version: '3.8'
   services:
     frontend-dev:
       image: heyanyisuxiyanqing/personaltalk-frontend:dev
       ports:
         - "5173:5173"
       volumes:
         - ./:/app
       stdin_open: true
       tty: true
   ```

2. 启动服务：
   ```bash
   # 启动容器
   docker compose up

   # 停止容器（另开终端执行）
   docker compose down
   ```


### 4. 访问项目
启动成功后，打开浏览器访问：  
[http://localhost:5173](http://localhost:5173)

修改本地代码（如 `src` 目录下的文件），浏览器会自动热更新。


## 开发流程
1. 日常开发：启动容器 → 编写代码 → 浏览器预览 → 提交代码
2. 依赖安装：若需新增依赖，在容器内执行 `npm install 包名`，并提交 `package.json` 和 `package-lock.json`
3. 构建镜像（维护者操作）：代码更新后，更新镜像并推送到仓库
   ```bash
   # 重新构建镜像
   docker build --target development -t frontend-dev:latest .

   # 打标签并推送（替换为你的 Docker Hub 用户名）
   docker tag frontend-dev:latest heyanyisuxiyanqing/personaltalk-frontend:dev
   docker push heyanyisuxiyanqing/personaltalk-frontend:dev
   ```


## 常见问题（FAQ）

### 1. 启动时报「端口被占用」# 更换本地端口（例如使用 5174 端口）
docker run -it --rm -p 5174:5173 -v $(pwd):/app heyanyisuxiyanqing/personaltalk-frontend:dev
# 访问地址改为 http://localhost:5174

### 2. 拉取镜像速度慢/超时
配置 Docker 国内镜像加速器：
1. 打开 Docker Desktop → Settings → Docker Engine
2. 替换配置为：
   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ]
   }
   ```
3. 点击「Apply & Restart」重启 Docker


### 3. 提示「Rollup 模块缺失」或依赖错误
进入容器重新安装依赖：# 进入容器终端
docker run -it --rm -v $(pwd):/app heyanyisuxiyanqing/personaltalk-frontend:dev sh

# 容器内执行
rm -rf node_modules package-lock.json && npm install

# 重新启动
npm run dev

### 4. 代码修改后浏览器不更新
- 检查启动命令是否包含 `-v $(pwd):/app`（确保代码挂载成功）
- 尝试重启容器：按 `Ctrl+C` 停止后重新执行启动命令
