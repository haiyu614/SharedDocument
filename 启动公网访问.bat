@echo off
chcp 65001 >nul
echo ========================================
echo   共享文档系统 - 公网访问模式
echo ========================================
echo.
echo 请选择内网穿透工具：
echo.
echo [1] cpolar（推荐 - 国内快速）
echo [2] ngrok（国际版）
echo [3] 仅启动应用（不穿透）
echo [0] 退出
echo.
set /p choice=请输入选项 (1/2/3/0): 

if "%choice%"=="1" goto cpolar
if "%choice%"=="2" goto ngrok
if "%choice%"=="3" goto app_only
if "%choice%"=="0" goto end
goto end

:cpolar
echo.
echo ========================================
echo 启动 cpolar 模式
echo ========================================
echo.
echo [提示] 如果还没安装 cpolar：
echo 1. 访问 https://www.cpolar.com/download 下载安装
echo 2. 注册账号获取 authtoken
echo 3. 运行: cpolar authtoken 你的token
echo.
echo 正在启动应用...
start "Flask App" cmd /k "python app.py"
timeout /t 3 /nobreak >nul
echo.
echo 正在启动 cpolar...
echo 访问 http://localhost:9200 查看公网地址
echo.
cpolar http 5000
goto end

:ngrok
echo.
echo ========================================
echo 启动 ngrok 模式
echo ========================================
echo.
echo [提示] 如果还没安装 ngrok：
echo 1. 访问 https://ngrok.com/download 下载
echo 2. 注册账号获取 authtoken
echo 3. 运行: ngrok config add-authtoken 你的token
echo.
echo 正在启动应用...
start "Flask App" cmd /k "python app.py"
timeout /t 3 /nobreak >nul
echo.
echo 正在启动 ngrok...
echo.
ngrok http 5000
goto end

:app_only
echo.
echo ========================================
echo 仅启动应用（局域网模式）
echo ========================================
echo.
echo 局域网访问地址：
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
    setlocal enabledelayedexpansion
    echo    http://!ip::=!:5000
    endlocal
)
echo.
python app.py
goto end

:end
echo.
pause
