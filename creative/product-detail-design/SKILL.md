---
name: product-detail-design
description: Design Chinese e-commerce product detail pages (商品详情页) with international brand aesthetic. Module-structured visual prototypes, asset inventory, multi-platform optimization (TJ/PDD/1688/Douyin).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ecommerce, detail-page, taobao, 1688, pinduoduo, china, prototype, product-design]
    related_skills: [claude-design, popular-web-designs, sketch]
---

# Chinese E-Commerce Product Detail Page Design

Design product detail pages (商品详情页) for Chinese e-commerce platforms with international brand aesthetic (Apple/MUJI/Dyson-style minimalism). Produces modular HTML visual prototypes that can guide final PSD production.

## When to Use

Use this skill when:
- Designing or upgrading a product detail page for 淘宝/天猫, 1688, 拼多多, 抖店, or 国际站
- User wants to shift from traditional Chinese e-commerce style to international brand minimalism
- Existing design needs a complete overhaul (旧版升级/详情页改版)
- AI rendering assets already exist and need to be organized into a coherent page flow

Related skills:
- **claude-design**: Use for generic artifact construction (HTML/CSS patterns, verification). This skill adds the e-commerce domain layer.
- **popular-web-designs**: Use when the user explicitly wants to match a known brand's system.
- **sketch**: Use for 2-way quick comparisons, not full detail pages.

## Three-Style Direction Triage

Before designing, help the user pick one of three aesthetic directions:

| Direction | Look | Best For | Chinese Market Position |
|-----------|------|----------|------------------------|
| **A. International Brand** | Minimalist, monochrome base, product as hero, Apple-style B/W gradients | Premium positioning, global market, brand building | 精品定位 / 国际视野 |
| **B. Industrial Craft** | Metal textures, CMF detail shots, exploded views, engineering precision | B2B, professional buyers, manufacturer credibility | 1688 / 企业客户 |
| **C. Scenario Story** | Lifestyle photography, real usage, emotional storytelling | C-end emotional purchase, gifting, impulse buy | 淘宝C端 / 抖音 |

Default to **A (International Brand)** unless user specifies otherwise. Capture the decision in the output filename.

## Asset Discovery Workflow

Before designing, exhaustively search local drives for existing assets. Across all drives (C:, D:, E:, F:), look for:

1. **Existing PSD files** — prior design work, templates, brand guidelines
2. **AI renderings** — GPT/ComfyUI/即梦/豆包 generated product images
3. **3D engineering files** — SLDPRT/SLDASM (SolidWorks), STEP, IGES, FBX, OBJ, STL for product visualization
4. **Product photos** — 白底图, 实拍图, 场景图, promotional images
5. **Video assets** — 操作视频, 宣传视频, 360° spin
6. **Brand collateral** — LOGO vectors, brand books, existing VI/sales materials
7. **Specifications** — parameter tables, certifications, packaging specs
8. **Competitor references** — downloaded competitor detail pages for comparison

Output this as a structured asset inventory table listing path, file type, size, and intended use.

## Detail Page Module Structure (15-20 Screens)

The standard Chinese e-commerce detail page follows a proven module sequence:

```
P01  Hero Image (首屏英雄图)        — Emotional hook + primary CTA
P02  Pain Point Contrast (痛点对比)   — Before/after or competitor comparison
P03  Feature Grid (卖点展示)         — 4-6 core features, icon + sentence
P04  Color/Variant Options (配色)    — If multiple SKUs/colors
P05  Craft/Detail Shots (工艺细节)   — Micro-photography + annotations
P06  Product Deconstruct (拆解爆炸图) — Shows internal quality, builds trust
P07  How-to-Use (使用步骤)           — 3-5 step visual flow
P08  Application Scenes (应用场景)   — 4-6 usage contexts
P09  Spec Comparison Table (参数对比) — vs competitors or older models
P10  Certifications (认证背书)       — CE/FDA/ISO/LFGB/CNAS/etc.
P11  Customer Cases (案例展示)       — Social proof, UGC, KOL
P12  Packaging Reveal (包装展示)     — Unboxing experience preview
P13  Tech Specs Table (规格表)       — Dense parameter listing
P14  FAQ (常见问题)                  — Objection handling
P15  Brand Story (品牌介绍)         — Company background, scale
P16  Bottom CTA (底部行动号召)       — Final purchase push + guarantee info
P17+ Supplementary (补充模块)        — Shipping, warranty, accessories as needed
```

