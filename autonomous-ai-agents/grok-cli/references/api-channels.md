# Grok API 渠道调查记录（2026-07-16 实测）

## 已验证的 API 渠道

### ❌ 不可用

| 渠道 | Base URL | 测试时间 | 错误 | 说明 |
|------|---------|---------|------|------|
| OpenRouter | `https://openrouter.ai/api/v1` | 2026-07-16 | 404 | Grok 模型（grok-2-1212, grok-3-mini-beta, grok-3-beta）均已从 OpenRouter 下架 |
| ChatAnywhere | `https://api.chatanywhere.tech` | 2026-07-16 | 404 | 不支持 Grok 模型 |
| JBBToken | `https://jbbtoken.cn` | 2026-07-16 | — | 仅支持 Claude 系列 |
| xAI 官方 | `https://api.x.ai/v1` | 2026-07-16 | `permission-denied` | API 配额耗尽 (`team has used all available credits`) |

### Grok CLI 可用功能

即使 API 不可用，CLI 以下功能仍然正常：
- `-u <url>` / `-k <key>` 路由到任意 OpenAI 兼容端点
- `-m <model>` 指定任意模型名
- `--no-sandbox` 禁用沙箱
- `-p "prompt"` headless 模式

## 替代方案优先级

1. **Claude Code**（已有，Fable 5 代理） + **Codex**（已有，GPT-5.6-sol）双 Agent 阵列
2. **OpenCode CLI**（`npm install -g @opencode-ai/cli`）开源编码 Agent
3. **Blackbox CLI**（多模型竞赛自动选最优）

## Grok CLI 配置模板（路由到其他端点时使用）

```bash
# 路由到 OpenRouter（如果用其他模型）
grok -u "https://openrouter.ai/api/v1" -k "$OPENROUTER_API_KEY" -m "model-id" -p "task"

# 路由到自定义端点
grok -u "https://your-proxy.com/v1" -k "$YOUR_KEY" -m "model" -p "task" --no-sandbox
```

## 有效的 OpenRouter 编码模型（可用作 Grok CLI 后端）

| 模型 ID | 类型 | 成本 |
|---------|------|------|
| `anthropic/claude-sonnet-4` | Claude | 付费 |
| `google/gemini-2.5-flash` | Gemini | 免费 |
| `meta-llama/llama-4-maverick` | LLAMA | 免费 |
| `deepseek/deepseek-chat` | DeepSeek | 付费 |

> 记录时间：2026-07-16。渠道状态随时可能变化，使用前应重新验证。
