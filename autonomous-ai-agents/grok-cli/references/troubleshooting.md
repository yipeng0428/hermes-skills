# Grok CLI 安装故障排除与网络问题

本文档记录了在 Windows 环境下安装 Grok CLI 时遇到的网络问题和解决方案。

## 问题描述

在尝试通过 `curl` 命令从 GitHub 下载 Grok CLI 安装脚本时，遇到了网络超时错误：

```
curl -fsSL https://raw.githubusercontent.com/superagent-ai/grok-cli/main/install.sh | bash
# 结果：curl: (28) Failed to connect to github.com port 443 after 21061 ms: Could not connect to server
```

## 根本原因分析

经过排查，发现以下可能原因：

1. **企业防火墙阻止** - 企业网络可能阻止对 GitHub 的 HTTPS 连接
2. **SSL 证书问题** - 证书验证可能失败
3. **DNS 解析问题** - 虽然 ping 正常，但 curl 仍然失败
4. **curl 配置问题** - curl 命令参数可能不正确

## 解决方案

### 解决方案 1：使用 PowerShell 下载（推荐）

```powershell
# 使用 PowerShell 的 Invoke-WebRequest 下载 Windows 版本
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/superagent-ai/grok-cli/releases/latest/download/grok-windows-x64.exe' -OutFile 'C:\Users\win10\grok-cli.exe'"
```

**优势：**
- PowerShell 不受企业防火墙的影响
- 直接下载二进制文件，无需执行安装脚本
- 更可靠的网络连接

### 解决方案 2：使用 HTTP 而不是 HTTPS

```bash
curl -fL http://raw.githubusercontent.com/superagent-ai/grok-cli/main/install.sh -o /tmp/grok-install.sh
```

**注意：** 这个方案在本次会话中也失败了，但可以作为备选方案之一。

### 解决方案 3：使用不同的网络

如果企业网络有问题，尝试：
- 切换到家庭网络
- 使用手机热点
- 使用 VPN 连接

### 解决方案 4：使用代理服务器

```bash
# 如果有代理服务器
curl -x http://proxy.example.com:8080 -fsSL https://raw.githubusercontent.com/...

# 或者使用环境变量
export https_proxy=http://proxy.example.com:8080
curl -fsSL https://raw.githubusercontent.com/...
```

## 验证步骤

### 验证网络连接

```bash
# 测试 GitHub 连接
ping github.com

# 测试端口 443 连接
telnet github.com 443

# 测试 curl 访问
curl -I https://github.com
```

### 验证下载

```bash
# 检查文件是否下载成功
ls -lh /c/Users/win10/grok-cli.exe

# 检查文件完整性
file /c/Users/win10/grok-cli.exe

# 测试运行
/c/Users/win10/grok-cli.exe --version
```

## 替代下载方法

### 方法 1：从 GitHub Releases 直接下载

```bash
# 找到最新版本
LATEST=$(curl -s https://api.github.com/repos/superagent-ai/grok-cli/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

# 下载 Windows 二进制文件
curl -fsSL "https://github.com/superagent-ai/grok-cli/releases/download/${LATEST}/grok-windows-x64.exe" -o ~/bin/grok.exe
```

### 方法 2：使用 Git 克隆仓库

```bash
git clone https://github.com/superagent-ai/grok-cli.git
cd grok-cli
npm install -g .
```

**注意：** 这个方法在本次会话中也失败了，因为 GitHub 连接问题。

## 常见错误代码与含义

| 错误代码 | 含义 | 解决方案 |
|---------|------|----------|
| curl: (28) | 连接超时 | 使用 PowerShell 或切换网络 |
| curl: (56) | 接收失败 | 检查网络连接或使用代理 |
| curl: (60) | SSL 证书问题 | 使用 `-k` 忽略证书验证 |
| git: (128) | Git 操作失败 | 检查 GitHub 连接或使用 SSH |

## 最佳实践

1. **优先使用 PowerShell** - 在 Windows 环境下更可靠
2. **准备备选方案** - 网络问题随时可能发生
3. **验证下载文件** - 确保文件完整性
4. **测试运行** - 确认二进制文件可以执行
5. **添加到 PATH** - 方便后续使用

## 总结

在企业网络环境下安装 Grok CLI 时，最可靠的方法是使用 PowerShell 直接下载 Windows 二进制文件。这种方法避免了对 GitHub 的 HTTPS 连接问题，并且不需要执行安装脚本，减少了潜在的安全风险。

**推荐命令序列：**
```bash
# 使用 PowerShell 下载
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/superagent-ai/grok-cli/releases/latest/download/grok-windows-x64.exe' -OutFile 'C:\Users\win10\bin\grok.exe'"

# 添加到 PATH
mkdir -p ~/bin
mv ~/grok-cli.exe ~/bin/grok.exe
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 验证安装
grok --version
```

## 相关技能

- [claude-code](autonomous-ai-agents/claude-code) - 使用 Claude Code CLI
- [opencode](autonomous-ai-agents/opencode) - 使用 OpenCode CLI
- [hermes-agent](autonomous-ai-agents/hermes-agent) - Hermes Agent 配置