## Visual System for International Brand Style

### Color Palette
```
Background:    #0A0A0A (deep void) or #FFFFFF (pure white)
Surface:       #141414 / #1C1C1A (card backgrounds)
Border:        #2A2A2A
Primary text:  #FFFFFF or #0A0A0A
Secondary:     #A1A1AA
Muted:         #71717A
Accent:        [Brand orange #E85D04 or product-specific color]
```

### Typography (International Brand Style)
```
Chinese: 思源黑体 (Source Han Sans) Heavy / Regular
English: Helvetica Neue / DIN Pro / Neue Haas Grok
Sizes:   Hero 56px, Section 36px, Title 24px, Body 14-16px, Caption 12px
Spacing: Generous whitespace between sections (60-100px)
```

### Composition Rules
- Product at 30-45° angle, never flat lay
- Radial gradient backgrounds for Hero (spotlight effect)
- Large drop-shadow on product as if floating
- Minimal text on Hero: brand + product name + one-line tagline
- One primary CTA button, accent-colored

## HTML Prototype Architecture

Produce a single self-contained `index.html` with:

- Embedded CSS using CSS custom properties for the entire palette
- Modular section structure (each P01-Pnn is a `<section>`)
- Responsive container (max-width 750px for mobile-first)
- Real imagery via `file:///` paths or local copies
- Professional Chinese typography via system font stack
- Smooth scroll, clean section dividers
- Copy real product images to a local directory next to the HTML for portability

### File Structure for Delivery
```
Project/
├── index.html          (main prototype)
├── hero.png            (copied key image)
├── screenshot_01.png   (optional preview images)
└── README.md           (brief usage notes)
```

## Multi-Platform Export Notes

When reporting output to the user, note the platform-specific requirements:

| Platform | Width | Max Image Size | Format | Notes |
|----------|-------|----------------|--------|-------|
| 淘宝/天猫 | 750px | 200KB/image | JPG/WebP | Long image mode, < 2MB total |
| 拼多多 | 750px | 150KB/image | JPG | Strict "no floating elements" policy |
| 1688 | 750-1920px | Variable | JPG | Supports wider layouts, B2B richer content |
| 抖店 | 750px | 200KB/image | JPG | Video modules interleaved, short-video priority |
| International | 1920px | 500KB/image | WebP | Scroll-heavy, minimal decoration mode |

Common constraints:
- No competitor platform logos or names in images
- No "best," "first," superlative claims (广告法 compliance)
- Price display must match SKU selection state
- All claims must be backed by visible certificates/evidence

## Production: From HTML Prototype to Platform-Ready PNG

The deliverable users actually want is the finished image set, not the HTML. Two production paths exist; pick based on user intent:

### Path A: Pillow Direct Image Generation (Python script → JPG/PNG)

USE THIS when the user says "要生成图片/图案，不要HTML" or "不是做成html单文件上". Pillow produces real image files directly with zero browser dependency, full typography control, and deterministic output. Better for text-heavy pages with precise positioning.

1. Write a Python script using `PIL.Image`, `ImageDraw`, `ImageFont`, `ImageFilter`.
2. Compose each page as an RGBA canvas, paste product images (with `trim_alpha()` for transparent PNGs), draw text blocks, cards, and decorative elements.
3. Output two sizes: 1500px (high-res archive) and 750px (platform-ready for Taobao/PDD).
4. Also merge all pages into a single long image for direct upload.

**Pillow-specific color/typography toolkit:**

