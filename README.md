# OfficeGuard - 系统优化助手

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

一款功能强大的 Windows 系统优化工具，支持定时任务、系统锁定、开机自启动和自动登录

</div>

## ✨ 主要特性

### ⏱️ 定时任务
- **定时关机/睡眠**: 灵活设置倒计时任务
- **圆形进度条**: 可视化显示倒计时进度
- **缓冲期机制**: 执行前可通过鼠标活动取消

### 🔒 系统锁定
- **内核级锁定**: 安全的键鼠屏蔽
- **密码保护**: 需输入密码解锁
- **全局快捷键**: 可自定义快捷键（默认 Ctrl+Alt+L）
- **系统托盘**: 静默运行于后台

### 🚀 开机自动化
- **开机自启动**: 使用 Windows 任务计划程序
- **自动登录**: 集成 Sysinternals Autologon，LSA 加密存储
- **启动软件管理**: 自定义开机启动的应用程序

### 🎨 现代化界面 (v2.0)
- **全新 UI**: 参考 shadcn/ui 设计语言
- **卡片式布局**: 简洁现代的视觉风格
- **4K 支持**: 自动适配高 DPI 显示
- **滚动支持**: 所有页面支持鼠标滚轮

### 🔐 安全保护
- **配置加密**: 使用 Windows DPAPI 加密
- **用户绑定**: 只有当前用户可解密
- **LSA 加密**: 自动登录密码系统级加密

## 📥 快速开始

### 使用 exe 版本（推荐）

1. 下载 [最新版本](https://github.com/xqy272/OfficeGuard/releases)
2. 右键"以管理员身份运行" exe 文件
3. 程序自动最小化到系统托盘

### 从源码运行

```powershell
# 克隆仓库
git clone https://github.com/xqy272/OfficeGuard.git
cd OfficeGuard

# 创建虚拟环境（推荐）
python -m venv .venv
.\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行（需要管理员权限）
python main.py
```

## 🔨 从源码构建

```powershell
# 自动构建
.\build.bat

# 或手动构建
pyinstaller OfficeGuard.spec
```

产物位置：`dist\系统优化助手.exe`

## 📁 项目结构

```
OfficeGuard/
├── main.py                 # 程序入口
├── src/
│   ├── core/              # 核心功能
│   │   ├── config.py      # 配置管理
│   │   ├── timer.py       # 定时任务
│   │   ├── lock.py        # 系统锁定
│   │   ├── hotkey.py      # 快捷键
│   │   └── tray.py        # 系统托盘
│   ├── ui/                # 用户界面
│   │   ├── app.py         # 主应用
│   │   ├── theme.py       # 主题系统
│   │   ├── components/    # UI 组件
│   │   └── pages/         # 功能页面
│   └── utils/             # 工具模块
├── docs/                  # 文档
└── requirements.txt       # 依赖
```

## 📖 使用说明

### 系统托盘
- 程序启动后自动最小化到托盘
- 右键托盘图标查看菜单
- 双击托盘图标打开主窗口

### 快捷键
- 默认：`Ctrl + Alt + L` 快速锁定
- 可在设置页面自定义组合键

### 定时任务
1. 设置定时时间（分钟）
2. 设置宽限期（秒）
3. 点击"定时关机"或"定时睡眠"
4. 宽限期内移动鼠标可取消任务

## 🛠️ 技术栈

- **Python 3.9+** - 核心语言
- **tkinter** - GUI 框架
- **pystray** - 系统托盘
- **pynput** - 全局快捷键
- **Pillow** - 图像处理
- **Windows API** - 系统集成

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细更新历史。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🙏 致谢

- [shadcn/ui](https://ui.shadcn.com/) - UI 设计灵感
- [Sysinternals Autologon](https://docs.microsoft.com/sysinternals/downloads/autologon) - 自动登录工具
