# OfficeGuard 开机自启动自动修复脚本
# 此脚本会：
# 1. 检测当前配置问题
# 2. 提供自动修复方案
# 3. 可选：将程序复制到推荐位置

param(
    [switch]$AutoFix,
    [string]$TargetPath = "C:\OfficeGuard"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "OfficeGuard 开机自启动自动修复工具" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  警告：未以管理员身份运行" -ForegroundColor Yellow
    Write-Host "   某些功能可能受限（如复制到Program Files）" -ForegroundColor Yellow
    Write-Host ""
}

# 读取注册表
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$appName = "OfficeGuard"

try {
    $regValue = Get-ItemProperty -Path $regPath -Name $appName -ErrorAction Stop
    $startupCmd = $regValue.$appName
    
    Write-Host "✅ 找到注册表启动项" -ForegroundColor Green
    Write-Host "   值: $startupCmd" -ForegroundColor Gray
    Write-Host ""
    
    # 解析路径
    if ($startupCmd -match '"([^"]+)"') {
        $exePath = $matches[1]
        
        # 检查文件是否存在
        if (Test-Path $exePath) {
            Write-Host "✅ EXE文件存在" -ForegroundColor Green
            Write-Host "   路径: $exePath" -ForegroundColor Gray
        } else {
            Write-Host "❌ EXE文件不存在！" -ForegroundColor Red
            Write-Host "   路径: $exePath" -ForegroundColor Red
            Write-Host ""
            Write-Host "请确认程序是否已被移动或删除。" -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host ""
        Write-Host "诊断结果：" -ForegroundColor Yellow
        Write-Host "------------------------------" -ForegroundColor Yellow
        
        $hasProblems = $false
        
        # 检查OneDrive
        if ($exePath -like "*OneDrive*") {
            Write-Host "⚠️  路径包含OneDrive" -ForegroundColor Yellow
            Write-Host "   开机时OneDrive可能未完全启动，导致路径不可用" -ForegroundColor Gray
            $hasProblems = $true
        }
        
        # 检查中文路径
        if ($exePath -match '[\u4e00-\u9fa5]') {
            Write-Host "⚠️  路径包含中文字符" -ForegroundColor Yellow
            Write-Host "   可能在某些系统环境下导致兼容性问题" -ForegroundColor Gray
            $hasProblems = $true
        }
        
        # 检查--boot-startup参数
        if ($startupCmd -notlike "*--boot-startup*") {
            Write-Host "❌ 缺少 --boot-startup 参数" -ForegroundColor Red
            Write-Host "   程序无法正确识别开机启动状态" -ForegroundColor Gray
            $hasProblems = $true
        } else {
            Write-Host "✅ 包含 --boot-startup 参数" -ForegroundColor Green
        }
        
        Write-Host ""
        
        if (-not $hasProblems) {
            Write-Host "🎉 开机自启动配置正常！" -ForegroundColor Green
            exit 0
        }
        
        # 提供修复方案
        Write-Host "修复建议：" -ForegroundColor Cyan
        Write-Host "------------------------------" -ForegroundColor Cyan
        Write-Host "1. 将程序移动到非OneDrive、非中文路径"
        Write-Host "   推荐路径: $TargetPath"
        Write-Host "2. 在新位置重新设置开机自启动"
        Write-Host ""
        
        if ($AutoFix) {
            Write-Host "🔧 自动修复模式" -ForegroundColor Cyan
            Write-Host ""
            
            # 创建目标目录
            if (-not (Test-Path $TargetPath)) {
                Write-Host "创建目录: $TargetPath" -ForegroundColor Yellow
                try {
                    New-Item -Path $TargetPath -ItemType Directory -Force | Out-Null
                    Write-Host "✅ 目录创建成功" -ForegroundColor Green
                } catch {
                    Write-Host "❌ 无法创建目录: $_" -ForegroundColor Red
                    Write-Host "   请以管理员身份运行此脚本" -ForegroundColor Yellow
                    exit 1
                }
            }
            
            # 复制文件
            $targetExe = Join-Path $TargetPath "OfficeGuard.exe"
            Write-Host "复制文件到: $targetExe" -ForegroundColor Yellow
            
            try {
                Copy-Item -Path $exePath -Destination $targetExe -Force
                Write-Host "✅ 文件复制成功" -ForegroundColor Green
                
                # 更新注册表
                Write-Host "更新注册表..." -ForegroundColor Yellow
                $newStartupCmd = "`"$targetExe`" --boot-startup"
                Set-ItemProperty -Path $regPath -Name $appName -Value $newStartupCmd
                
                # 验证
                $verifyValue = (Get-ItemProperty -Path $regPath -Name $appName).$appName
                if ($verifyValue -eq $newStartupCmd) {
                    Write-Host "✅ 注册表更新成功" -ForegroundColor Green
                    Write-Host ""
                    Write-Host "🎉 修复完成！" -ForegroundColor Green
                    Write-Host ""
                    Write-Host "新的启动命令: $newStartupCmd" -ForegroundColor Gray
                    Write-Host ""
                    Write-Host "建议：" -ForegroundColor Yellow
                    Write-Host "1. 启动新位置的程序: $targetExe"
                    Write-Host "2. 重启电脑验证开机自启动"
                } else {
                    Write-Host "❌ 注册表验证失败" -ForegroundColor Red
                }
            } catch {
                Write-Host "❌ 复制失败: $_" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "运行自动修复：" -ForegroundColor Cyan
            Write-Host "  .\fix_autostart.ps1 -AutoFix" -ForegroundColor White
            Write-Host ""
            Write-Host "或手动修复：" -ForegroundColor Cyan
            Write-Host "  1. 在非OneDrive位置创建目录（如 C:\OfficeGuard）"
            Write-Host "  2. 复制程序文件到新位置"
            Write-Host "  3. 运行新位置的程序"
            Write-Host "  4. 在程序中重新设置开机自启动"
        }
        
    } else {
        Write-Host "❌ 无法解析注册表值" -ForegroundColor Red
        Write-Host "   值: $startupCmd" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ 未找到开机启动项" -ForegroundColor Red
    Write-Host ""
    Write-Host "请在程序中开启开机自启动功能：" -ForegroundColor Yellow
    Write-Host "1. 启动 OfficeGuard"
    Write-Host "2. 打开"开机管理"页面"
    Write-Host "3. 勾选"开机自启动""
    Write-Host "4. 点击"保存设置""
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