```python
# Windows fonts for Chinese premium typography
FONT_CN = Path(r"C:\Windows\Fonts\msyh.ttc")       # 微软雅黑 Regular
FONT_CN_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc") # 微软雅黑 Bold
FONT_EN = Path(r"C:\Windows\Fonts\segoeuisl.ttf")   # Segoe UI Semilight (Apple-like)
FONT_EN_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")  # Segoe UI Bold

# Premium palettes
GOLD = "#C8A45C"     # Warm gold accent (replaces orange for more premium feel)
TEAL = "#3DD6C8"     # Tech accent for callouts
BG_DARK_TOP = "#080C10"   # Deep obsidian
BG_DARK_BOT = "#131A22"   # Rich charcoal
```

**Product glow effect (Apple-style hero lighting):**
```python
def glow_ellipse(canvas, center, rx, ry, color, opacity=60):
    # Multi-layer soft radial glow behind product
    for i in range(8):
        r, alpha = rx*2 - i*(rx//8), opacity - i*6
        if alpha <= 0: break
        draw.ellipse(…, fill=rgb(color)+(alpha,))
    return glow.filter(ImageFilter.GaussianBlur(35))
```

**Alternating dark/light theme for visual rhythm:**
- Odd pages (Hero, Structure, Lightweight, Compatibility, Scenarios, Components): dark background
- Even pages (Why, Details, Adjustment, Usage, Specs, CTA): light background
- This creates breathing room and prevents visual fatigue on long scroll

**Pitfall: Chinese quotes in Python strings.** `"万能适配"` (U+201C/U+201D curly quotes inside a `"`-delimited Python string) causes `SyntaxError: invalid syntax`. Replace with corner brackets: `「万能适配」`.

- **Chinese quote pitfall**: `"看起来差不多"` in Python strings caused SyntaxError; replaced with `「看起来差不多」`.

**Starter template:** `templates/pillow_detail_page.py` — copy and fill in your product pages. Contains all helper functions (gradient_v, shadow, glow_ellipse, rounded, text_block, section_header) ready to use.

### Path B: HTML Prototype → Puppeteer Screenshot (original pipeline)

When PSD editing is **not available** (binary PSD/PSB can't be opened by the agent, or Photoshop is the user's tool only), render the HTML prototype directly to PNG with a headless browser. This produces shop-ready 750px-wide detail-page slices and a full long-image — visually equivalent to a PSD export, and far faster to iterate.

### Why this path
- The user's PSD/PSB files (often 100-900MB) live on disk but the agent cannot edit binary Photoshop layers. Past attempts to "open the PSB and rearrange" stall. Instead: build the design once as HTML/CSS, screenshot it, hand over PNGs. The user can still open the original PSD in Photoshop for final pixel retouching if needed.
- Iteration is instant: edit CSS/HTML → re-run the screenshot script → new PNGs. No manual Photoshop comping.

### Screenshot pipeline (Windows / git-bash environment)
Use `puppeteer-core` (NOT full `puppeteer` — the full package is often not installed globally and NODE_PATH does not reliably resolve under git-bash). Steps that worked:

1. `cd` into the prototype directory, then `npm install puppeteer-core` (lightweight, no Chrome download).
2. Point `executablePath` at the Chrome already cached by the anygen/Puppeteer setup:
   `C:/Users/win10/.cache/puppeteer/chrome/win64-150.0.7871.24/chrome-win64/chrome.exe`
   (Verify with `ls` first; version folder may differ.)
3. Render at `deviceScaleFactor: 2` and viewport width `750` for crisp 1500px-wide output.
4. Capture `fullPage: true` for the long image, AND loop `page.$$('.section, .hero, .full-img, .brand-block, .cta-block, .footer-block')` to screenshot each block as a separate upload-ready slice (P01.png…Pnn.png).
5. Set `args: ['--no-sandbox','--disable-setuid-sandbox','--disable-gpu','--force-color-profile=srgb']`.

Working script: `scripts/render_detail_page.js` (copy into the prototype folder, edit the 3 constants at top, run `node render_detail_page.js`).

