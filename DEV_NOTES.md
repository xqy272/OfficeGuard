# 开发者说明

## 🏗️ 项目结构

```
OfficeGuard/
├── office_tool_final.py       # 主程序代码
├── version.txt                 # 版本信息
├── build.bat                   # 打包脚本
├── install_deps.bat            # 依赖安装脚本
├── requirements.txt            # Python依赖
│
├── README_zh.md                # 中文说明
├── README.md                   # 英文说明
├── CHANGELOG.md                # 更新日志
├── QUICK_START.md              # 快速指南
├── DEPENDENCIES.md             # 依赖说明
├── RELEASE_NOTES_v1.1.0.md     # 发布说明
├── UPDATE_SUMMARY_v1.1.0.md    # 更新总结
└── DEV_NOTES.md                # 本文件
```

## 🛠️ 技术栈

### 核心技术
- **Python 3.9+**
- **tkinter** - GUI界面
- **pystray** - 系统托盘
- **Pillow (PIL)** - 图像处理
- **ctypes** - Windows API调用

### Windows API
- **SetWindowsHookEx** - 全局键盘鼠标钩子
- **ClipCursor** - 鼠标范围限制
- **SetThreadExecutionState** - 防止系统休眠
- **GetAsyncKeyState** - 按键状态检测

## 📋 关键功能实现

### 1. 系统托盘
```python
# 使用 pystray 实现
import pystray
from PIL import Image, ImageDraw

# 创建图标
icon_image = Image.new('RGB', (64, 64), (255, 255, 255))
dc = ImageDraw.Draw(icon_image)
dc.ellipse((8, 8, 56, 56), fill=(41, 128, 185))

# 创建菜单
menu = pystray.Menu(
    pystray.MenuItem("进入", callback),
    pystray.MenuItem("快捷键", callback),
    pystray.MenuItem("关闭", callback)
)

# 运行托盘
tray_icon = pystray.Icon("name", icon_image, "title", menu)
tray_icon.run()
```

### 2. 全局快捷键
```python
# 使用 Windows Hook 实现
def hotkey_callback(nCode, wParam, lParam):
    if nCode == 0 and wParam == WM_KEYDOWN:
        kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        if kb.vkCode == VK_L:  # L键
            ctrl = user32.GetAsyncKeyState(0x11) & 0x8000
            alt = user32.GetAsyncKeyState(0x12) & 0x8000
            if ctrl and alt:
                trigger_action()
                return 1
    return user32.CallNextHookEx(hook, nCode, wParam, lParam)

# 安装钩子
proc_ref = HOOKPROC(hotkey_callback)
hook = user32.SetWindowsHookExA(WH_KEYBOARD_LL, proc_ref, 0, 0)
```

### 3. 键鼠屏蔽
```python
# 键盘钩子 - 只接受数字输入
def kb_callback(nCode, wParam, lParam):
    if nCode == 0 and wParam == WM_KEYDOWN:
        vk = ctypes.cast(lParam, KBDLLHOOKSTRUCT).vkCode
        if 48 <= vk <= 57 or 96 <= vk <= 105:
            # 数字键，处理输入
            return 0
        return 1  # 屏蔽其他按键
    return user32.CallNextHookEx(hook, nCode, wParam, lParam)

# 鼠标钩子 - 完全屏蔽
def ms_callback(nCode, wParam, lParam):
    if nCode >= 0:
        return 1  # 屏蔽所有鼠标事件
    return user32.CallNextHookEx(hook, nCode, wParam, lParam)
```

### 4. 鼠标困禁
```python
# 限制鼠标在1x1像素区域
def trap_mouse():
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    cx, cy = sw // 2, sh // 2
    
    rect = RECT(cx, cy, cx + 1, cy + 1)
    user32.ClipCursor(ctypes.byref(rect))
```

## 🔧 配置系统

### ConfigManager
```python
class ConfigManager:
    defaults = {
        "password": "000",
        "win_w": 520,
        "win_h": 400,
        "win_x": -1,
        "win_y": -1,
        "first_run": True,
        "hotkey_enabled": True
    }
```

配置文件路径：
```
C:\Users\{用户}\AppData\Local\OfficeGuard\config\guard_config.json
```

## 📝 日志系统

### 日志配置
```python
# 位置
C:\Users\{用户}\AppData\Local\OfficeGuard\logs\guard.log

# 轮转策略
- 单文件最大: 5MB
- 保留备份: 3个
- 总大小: 20MB
```

