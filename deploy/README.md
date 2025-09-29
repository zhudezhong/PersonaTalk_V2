# PersonaTalk 一键启动指南

## 🚀 快速启动

在 `deploy` 目录下运行：

```bash
./start.sh
```

或者：

```bash
bash start.sh
```

## 📋 启动流程

脚本会自动完成以下操作：

1. **环境检查**
   - 检查 Docker 和 Docker Compose 是否安装
   - 验证必要的配置文件是否存在
   - 确认 Docker 服务是否运行

2. **服务启动**
   - 停止现有容器（如果有）
   - 拉取最新的基础镜像
   - 构建并启动所有服务

3. **健康检查**
   - 等待数据库初始化完成
   - 检查后端服务状态
   - 检查前端服务状态
   - 验证 Nginx 代理是否正常

4. **结果展示**
   - 显示各服务状态
   - 提供访问地址和管理命令
   - 可选择自动打开浏览器

## 🌐 服务访问

启动成功后，可以通过以下地址访问：

- **完整应用**: http://localhost (推荐)
- **备用端口**: http://localhost:8003
- **后端 API**: http://localhost/api
- **数据库**: localhost:6036 (用户: personatalk, 密码: personatalk123)

## 🐳 管理命令

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f mysql

# 重启特定服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 完全清理（包括数据卷）
docker-compose down -v
```

## ⚠️ 故障排除

### 常见问题

1. **端口占用**
   - 确保端口 80、3000、6036、8888 没有被其他程序占用
   - 可以修改 docker-compose.yml 中的端口映射

2. **服务启动失败**
   - 查看具体日志：`docker-compose logs [服务名]`
   - 检查 Docker 内存和磁盘空间是否充足

3. **网页无法访问**
   - 等待 1-2 分钟，服务可能还在初始化
   - 检查防火墙设置
   - 尝试访问备用端口 8003

4. **数据库连接失败**
   - 等待数据库完全启动（约 30-60 秒）
   - 检查数据库容器日志：`docker-compose logs mysql`

### 重新启动

如果遇到问题，可以尝试完全重新启动：

```bash
# 停止并清理
docker-compose down -v
docker system prune -f

# 重新启动
./start.sh
```

## 📞 技术支持

如果遇到问题，请建立issue，我们会及时解决

1. 检查上述故障排除步骤
2. 查看详细日志信息
3. 确认系统环境符合要求

---

💡 **提示**: 首次启动可能需要较长时间（下载镜像、构建服务），请耐心等待。
