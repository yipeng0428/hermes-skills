---
name: grok-cli
description: "Install, configure, and use Grok CLI — xAI's autonomous AI coding agent for terminal automation and workflow integration."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [AI-Agent, Grok, xAI, Autonomous-Coding, Terminal-Automation]
    related_skills: [claude-code, opencode, hermes-agent]
    references:
      - troubleshooting.md
---

# Grok CLI — xAI Autonomous Coding Agent

Install and orchestrate [Grok CLI](https://github.com/superagent-ai/grok-cli), xAI's autonomous AI coding agent built with Bun and OpenTUI. Grok CLI enables terminal automation, workflow integration, and autonomous coding tasks with xAI's models.

## When to Use

- **Automate repetitive coding tasks** in CI/CD pipelines
- **Delegate complex refactoring or feature implementation** to an autonomous agent
- **Run headless AI coding sessions** without interactive UI
- **Integrate xAI models** into your terminal workflows
- **Batch process multiple coding tasks** in parallel
- **Generate, review, or fix code** autonomously

## Installation

### Prerequisites

- **Node.js** (v18+ recommended) or **Bun** runtime
- **Git** (for cloning repositories)
- **Network access** to GitHub and xAI APIs

### Install Grok CLI

#### Method 1: Direct Download (Recommended for Windows)
```bash
# Download the Windows executable
curl -fsSL https://github.com/superagent-ai/grok-cli/releases/latest/download/grok-windows-x64.exe -o ~/bin/grok.exe

# Make executable
chmod +x ~/bin/grok.exe

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Method 2: npm Installation
```bash
npm install -g @superagent-ai/grok-cli
```

#### Method 3: Build from Source
```bash
# Clone repository
git clone https://github.com/superagent-ai/grok-cli.git
git checkout main

# Install dependencies
cd grok-cli
npm install

# Build
npm run build

# Install globally
npm install -g .
```

### Verify Installation
```bash
grok --version
# Should output version like: 1.1.7

grok --help
# View all available commands and options
```

## Configuration

### API Key Setup

Grok CLI requires an xAI API key to function. You can get one from [xAI's developer portal](https://console.x.ai/).

```bash
# Set API key (persists in config)
grok config set api-key your_xai_api_key_here

# Verify configuration
grok config get api-key

# List all config values
grok config list
```

### Alternative Configuration Methods

#### Environment Variable
```bash
export GROK_API_KEY="your_xai_api_key_here"
grok
```

#### Command-line Flag
```bash
grok -k your_xai_api_key_here
```

## Basic Usage

### Interactive Mode (TUI)

Start an interactive terminal interface:
```bash
grok
```

**Features:**
- Multi-turn conversations
- Real-time code editing
- Shell command execution
- File browsing and editing
- Model switching

### Single-Prompt Mode (Headless)

Run a single prompt and exit:
```bash
# Basic usage
grok -p "Write a Python script to download and process CSV files from a URL"

# With API key
grok -k your_api_key -p "Refactor this legacy codebase to use modern Python patterns"

# Specify working directory
grok -p "Add error handling to all API endpoints" -d /path/to/project
```

### Model Selection

Choose different xAI models:
```bash
# List available models
grok models

# Use a specific model
grok -p "Implement JWT authentication" -m grok-2-latest

# Use batch API for cost savings (async, lower latency)
grok -p "Generate unit tests" -m grok-2-latest --batch-api
```

## Advanced Usage Patterns

### 1. Automated Code Reviews

```bash
# Review a PR
grok -p "Review this GitHub pull request for security vulnerabilities, bugs, and code quality issues" \
  --from-pr 42 \
  -d /path/to/repo

# Review specific files
grok -p "Analyze src/auth.py for security flaws and suggest improvements" \
  -d /path/to/project
```

### 2. Feature Implementation

```bash
# Implement a new feature
grok -p "Add user authentication system with JWT tokens, refresh tokens, and role-based access control" \
  -d /path/to/backend

# Implement a frontend component
grok -p "Create a React dashboard component for displaying real-time data with TypeScript and TailwindCSS" \
  -d /path/to/frontend
```

### 3. Refactoring Tasks

```bash
# Refactor legacy code
grok -p "Refactor this Python codebase to use type hints, dataclasses, and modern Python patterns" \
  -d /path/to/project \
  --max-tool-rounds 200

# Optimize performance
grok -p "Identify and fix performance bottlenecks in this API server" \
  -d /path/to/server
```

### 4. Test Generation

```bash
# Generate unit tests
grok -p "Write comprehensive unit tests for all functions in src/utils/ with 100% coverage" \
  -d /path/to/project

# Generate integration tests
grok -p "Create integration tests for the REST API endpoints using pytest" \
  -d /path/to/backend
```

### 5. Documentation Generation

```bash
# Generate documentation
grok -p "Write comprehensive README.md, API documentation, and inline code comments for this project" \
  -d /path/to/project

# Generate technical documentation
grok -p "Create architecture decision records (ADRs) for the current system design" \
  -d /path/to/docs
```

## Configuration Management

### Config File Location

Grok CLI stores configuration in:
- **Linux/macOS:** `~/.config/grok/config.yaml`
- **Windows:** `%APPDATA%\grok\config.yaml`

### Common Configuration Options

```yaml
# ~/.config/grok/config.yaml
api_key: "your_xai_api_key_here"
model: "grok-2-latest"
default_directory: "/path/to/your/project"
max_tool_rounds: 400
batch_api: false
```

### Environment Variables

```bash
# API key
export GROK_API_KEY="your_key"

# Model selection
export GROK_MODEL="grok-2-latest"

# Base URL (for custom endpoints)
export GROK_BASE_URL="https://api.x.ai/v1"

# Debug mode
export GROK_DEBUG=true
```

## Session Management

### Save and Resume Sessions

```bash
# Start a session
grok -p "Start implementing the user authentication system" > session1.json

# Resume later
cat session1.json | grok -p "Continue with JWT implementation and add refresh tokens"

# Continue most recent session
grok -p "What did you do last time?"
```

### Session ID Management

```bash
# List sessions (stored in ~/.local/share/grok/sessions/)
ls ~/.local/share/grok/sessions/

# Resume specific session
grok -s session_id_here -p "Continue working on this feature"
```

## Network and Sandbox Configuration

### Sandbox Modes

Grok CLI can run in different security modes:

```bash
# Default: Run in sandbox with network restrictions
grok -p "Your task here"

# Disable sandbox (run directly on host - USE WITH CAUTION)
grok --no-sandbox -p "Your task here"

# Allow network access in sandbox
grok --allow-net -p "Fetch data from external API"

# Restrict sandbox network to specific hosts
grok --allow-host api.example.com --allow-host github.com -p "Your task"

# Port forwarding for sandbox
grok --port 8080:8080 --port 3000:3000 -p "Run local server"
```

### Security Considerations

- **Sandbox mode** is recommended for security
- **Disable sandbox only** for trusted tasks
- **Restrict network access** to specific hosts when possible
- **Review tool permissions** before executing untrusted code

## Integration with Hermes Agent

### Direct Terminal Execution

```bash
# Simple task
todo add -c "Use Grok CLI to implement a Python script that downloads and processes CSV files from a URL"

# Execute via terminal tool
terminal(command="grok -p 'Write a Python script to download and process CSV files from a URL' --max-tool-rounds 10", workdir="/path/to/project")
```

### Background Processing

```bash
# Start Grok in background for long-running tasks
todo add -c "Use Grok CLI to refactor the authentication module and add comprehensive tests"

# Monitor progress
grok daemon
```

### Error Handling and Retries

```bash
# Retry pattern for transient failures
for attempt in {1..3}; do
  if grok -p "Your task" --max-tool-rounds 5; then
    echo "Task completed successfully"
    break
  else
    echo "Attempt $attempt failed, retrying..."
    sleep 5
  fi
done
```

## Common Flags Reference

| Flag | Description | Example |
|------|-------------|---------|
| `-p, --prompt <text>` | Single prompt for headless execution | `grok -p "Write tests"` |
| `-k, --api-key <key>` | Specify API key | `grok -k sk-xxx -p "task"` |
| `-m, --model <model>` | Select model | `grok -m grok-2-latest -p "task"` |
| `-d, --directory <dir>` | Working directory | `grok -d /project -p "task"` |
| `--verify` | Run built-in verification | `grok --verify` |
| `--format <text|json>` | Output format | `grok --format json -p "task"` |
| `--sandbox` | Enable sandbox (default) | `grok --sandbox -p "task"` |
| `--no-sandbox` | Disable sandbox | `grok --no-sandbox -p "task"` |
| `--allow-net` | Allow network in sandbox | `grok --allow-net -p "task"` |
| `--max-tool-rounds <n>` | Limit agent loops | `grok --max-tool-rounds 200 -p "task"` |
| `--batch-api` | Use batch API for cost savings | `grok --batch-api -p "task"` |
| `-s, --session <id>` | Resume session | `grok -s ses_abc123 -p "continue"` |
| `-V, --version` | Show version | `grok --version` |
| `-h, --help` | Show help | `grok --help` |

## Troubleshooting

### Common Issues and Solutions

#### 1. Network Timeout When Downloading

**Problem:** `curl` times out when downloading Grok CLI

**Solutions:**
```bash
# Use PowerShell on Windows
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/superagent-ai/grok-cli/releases/latest/download/grok-windows-x64.exe' -OutFile 'grok.exe'"

# Use wget if available
wget https://github.com/superagent-ai/grok-cli/releases/latest/download/grok-windows-x64.exe -O grok.exe

# Try different network (corporate proxy, VPN, switch network)

# Use GitHub releases API to find direct download URL
```

#### 2. API Key Authentication Failed

**Problem:** `Error: Invalid API key` 或 `Permission denied - 团队已达到月度使用限制`

**解决方案：**
```bash
# 验证 API 密钥是否正确
# 从 https://console.x.ai/ 获取新的 API 密钥
# 检查 API 密钥格式（应以 'xai-' 开头）

# 使用环境变量代替（推荐方法）
export GROK_API_KEY="xai-..."
source ~/.bashrc

# 或者直接设置密钥
grok config set api-key xai-...

# 检查团队额度状态
# 访问 https://console.x.ai/ 购买更多额度或等待重置
```

**Windows 用户特别注意：**
```bash
# 在 Windows 的 Git Bash 中，使用以下方式设置环境变量
# 编辑 ~/.bashrc 文件，添加：
echo 'export GROK_API_KEY="xai-..."' >> ~/.bashrc
source ~/.bashrc

# 或者临时设置（当前会话有效）
export GROK_API_KEY="xai-..."
```

#### 3. Grok CLI Not Found

**Problem:** `command not found: grok`

**Solutions:**
```bash
# Check installation
which grok
ls -lh $(which grok)

# Verify PATH
echo $PATH

# Reinstall
grok update

# Check installation location
ls -la ~/bin/grok
grok --version
```

#### 4. Permission Denied

**Problem:** `Permission denied` when executing Grok CLI

**Solutions:**
```bash
# Make executable
chmod +x ~/bin/grok

# Run with explicit path
./bin/grok

# Use full path
/home/user/bin/grok
```

#### 5. Slow Response Times

**Problem:** Grok CLI is slow to respond

**Solutions:**
```bash
# Use batch API for cost savings
grok --batch-api -p "your task"

# Select a faster model
grok -m grok-2-latest -p "your task"

# Reduce max tool rounds
grok --max-tool-rounds 100 -p "your task"

# Check network connectivity
ping api.x.ai
```

### Debug Mode

```bash
# Enable verbose output
grok -p "your task" --verbose

# Check configuration
grok config list

# View logs (stored in ~/.local/share/grok/logs/)
ls ~/.local/share/grok/logs/
```

## Best Practices

### 1. Start Small

Begin with simple, bounded tasks before attempting complex refactoring:
```bash
grok -p "Write a function to validate email addresses" -d /project
```

### 2. Use Specific Prompts

Be explicit about requirements:
```bash
# Good
"Write a Python class for user authentication with JWT tokens, refresh tokens, and role-based access control. Include unit tests and documentation."

# Bad
"Fix the auth stuff"
```

### 3. Set Working Directory

Always specify the correct project directory:
```bash
cd /path/to/your/project
grok -p "Implement the feature" -d /path/to/your/project
```

### 4. Limit Tool Rounds

Prevent runaway loops:
```bash
grok --max-tool-rounds 100 -p "your task"
```

### 5. Review Output

Always review generated code before committing:
```bash
# Save output to file
grok -p "Implement feature X" > output.txt

# Review changes
less output.txt

# Apply changes manually or use git
```

### 6. Use Version Control

Commit changes before and after Grok sessions:
```bash
git add .
git commit -m "Before Grok session"
grok -p "Implement feature" -d .
git add .
git commit -m "After Grok session: feature implementation"
```

### 7. Parallel Execution

Run multiple independent tasks in parallel:
```bash
# Task 1
grok -p "Write backend API" -d /project/backend &

# Task 2
grok -p "Create frontend component" -d /project/frontend &

# Task 3
grok -p "Generate documentation" -d /project/docs &

wait
```

## Examples

### Example 1: Create a REST API Endpoint

```bash
cd /path/to/backend
grok -p "Create a FastAPI endpoint for user registration with email validation, password hashing, and database integration. Include request/response models, error handling, and unit tests." -d /path/to/backend --max-tool-rounds 150
```

### Example 2: Refactor Legacy Code

```bash
cd /path/to/legacy-project
grok -p "Refactor this Python 2 codebase to Python 3. Include type hints, modern Python patterns, and comprehensive test coverage. Maintain backward compatibility where possible." -d /path/to/legacy-project --max-tool-rounds 200
```

### Example 3: Generate Documentation

```bash
cd /path/to/project
grok -p "Generate comprehensive README.md, API documentation using MkDocs, and inline code comments for all public functions. Include architecture overview, installation instructions, and usage examples." -d /path/to/project
```

### Example 4: Security Audit

```bash
cd /path/to/project
grok -p "Perform a security audit of this codebase. Identify SQL injection vulnerabilities, XSS risks, authentication flaws, and sensitive data exposure. Provide remediation recommendations for each finding." -d /path/to/project
```

## 📚 支持文件

- **[references/api-channels.md](references/api-channels.md)** — Grok API 渠道实测记录（2026-07-16），列出所有已验证可用/不可用渠道
- **[references/windows-installation.md](references/windows-installation.md)** — Windows 安装指南
- **[references/troubleshooting.md](references/troubleshooting.md)** — 故障排除

## API 可用性说明（2026-07-16）

**当前国内无可用 Grok API 渠道。** OpenRouter/ChatAnywhere/JBBToken 均已下架或不支持 Grok 模型。xAI 官方 API 需支付且国内购买受限。

**实战替代方案（已验证可用）：**
- Claude Code（Fable 5）+ Codex（GPT-5.6-sol）双 Agent 阵列
- OpenCode CLI（开源，接现有 key 即用）
- Grok CLI 可路由到 OpenRouter 的其他编码模型作为后端

详见 [references/api-channels.md](references/api-channels.md)。

## Pitfalls

### 1. **Overly Broad Prompts**
**Problem:** Vague prompts lead to incomplete or incorrect results
**Solution:** Be specific about requirements, constraints, and expected output format

### 2. **Missing Dependencies**
**Problem:** Grok may try to use unavailable libraries or tools
**Solution:** Install required dependencies beforehand or specify allowed tools

### 3. **Context Window Limits**
**Problem:** Large codebases may exceed context window limits
**Solution:** Work on specific files or modules rather than entire repositories

### 4. **Network Restrictions**
**Problem:** Corporate firewalls may block xAI API endpoints
**Solution:** Use VPN, configure proxy, or check firewall settings

### 5. **API Rate Limits**
**Problem:** Too many requests may hit rate limits
**Solution:** Use `--batch-api` flag, space out requests, or monitor usage

### 6. **Sandbox Limitations**
**Problem:** Sandbox may prevent necessary operations
**Solution:** Use `--no-sandbox` for trusted tasks or configure `--allow-host` flags

### 7. **Session Persistence**
**Problem:** Sessions may not persist across terminal restarts
**Solution:** Save important sessions to files and resume with `-s` flag

### 8. **Model Limitations**
**Problem:** Grok-2 may not handle all edge cases correctly
**Solution:** Review output carefully and iterate with follow-up prompts

---

**Remember:** Grok CLI is a powerful tool, but it's not perfect. Always review generated code, test thoroughly, and use your judgment. Treat it as an assistant, not a replacement for human expertise.

**Tip:** For complex tasks, break them down into smaller subtasks and tackle them one at a time.
