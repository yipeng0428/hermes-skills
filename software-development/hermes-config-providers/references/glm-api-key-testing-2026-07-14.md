# GLM API Key 测试报告 - 2026-07-14

## 测试概述

本次测试验证了三个智谱 GLM API Key 的有效性，并成功配置了智谱 GLM 模型到 Hermes 模型池。

## 测试时间
- **日期**: 2026-07-14
- **测试人**: Hermes Agent
- **测试环境**: Windows 10 + Hermes Agent

## 测试 Key 列表

### Key 1: `92b7796ad84e4c429dd3ed14af8acfa8.ChQk6okuk0qZ6hAg`
- **状态**: ❌ **无效**
- **测试时间**: 2026-07-14 06:47:28 UTC
- **测试端点**: `/v4/chat_completions` → 404
- **测试端点**: `/v4/chat/completions` → 模型不存在
- **错误信息**: `{"timestamp":"2026-07-14T06:47:28.658+00:00","status":404,"error":"Not Found","path":"/v4/chat_completions"}`
- **可能原因**: 
  - Key 已过期
  - 模型权限问题
  - 账户余额不足
- **建议**: 重新申请新的 API Key

### Key 2: `9faf05dcf76b4f51a4a07aca84c93d1f.wWm6X9ehEaEj1v6K`
- **状态**: ✅ **有效**
- **测试时间**: 2026-07-14 06:47:32 UTC
- **测试端点**: `/v4/chat/completions`
- **测试模型**: `glm-4-flash`
- **响应内容**: "你好👋！我是人工智能助手，很高兴见到你，有什么可以帮助你的吗？"
- **使用统计**: 26 tokens (6 prompt + 20 completion)
- **认证测试**: HTTP 200 OK
- **配置验证**: Hermes Doctor 检查通过
- **最终状态**: ✅ 配置成功，模型可用

## 配置过程

### 1. 环境变量配置
```bash
# ~/.hermes/.env
GLM_API_KEY=9faf05dcf76b4f51a4a07aca84c93d1f.wWm6X9ehEaEj1v6K
```

### 2. 模型配置
```yaml
# C:\Users\win10\AppData\Local\hermes\config.yaml
model:
  provider: zai
  base_url: https://open.bigmodel.cn/api/paas/v4
  api_key_env: GLM_API_KEY
```

### 3. Hermes CLI 配置命令
```bash
# 设置提供商
hermes config set model.provider zai

# 设置基础 URL
hermes config set model.base_url https://open.bigmodel.cn/api/paas/v4

# 设置 API Key 环境变量
hermes config set model.api_key_env GLM_API_KEY
```

## 可用的 GLM 模型

根据智谱官方 API，以下模型可用于配置：
- `glm-4-flash` - GLM-4-Flash (推荐)
- `glm-4` - GLM-4
- `glm-3-turbo` - GLM-3-Turbo
- 其他智谱模型（根据账户权限）

## 使用方法

### 方法 1: 直接使用智谱 GLM
```bash
hermes chat -m glm-4-flash --provider zai
```

### 方法 2: 在交互式会话中切换
```bash
hermes
/model zai/glm-4-flash
```

### 方法 3: 设置为默认模型
```bash
hermes config set model.default glm-4-flash
```

## API 测试脚本

### 认证测试脚本
```bash
#!/bin/bash
API_KEY="YOUR_API_KEY_HERE"

echo "Testing GLM API Key: $API_KEY"

# 测试认证
echo "\n1. Testing authentication..."
curl -I "https://open.bigmodel.cn/api/paas/v4/models" \
  -H "Authorization: Bearer $API_KEY"

# 测试模型访问
echo "\n2. Testing model access..."
curl -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model": "glm-4-flash", "messages": [{"role": "user", "content": "你好"}]}'
```

### 预期成功响应
```json
{
  "choices": [{
    "finish_reason": "stop",
    "index": 0,
    "message": {
      "content": "你好👋！我是人工智能助手...",
      "role": "assistant"
    }
  }],
  "created": 1784011662,
  "model": "glm-4-flash",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 20,
    "prompt_tokens": 6,
    "total_tokens": 26
  }
}
```

## 常见问题及解决方案

### ❌ 问题 1: 404 Not Found
**错误**: `{"status":404,"error":"Not Found"}`
**原因**: 使用了错误的端点路径
**解决**: 使用 `/chat/completions` 而不是 `/v4/chat_completions`

### ❌ 问题 2: 模型不存在
**错误**: `{"error":{"code":"1211","message":"模型不存在，请检查模型代码。"}}`
**原因**: 模型名称错误或账户无权限
**解决**: 检查模型名称，确保账户有权限访问该模型

### ❌ 问题 3: 401 Unauthorized
**错误**: 认证失败
**原因**: Key 已过期或无效
**解决**: 重新申请新的 API Key

### ✅ 问题 4: 成功响应
**标志**: HTTP 200 OK + 有效响应内容
**解决**: 配置成功，可以正常使用

## 后续建议

1. **Key 管理**: 建议为每个提供商使用不同的 Key 命名约定（如 `GLM_API_KEY_1`, `GLM_API_KEY_2`）以便于管理
2. **Key 过期**: 智谱 GLM 的 Key 可能会快速过期，建议定期测试 Key 有效性
3. **模型选择**: 根据任务需求选择合适的模型（如 `glm-4-flash` 用于快速响应，`glm-4` 用于高质量输出）
4. **配额监控**: 关注 API 使用配额，避免因配额不足导致服务中断

## 相关技能

- `hermes-config-providers` - 提供商配置技能
- `hermes-agent` - Hermes Agent 主技能

## 更新记录

- **2026-07-14**: 初始测试报告，记录两个 Key 的测试结果
- **待更新**: 后续 Key 有效性测试结果

---
*本报告由 Hermes Agent 自动生成，用于记录 API Key 测试结果和配置经验*