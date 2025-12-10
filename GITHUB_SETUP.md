# GitHub 仓库设置建议

## 仓库描述 (Description)

```
🛡️ 功能强大的 Windows 系统管理工具 - 定时任务与系统锁定 | Powerful Windows system management tool with scheduled tasks and system lock
```

## 网站 (Website)

```
https://github.com/xqy272/OfficeGuard
```

## 主题标签 (Topics)

建议添加以下标签以提高项目可见性：

```
python
windows
system-utilities
task-scheduler
security-tools
desktop-application
pyinstaller
tkinter
windows-automation
system-lock
shutdown-timer
office-tools
gui-application
windows-10
windows-11
```

## 仓库设置

### Features
- ✅ Issues (启用问题追踪)
- ✅ Projects (启用项目管理)
- ✅ Wiki (可选，用于详细文档)
- ✅ Discussions (可选，用于社区讨论)

### Pull Requests
- ✅ Allow squash merging (允许压缩合并)
- ✅ Allow auto-merge (允许自动合并)
- ✅ Automatically delete head branches (自动删除已合并分支)

### Branch Protection (main 分支保护)

建议的保护规则：
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ⬜ Require branches to be up to date before merging

## Release 发布

### 创建首个 Release

1. 访问 https://github.com/xqy272/OfficeGuard/releases
2. 点击 "Create a new release"
3. 标签: `v1.0.0`
4. 标题: `v1.0.0 - 初始发布版本`
5. 描述使用以下模板:

```markdown
## 🎉 OfficeGuard v1.0.0 初始发布

### ✨ 主要功能

- **定时任务**: 设置定时关机/睡眠，带智能缓冲期
- **系统锁定**: 内核级键盘鼠标屏蔽，密码保护
- **数据管理**: 自动保存配置到 AppData，日志轮转
- **用户体验**: 首次运行引导，窗口位置记忆

### 📦 下载

- **Windows exe (推荐)**: `办公室全能卫士.exe` - 双击运行，无需 Python
- **源代码**: 适合开发者和自定义需求

### 📋 系统要求

- Windows 10/11
- 管理员权限
- .NET Framework 4.0+

### 🚀 快速开始

1. 下载 `办公室全能卫士.exe`
2. 右键"以管理员身份运行"
3. 按照首次运行引导操作

### 📝 完整功能

详见 [README](https://github.com/xqy272/OfficeGuard/blob/main/README_zh.md)

### 🐛 问题反馈

遇到问题请提交 [Issue](https://github.com/xqy272/OfficeGuard/issues)

---

**完整更新日志**: [CHANGELOG.md](https://github.com/xqy272/OfficeGuard/blob/main/CHANGELOG.md)
```

### 上传文件

需要构建 exe 后上传：
1. 运行 `build.bat` 构建 exe
2. 上传 `dist\办公室全能卫士.exe`
3. (可选) 压缩 `OfficeGuard_v1.0.0\` 文件夹并上传

## README 徽章

在 README.md 顶部已包含：

```markdown
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
```

可选添加（需要配置 GitHub Actions）：
```markdown
![Build Status](https://github.com/xqy272/OfficeGuard/workflows/Build/badge.svg)
![Downloads](https://img.shields.io/github/downloads/xqy272/OfficeGuard/total.svg)
![Stars](https://img.shields.io/github/stars/xqy272/OfficeGuard.svg)
```

## Social Preview (社交预览图)

建议创建一张 1280x640 的预览图，包含：
- 项目 Logo
- 项目名称: OfficeGuard
- 标语: 办公室全能卫士
- 主要功能图标

上传位置：仓库 Settings → Options → Social Preview

## 后续维护

### Issue 模板

可创建 `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug 报告
about: 报告一个问题帮助我们改进
title: '[BUG] '
labels: bug
---

**问题描述**
清楚简洁地描述问题

**重现步骤**
1. 进入 '...'
2. 点击 '...'
3. 滚动到 '...'
4. 看到错误

**期望行为**
描述你期望发生什么

**截图**
如果适用，添加截图帮助解释问题

**环境信息:**
 - OS: [如 Windows 10]
 - 版本: [如 v1.0.0]
 - Python 版本（如从源码运行）: [如 3.9]

**日志文件**
请附上 `%LOCALAPPDATA%\OfficeGuard\logs\guard.log` 的相关内容

**其他信息**
添加任何其他相关信息
```

### Pull Request 模板

创建 `.github/pull_request_template.md`:

```markdown
## 更改描述

简要描述此 PR 的更改内容

## 更改类型

- [ ] Bug 修复
- [ ] 新功能
- [ ] 代码重构
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他（请说明）

## 测试

- [ ] 已在本地测试
- [ ] 已添加单元测试
- [ ] 所有测试通过

## 检查清单

- [ ] 代码遵循项目风格指南
- [ ] 已更新相关文档
- [ ] 已更新 CHANGELOG.md
- [ ] 提交信息清晰明确

## 相关 Issue

关闭 #(issue编号)
```

## GitHub Actions (可选)

创建自动化构建流程（高级功能，可后续添加）
