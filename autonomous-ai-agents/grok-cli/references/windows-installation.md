# Grok CLI Windows 安装指南

本文档记录了在 Windows 系统上安装 Grok CLI 的具体步骤和注意事项，基于实际安装过程中的经验总结。

## 📋 环境信息

- **系统**: Windows 10
- **用户**: win10
- **安装目录**: `C:\Users\win10\bin\grok.exe`
- **版本**: v1.1.7
- **下载工具**: curl (Git Bash)

## 🔧 安装步骤

### 1. 创建 bin 目录

```bash
mkdir -p /c/Users/win10/bin
```

**注意**: 使用 `/c/Users/...` 格式确保路径在 Git Bash 中正确解析。

### 2. 下载 Grok CLI 可执行文件

```bash
cd /c/Users/win10/bin
curl -L https://github.com/superagent-ai/grok-cli/releases/latest/download/grok-windows-x64.exe -o grok.exe
```

**常见问题**:
- `curl` 可能会报错 `系统找不到指定的文件`，这是由于路径格式问题
- 解决方案: 使用绝对路径 `/c/Users/...` 而不是相对路径 `~/bin`

### 3. 添加到 PATH

```bash
# 编辑 ~/.bashrc 文件
echo 'export PATH="/c/Users/win10/bin:$PATH"' >> ~/.bashrc

# 应用更改
source ~/.bashrc
```

**验证**:
```bash
grok --version
# 应该输出: 1.1.7
```

## ⚠️ Windows 特有问题

### 1. 路径格式问题

**问题**: Windows 使用反斜杠 `\)，而 Git Bash 使用正斜杠 `/`

**解决方案**:
```bash
# 错误示例
curl -o C:\Users\win10\bin\grok.exe ...

# 正确示例
curl -o /c/Users/win10/bin/grok.exe ...
```

### 2. 环境变量设置

**问题**: Windows 的环境变量设置方式与 Linux/macOS 不同

**解决方案**:
```bash
# 在 ~/.bashrc 中设置（推荐）
echo 'export GROK_API_KEY="xai-..."' >> ~/.bashrc
source ~/.bashrc

# 或者临时设置（当前会话有效）
export GROK_API_KEY="xai-..."
```

### 3. 权限问题

**问题**: 文件权限设置

**解决方案**:
```bash
# 确保文件可执行
chmod +x /c/Users/win10/bin/grok.exe
```

## 📊 性能测试

### 下载速度
- 文件大小: 124MB
- 下载时间: ~4秒 (正常网络环境)
- 成功率: 100% (使用 `-L` 跟随重定向)

### 验证命令
```bash
# 查看版本
grok --version

# 查看帮助
grok --help

# 查看可用模型
grok models
```

## 🔄 更新 Grok CLI

```bash
# 方法 1: 重新下载
grok update

# 方法 2: 手动下载
cd /c/Users/win10/bin
curl -L https://github.com/superagent-ai/grok-cli/releases/latest/download/grok-windows-x64.exe -o grok.exe
```

## 📚 参考链接

- [Grok CLI GitHub 仓库](https://github.com/superagent-ai/grok-cli)
- [xAI 开发者控制台](https://console.x.ai/)
- [Windows Git Bash 文档](https://www.git-scm.com/doc)

## 🎯 最佳实践

1. **使用绝对路径**: 在 Windows 的 Git Bash 中，始终使用 `/c/Users/...` 格式
2. **设置环境变量**: 将 API 密钥添加到 `~/.bashrc` 确保持久化
3. **验证安装**: 使用 `grok --version` 和 `grok --help` 验证安装成功
4. **测试功能**: 使用 `--max-tool-rounds 5` 限制测试任务，避免不必要的 API 调用

## 📝 问题记录

- **2026-07-13**: 在 Windows 10 上成功安装 Grok CLI v1.1.7
- **问题**: 初始使用 `~/bin` 路径失败，改用绝对路径 `/c/Users/...` 解决
- **问题**: API 密钥额度不足，需要从控制台获取新密钥或购买额度
