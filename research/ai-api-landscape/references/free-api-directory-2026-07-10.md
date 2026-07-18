# AI Free API Complete Directory — 2026-07-10

> 核验日期：2026-07-10 | 仅收录经官方文档核实的免费 API（区别于网页端免费）
>
> 标记说明：
> - ✅ 永久/每月免费 → 明确的周期性免费额度
> - 🆓 免费模型但限速 → 模型不对调用收费，仅限速
> - 🎁 新客赠送/一次性赠金 → 注册赠送，到期或耗尽后需付费
> - ⚠️ 需实名/绑卡
> - ❌ 无免费 API

---

## 海外文本/多模态 LLM API

### ✅ 永久免费层 / 免费模型

| 平台 | 免费类型 | 涵盖模型 | 额度 / 限速 | 绑卡？ | 官方链接 |
|------|---------|---------|-----------|-------|---------|
| **Google AI Studio / Gemini API** | 免费层 Free Tier | Gemini 2.0 Flash / Flash-Lite、1.5 Flash / Flash-Lite、1.5 Pro、2.5 Pro/Flash/Flash-Lite (Preview) | Flash 类：RPM 15, TPM 1M, RPD 1500；Pro 类：RPM 2~10, TPM 32K~250K, RPD 50~500。图像和音频不在免费层内 | ❌ | https://ai.google.dev/gemini-api/docs/pricing |
| **Groq** | 免费模型 Free Plan | llama-3.3-70b-versatile、llama-3.1-8b-instant、qwen/qwen3-32b、meta-llama/llama-4-scout-17b、openai/gpt-oss-20b/120b 等约 20 个模型 | 逐模型限速，如 llama-3.3-70b-versatile 30 RPM / 1K RPD / 12K TPM / 100K TPD；whisper-large-v3 20 RPM / 2K RPD | ❌ | https://console.groq.com/docs/rate-limits |
| **Cloudflare Workers AI** | 每日免费额度 | LLaMA 系列、Whisper、Stable Diffusion、文本嵌入等 | 每日 10,000 Neurons；超出付费 $0.011/1K neurons | ❌ | https://developers.cloudflare.com/workers-ai/platform/pricing/ |
| **Cerebras** | 全部模型免费 | GPT-OSS 系列、GLM-4.7 等 | 所有公开端点免费调用，仅限制速（具体查阅 docs） | ❌ | https://inference-docs.cerebras.ai/support/rate-limits |
| **SambaNova** | 免费层 | 开源模型 | 无需 API Key 的免费层（较低限速） | ❌ | https://docs.sambanova.ai/docs/en/models/rate-limits |
| **GitHub Models** | 免费层 | Azure OpenAI o1/o3/gpt-4.1/gpt-5-chat、DeepSeek-R1、Grok-3-Mini、LLaMA 等 | 分级限速：Low (15 RPM / 150 RPD / 4K tpr)、Medium/High (10 RPM / 50 RPD / 8K tpr)；高级模型如 DeepSeek-R1 每天 1 次请求 | ❌ GitHub 账号 | https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits |
| **OpenRouter** | 免费模型变体 `:free` | 多个模型支持 `:free` 后缀 | 免费模型 20 RPM；购买 >= 10 credit 后 1000 RPD，否则 50 RPD | ❌ | https://openrouter.ai/docs/guides/routing/model-variants/free |
| **NVIDIA NIM** | 免费试用 | 各类 NIM API 模型 | 注册即获取 API Key，免费用于开发测试 | ❌ | https://build.nvidia.com/ |

### 🎁 新客赠送 / 有限试用

| 平台 | 免费类型 | 涵盖模型 | 额度 / 有效期 | 绑卡？ | 官方链接 |
|------|---------|---------|-----------|-------|---------|
| **Cohere** | Trial API Key | Command A/A+、Rerank、Embed 等 | 每月 1000 次 API 调用；Chat 20 RPM、Embed 2000 inputs/min、Rerank 10 RPM | ❌ | https://docs.cohere.com/docs/rate-limits |
| **Mistral** | Free Tier | Mistral 开源模型 | 免费层限速（查阅 Limits 页面），超出需 Scale 付费 | ❌ | https://docs.mistral.ai/admin/billing-usage/usage-limits |
| **HuggingFace Inference** | 月度赠送 | 200+ 模型 | 免费用户：$0.10/月；PRO 用户：$2.00/月 | ❌ | https://huggingface.co/docs/inference-providers/pricing |

