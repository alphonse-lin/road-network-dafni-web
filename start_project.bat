@echo off
echo Starting DAFNI Platform...

:: 启动前端服务
start cmd /k "npm run serve"

:: 等待2秒确保前端服务启动
timeout /t 2 /nobreak

:: 进入backend目录并启动后端服务
cd backend
call conda activate dafni_project
start cmd /k "python app.py"

echo Services are starting...
echo Frontend: http://localhost:8080
echo Backend: http://localhost:5000 