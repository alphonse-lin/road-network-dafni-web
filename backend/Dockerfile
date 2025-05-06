FROM python:3.10.16-slim

WORKDIR /app

# 安装系统依赖和.NET运行时
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# 安装.NET运行时
RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-runtime-6.0 \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 确保.exe文件有执行权限
RUN find /app -name "*.exe" -exec chmod +x {} \;

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"] 