@echo off
chcp 65001 >nul
echo ========================================
echo   共享文档系统 - ngrok 一键启动
echo ========================================
echo.

echo [1] 检查并停止旧进程...
taskkill /F /IM ngrok.exe 2>nul
timeout /t 1 /nobreak >nul

echo [2] 启动 Flask 应用...
start "Flask App" cmd /k "python app.py"
timeout /t 3 /nobreak >nul

echo [3] 启动 ngrok...
start "ngrok" cmd /k "ngrok.exe http 127.0.0.1:5000"
timeout /t 3 /nobreak >nul

echo [4] 打开 ngrok 管理界面...
start http://127.0.0.1:4040

echo.
echo ========================================
echo ✓ 启动完成！
echo.
echo 在 ngrok 管理界面查看公网地址
echo 地址: http://127.0.0.1:4040
echo ========================================
echo.
pause
