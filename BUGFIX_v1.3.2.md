# Bug修复说明 - v1.3.2 Hotfix

## 🐛 修复的Bug

**问题描述**：当用户只启用"开机自启动"而不勾选"自动登录"时，保存设置会报错。

**错误信息**：
```
Usage: autologon <username> <domain> <password>
```

## 🔍 问题原因

在 `save_autostart_settings()` 函数中，当用户未勾选"自动登录"时，代码仍然会调用 `set_autologon(False)`，而该函数在执行时会：

1. 尝试下载Autologon工具（即使用户从未启用过自动登录）
2. 执行Autologon命令，但没有提供必需的参数
3. 导致Autologon工具报错

## ✅ 修复方案

### 修改1：优化保存逻辑

**位置**：`office_tool_final.py` 第2000-2020行

**修改前**：
```python
else:
    # 禁用自动登录
    set_autologon(False)
    self.cfg.set("autologon_enabled", False)
    messagebox.showinfo("成功", "开机设置已保存！\n自动登录已禁用。")
```

**修改后**：
```python
else:
    # 禁用自动登录
    # 只有之前启用过才需要禁用
    if self.cfg.get("autologon_enabled"):
        result = set_autologon(False)
        if result:
            self.cfg.set("autologon_enabled", False)
            messagebox.showinfo("成功", "开机设置已保存！\n自动登录已禁用。")
        else:
            logger.warning("禁用自动登录失败，但继续保存其他设置")
            self.cfg.set("autologon_enabled", False)
            messagebox.showinfo("成功", "开机设置已保存！")
    else:
        # 从未启用过，无需禁用
        self.cfg.set("autologon_enabled", False)
        messagebox.showinfo("成功", "开机设置已保存！")
```

**改进点**：
- 检查用户之前是否启用过自动登录
- 如果从未启用，直接保存配置，不调用Autologon工具
- 即使禁用失败，也继续保存其他设置

### 修改2：优化Autologon工具调用

**位置**：`office_tool_final.py` 第653-730行

**修改前**：
```python
def set_autologon(enable, username="", password="", domain="."):
    try:
        import subprocess
        
        # 获取或下载Autologon工具（无论启用还是禁用都会执行）
        autologon_path = download_autologon()
        
        if not autologon_path:
            logger.error("无法获取Autologon工具")
            return False
        
        if enable:
            # ... 启用逻辑
```

**修改后**：
```python
def set_autologon(enable, username="", password="", domain="."):
    try:
        import subprocess
        
        if enable:
            # 启用自动登录时才下载Autologon工具
            autologon_path = download_autologon()
            
            if not autologon_path:
                logger.error("无法获取Autologon工具")
                return False
            # ... 启用逻辑
```

**改进点**：
- 只在启用自动登录时才下载Autologon工具
- 禁用时先检查工具是否存在，如果不存在则直接清理注册表
- 避免不必要的网络请求和工具下载

### 修改3：安全的禁用逻辑

**修改前**：
```python
else:
    # 禁用自动登录
    logger.info("正在禁用自动登录")
    
    # 直接调用Autologon工具（可能不存在）
    cmd = [autologon_path, '/delete', '/accepteula']
    result = subprocess.run(cmd, ...)
```

**修改后**：
```python
else:
    # 禁用自动登录
    logger.info("正在禁用自动登录")
    
    # 方法1: 尝试使用Autologon工具禁用（如果已下载）
    app_dir = get_app_data_dir()
    tools_dir = app_dir / 'tools'
    autologon_exe = tools_dir / 'Autologon.exe'
    
    if autologon_exe.exists():
        logger.info("使用Autologon工具禁用")
        try:
            cmd = [str(autologon_exe), '/delete', '/accepteula']
            result = subprocess.run(cmd, ...)
            logger.info("已使用Autologon工具禁用自动登录")
        except Exception as e:
            logger.warning(f"Autologon工具禁用失败: {e}")
    else:
        logger.info("Autologon工具未安装，直接清理注册表")
    
    # 方法2: 手动清理注册表（确保完全清除）
    # ... 注册表清理逻辑
```

