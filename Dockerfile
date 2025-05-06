FROM node:20-slim

WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建应用 - 确保环境变量在构建时可用
ARG VUE_APP_API_URL=http://backend:5000
ENV VUE_APP_API_URL=${VUE_APP_API_URL}

# 构建
RUN npm run build

# 安装serve来运行构建后的应用
RUN npm install -g serve

# 创建启动脚本
RUN echo '#!/bin/sh\n\
sed -i "s|VUE_APP_API_URL=.*|VUE_APP_API_URL=${VUE_APP_API_URL}|g" /app/dist/js/*.js\n\
exec serve -s dist -l 8080' > /app/start.sh && chmod +x /app/start.sh

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["/app/start.sh"] 