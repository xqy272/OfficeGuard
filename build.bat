@echo off
chcp 65001 >nul
echo ==========================================
echo   办公室全能卫士 - 一键打包工具
echo ==========================================
echo.

:: 检查是否安装 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [错误] 未安装 PyInstaller
    echo.
    echo 正在安装 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [失败] 安装失败，请手动执行: pip install pyinstaller
        pause
        exit /b 1
    )
)

echo [✓] PyInstaller 已就绪
echo.

:: 清理旧文件
echo [1/4] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "办公室全能卫士.spec" del /q "办公室全能卫士.spec"
echo [✓] 清理完成
echo.

:: 开始打包
echo [2/4] 开始打包（这可能需要几分钟）...
echo.

:: 打包命令（单文件模式）
pyinstaller ^
    --onefile ^
    --windowed ^
    --name="办公室全能卫士" ^
    --uac-admin ^
    --version-file=version.txt ^
    --clean ^
    office_tool_final.py

if errorlevel 1 (
    echo.
    echo [失败] 打包过程出错
    pause
    exit /b 1
)

echo.
echo [✓] 打包完成
echo.

:: 检查产物
echo [3/4] 检查打包产物...
if exist "dist\办公室全能卫士.exe" (
    echo [✓] exe 文件已生成
    
    :: 获取文件大小
    for %%A in ("dist\办公室全能卫士.exe") do (
        set size=%%~zA
    )
    
    :: 转换为MB
    set /a size_mb=!size! / 1048576
    echo [i] 文件大小: !size_mb! MB
) else (
    echo [错误] exe 文件未找到
    pause
    exit /b 1
)
echo.

:: 创建发布包
echo [4/4] 创建发布包...
set version=1.0.0
set release_dir=OfficeGuard_v%version%
if exist "%release_dir%" rmdir /s /q "%release_dir%"
mkdir "%release_dir%"

:: 复制exe
copy "dist\办公室全能卫士.exe" "%release_dir%\" >nul

:: 创建使用说明
(
echo 办公室全能卫士 v%version%
echo ===================================
echo.
echo 【安装说明】
echo 1. 双击运行 exe 文件
echo 2. 允许管理员权限（必需）
echo 3. 首次运行会显示引导界面
echo.
echo 【功能说明】
echo • 定时任务：设置定时关机/睡眠
echo • 隐形卫士：完全锁定键盘鼠标
echo.
echo 【数据位置】
echo 日志文件：C:\Users\{用户}\AppData\Local\OfficeGuard\logs\
echo 配置文件：C:\Users\{用户}\AppData\Local\OfficeGuard\config\
echo.
echo 【卸载说明】
echo 直接删除 exe 文件即可
echo 如需清理数据，手动删除上述数据目录
echo.
echo 【技术支持】
echo 遇到问题请查看日志文件
) > "%release_dir%\使用说明.txt"

:: 创建更新日志
(
echo 办公室全能卫士 - 更新日志
echo ===================================
echo.
echo v%version% - %date%
echo ------------------
echo [新增] 首次运行引导界面
echo [新增] 完整的日志记录系统
echo [新增] 数据自动保存到 AppData
echo [优化] exe 打包适配，移除 Python 依赖
echo [优化] 关机任务安全退出机制
echo [修复] 鼠标困禁逻辑缺陷
echo [修复] 键盘输入识别问题
echo [修复] 多个异常处理改进
echo.
) > "%release_dir%\更新日志.txt"

echo [✓] 发布包创建完成: %release_dir%\
echo.

:: 显示结果
echo ==========================================
echo   打包成功！
echo ==========================================
echo.
echo 📦 产物位置:
echo     • EXE 文件: dist\办公室全能卫士.exe
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

:: 询问是否打开文件夹
choice /C YN /M "是否打开产物文件夹"
if errorlevel 2 goto end
if errorlevel 1 explorer dist

:end
pause
