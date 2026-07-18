# SMA Model Selection Guide

Last verified: 2026-07-18

## Recommended Combo by Task Type

| 任务类型 | 国内系 | 国际系 | 混合系 |
|---------|--------|--------|--------|
| 文案撰写 | DeepSeek + LongCat | Claude + GPT | DeepSeek + Claude |
| 策略分析 | DeepSeek + InternLM | Claude + Mistral | GPT + DeepSeek |
| 设计方案 | LongCat + DeepSeek | Claude + GPT | 三者混搭 |
| 数据报告 | DeepSeek + InternLM | GPT + Mistral | Claude + DeepSeek |
| 代码+技术 | DeepSeek + InternLM | Claude + GPT | GPT + DeepSeek |
| 创意发散 | LongCat + GPT | Claude + Mistral | DeepSeek + Claude |

## Per-Dimension Recommendation

| 维度 | 推荐模型 | 不推荐 | 原因 |
|------|---------|--------|------|
| 深度逻辑推理 | Claude Sonnet | GPT-4o | Claude在结构化推理上更可靠 |
| 中文商业分析 | DeepSeek-Chat | Mistral | DeepSeek对中国商业场景理解更深 |
| 创意发散+隐喻 | GPT-4o | DeepSeek | GPT在创意文本上更流畅 |
| 质量检查+纠错 | Claude Sonnet | Mistral | Claude对识别"AI套话"更敏感 |
| 数据驱动分析 | DeepSeek | LongCat | DeepSeek在数字敏感度更好 |
| 表达润色 | GPT-4o | Intern | GPT在英文+中文表达上都更地道 |
| 快速覆盖基础视角 | Mistral-Small | Claude | Mistral便宜，不会显著降质 |

## 禁止组合（同质无效）

| 组合 | 原因 |
|------|------|
| 同一模型的两个实例 | 同质无效，浪费token |
| GPT + ChatGPT（实为同模型） | 没有互补性 |
| 全部免费弱模型 | 堆叠物理天花板限制 |

## 实际可用Provider列表（本机配置）

Env变量 → Provider → 模型族

| Env Var | Provider | 可用模型 | 擅长 |
|---------|----------|---------|------|
| `JBBTOKEN_API_KEY` | jbbtoken.cn | claude-sonnet-4-20250514 | 逻辑、结构化、纠错 |
| `DEEPSEEK_API_KEY` | api.deepseek.com | deepseek-chat | 中文、商业、数据 |
| `CHATANYWHERE_API_KEY` | api.chatanywhere.tech | gpt-5.6-luna-ca, gpt-4o | 创意、表达、润色 |
| `LONGCAT_API_KEY` | - | LongCat-2.0 | 中文商业分析 |
| `INTERN_API_KEY` | - | InternLM | 基础研究覆盖 |
| `MISTRAL_API_KEY` | api.mistral.ai | mistral-small-latest | 快速/风控（可能401） |
| `SENSENOVA_API_KEY` | - | SenseNova | 待验证 |

> ⚠️ jbbtoken和deepseek的API Key是独立的！不要把DEEPSEEK_KEY传给jbbtoken（会得到错误的模型）。