### ❌ 不提供免费 API

| 平台 | 说明 |
|------|------|
| **Together AI** | 需最低充值 $5，无免费试用 |
| **Replicate** | 纯按量计费，无免费额度 |
| **Anthropic / OpenAI / xAI** | 无永久免费 API 层，仅可能有短期新客 credits |

---

## 中国大陆文本/多模态 LLM API

### 🎁 新人一次性赠送

| 平台 | 免费额度 | 有效期 | 涵盖模型 | 要实名？ | 官方链接 |
|------|---------|-------|---------|----------|---------|
| **阿里云百炼** | 总约 340 万+ tokens（qwen-max 100万、qwen-turbo/vl-max/vl-turbo 各70万、qwen-long 30万）+ 每日 100 万 tokens | 30~90 天 | 通义千问系列 | ⚠️ | https://help.aliyun.com/zh/model-studio/new-free-quota |
| **火山方舟（豆包）** | 注册即送免费推理额度，按模型分别计算（示例 500K tokens/模型） | 耗尽为止 | 豆包系列基础及精调模型 | ⚠️耗尽后 | https://www.volcengine.com/docs/82379/1399514 |
| **腾讯混元** | 生文 100 万 tokens；生图 50 次（一次性资源包） | 1 年 | Hunyuan-a13b、role-latest、translation、Vision、embedding 等 | ⚠️ | https://cloud.tencent.com/document/product/1729/97731 |
| **Kimi (月之暗面)** | 注册赠送免费 tokens（旧型号） | 赠送余额有效期 | Kimi K2.6 / K2.7 Code（K3 无免费层） | 需注册 | https://platform.moonshot.cn/docs/pricing/chat |
| **DeepSeek** | 无纯免费层，首次充值有赠送余额；充值余额永久有效 | 赠送余额有时限 | DeepSeek-V4-Flash / V4-Pro | ⚠️需实名充值 | https://api-docs.deepseek.com/zh-cn/quick_start/pricing/ |
| **硅基流动** | 按量付费；开源模型 API 极低价，部分有免费额度 | 查阅模型页 | 100+ 开源模型 | 需注册 | https://siliconflow.cn/pricing |
| **MiniMax** | Token Plan 订阅套餐内含额度 | 月度重置 | 语言/视频/语音/图像全模态 | 需注册 | https://platform.minimaxi.com/docs/pricing/overview |

### 其他

| 平台 | 说明 |
|------|------|
| **智谱 BigModel** | GLM Coding Plan 订阅制（Lite/Pro/Max），按 5 小时限额+每周限额；非传统免费 API。知识库存储 1GB 永久免费 |
| **讯飞星火** | 星火大模型有试用额度；语音类每日 500 次免费 |

---

## 语音 API (STT/TTS)

### 海外

| 平台 | 类型 | 免费额度 | 有效期 | 绑卡？ | 官方链接 |
|------|------|---------|-------|-------|---------|
| **Google Cloud STT (V1)** | STT | 每月 60 分钟 | 月度 | ⚠️需绑卡 | https://cloud.google.com/speech-to-text/pricing |
| **Google Cloud TTS** | TTS | 每月 100 万字符（标准） | 月度 | ⚠️ | https://cloud.google.com/text-to-speech/pricing |
| **Azure Speech (F0)** | STT+TTS | STT 5h/月；TTS 50万字符/月 | 月度 | ⚠️ | F0 tier |
| **AWS Polly (Free Tier)** | TTS | 每月 500 万字符（标准，首 12 个月） | 12月 | ⚠️ | https://aws.amazon.com/polly/pricing/ |
| **AWS Transcribe (Free Tier)** | STT | 每月 60 分钟（首 12 个月） | 12月 | ⚠️ | https://aws.amazon.com/transcribe/pricing/ |
| **Deepgram** | STT | $200 免费 credit | 一次性 | ❌ | https://developers.deepgram.com/docs/getting-started |
| **Gladia** | STT | 每月 10 小时 | 月度 | ❌ | https://docs.gladia.io/ |
| **Groq Whisper** | STT | Groq Free Plan 含 Whisper：20 RPM / 2K RPD | 永久 | ❌ | https://console.groq.com/docs/rate-limits |
| **ElevenLabs** | TTS+STT | Free 每月 10K credits（TTS ~60min）；Startup Grant 12 月免费 3300 万字符 | 月度 | ❌ | https://elevenlabs.io/pricing |
| **讯飞开放平台** | TTS+STT | TTS 每日 500 次免费（SDK+WebAPI）；STT 有试用包；基础发音人免费 | 每日 | 需注册 | https://www.xfyun.cn/doc/tts/online_tts/tts_description.html |

