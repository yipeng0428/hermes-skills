# China GFW Diagnosis (Sessions with Nous Portal)

## Typical User Report

> "为什么我买了hermes一个月会员后，模型却用不了，发对话都没有回应"

Translation: "Why after I bought a one-month Hermes membership, the model can't be used and sending messages gets no response?"

## Initial Observations

From `hermes status --all`:
- Nous Portal: ✓ logged in
- Portal URL: `https://portal.nousresearch.com`
- Inference: `https://inference-api.nousresearch.com/v1`
- Access/key exp: current date + time (valid)
- Refresh: yes (auto-refresh enabled)
- But: Current provider may be set to `nous` or may have been switched to DeepSeek as workaround

## Diagnostic Commands

### 1. Check provider connectivity

```bash
curl -v --connect-timeout 10 --max-time 15 "https://inference-api.nousresearch.com/v1/models" 2>&1 | tail -10
```

Expected failure output:
```
* Host inference-api.nousresearch.com:443 was resolved.
* IPv6: (none)
* IPv4: 69.46.46.21
*   Trying 69.46.46.21:443...
* Connection timed out after 10008 milliseconds
* closing connection #0
curl: (28) Connection timed out after 10008 milliseconds
```

### 2. Check proxy env vars

```bash
echo "http_proxy=$http_proxy" && echo "https_proxy=$https_proxy"
```

On Windows / git-bash, these are often empty. But curl may still show `Uses proxy env variable no_proxy` — this comes from Windows system proxy settings, not bash env vars.

### 3. Find the VPN/proxy port (Windows)

If the user has a VPN running (e.g. 快柠檬, Clash, V2Ray):

```bash
# Method 1: Windows registry (most reliable)
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" | grep ProxyServer
# → ProxyServer    REG_SZ    http://127.0.0.1:10793

# Method 2: Port scan
for port in 7890 1080 10809 8118 8080 7891 9090 3128 1087 10793; do
  curl -s --connect-timeout 2 -x "http://127.0.0.1:$port" -o /dev/null -w "port $port: HTTP %{http_code}\n" "https://www.google.com" 2>/dev/null
done
```

### 4. Test proxy → Nous Portal chain

```bash
# Verify tunnel establishment
curl -v --connect-timeout 10 -x "http://127.0.0.1:10793" "https://inference-api.nousresearch.com/" 2>&1 | head -15
# Look for: "CONNECT phase completed" / "CONNECT tunnel established, response 200"

# Verify API access
curl -s --connect-timeout 15 --max-time 30 \
  -x "http://127.0.0.1:10793" \
  "https://inference-api.nousresearch.com/v1/models"
# Should return JSON model list
```

### 5. Check current config

```bash
grep -A5 "model:" ~/AppData/Local/hermes/config.yaml | head -10
```

Common finding: `base_url: https://api.deepseek.com` lingers from a previous provider switch.

### 6. Test Nous chat (without proxy — fails)

```bash
hermes chat -q "hello" --provider nous --model hermes-3-llama-4-405b -Q
```

Expected failure:
```
API call failed after 3 retries: Request timed out.
```

### 7. Test Nous chat (with proxy — succeeds)

```bash
hermes chat -q "hello" --provider nous --model anthropic/claude-sonnet-4.6 -Q
```

Expected: Normal text response. Verified with 快柠檬 on `127.0.0.1:10793`.

### 8. List available models through Nous Portal

```bash
curl -s -x "http://127.0.0.1:10793" "https://inference-api.nousresearch.com/v1/models" | python -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data'] if m.get('id')]"
```

Nous Portal acts as an OpenRouter-compatible gateway — exposes the full OpenRouter catalog including `nousresearch/hermes-4-405b`, `anthropic/claude-sonnet-4.6`, `deepseek/deepseek-v4-pro`, `openai/gpt-5.6-luna`, etc.

## Resolution Path A: Proxy/VPN (Use Nous Portal models)

1. Confirm VPN is running and in global/rule mode
2. Find proxy port: `reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" | grep ProxyServer`
3. Verify proxy reaches Nous: `curl -x http://127.0.0.1:<PORT> https://inference-api.nousresearch.com/v1/models`
4. Configure Hermes:
   ```bash
   echo "" >> ~/AppData/Local/hermes/.env
   echo "HTTPS_PROXY=http://127.0.0.1:<PORT>" >> ~/AppData/Local/hermes/.env
   echo "HTTP_PROXY=http://127.0.0.1:<PORT>" >> ~/AppData/Local/hermes/.env
   ```
5. Switch provider:
   ```bash
   hermes config set model.provider nous
   hermes config set model.default anthropic/claude-sonnet-4.6
   ```
6. Restart Hermes (`/reset`) and test

⚠️ **Constraint:** VPN MUST be running. If it's off, fall back to Path B.

## Resolution Path B: China-Friendly Provider (No VPN needed)

1. Identify the network block (curl timeout on inference-api.nousresearch.com)
2. Explain to user: subscription is fine, tools work, just model inference is blocked
3. Switch to China-accessible provider:
   ```bash
   hermes config set model.provider deepseek
   hermes config set model.default deepseek-v4-flash
   ```
4. If `model.base_url` has a stale value (e.g. `https://api.deepseek.com`), clear it:
   ```bash
   hermes config set model.base_url ""
   ```
5. Verify: send a test message

## Key Talking Points (for Chinese users)

- "你的 Hermes 会员（Nous 订阅）没白买 — 网页搜索、图片生成、语音等功能依然正常使用。"
- "只是模型推理服务器在美国（inference-api.nousresearch.com），国内网络连不上。"
- "有 VPN 的话配个代理就能用 Nous Portal 模型了：HTTPS_PROXY=http://127.0.0.1:端口 写入 .env。"
- "没 VPN 的话换个国内能用的模型提供商（DeepSeek、通义千问、Kimi 等），工具功能不受影响。"
- "模型提供商和 Nous 订阅是分开的，互不影响。"

## Provider Comparison for Chinese Users

| Scenario | Recommendation |
|----------|---------------|
| Want fast responses, no extra setup | DeepSeek (`deepseek-v4-flash`) |
| Want Chinese-language-optimized | Alibaba DashScope (通义千问), Kimi/Moonshot |
| Want to use Nous Portal models (Claude, GPT, Hermes-4) | Need VPN + `HTTPS_PROXY` in `.env` |
| Have VPN (快柠檬, Clash, V2Ray) | Set `HTTPS_PROXY` → use `nous` provider → full OpenRouter catalog |
| Tools working but model failing | Switch provider, keep subscription |

## Refund Policy

Nous Portal Terms of Service: "All Fees are non-refundable." No refunds or credits for unused/partial use. Users in restricted regions should contact Nous Research:
- Discord: https://discord.gg/jqVphNsB4H
- GitHub: https://github.com/NousResearch/hermes-agent/issues