### Output structure
```
成品图/
├── 第六代手动压盖机_详情页_全图.png   (12MB full long-image, direct upload)
├── P01.png … P17.png                  (per-module slices, single upload)
```
Verify output with a Node one-liner reading PNG IHDR (width at byte 16, height at byte 20) — confirms every slice rendered and images loaded (a very tall slice = stacked real photos present).

### Pitfall: vision_analyze unavailable on text-only providers
The deepseek provider (and any text-only LLM) rejects ALL vision_analyze calls — not just large files — with `unknown variant image_url, expected text`. This means zero images can be visually inspected during the session. Workaround: verify renders via PNG-header dimensions + file sizes only (see Verification below). If visual QA is essential and another vision-capable provider is configured, switch to it before calling vision_analyze; otherwise rely on the dimension/size check.

## Workflow

1. **Inventory** — Catalog all local assets across all drives
2. **Triaging** — Help user pick style direction (A/B/C)
3. **Planning** — Confirm module sequence (P01-Pnn)
4. **System** — Define colors/type/spacing
5. **Build** — Create `index.html` prototype, copy images locally
6. **Produce** — Run `render_detail_page.js` → `成品图/` PNG set (full + slices)
7. **Verify** — PNG-header dims + file sizes; optional low-res JPEG for vision QA
8. **Report** — Asset inventory + PNG paths + platform notes

## Output Template

```
创建了: /path/to/index.html（视觉原型，含 P01-Pnn 共 N 屏）
素材来源: E:/封盖机AI效果图/..., F:/美工工作文件/...
风格方向: A-国际品牌感（对标 Apple/MUJI/Dyson）
适用范围: 淘宝750px / 1688全宽 / 拼多多750px

下一步:
- 确认原型方向后，在 PSD 里替换为最终精修产品图
- 按平台导出对应尺寸（TB 750px / PDD 750px / 1688 1920px）
- SEO关键词优化标题和详情文案
```

## Pitfalls

- **Don't invent product specs.** Always pull from existing spec sheets, brand docs, or product manuals found locally.
- **Don't skip the asset inventory.** Existing PSDs, AI renders, and 3D files save hours of recreation. Always search first.
- **Don't design in isolation.** Show the user the 3 style directions with concrete visual examples (hero image comparison) before full build.
- **Don't use stock placeholder copy.** Use real brand copy, product descriptions, or mark `[文案待补]` for anything missing.
- **Don't ignore platform compliance.** Chinese e-commerce has specific rules about superlatives, competitor mentions, and price display. Flag any risky claims.
- **Remember: AI renders are early-stage direction tools, not final assets.** They define mood, composition, and color grading but must be replaced with real photography + retouching for production.
- **PSD/PSB are NOT agent-editable.** Users say "对着 第六代手动.psb 改" but the agent cannot open binary Photoshop layers. Do NOT promise to edit the PSB. Instead build the design as HTML/CSS and render to PNG (see Production section) — this is the real deliverable. If pixel-perfect Photoshop retouching is required, deliver the PNGs + HTML as the brief for the user's manual PSD pass.
- **Don't rely on NODE_PATH under git-bash on Windows.** It does not reliably resolve global modules. Install `puppeteer-core` locally in the prototype folder instead (see Production section).
- **npm init fails on directories with Chinese characters.** `npm init -y` rejects project dirs containing CJK characters with "Invalid name". Workaround: write a minimal `package.json` manually via `write_file` (`{"name":"...","version":"1.0.0","private":true}`) before `npm install`.

## Session References

Session-specific details, asset inventories, and reproduction notes from actual jobs:

- `references/neze-6th-gen-manual-capper.md` — NEZE 第六代手动压盖机 upgrade (2026-07): 6GB PSD sources, 200+ AI renders across 4 drives, 3D SLDPRT/STEP/SolidWorks, product photos, certifications, brand collateral. Full modular 15-screen HTML prototype with Apple/MUJI-style minimalist system. Multi-platform 淘宝/1688/拼多多/抖店 export notes + 广告法 compliance checklist.