### 国内语音

| 平台 | 类型 | 免费额度 | 有效期 | 实名？ | 官方链接 |
|------|------|---------|-------|-------|---------|
| **百度智能云语音** | STT+TTS+大模型语音 | STT 识别 5~10 万次、实时 10h、转写 10h；TTS 5~10 万次/5~10 万字符；大模型声音复刻 5~50 万字符；端到端语音 LLM 50~100 万 tokens | **永久有效** | ⚠️需个人/企业实名 | https://cloud.baidu.com/doc/SPEECH/s/Wl9mh4doe |
| **腾讯云语音合成** | TTS | 800 万字符一次性免费资源包 | 领取后 3 月 | ⚠️ | https://cloud.tencent.com/document/product/1073/34112 |
| **阿里云智能语音** | STT+TTS | 新用户免费试用 3 个月（全品类） | 3 月 | ⚠️ | https://help.aliyun.com/zh/isi/product-overview/billing-10 |

---

## 图像/视觉 API

| 平台 | 免费额度 | 备注 |
|------|---------|------|
| **Google Gemini API** | ❌ 图像生成不在免费层 | 需付费 |
| **Cloudflare Workers AI** | 包含在每日 10K Neurons 内 | 可出少量图 |
| **HuggingFace Inference** | 包含在每月 $0.10/$2.00 credit 内 | 按模型计费 |
| **Stability AI** | 25 免费 credits（1 credit ≈ $0.01） | 一次性赠送 |
| **Leonardo.ai** | 新用户有免费 credit | 需绑支付方式 |
| **Fal.ai** | ❌ Sandbox 免费 credits 不可通过 API 使用 | API 需付费 |

---

## 快速选型建议

### 最大方（额度充足）
1. **百度智能云语音** — 永久有效、5万+次额度
2. **Google Gemini API** — 1500 RPD × 30 天 ≈ 海量免费
3. **Groq** — 完全免费、速度极快、模型丰富
4. **Cerebras** — 全部模型免费
5. **Cloudflare Workers AI** — 文本/图像/语音全覆盖

### 国内用户最优路径
- **文本**：阿里云百炼新人赠送 → 用完转 DeepSeek（极低价）
- **语音**：百度智能云（永久免费）+ 讯飞（每日 500 次）
- **图像**：Cloudflare Workers AI（神经元内免费出图）

### 零门槛（无需绑卡/实名）
Gemini API、Groq、Cloudflare Workers AI、Cerebras、SambaNova、OpenRouter、Deepgram、Gladia

---

## KIMI K3 Status (2026-07-17 Update)

> 专项调研结论：KIMI K3 目前**无免费 API 层**，仅有以下可用渠道：

| 渠道 | 类型 | 费用 | 验证方式 |
|------|------|------|---------|
| **Kimi Web Chat** (kimi.moonshot.cn) | 网页对话 | ✅ 免费 | 网页直接访问，K3已上线 |
| **OpenRouter** (`moonshotai/kimi-k3`) | API | ❌ $0.00003/1K input tokens | API直接调用验证 |
| **Moonshot 官方 API** (platform.moonshot.cn) | API | ❌ 按量计费，充值返券30% | 官方定价页面确认 |

### 未上架 K3 的平台（已逐一验证）
- DeepInfra — 仅 K2.5 / K2.6 / K2.7-Code
- Ollama — 仅 K2.5 / K2.6 / K2.7-Code
-阿里云百炼 / 百度千fan / 火山方舟 / 硅基流动 / Together — 均未上架 K3

### 潜在免费路径
K3 被 OpenRouter 标记为 **open-weight**（开放权重），待社区发布 GGUF 量化版本后，可通过 Ollama/llama.cpp 本地运行获得免费 API。

---

*以上数据均基于截至 2026-07-10 各平台官方文档直接核验。政策随时可能调整，请以官方最新页面为准。*