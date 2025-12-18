# OfficeGuard v1.3.2 - 任务计划程序自启动版

## 🎉 主要更新

### ✅ 已解决：开机自启动问题

**问题原因**：程序设置了 `uac_admin=True` 需要管理员权限，但通过注册表启动时无法获得足够权限，导致自启动失败。

**解决方案**：改用Windows任务计划程序，可以设置"最高权限运行"，完美绕过UAC限制。

### 🔧 技术改进

1. **开机自启动机制**
   - ❌ 旧方案：注册表 `HKEY_CURRENT_USER\...\Run`
   - ✅ 新方案：任务计划程序 `OfficeGuard_AutoStart`
   - 优势：可以设置最高权限运行，不受UAC限制

2. **自动清理功能**
   - 用户关闭"开机自启动"时，自动删除任务计划
   - 用户关闭"自动登录"时，完全清理注册表设置

3. **状态检测升级**
   - 自动检测任务计划程序状态
   - 显示任务详细信息和可能的问题

## 📦 使用说明

### 在虚拟机中的步骤

1. **复制新版本到虚拟机**
   - `dist\OfficeGuard.exe` (最新版本)

2. **首次设置**
   - 运行 `OfficeGuard.exe`
   - 切换到"设置"标签
   - 启用"开机自启动"
   - 程序会自动创建任务计划程序

3. **验证设置**
   - 按 `Win + R`，输入 `taskschd.msc`
   - 在任务计划程序库中找到 `OfficeGuard_AutoStart`
   - 确认任务状态为"就绪"

4. **测试自启动**
   - 重启虚拟机
   - 登录后检查系统托盘
   - 应该看到 OfficeGuard 图标

## 🔍 技术细节

### 任务计划程序命令

**创建任务**：
```cmd
schtasks /Create /TN "OfficeGuard_AutoStart" /TR "\"路径\OfficeGuard.exe\" --boot-startup" /SC ONLOGON /RL HIGHEST /F
```

参数说明：
- `/TN` - 任务名称
- `/TR` - 要运行的程序和参数
- `/SC ONLOGON` - 触发条件：用户登录时
- `/RL HIGHEST` - 使用最高权限运行
- `/F` - 强制创建（覆盖已存在的任务）

**删除任务**：
```cmd
schtasks /Delete /TN "OfficeGuard_AutoStart" /F
```

**查询任务**：
```cmd
schtasks /Query /TN "OfficeGuard_AutoStart" /FO LIST /V
```

### 代码改进位置

**文件**：`office_tool_final.py`

**主要修改**：

1. `set_autostart()` 函数（第440-540行）
   - 改用 `subprocess` 调用 `schtasks` 命令
   - 创建时设置 `/RL HIGHEST` 最高权限
   - 删除时完全清理任务

2. `check_autostart_status()` 函数（第512-580行）
   - 查询任务计划程序状态
   - 解析任务详细信息
   - 检测常见问题

3. `set_autologon()` 函数（第653-750行）
   - 增强禁用逻辑
   - 使用Autologon工具删除
   - 手动清理注册表确保完全清除

## 🎯 功能对比

| 功能 | 旧版本（注册表） | 新版本（任务计划） |
|------|-----------------|-------------------|
| **UAC限制** | ❌ 受限制 | ✅ 不受限制 |
| **管理员权限** | ❌ 无法获取 | ✅ 自动获取 |
| **可靠性** | ⚠️ 不稳定 | ✅ 稳定 |
| **自动清理** | ✅ 支持 | ✅ 支持 |
| **状态检测** | ✅ 支持 | ✅ 支持 |
| **用户体验** | ⚠️ 可能失败 | ✅ 一键完成 |

## ⚙️ 配置文件变化

无需修改配置文件，程序会自动：
1. 启用自启动时：创建任务计划
2. 禁用自启动时：删除任务计划
3. 保存配置到：`C:\Users\用户名\AppData\Local\OfficeGuard\config\`

## 📝 日志记录

所有操作都会记录到日志文件：
```
C:\Users\用户名\AppData\Local\OfficeGuard\logs\guard.log
```

关键日志信息：
- `正在创建任务计划: OfficeGuard_AutoStart`
- `任务计划创建成功`
- `检测到开机启动标志（命令行参数: --boot-startup）`

## 🐛 问题排查

### Q1: 任务计划创建失败？
**A**: 检查是否以管理员身份运行程序

### Q2: 任务计划已创建但没有自启动？
**A**: 
1. 打开任务计划程序，检查任务状态
2. 右键任务 → 属性 → 确认"使用最高权限运行"已勾选
3. 查看任务历史记录中的错误信息

### Q3: 如何手动删除任务？
**A**: 
```cmd
schtasks /Delete /TN "OfficeGuard_AutoStart" /F
```

### Q4: 如何验证任务是否存在？
**A**: 
```cmd
schtasks /Query /TN "OfficeGuard_AutoStart"
```

### Q5: 关闭自启动后任务还在？
**A**: 程序会自动删除，如未删除可手动运行上述删除命令

## 🔄 升级路径

### 从旧版本升级

1. **清理旧的注册表项**（可选）
   ```cmd
   reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "OfficeGuard" /f
   reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "系统优化助手" /f
   ```

2. **使用新版本**
   - 直接覆盖旧的 `OfficeGuard.exe`
   - 运行程序，在设置中重新启用自启动
   - 程序会自动创建任务计划

## 🎨 用户界面变化

无明显变化，用户操作保持一致：
1. 打开程序
2. 切换到"设置"标签
3. 切换"开机自启动"开关
4. 程序自动处理一切

## 📊 性能影响

- **启动速度**：无影响
- **内存占用**：无影响
- **CPU占用**：无影响
- **可靠性**：⬆️ 显著提升

## 🔐 安全性

- 任务计划程序是Windows官方机制，安全可靠
- 不需要修改系统文件
- 可以通过Windows设置或任务计划程序管理
- 所有操作都有日志记录

## 📞 技术支持

如遇问题，请提供：
1. 日志文件最后100行
2. 任务计划程序截图
3. 错误信息截图

---

**版本**：v1.3.2  
**发布日期**：2025-12-18  
**核心改进**：使用Windows任务计划程序实现可靠的开机自启动
