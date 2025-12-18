# 依赖安装指南

## 📦 v1.1.0 新增依赖

本版本新增了以下依赖库：

### 1. pystray
**用途**：系统托盘图标支持

**安装**：
```bash
pip install pystray
```

### 2. Pillow (PIL)
**用途**：托盘图标图像生成

**安装**：
```bash
pip install pillow
```

## 🚀 快速安装

### 方式一：一键安装（推荐）

```bash
pip install pystray pillow
```

### 方式二：使用 requirements.txt

1. 创建 `requirements.txt` 文件：
```txt
pystray>=0.19.0
Pillow>=10.0.0
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## ✅ 验证安装

运行以下代码验证依赖是否正确安装：

```python
# 验证 pystray
try:
    import pystray
    print("✓ pystray 安装成功")
except ImportError:
    print("✗ pystray 未安装")

# 验证 Pillow
try:
    from PIL import Image, ImageDraw
    print("✓ Pillow 安装成功")
except ImportError:
    print("✗ Pillow 未安装")
```

## 🔧 打包说明

打包为 exe 时，PyInstaller 会自动包含这些依赖。

如果打包失败，可以尝试：

```bash
pip install --upgrade pyinstaller
```

## ⚠️ 常见问题

### Q: pip install 失败
**A**: 尝试使用国内镜像源：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pystray pillow
```

### Q: Pillow 安装报错
**A**: 可能需要先安装 C++ 构建工具（Windows）：
- 下载 [Visual C++ Build Tools](https://visualstudio.microsoft.com/downloads/)
- 或使用预编译的 wheel 文件

### Q: pystray 托盘图标不显示
**A**: 确保：
1. 运行在主线程或正确的线程中
2. 图标图像格式正确（RGB模式）
3. 系统托盘未被禁用

## 📝 依赖版本

推荐版本：
- `pystray >= 0.19.0`
- `Pillow >= 10.0.0`

测试通过的版本组合：
- Python 3.11 + pystray 0.19.5 + Pillow 10.2.0 ✅
- Python 3.10 + pystray 0.19.4 + Pillow 10.0.1 ✅
- Python 3.9 + pystray 0.19.0 + Pillow 9.5.0 ✅

## 📚 相关文档

- [pystray 官方文档](https://pystray.readthedocs.io/)
- [Pillow 官方文档](https://pillow.readthedocs.io/)
