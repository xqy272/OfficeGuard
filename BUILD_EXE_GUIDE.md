# 构建指南

## 📦 快速构建

### 自动构建（推荐）

```powershell
.\build.bat
```

构建脚本会自动完成所有步骤。

### 手动构建

```powershell
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 构建
pyinstaller --onefile --windowed --name="办公室全能卫士" --uac-admin --version-file=version.txt office_tool_final.py

# 3. 输出位置
# dist\办公室全能卫士.exe
```

## 🔧 构建参数说明

| 参数 | 说明 |
|------|------|
| `--onefile` | 打包为单文件 exe |
| `--windowed` | 无控制台窗口 |
| `--name` | 设置 exe 文件名 |
| `--uac-admin` | 要求管理员权限 |
| `--version-file` | 添加版本信息 |

## ✅ 测试清单

构建完成后测试：

- [ ] exe 正常启动
- [ ] 显示首次运行引导
- [ ] 定时任务功能正常
- [ ] 系统锁定功能正常
- [ ] 日志文件生成正确
- [ ] 配置保存正常

## 📂 构建产物

```
dist\
└── 办公室全能卫士.exe    # 独立可执行文件

OfficeGuard_v1.0.0\       # 发布包（build.bat 生成）
├── 办公室全能卫士.exe
├── 使用说明.txt
└── 更新日志.txt
```

## 🐛 常见问题

### 缺少 PyInstaller

```powershell
pip install pyinstaller
```

### exe 体积过大

正常情况下约 15-20MB，包含了完整的 Python 运行时和 tkinter。

### 杀毒软件误报

PyInstaller 打包的 exe 可能被误报，可以：
- 添加到杀毒软件白名单
- 提交到杀毒软件厂商

## 📊 优化建议

1. 使用虚拟环境减少不必要的依赖
2. 考虑使用 UPX 压缩
3. 添加数字签名（需购买证书）

详见 [官方文档](https://pyinstaller.readthedocs.io/)

