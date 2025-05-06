# Docker 环境调试指南

## 常见问题与解决方案

### 问题：Space Syntax计算失败

#### 症状
- 前端显示"Calculation failed: Space syntax calculation failed"
- 无法执行空间语法计算

#### 解决方案
1. 确保 `.NET运行时环境` 已正确安装在容器中：
   ```bash
   # 进入容器
   docker exec -it road-network-vulnerability_backend_1 bash
   
   # 检查.NET是否已安装
   dotnet --info
   ```

2. 检查TopologyCalculation.exe文件是否存在并有执行权限：
   ```bash
   # 查找并检查执行文件
   find /app -name "TopologyCalculation.exe" -ls
   ```

3. 尝试手动运行计算程序来查看详细错误信息：
   ```bash
   cd /app/prepare/topology_calc_csharp/topology_calc
   ./TopologyCalculation.exe <输入参数>
   ```

### 问题：前端与后端通信失败

#### 症状
- 网络错误：ERR_NAME_NOT_RESOLVED 或 Connection Refused
- API请求失败

#### 解决方案
1. 检查容器之间的网络连接：
   ```bash
   # 从前端容器ping后端
   docker exec road-network-vulnerability_frontend_1 ping backend
   ```

2. 检查环境变量是否正确设置：
   ```bash
   docker exec road-network-vulnerability_frontend_1 env | grep VUE_APP_API_URL
   ```

3. 检查后端服务是否正常运行：
   ```bash
   docker exec road-network-vulnerability_backend_1 ps aux | grep python
   ```

## 获取后端日志

查看后端容器的日志以获取更多调试信息：
```bash
docker logs road-network-vulnerability_backend_1
```

保存日志到文件：
```bash
docker logs road-network-vulnerability_backend_1 > backend.log 2>&1
```

## 与后端容器交互

进入后端容器进行调试：
```bash
docker exec -it road-network-vulnerability_backend_1 bash
```

## 重建所有容器

当你修改了Dockerfile后，需要重新构建所有容器：
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## 故障排除步骤

1. **检查数据文件**：
   - 确保所有必需的输入文件（如GeoJSON）已正确上传到容器
   - 检查文件权限和格式是否正确

2. **追踪计算过程**：
   - 在`csharpCalculation.py`中添加更多的打印语句来追踪执行流程
   - 检查输入参数是否正确传递

3. **检查路径问题**：
   - Docker容器中的路径与本地开发环境可能不同
   - 确保所有路径引用都使用正确的格式

## 已知问题

1. **.NET兼容性**：
   - TopologyCalculation.exe可能与特定版本的.NET运行时不兼容
   - 尝试安装不同版本的.NET运行时（如5.0或7.0）

2. **计算资源限制**：
   - 容器可能受到资源限制导致计算失败
   - 尝试增加Docker容器的内存和CPU限制 