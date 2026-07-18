# Model Availability Research — Systematic Platform Probing

> When the user asks "is model X available on platform Y" or "where can I find free access to model Z",
> this workflow checks platforms in priority order, from most likely to have new models to least likely.

---

## Priority Order for New Model Availability

When a new model is released (e.g., KIMI K3 on 2026-07-15), platforms typically onboard in this order:

### Tier 1: Same-Day to 48 Hours
| Platform | Check Method | Notes |
|----------|-------------|-------|
| **Official API** | `curl -s 'https://api.official.com/v1/models'` | Always first; may need key |
| **OpenRouter** | `curl -s 'https://openrouter.ai/api/v1/models' \| grep -i 'model-name'` | Aggregator with fastest onboarding; usually 1-2 days |
| **Official Web Chat** | Browser or HTML scrape | Free UI often launches simultaneously with API |

### Tier 2: 1-4 Weeks
| Platform | Check Method | Notes |
|----------|-------------|-------|
| **DeepInfra** | `curl -s 'https://api.deepinfra.com/v1/openai/models'` | Usually 1-2 weeks for popular models |
| **NVIDIA NIM** | `curl -s 'https://integrate.api.nvidia.com/v1/models'` | Enterprise-focused; 2-4 weeks |
| **Together AI** | Requires API key | Often 2-3 weeks |
| **Fireworks AI** | API path varies | Often 2-3 weeks |

### Tier 3: 1-3 Months
| Platform | Check Method | Notes |
|----------|-------------|-------|
| **HuggingFace Inference** | `curl -s 'https://huggingface.co/api/models?search=model-name'` | Needs GGUF/weights upload first |
| **Replicate** | Requires auth | Community uploads; variable timing |
| **Cloud Marketplaces** | Browser (JS SPAs) | AWS/GCP/Azure marketplace listings lag significantly |

### Tier 4: 3+ Months (or Never)
| Platform | Check Method | Notes |
|----------|-------------|-------|
| **Chinese Cloud Platforms** | Browser + vision | Huawei/JDCloud/360 rarely aggregate foreign models |
| **Groq/Cerebras/SambaNova** | Hardware-specific | Only models compiled for their hardware |

---

## Workflow: "Is Model X Available?"

### Step 1: Direct API Probe (no auth needed for listing)
```bash
# OpenRouter — most comprehensive aggregator
curl -sL --max-time 30 'https://openrouter.ai/api/v1/models' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data['data']:
    if 'kimi' in m['id'].lower() or 'moonshot' in m['id'].lower():
        print(f\"{m['id']}: {m['pricing']}\")
"

# DeepInfra — second most likely
curl -sL --max-time 30 'https://api.deepinfra.com/v1/openai/models' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data['data']:
    if 'kimi' in m['id'].lower() or 'moonshot' in m['id'].lower():
        print(f\"{m['id']}: {m['metadata']['pricing']}\")
"

# NVIDIA NIM
curl -sL --max-time 30 'https://integrate.api.nvidia.com/v1/models' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data['data']:
    if 'kimi' in m['id'].lower() or 'moonshot' in m['id'].lower():
        print(m['id'])
"

# SambaNova
curl -sL --max-time 30 'https://api.sambanova.ai/v1/models' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data['data']:
    if 'kimi' in m['id'].lower() or 'moonshot' in m['id'].lower():
        print(m['id'])
"
```

### Step 2: Check for Free Variants
```bash
# OpenRouter :free suffix check
curl -sL --max-time 30 'https://openrouter.ai/api/v1/models' | python3 -c "
import sys, json
data = json.load(sys.stdin)
free = [m for m in data['data'] if ':free' in m['id']]
print(f'Total free models: {len(free)}')
for m in free:
    print(f\"  {m['id']}\")
"
```

### Step 3: HuggingFace Open Source Check
```bash
# Search for model weights (needed for local deployment)
curl -sL --max-time 30 'https://huggingface.co/api/models?search=model-name&sort=downloads&direction=-1' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data:
    print(f\"{m['id']}: {m.get('downloads', 0)} downloads\")
"
```

### Step 4: Chinese Cloud Platform Scan
Chinese cloud platforms (Huawei ModelArts, JDCloud, 360 AI, SenseTime) are **JS SPAs** and cannot be scraped with curl. Pattern:
- `curl | grep -i 'kimi\|moonshot'` returns nothing → JS SPA, inaccessible
- These platforms almost never aggregate foreign models within the first month
- Skip unless user specifically requires Chinese domestic platforms

### Step 5: Compile Report
Use this template:
```
## Platform
- URL: 
- Model Available: ✅/❌
- Free Tier: 
- Pricing: 
-获取方式: 
```

---

## Key Findings: KIMI K3 (2026-07-17)

| Platform | K3 Available | Free | Onboard Time |
|----------|-------------|------|--------------|
| Moonshot Official API | ✅ | ❌ | Day 0 |
| Kimi Web Chat | ✅ | ✅ (UI only) | Day 0 |
| OpenRouter | ✅ | ❌ | Day 2 |
| DeepInfra | ❌ | — | Not yet (only K2.x) |
| NVIDIA NIM | ❌ | — | Not yet (only K2.6) |
| HuggingFace | ❌ | — | Waiting for weights upload |
| All Chinese clouds | ❌ | — | Unlikely in near term |

**Pattern**: OpenRouter is consistently the fastest aggregator for new models.
For K3 specifically: no free API exists anywhere as of 2026-07-17.

---

## Adapting for Other Models

Replace `kimi`/`moonshot` with the target model's identifier:
- GPT-5: `gpt-5`, `openai`
- Claude 4: `claude`, `anthropic`
- Llama 4: `llama`, `meta`
- DeepSeek V4: `deepseek`
- Qwen 3: `qwen`

---

*Verified: 2026-07-17 during KIMI K3 availability research*
