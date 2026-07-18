# GLM API Testing & Validation

## Quick Validation Commands

### 1. Authentication Test (Should return 200)
```bash
curl -I "https://open.bigmodel.cn/api/paas/v4/models" \
  -H "Authorization: Bearer YOUR_API_KEY"
```
Expected: `HTTP/1.1 200 OK`

### 2. Model Access Test (Should return 200 or 401)
```bash
curl -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"model": "glm-4-flash", "messages": [{"role": "user", "content": "你好"}]}'
```

Expected responses:
- ✅ `200 OK` with response body → Key valid and model accessible
- ❌ `401 Unauthorized` → Key expired/invalid
- ❌ `{"error":{"code":"401","message":"令牌已过期或验证不正确"}}` → Key expired
- ❌ `{"error":{"code":"1211","message":"模型不存在，请检查模型代码。"}}` → Model not available for account
- ❌ `404 Not Found` → Wrong endpoint

## API Endpoint Variations (Historical)

- `/api/paas/v3/model_api/invoke` → Older endpoint (deprecated)
- `/api/paas/v4/chat_completions` → Incorrect path (404)
- `/api/paas/v4/chat/completions` → ✅ Correct path
- `/api/paas/v4/models` → Models list endpoint

## Model Names by Tier

### Free Tier
- `glm-4-flash`
- `glm-3-turbo`

### Paid Tier
- `glm-4`
- `glm-4-air`
- `glm-4-airx`
- `glm-4-long`

## Common Issues & Solutions

### Issue: "模型不存在"
**Solution**: Try a different model name or upgrade account tier

### Issue: Key works in curl but fails in Hermes
**Solution**: Ensure the key is in `.env` file, not inlined in config.yaml

### Issue: Intermittent 401 errors
**Solution**: Keys can expire quickly; regenerate if needed

## References
- [智谱 GLM 官方文档](https://open.bigmodel.cn/)
- [API 认证指南](https://open.bigmodel.cn/dev/api)
- [模型价格与限制](https://open.bigmodel.cn/pricing)