### 日志级别
- `INFO` - 正常操作
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `DEBUG` - 调试信息（开发环境）

## 🎨 UI设计

### 窗口尺寸
```python
默认大小: 520 x 400
最小大小: 400 x 300
```

### 配色方案
```python
主色调: #2980b9 (蓝色)
成功色: #27ae60 (绿色)
背景色: #f0f0f0 (浅灰)
```

## 🔐 安全机制

### 1. 管理员权限
```python
# UAC提权
ctypes.windll.shell32.ShellExecuteW(
    None, "runas", sys.executable, " ".join(sys.argv), None, 1
)
```

### 2. 进程优先级
```python
# 实时优先级
pid = ctypes.windll.kernel32.GetCurrentProcess()
ctypes.windll.kernel32.SetPriorityClass(pid, 0x00000100)
```

### 3. 密码验证
```python
# 滚动验证
input_buffer += char
input_buffer = input_buffer[-len(password):]
if input_buffer == password:
    unlock()
```

## 📦 打包配置

### PyInstaller 参数
```bash
--onefile          # 单文件
--windowed         # 无控制台
--uac-admin        # 管理员权限
--version-file     # 版本信息
--clean            # 清理缓存
```

### 依赖处理
PyInstaller 自动包含：
- tkinter (Python内置)
- pystray
- Pillow
- ctypes (Python内置)

### 产物大小
```
未压缩: ~18MB
UPX压缩后: ~10MB
```

## 🧪 测试清单

### 功能测试
- [ ] 托盘图标显示
- [ ] 托盘菜单功能
- [ ] 快捷键触发
- [ ] 快捷键开关
- [ ] 密码输入识别
- [ ] 键鼠屏蔽效果
- [ ] 鼠标困禁
- [ ] 窗口隐藏/显示
- [ ] 配置保存/加载
- [ ] 日志记录

### 兼容性测试
- [ ] Windows 10
- [ ] Windows 11
- [ ] 1080p 显示器
- [ ] 4K 显示器
- [ ] 多显示器

### 异常测试
- [ ] 非管理员运行
- [ ] 配置文件损坏
- [ ] 密码错误输入
- [ ] 快捷键冲突
- [ ] 托盘图标异常

## 🐛 已知限制

### 1. 系统级快捷键
- 某些全屏游戏中可能无效
- 受系统安全策略限制
- 可能与其他软件冲突

### 2. 鼠标困禁
- 无法限制触摸板手势
- 多显示器可能有问题
- 某些游戏鼠标可以绕过

### 3. 键盘钩子
- 只支持标准键盘布局
- 部分特殊键盘可能不支持
- 输入法状态可能影响

## 🔮 未来计划

### v1.2.0
- [ ] 自定义快捷键
- [ ] 多密码支持
- [ ] 定时自动优化
- [ ] 开机自启动

### v1.3.0
- [ ] 远程控制
- [ ] 日志查看器
- [ ] 主题定制
- [ ] 插件系统

### v2.0.0
- [ ] 跨平台支持
- [ ] Web管理界面
- [ ] 数据统计
- [ ] 云同步配置

## 📚 开发资源

### 文档链接
- [pystray文档](https://pystray.readthedocs.io/)
- [Pillow文档](https://pillow.readthedocs.io/)
- [Python ctypes](https://docs.python.org/3/library/ctypes.html)
- [Windows API](https://docs.microsoft.com/en-us/windows/win32/api/)

### 参考项目
- [python-windows-tiler](https://github.com/ipaleka/python-windows-tiler)
- [keyboard](https://github.com/boppreh/keyboard)
- [pynput](https://github.com/moses-palmer/pynput)

## 🤝 贡献指南

### 代码规范
```python
# 使用4空格缩进
# 函数名使用snake_case
# 类名使用PascalCase
# 常量使用UPPER_CASE
```

### 提交规范
```
feat: 新增功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

### 分支策略
```
main - 稳定版本
develop - 开发版本
feature/* - 新功能
hotfix/* - 紧急修复
```

## 📧 联系方式

- **Issues**: [GitHub Issues](https://github.com/xqy272/OfficeGuard/issues)
- **Email**: 技术支持邮箱
- **文档**: 查看项目 README

---

**祝开发顺利！** 🚀
