# 贡献指南

感谢你考虑为 OfficeGuard 做出贡献！

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 检查 [Issues](https://github.com/xqy272/OfficeGuard/issues) 中是否已有相同问题
2. 如果没有，创建新的 Issue
3. 清楚地描述问题或建议
4. 如果是 bug，请包含：
   - 操作系统版本
   - Python 版本（如果从源码运行）
   - 重现步骤
   - 错误日志（位于 `%LOCALAPPDATA%\OfficeGuard\logs\guard.log`）

### 提交代码

1. **Fork 仓库**
   ```bash
   # 在 GitHub 上点击 Fork 按钮
   ```

2. **克隆你的 Fork**
   ```bash
   git clone https://github.com/你的用户名/OfficeGuard.git
   cd OfficeGuard
   ```

3. **创建特性分支**
   ```bash
   git checkout -b feature/你的功能名称
   # 或
   git checkout -b fix/你修复的问题
   ```

4. **进行更改**
   - 遵循现有代码风格
   - 添加必要的注释
   - 测试你的更改

5. **提交更改**
   ```bash
   git add .
   git commit -m "描述你的更改"
   ```

6. **推送到你的 Fork**
   ```bash
   git push origin feature/你的功能名称
   ```

7. **创建 Pull Request**
   - 在 GitHub 上打开 Pull Request
   - 详细描述你的更改
   - 链接相关的 Issue

## 代码规范

### Python 代码风格

- 遵循 PEP 8 规范
- 使用有意义的变量名
- 添加文档字符串（docstring）
- 保持函数简洁（建议不超过 50 行）

### 提交信息规范

使用清晰的提交信息：

- `feat: 添加新功能`
- `fix: 修复 bug`
- `docs: 更新文档`
- `style: 代码格式调整`
- `refactor: 重构代码`
- `test: 添加测试`
- `chore: 构建/工具链变更`

示例：
```
feat: 添加多语言支持

- 添加英文界面
- 添加语言切换功能
- 更新配置文件结构
```

## 开发环境设置

### 要求

- Windows 10/11
- Python 3.7+
- 管理员权限

### 安装依赖

```powershell
# 克隆仓库
git clone https://github.com/xqy272/OfficeGuard.git
cd OfficeGuard

# 直接运行（无需安装额外依赖，仅使用标准库）
python office_tool_final.py
```

### 测试

在提交前请测试以下功能：

- [ ] 定时关机功能
- [ ] 定时睡眠功能
- [ ] 缓冲期取消
- [ ] 系统锁定
- [ ] 密码解锁
- [ ] 配置保存
- [ ] 窗口位置记忆
- [ ] 日志记录

### 构建 exe

```powershell
.\build.bat
```

## 优先级

我们特别欢迎以下类型的贡献：

1. **Bug 修复** - 最高优先级
2. **性能优化** - 高优先级
3. **文档改进** - 中优先级
4. **新功能** - 中优先级（请先讨论）
5. **代码重构** - 低优先级

## 功能建议

在开发新功能前，请先：

1. 创建 Issue 讨论
2. 等待维护者反馈
3. 达成共识后再开始开发

这样可以避免不必要的工作。

## 问题讨论

- 使用 GitHub Issues 讨论
- 使用中文或英文
- 保持友好和专业

## 许可证

提交代码即表示你同意：

- 你的贡献将使用 MIT 许可证
- 你拥有你提交代码的版权或已获得授权

## 行为准则

- 尊重所有贡献者
- 接受建设性批评
- 关注对项目最有利的事情
- 对社区其他成员保持同理心

## 需要帮助？

如果你有任何问题：

- 查看 [README](README.md)
- 查看 [Issues](https://github.com/xqy272/OfficeGuard/issues)
- 创建新的 Issue 提问

再次感谢你的贡献！🎉
