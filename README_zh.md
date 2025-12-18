# 系统优化助手 (System Optimizer)

<div align="center">

![Version](https://img.shields.io/badge/version-1.3.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

一款功能强大的 Windows 系统优化工具，支持定时任务、系统优化、开机自启动和自动登录

[简体中文](README_zh.md) | [English](README.md)

</div>

## ✨ 主要特性

### ⏱️ 定时任务
- **定时关机/睡眠**: 灵活设置倒计时任务
- **缓冲期机制**: 执行前可通过鼠标活动取消
- **进度可视化**: 实时显示倒计时和进度条

### ⚡ 系统优化
- **深度优化**: 优化系统性能，清理内存碎片
- **全局快捷键**: 可自定义快捷键（默认Ctrl+Alt+L）
- **系统托盘**: 静默运行于后台，随时可用
- **密码保护**: 优化完成后需输入密码恢复

### 🚀 开机自动化 (v1.3.2优化)
- **开机自启动**: 使用Windows任务计划程序，不受UAC限制
- **自动获取权限**: 任务计划自动以最高权限运行
- **一键清理**: 关闭自启动时自动删除任务
- **自动登录**: 集成Sysinternals Autologon，LSA加密存储
- **启动软件管理**: 自定义开机启动的应用程序列表
- **智能判断**: 区分开机和睡眠唤醒

### 🔒 安全保护
- **配置加密**: 使用Windows DPAPI加密配置文件
- **用户绑定**: 只有当前用户可解密配置
- **LSA加密**: 自动登录密码使用系统级加密
- **安全存储**: 所有敏感信息加密保护

## 📥 快速开始

### 使用 exe 版本（推荐）

1. 下载 [最新版本](https://github.com/xqy272/OfficeGuard/releases)
2. 右键"以管理员身份运行" exe 文件
3. 按照首次运行引导操作

### 从源码运行

```powershell
# 克隆仓库
git clone https://github.com/xqy272/OfficeGuard.git
cd OfficeGuard

# 安装依赖
pip install -r requirements.txt

# 直接运行（需要管理员权限）
python office_tool_final.py
```

## 🔨 从源码构建

### 自动构建（推荐）

```powershell
# 双击运行或在命令行执行
.\build.bat
```

构建脚本会自动：
- ✅ 检查并安装 PyInstaller
- ✅ 清理旧文件
- ✅ 打包为独立 exe
- ✅ 创建发布包

### 手动构建

```powershell
# 安装依赖
pip install -r requirements.txt

# 打包为单文件 exe
pyinstaller --onefile --windowed --name="系统优化助手" --uac-admin --version-file=version.txt office_tool_final.py
```

产物位置：`dist\系统优化助手.exe`

## 📖 使用说明

### 首次使用

1. 以管理员身份运行程序
2. 程序自动隐藏到系统托盘（右下角）
3. 右键托盘图标查看菜单

### 快速优化

**方式一：使用快捷键**
- 按下 `Ctrl+Alt+L` 立即启动优化
- 无需打开界面，快速方便

**方式二：使用界面**
1. 右键托盘图标 → 选择"进入"
2. 设置恢复密码（纯数字）
3. 点击"立即优化系统"

### 恢复系统

- 优化期间盲打设置的密码
- 系统自动恢复正常
- 不会弹出任何提示

### 快捷键管理

- 右键托盘图标
- 点击"快捷键：✓ 开启/✗ 关闭"
- 切换快捷键启用状态

## 📂 数据存储

所有数据存储在用户目录，不会在程序目录生成文件：

```
C:\Users\{用户}\AppData\Local\OfficeGuard\
├── logs\               # 日志文件
│   ├── guard.log      # 当前日志（最大 5MB）
│   ├── guard.log.1    # 备份 1
│   ├── guard.log.2    # 备份 2
│   └── guard.log.3    # 备份 3
└── config\
    └── guard_config.json  # 配置文件
```

## ⚙️ 系统要求

- **操作系统**: Windows 10/11
- **权限**: 管理员权限（必需）
- **运行环境**: .NET Framework 4.0+
- **Python**: 3.9+ (仅源码运行需要)
- **依赖**: pystray, Pillow (自动打包)

## 🔧 配置文件

配置文件 `guard_config.json` 包含以下选项：

```json
{
    "password": "000",           // 恢复密码
    "mouse_threshold": 15,       // 鼠标移动阈值（像素）
    "win_w": 520,               // 窗口宽度
    "win_h": 400,               // 窗口高度
    "win_x": -1,                // 窗口 X 坐标
    "win_y": -1,                // 窗口 Y 坐标
    "first_run": false,         // 首次运行标志
    "hotkey_enabled": true      // 快捷键开关
}
```

## ⚠️ 安全提示

1. **记住密码**: 优化后只能通过密码恢复，请牢记密码
2. **管理员权限**: 本软件需要管理员权限才能正常工作
3. **快捷键**: Ctrl+Alt+L 可能与其他软件冲突，可通过托盘关闭
4. **数据备份**: 所有配置保存在 AppData 目录
5. **退出方式**: 必须通过托盘菜单退出，关闭窗口仅隐藏

## 🐛 问题排查

### exe 无法启动

```powershell
# 查看日志文件
notepad %LOCALAPPDATA%\OfficeGuard\logs\guard.log
```

### 功能异常

```powershell
# 重置配置
rmdir /s /q "%LOCALAPPDATA%\OfficeGuard\config"
```

### 权限不足

右键 exe 文件，选择"以管理员身份运行"

## 🗑️ 卸载

1. 删除 exe 文件
2. （可选）清理数据目录：
   ```powershell
   rmdir /s /q "%LOCALAPPDATA%\OfficeGuard"
   ```

## 📝 更新日志

### v1.1.0 (2025-12-18)

**新增功能**
- ✅ 系统托盘功能，默认隐藏运行
- ✅ 全局快捷键 Ctrl+Alt+L
- ✅ 托盘菜单：进入、快捷键开关、关闭
- ✅ 快捷键启用/禁用开关

**优化改进**
- ✅ 精简UI界面，移除非必要内容
- ✅ 迷惑性名称和描述
- ✅ 优化完成后静默恢复
- ✅ 窗口关闭改为隐藏到托盘

**问题修复**
- ✅ 修复窗口管理逻辑
- ✅ 优化托盘图标显示

### v1.0.1 (2025-12-10)

**新增功能**
- ✅ UI 自动重置功能
- ✅ 密码显示/隐藏切换

**优化改进**
- ✅ 改善用户体验
- ✅ 提高密码安全性

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 💖 致谢

感谢所有贡献者和用户的支持！

## 📧 联系方式

- **GitHub**: [xqy272](https://github.com/xqy272)
- **Issues**: [提交问题](https://github.com/xqy272/OfficeGuard/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star！**

</div>
