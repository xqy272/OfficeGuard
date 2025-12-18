@echo off
chcp 65001 >nul
echo ==========================================
echo   安装依赖包
echo ==========================================
echo.

echo 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    echo.
    echo 请确保：
    echo   1. 已安装 Python 3.9+
    echo   2. Python 已添加到系统 PATH
    echo.
    echo 下载 Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo [✓] Python 环境正常
echo.

echo 正在安装 pystray...
python -m pip install pystray
if errorlevel 1 (
    echo [失败] pystray 安装失败
    echo.
    echo 尝试使用国内镜像源...
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pystray
    if errorlevel 1 (
        echo [失败] 安装仍然失败
        pause
        exit /b 1
    )
)
echo [✓] pystray 安装成功
echo.

echo 正在安装 Pillow...
python -m pip install Pillow
if errorlevel 1 (
    echo [失败] Pillow 安装失败
    echo.
    echo 尝试使用国内镜像源...
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Pillow
    if errorlevel 1 (
        echo [失败] 安装仍然失败
        pause
        exit /b 1
    )
)
echo [✓] Pillow 安装成功
echo.

echo ==========================================
echo   依赖安装完成！
echo ==========================================
echo.
echo 已安装的包：
echo   • pystray  - 系统托盘支持
echo   • Pillow   - 图像处理
echo.
echo 现在可以运行程序或打包了
echo.
pause
