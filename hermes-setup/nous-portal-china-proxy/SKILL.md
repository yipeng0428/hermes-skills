---
name: nous-portal-china-proxy
description: "在中国使用 Nous Portal 模型：诊断连接超时并配置 VPN 代理（快柠檬等）"
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [hermes, proxy, china, vpn, nous-portal, troubleshooting]
---

# Nous Portal 中国代理配置

## 触发条件

- 用户在中国，Nous Portal 模型（provider=nous）发消息无响应/超时
- `hermes chat` 报 "API call failed after 3 retries: Request timed out"
- 切换到 nous 提供商后自动 fallback 回其他提供商

## 背景

`inference-api.nousresearch.com`（69.46.46.21，美国 IP）在中国大陆被墙，TCP 直连超时。
Nous 订阅的**工具功能**（Firecrawl 搜索、FAL 图片、TTS/STT）走另一通道，不受影响。
只有**模型推理**需要代理。

## 步骤

### 1. 确认问题是网络而非账号

```bash
curl -s --connect-timeout 10 -o /dev/null -w "HTTP %{http_code} Time: %{time_total}s\n" "https://inference-api.nousresearch.com/v1/models"
# HTTP 000 = 连接超时 = 被墙
hermes auth list nous   # 确认已登录（应显示 1 credentials）
```

### 2. 找到 VPN 的本地代理端口

用户需先开启 VPN（如快柠檬）的**全局模式**。然后从 Windows 注册表读系统代理：

```bash
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" | grep -i proxy
# 看 ProxyServer 行，例如: ProxyServer REG_SZ http://127.0.0.1:10793
```

快柠檬用的端口是 **10793**（可能变化，以注册表为准）。
如果注册表没有，扫描常见端口：7890, 1080, 10809, 8118, 8080, 10793。

### 3. 验证代理能连通 Nous API

```bash
# 先测 Google 确认代理本身工作
curl -s --connect-timeout 5 -x "http://127.0.0.1:10793" -o /dev/null -w "HTTP %{http_code}\n" "https://www.google.com"
# 再测 Nous 模型列表（成功会返回 JSON 模型列表）
curl -s --connect-timeout 15 -x "http://127.0.0.1:10793" "https://inference-api.nousresearch.com/v1/models" | head -5
```

### 4. 写入 Hermes .env

```bash
echo "" >> "$HOME/AppData/Local/hermes/.env"
echo "# VPN 代理" >> "$HOME/AppData/Local/hermes/.env"
echo "HTTPS_PROXY=http://127.0.0.1:10793" >> "$HOME/AppData/Local/hermes/.env"
echo "HTTP_PROXY=http://127.0.0.1:10793" >> "$HOME/AppData/Local/hermes/.env"
```

### 5. 设置模型提供商

```bash
hermes config set model.provider nous
hermes config set model.default anthropic/claude-fable-5   # 或其他 Nous Portal 目录中的模型
```

注意：模型 ID 必须是 Nous Portal 目录里存在的（`/v1/models` 返回的列表），
例如 `nousresearch/hermes-4-405b`、`anthropic/claude-sonnet-4.6`、`deepseek/deepseek-v4-pro`。
不存在的模型名会返回 404 "Model not found"。

### 6. 重启 Hermes 应用（关键！）

`.env` 里的 `HTTPS_PROXY` 只在**进程启动时**加载。改完必须完全退出并重启 Hermes
桌面应用（CLI 则退出重开）。不重启会继续超时并自动 fallback 到其他提供商。

### 7. 验证

重启后发一条消息，或：

```bash
hermes chat -q "只说三个字：我通了" --provider nous -Q
```

## 陷阱

- **不重启不生效** — 最常见的失败原因。改 .env 后必须重启应用。
- **fallback 会改写 config.yaml** — 超时后 Hermes 可能把 model.provider 自动回退成
  其他提供商，配好代理后要重新检查/设置 `model.provider nous`。
- **VPN 必须保持开启**（全局模式）。VPN 关闭后 Nous 模型立即不可用；
  临时切回国内直连提供商：
  ```bash
  hermes config set model.provider deepseek
  hermes config set model.default deepseek-v4-pro
  ```
- **不同电脑/不同 VPN 端口可能不同** — 每台机器都要用步骤 2 重新确认端口。
- `hermes chat` 没有 `--timeout` 参数，别加。
- curl 测试时注意 `no_proxy` 环境变量可能排除某些域名。

## 用户环境备注

- 办公室与家里两台电脑都用快柠檬 VPN，办公室端口为 10793（家里的以注册表实测为准）。
- **快柠檬智能模式即可用**，无需全局模式：实测智能模式下 inference-api.nousresearch.com
  自动分流走境外（HTTP 200，<1秒），端口不变仍为 10793。日常开智能模式，
  国内流量不受影响。若智能模式某天失效再切全局排查。
