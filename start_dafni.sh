#!/bin/bash

# 设置环境变量
export FLASK_ENV=production

# 处理输入文件
if [ -f /data/inputs/files/roadnetwork.geojson ]; then
    echo "Copying road network data..."
    mkdir -p /app/data/input
    cp /data/inputs/files/roadnetwork.geojson /app/data/input/
fi

if [ -f /data/inputs/files/flooding_output.zip ]; then
    echo "Copying flood maps data..."
    mkdir -p /app/data/input
    cp /data/inputs/files/flooding_output.zip /app/data/input/
fi

if [ -f /data/inputs/files/building.geojson ]; then
    echo "Copying buildings data..."
    mkdir -p /app/data/input
    cp /data/inputs/files/building.geojson /app/data/input/
fi

# 获取输入参数
export RADIUS="$(cat /data/inputs/parameters/RADIUS)"
export FLOOD_THRESHOLD="$(cat /data/inputs/parameters/FLOOD_THRESHOLD)"
export AGENT_COUNT="$(cat /data/inputs/parameters/AGENT_COUNT)"
export SIMULATION_PERIODS="$(cat /data/inputs/parameters/SIMULATION_PERIODS)"

echo "Starting backend service..."
# 在后台启动Flask服务
cd /app/backend
python app.py &
BACKEND_PID=$!

# 等待后端启动
echo "Waiting for backend to start..."
sleep 5

echo "Starting frontend service..."
# 启动前端服务
cd /app/frontend
npx serve -s dist -l 80 &
FRONTEND_PID=$!

# 等待计算完成
wait $BACKEND_PID

# 复制输出文件到DAFNI输出目录
echo "Copying output files to DAFNI output directory..."
mkdir -p /data/outputs/datasets
cp /app/data/output/002_topology_calculation/*.geojson /data/outputs/datasets/topology_calculation.geojson
cp /app/data/output/004_merged_data/vulnerability_network.geojson /data/outputs/datasets/vulnerability_network.geojson
cp /app/data/output/004_merged_data/traffic_flow_450s.csv /data/outputs/datasets/traffic_flow.csv
cp /app/data/output/004_merged_data/road_vulnerability_index.csv /data/outputs/datasets/road_vulnerability_index.csv

echo "Processing complete."

# 保持容器运行，以便访问前端界面
# 如果DAFNI不需要持久化前端，可以删除这一行
wait $FRONTEND_PID 