**改进点**：
- 检查Autologon工具是否存在
- 如果不存在，直接跳过，使用注册表方式清理
- 两种清理方式互为补充，确保完全清除

## 📊 测试场景

### 场景1：从未启用过自动登录（Bug场景）

**操作**：
1. 首次运行程序
2. 只勾选"开机自启动"
3. 不勾选"自动登录"
4. 点击保存

**修复前**：❌ 报错 `Usage: autologon <username> <domain> <password>`

**修复后**：✅ 成功保存，提示"开机设置已保存！"

### 场景2：曾启用过自动登录，现在禁用

**操作**：
1. 之前启用过"自动登录"
2. 现在取消勾选"自动登录"
3. 点击保存

**修复前**：✅ 正常工作（但会尝试下载工具）

**修复后**：✅ 正常工作（使用已有工具或注册表清理）

### 场景3：只修改开机自启动，不碰自动登录

**操作**：
1. 修改"开机自启动"设置
2. "自动登录"保持原状（不管是否启用）
3. 点击保存

**修复前**：⚠️ 可能触发Bug

**修复后**：✅ 完全正常

## 📦 修复后的文件

**文件位置**：`dist_v1.3.2_fix\OfficeGuard.exe`

**文件大小**：19.4 MB

**修复版本**：v1.3.2 Hotfix

## 🚀 使用说明

### 升级步骤

1. 关闭旧版本程序
2. 用新版本覆盖旧文件
3. 重新运行程序
4. 测试开机自启动和自动登录功能

### 验证修复

1. 运行程序
2. 切换到"设置"标签
3. 只勾选"开机自启动"
4. 不勾选"自动登录"
5. 点击"保存开机设置"
6. 应该看到"开机设置已保存！"提示
7. 不应该出现任何错误

## 📝 日志记录

修复后的日志示例：

**场景1：从未启用过自动登录**
```
2025-12-18 23:30:00 - INFO - 正在创建任务计划: OfficeGuard_AutoStart
2025-12-18 23:30:01 - INFO - 任务计划创建成功: OfficeGuard_AutoStart
2025-12-18 23:30:01 - INFO - 开机设置已保存: 自启动=True, 自动登录=False
```
（注意：没有任何Autologon相关的错误）

**场景2：禁用自动登录**
```
2025-12-18 23:30:00 - INFO - 正在禁用自动登录
2025-12-18 23:30:00 - INFO - Autologon工具未安装，直接清理注册表
2025-12-18 23:30:00 - INFO - 自动登录已禁用
2025-12-18 23:30:00 - INFO - 开机设置已保存: 自启动=True, 自动登录=False
```

## 🔄 版本历史

- **v1.3.2** (2025-12-18 23:20)
  - 使用任务计划程序实现开机自启动
  - 完善自动登录功能
  
- **v1.3.2 Hotfix** (2025-12-18 23:32)
  - 🐛 修复：只启用开机自启动时的Autologon报错
  - ✨ 改进：只在需要时下载Autologon工具
  - ✨ 改进：优化禁用自动登录的逻辑

## 💡 技术要点

1. **条件调用**：根据实际需求决定是否调用工具
2. **错误容忍**：即使某个步骤失败，也继续保存其他设置
3. **资源节约**：只在必要时下载和使用Autologon工具
4. **用户体验**：避免不必要的错误提示

## 📞 如有问题

如果仍然遇到问题，请提供：
1. 日志文件 `guard.log`
2. 错误截图
3. 操作步骤

---

**修复版本**：v1.3.2 Hotfix  
**发布时间**：2025-12-18 23:32  
**核心修复**：只启用开机自启动时不再触发Autologon错误
