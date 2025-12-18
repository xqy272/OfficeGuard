# 贡献指南

感谢你考虑为 OfficeGuard 做出贡献！

## 🏗️ 项目结构

```
OfficeGuard/
├── main.py                     # 程序入口
├── src/
│   ├── __init__.py
│   ├── core/                   # 核心功能模块
│   │   ├── config.py           # 配置管理（DPAPI 加密）
│   │   ├── timer.py            # 定时任务
│   │   ├── lock.py             # 系统锁定
│   │   ├── hotkey.py           # 全局快捷键
│   │   ├── tray.py             # 系统托盘
│   │   ├── autostart.py        # 开机自启动
│   │   └── autologon.py        # 自动登录
│   ├── ui/                     # 用户界面
│   │   ├── app.py              # 主应用窗口
│   │   ├── theme.py            # 主题和样式
│   │   ├── components/         # UI 组件
│   │   │   ├── base.py         # 基础组件
│   │   │   ├── card.py         # 卡片组件
│   │   │   ├── progress.py     # 进度条
│   │   │   ├── switch.py       # 开关组件
│   │   │   ├── sidebar.py      # 侧边栏
│   │   │   └── scrollable.py   # 滚动容器
│   │   └── pages/              # 功能页面
│   │       ├── timer_page.py   # 定时任务
│   │       ├── lock_page.py    # 系统锁定
│   │       ├── settings_page.py# 设置
│   │       └── about_page.py   # 关于
│   └── utils/                  # 工具模块
│       └── logger.py           # 日志管理
├── docs/                       # 文档
│   └── archive/                # 归档文档
├── requirements.txt            # Python 依赖
├── version.txt                 # 版本信息
├── build.bat                   # 构建脚本
└── OfficeGuard.spec            # PyInstaller 配置
```

## 🛠️ 技术栈

### 核心技术
- **Python 3.9+** (支持 3.14)
- **tkinter** - GUI 界面
- **pystray** - 系统托盘
- **pynput** - 全局快捷键
- **Pillow** - 图像处理
- **ctypes** - Windows API

### Windows API
- **SetWindowsHookEx** - 全局键盘鼠标钩子
- **ClipCursor** - 鼠标范围限制
- **CryptProtectData** - DPAPI 加密
- **Task Scheduler** - 任务计划程序

## 📦 依赖安装

```powershell
# 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 依赖列表
```
pystray>=0.19.0      # 系统托盘
Pillow>=10.0.0       # 图像处理
pynput>=1.7.0        # 全局快捷键
pyinstaller>=6.0.0   # 打包工具（开发）
```

## 🔨 构建指南

### 自动构建（推荐）

```powershell
.\build.bat
```

### 手动构建

```powershell
# 使用 spec 文件
pyinstaller OfficeGuard.spec

# 或直接构建
pyinstaller --onefile --windowed --name="系统优化助手" --uac-admin --version-file=version.txt main.py
```

### 构建产物
```
dist\
└── 系统优化助手.exe    # 独立可执行文件
```

## 📋 如何贡献

### 报告问题

1. 检查 [Issues](https://github.com/xqy272/OfficeGuard/issues) 中是否已有相同问题
2. 创建新的 Issue，包含：
   - 操作系统版本
   - Python 版本
   - 重现步骤
   - 错误日志（位于 `%LOCALAPPDATA%\OfficeGuard\logs\`）

### 提交代码

1. **Fork 仓库**

2. **克隆你的 Fork**
   ```bash
   git clone https://github.com/你的用户名/OfficeGuard.git
   cd OfficeGuard
   ```

3. **创建特性分支**
   ```bash
   git checkout -b feature/你的功能名称
   ```

4. **进行更改并提交**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

5. **推送并创建 Pull Request**

## 📝 代码规范

### Python 风格
- 遵循 PEP 8
- 使用有意义的变量名
- 添加类型注解
- 添加文档字符串

### 提交信息规范
- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `chore:` 构建/工具

### UI 组件规范
- 继承 `tk.Frame` 作为容器
- 使用 `Theme` 对象获取颜色和字体
- 支持自定义样式参数
- 提供 `get()`/`set()` 方法

## ✅ 测试清单

提交前请测试：

- [ ] 定时关机/睡眠功能
- [ ] 系统锁定/解锁
- [ ] 快捷键监听
- [ ] 系统托盘
- [ ] 配置保存/加载
- [ ] 开机自启动
- [ ] 界面各页面切换
- [ ] 4K/高 DPI 显示

## 📄 许可证

提交代码即表示你同意使用 MIT 许可证。

感谢你的贡献！🎉
