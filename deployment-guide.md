# DAFNI 平台部署指南

## 部署环境

本指南提供了如何在不同环境中部署 DAFNI 平台的说明。

### 本地开发环境

在本地开发环境中运行：

```bash
# 设置API URL为本地后端
export VUE_APP_API_URL=http://localhost:5000

# 启动Docker容器
docker-compose up --build
```

### 云服务器部署

在云服务器上部署时，需要确保容器间可以通过Docker网络通信：

```bash
# 使用默认配置（容器间通过服务名通信）
docker-compose up --build
```

如果需要通过自定义URL访问后端：

```bash
# 设置自定义API URL
export VUE_APP_API_URL=http://your-custom-backend-url:5000

# 启动Docker容器
docker-compose up --build
```

### 调整Docker Compose配置

如果在云服务器上部署，请删除`docker-compose.yml`中的`extra_hosts`部分：

```yaml
# 删除这部分
extra_hosts:
  - "backend:host-gateway"
```

## 镜像导出和导入

导出Docker镜像以便在其他环境部署：

```bash
# 导出前端镜像
docker save dafni-frontend > dafni-frontend.tar

# 导出后端镜像
docker save dafni-backend > dafni-backend.tar
```

在其他环境导入镜像：

```bash
# 导入镜像
docker load < dafni-frontend.tar
docker load < dafni-backend.tar

# 在目标服务器运行
docker-compose up
```

## 注意事项

1. 确保后端服务器对外暴露了5000端口
2. 如果前后端部署在不同服务器，需要设置正确的`VUE_APP_API_URL`环境变量
3. 如果使用反向代理，确保正确转发API请求 