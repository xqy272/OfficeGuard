@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: 检测 Python 解释器
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    echo [信息] 使用虚拟环境: .venv
) else (
    set "PYTHON_EXE=python"
    echo [信息] 使用系统 Python
)

echo ==========================================
echo   办公室全能卫士 - 一键打包工具
echo ==========================================
echo.

"%PYTHON_EXE%" -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [错误] 未安装 PyInstaller
    echo.
    echo 正在安装 PyInstaller...
    "%PYTHON_EXE%" -m pip install pyinstaller
    if errorlevel 1 (
        echo [失败] 安装失败，请手动执行: pip install pyinstaller
        pause
        exit /b 1
    )
)

echo [✓] PyInstaller 已就绪
echo.

echo [1/5] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "办公室全能卫士.spec" del /q "办公室全能卫士.spec"
echo [✓] 清理完成
echo.

echo [2/5] 更新版本信息...
:: 获取日期
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set BUILD_DATE=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

:: 获取版本号
set VERSION=2.0.0
for /f "tokens=4 delims='" %%a in ('findstr "ProductVersion" version.txt') do set VERSION=%%a
:: 去除末尾的 .0
if "%VERSION:~-2%"==".0" set VERSION=%VERSION:~0,-2%

echo 检测到版本: %VERSION%
echo 构建日期: %BUILD_DATE%

if not exist src\core mkdir src\core
(
echo """
echo 版本信息
echo 此文件由构建脚本自动更新
echo """
echo.
echo VERSION = "%VERSION%"
echo BUILD_DATE = "%BUILD_DATE%"
) > src\core\version.py
echo [✓] 版本信息已更新
echo.

echo [3/5] 开始打包（这可能需要几分钟）...
echo.

"%PYTHON_EXE%" -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name="系统优化助手" ^
    --uac-admin ^
    --version-file=version.txt ^
    --hidden-import=pynput ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse._win32 ^
    --clean ^
    main.py

if errorlevel 1 (
    echo.
    echo [失败] 打包过程出错
    pause
    exit /b 1
)

echo.
echo [✓] 打包完成
echo.

echo [4/5] 检查打包产物...
if exist "dist\系统优化助手.exe" (
    echo [✓] exe 文件已生成
    dir "dist\系统优化助手.exe" | findstr "系统优化助手.exe"
) else (
    echo [错误] exe 文件未找到
    pause
    exit /b 1
)
echo.

echo [5/5] 创建发布包...
set version=%VERSION%
set release_dir=OfficeGuard_v%version%
if exist "%release_dir%" rmdir /s /q "%release_dir%"
mkdir "%release_dir%"

copy "dist\系统优化助手.exe" "%release_dir%\" >nul

(
echo 系统优化助手 v%version%
echo ===================================
echo.
echo 【安装说明】
echo 1. 双击运行 exe 文件
echo 2. 允许管理员权限（必需）
echo 3. 首次运行会显示引导界面
echo 4. 程序将隐藏到系统托盘
echo.
echo 【功能说明】
echo • 定时任务：设置定时关机/睡眠
echo • 系统优化：优化系统性能
echo • 全局快捷键：完全自定义
echo • 开机自启动：系统启动时自动运行
echo • 自动登录：安全的开机自动登录（LSA加密）
echo • 启动软件管理：自定义开机启动软件列表
echo • 托盘菜单：右键图标可进入设置
echo.
echo 【数据位置】
echo 日志文件：C:\Users\{用户}\AppData\Local\OfficeGuard\logs\
echo 配置文件：C:\Users\{用户}\AppData\Local\OfficeGuard\config\ (已加密)
echo 工具目录：C:\Users\{用户}\AppData\Local\OfficeGuard\tools\
echo.
echo 【卸载说明】
echo 直接删除 exe 文件即可
echo 如需清理数据，手动删除上述数据目录
echo.
echo 【技术支持】
echo 遇到问题请查看日志文件
) > "%release_dir%\使用说明.txt"

(
echo 系统优化助手 - 更新日志
echo ===================================
echo.
echo v%version% - %date%
echo ------------------
echo [新增] 开机自启动：系统启动时自动运行程序
echo [新增] 自动登录：集成Sysinternals Autologon，LSA加密
echo [新增] 启动软件管理：自定义开机启动的应用程序列表
echo [新增] 配置加密：使用Windows DPAPI加密配置文件
echo [优化] 安全性大幅提升：LSA加密 + AES-256
echo [优化] 智能判断：区分系统开机和睡眠唤醒
echo.
echo 详细更新内容请查看 RELEASE_NOTES_v%version%.md
echo.
) > "%release_dir%\更新日志.txt"

echo [✓] 发布包创建完成: %release_dir%\
echo.

echo ==========================================
echo   打包成功！
echo ==========================================
echo.
echo 📦 产物位置:
echo     • EXE 文件: dist\系统优化助手.exe
echo     • 发布包: %release_dir%\
echo.
echo 📋 下一步:
echo     1. 测试 exe 文件是否正常运行
echo     2. 检查管理员权限提示
echo     3. 验证数据目录创建
echo     4. 发布 %release_dir% 文件夹
echo.
echo ==========================================
echo.

:: 自动打开输出目录
explorer dist
exit /b 0
