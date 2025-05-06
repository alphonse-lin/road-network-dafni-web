@echo off
echo Exporting Docker images...

:: 获取当前时间作为版本号
set VERSION=%date:~0,4%%date:~5,2%%date:~8,2%

:: 创建导出目录
mkdir exports 2>nul

:: 给镜像打标签
docker tag road-network-vulnerability_frontend:latest dafni-frontend:%VERSION%
docker tag road-network-vulnerability_backend:latest dafni-backend:%VERSION%

:: 导出镜像
echo Exporting frontend image...
docker save dafni-frontend:%VERSION% > exports/dafni-frontend-%VERSION%.tar

echo Exporting backend image...
docker save dafni-backend:%VERSION% > exports/dafni-backend-%VERSION%.tar

echo.
echo Images exported successfully!
echo Frontend image: exports/dafni-frontend-%VERSION%.tar
echo Backend image: exports/dafni-backend-%VERSION%.tar
echo.
echo To import these images on another machine, use:
echo docker load ^< exports/dafni-frontend-%VERSION%.tar
echo docker load ^< exports/dafni-backend-%VERSION%.tar 