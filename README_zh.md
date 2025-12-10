# OfficeGuard - 办公室全能卫士

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

一款功能强大的 Windows 系统管理工具，提供定时任务和系统锁定功能

[简体中文](README_zh.md) | [English](README.md)

</div>

## ✨ 主要特性

### 🕒 定时任务
- **定时关机/睡眠**: 设置倒计时自动执行系统关机或睡眠
- **智能缓冲期**: 执行前提供缓冲时间，移动鼠标即可取消
- **安全机制**: 关闭应用即可取消所有任务，完全可控

### 🛡️ 系统锁定
- **完全锁定**: 内核级键盘鼠标屏蔽，包括 Win键、Alt+Tab 等组合键
- **物理限制**: 限制鼠标活动范围，防止误操作
- **密码保护**: 只能通过输入正确密码解锁
- **防止休眠**: 锁定期间保持屏幕常亮

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
pip install pyinstaller

# 打包为单文件 exe
pyinstaller --onefile --windowed --name="办公室全能卫士" --uac-admin --version-file=version.txt office_tool_final.py
```

产物位置：`dist\办公室全能卫士.exe`

## 📖 使用说明

### 定时任务

1. 切换到"定时任务"标签页
2. 设置倒计时时间（分钟）
3. 设置缓冲时间（秒）
4. 点击"启动关机"或"启动睡眠"
5. 倒计时结束前移动鼠标可取消

### 系统锁定

1. 切换到"隐形卫士"标签页
2. 设置解锁密码（纯数字）
3. 点击"立即锁死系统"
4. 锁定后盲打密码即可解锁

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
- **Python**: 3.7+ (仅源码运行需要)

## 🔧 配置文件

配置文件 `guard_config.json` 包含以下选项：

```json
{
    "password": "000",           // 解锁密码
    "timer_minutes": 60,         // 默认倒计时（分钟）
    "grace_seconds": 30,         // 缓冲时间（秒）
    "mouse_threshold": 15,       // 鼠标移动阈值（像素）
    "win_w": 520,               // 窗口宽度
    "win_h": 480,               // 窗口高度
    "win_x": -1,                // 窗口 X 坐标
    "win_y": -1,                // 窗口 Y 坐标
    "first_run": false          // 首次运行标志
}
```

## ⚠️ 安全提示

1. **定时任务**: 关闭应用即可安全取消所有任务
2. **系统锁定**: 锁定后只能通过密码解锁，请牢记密码
3. **管理员权限**: 本软件需要管理员权限才能正常工作
4. **数据备份**: 所有配置保存在 AppData 目录

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

### v1.0.0 (2025-12-10)

**新增功能**
- ✅ 首次运行引导界面
- ✅ 完整的日志记录系统
- ✅ 数据自动保存到 AppData
- ✅ 支持打包为独立 exe

**优化改进**
- ✅ 优化 exe 打包适配
- ✅ 改进关机任务安全退出机制
- ✅ 优化鼠标困禁逻辑
- ✅ 增强键盘输入识别

**问题修复**
- ✅ 修复多个异常处理问题
- ✅ 修复配置文件保存问题
- ✅ 修复窗口位置记忆问题

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
