"""
Pillow E-Commerce Detail Page Generator — Template
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use when user says "要生成图片，不要HTML" for Taobao/PDD/1688 detail pages.
Copy this skeleton, replace placeholders, fill in page_01()…page_NN().

Requires: pip install Pillow
Fonts on Windows: msyh.ttc, msyhbd.ttc, segoeuisl.ttf, segoeuib.ttf
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

# ── Project paths ──────────────────────────
ROOT = Path(__file__).resolve().parents[1]   # material pack root
OUT = ROOT / "output" / "PROJECT_详情页"
OUT_1500 = OUT / "1500px_高清版"
OUT_750 = OUT / "750px_平台版"

WIDTH = 1500
MARGIN = 120      # breathing room

# ── Premium colors ─────────────────────────
GOLD = "#C8A45C"       # warm accent
TEAL = "#3DD6C8"       # tech accent
BG_DARK_TOP = "#080C10"
BG_DARK_BOT = "#131A22"
SURFACE_DARK = "#1A2129"
BG_LIGHT = "#F7F8FA"
SURFACE_LIGHT = "#FFFFFF"
TEXT_DARK = "#EEF1F5"
TEXT_DARK_MUTED = "#8899A6"
TEXT_LIGHT = "#1A1E25"
TEXT_LIGHT_MUTED = "#6B7785"

# ── Windows fonts ──────────────────────────
FONT_CN = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_CN_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
FONT_EN_LIGHT = Path(r"C:\Windows\Fonts\segoeuisl.ttf")
FONT_EN_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")

# ═══════════════════════════════════════════
# HELPER FUNCTIONS (copy these verbatim)
# ═══════════════════════════════════════════

def rgb(hex_str: str) -> tuple[int, int, int]:
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def cn_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_CN_BOLD if bold else FONT_CN), size)

def en_font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    path = FONT_EN_BOLD if weight == "bold" else FONT_EN_LIGHT
    return ImageFont.truetype(str(path), size)

def load(path: Path) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(path)).convert("RGBA")

def trim_alpha(img: Image.Image) -> Image.Image:
    bbox = img.convert("RGBA").getchannel("A").getbbox()
    return img.crop(bbox) if bbox else img

def contain(img: Image.Image, size: tuple) -> Image.Image:
    img = img.copy(); img.thumbnail(size, Image.Resampling.LANCZOS); return img

def cover(img: Image.Image, size: tuple, fy: float = 0.5) -> Image.Image:
    scale = max(size[0]/img.width, size[1]/img.height)
    img = img.resize((round(img.width*scale), round(img.height*scale)), Image.Resampling.LANCZOS)
    top = round(max(0, img.height-size[1]) * min(1, max(0, fy)))
    return img.crop((max(0, (img.width-size[0])//2), top, max(0, (img.width-size[0])//2)+size[0], top+size[1]))

def rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,img.width,img.height), radius=radius, fill=255)
    result = img.convert("RGBA"); result.putalpha(mask); return result

def gradient_v(size: tuple, top_hex: str, bottom_hex: str) -> Image.Image:
    top, bottom = rgb(top_hex), rgb(bottom_hex)
    strip = Image.new("RGB", (1, size[1]))
    denom = max(1, size[1]-1)
    strip.putdata([tuple(round(top[i]*(1-y/denom)+bottom[i]*y/denom) for i in range(3)) for y in range(size[1])])
    return strip.resize(size)

def shadow(canvas, layer, xy, blur=40, opacity=80, offset=(0,24)):
    layer = layer.convert("RGBA")
    alpha = layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v*opacity//255)
    shadow_img = Image.new("RGBA", layer.size, (0,0,0,0)); shadow_img.putalpha(alpha)
    canvas.alpha_composite(shadow_img, (xy[0]+offset[0], xy[1]+offset[1]))
    canvas.alpha_composite(layer, xy)

def glow_ellipse(canvas, center, rx, ry, color, opacity=60):
    """Apple-style product glow. Place before pasting product."""
    gs = (rx*4, ry*4)
    glow = Image.new("RGBA", gs, (0,0,0,0)); draw = ImageDraw.Draw(glow)
    for i in range(8):
        r, a = rx*2-i*(rx//8), opacity-i*6
        if a <= 0: break
        draw.ellipse((gs[0]//2-r, gs[1]//2-ry*2+i*(ry//8), gs[0]//2+r, gs[1]//2+ry*2-i*(ry//8)), fill=rgb(color)+(a,))
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    canvas.alpha_composite(glow, (center[0]-gs[0]//2, center[1]-gs[1]//2))

def text_block(draw, xy, text, font, fill, max_width, line_spacing=12) -> int:
    """Draw wrapped text; returns bottom Y."""
    y = xy[1]
    for para in text.split("\n"):
        if not para: y += line_spacing; continue
        cur = ""
        for ch in para:
            cand = cur + ch
            if cur and draw.textbbox((0,0), cand, font=font)[2] > max_width:
                draw.text((xy[0], y), cur.rstrip(), font=font, fill=fill)
                y += draw.textbbox((xy[0], y), cur or "口", font=font)[3] - draw.textbbox((xy[0], y), cur or "口", font=font)[1] + line_spacing
                cur = ch.lstrip()
            else: cur = cand
        if cur:
            draw.text((xy[0], y), cur, font=font, fill=fill)
            y += draw.textbbox((xy[0], y), cur or "口", font=font)[3] - draw.textbbox((xy[0], y), cur or "口", font=font)[1] + line_spacing
    return y

def fit_text(text, max_width, start, minimum, bold=False):
    probe = ImageDraw.Draw(Image.new("RGB", (10,10)))
    for sz in range(start, minimum-1, -2):
        f = cn_font(sz, bold)
        if probe.textbbox((0,0), text, font=f)[2] <= max_width: return f
    return cn_font(minimum, bold)

def page_footer(canvas, page_num, dark=True):
    draw = ImageDraw.Draw(canvas)
    fill = "#5A6975" if dark else "#9BA5B0"
    y = canvas.height - 66
    draw.line((MARGIN, y-14, WIDTH-MARGIN, y-14), fill=fill, width=1)
    draw.text((MARGIN, y+6), "BRAND · PRODUCT", font=en_font(18), fill=fill, anchor="ls")
    draw.text((WIDTH-MARGIN, y+6), f"{page_num:02d}", font=en_font(20, "regular"), fill=fill, anchor="rs")

def section_header(canvas, kicker_en, title_cn, subtitle, dark, y=100) -> int:
    """Draw refined section header. Returns Y after block."""
    draw = ImageDraw.Draw(canvas)
    accent = GOLD; main = TEXT_DARK if dark else TEXT_LIGHT
    muted = TEXT_DARK_MUTED if dark else TEXT_LIGHT_MUTED
    draw.text((MARGIN, y), kicker_en.upper(), font=en_font(22, "regular"), fill=accent)
    tf = fit_text(title_cn, WIDTH-MARGIN*2, 64, 46, bold=True)
    draw.text((MARGIN, y+42), title_cn, font=tf, fill=main)
    return text_block(draw, (MARGIN, y+130), subtitle, cn_font(25), muted, WIDTH-MARGIN*2, 10) + 80


# ═══════════════════════════════════════════
# PAGES — fill in with your product
# ═══════════════════════════════════════════

def page_01() -> Image.Image:
    """Hero — product center stage with dramatic lighting"""
    h = 2000
    page = gradient_v((WIDTH, h), BG_DARK_TOP, BG_DARK_BOT).convert("RGBA")
    draw = ImageDraw.Draw(page)

    # Glow behind product
    glow_ellipse(page, (WIDTH//2, 700), 340, 280, GOLD, 35)

    # TODO: load and paste product
    # prod = contain(trim_alpha(load(ROOT / "product_transparent.png")), (880, 1050))
    # shadow(page, prod, ((WIDTH-prod.width)//2, 250), blur=50, opacity=100)

    # Brand + title
    draw.text((MARGIN, 85), "BRAND", font=en_font(26, "regular"), fill=GOLD)
    draw.text((WIDTH//2, 1120), "产品名称", font=cn_font(96, bold=True), fill=TEXT_DARK, anchor="mt")

    # Stats bar
    stats = [("STAT", "LABEL"), ("STAT", "LABEL"), ("STAT", "LABEL")]
    sx = MARGIN
    for val, lbl in stats:
        draw.text((sx, 1590), val, font=cn_font(46, bold=True), fill=TEXT_DARK)
        draw.text((sx, 1660), lbl, font=cn_font(24), fill=TEXT_DARK_MUTED)
        sx += 370

    page_footer(page, 1, dark=True)
    return page


def page_02() -> Image.Image:
    """Feature cards — 4 reasons to buy (light theme)"""
    h = 1800
    page = Image.new("RGBA", (WIDTH, h), rgb(BG_LIGHT)+(255,))
    draw = ImageDraw.Draw(page)
    section_header(page, "WHY", "标题文案", "副标题描述。", dark=False, y=90)

    # TODO: 4 feature cards in 2x2 grid
    for i, (num, title, body) in enumerate([
        ("01", "特性一", "描述文字"),
        ("02", "特性二", "描述文字"),
    ]):
        x = MARGIN + (i % 2) * 630
        y = 420 + (i // 2) * 410
        card_w, card_h = 570, 330
        shadow(page, Image.new("RGBA", (card_w, card_h), rgb(SURFACE_LIGHT)+(255,)), (x,y), blur=18, opacity=40, offset=(0,8))
        draw.rounded_rectangle((x, y, x+card_w, y+card_h), radius=28, fill=SURFACE_LIGHT, outline="#E2E6EA", width=1)
        draw.text((x+40, y+42), num, font=en_font(32, "regular"), fill=TEAL)
        draw.text((x+40, y+100), title, font=cn_font(38, bold=True), fill=TEXT_LIGHT)
        text_block(draw, (x+40, y+170), body, cn_font(24), TEXT_LIGHT_MUTED, card_w-80, 10)

    page_footer(page, 2, dark=False)
    return page


# ═══════════════════════════════════════════
# RENDER PIPELINE (don't modify)
# ═══════════════════════════════════════════

def save_page(img: Image.Image, index: int) -> tuple[Path, Path]:
    fname = f"DETAIL_{index:02d}.jpg"
    rgb_img = img.convert("RGB")
    p1500 = OUT_1500 / fname; p1500.parent.mkdir(parents=True, exist_ok=True)
    rgb_img.save(p1500, quality=94, subsampling=0, optimize=True)
    p750 = OUT_750 / fname; p750.parent.mkdir(parents=True, exist_ok=True)
    resized = rgb_img.resize((750, round(rgb_img.height*0.5)), Image.Resampling.LANCZOS)
    resized.save(p750, quality=92, subsampling=0, optimize=True)
    return p1500, p750

def merge_long(pages, width, out_path, quality=93):
    converted = [p.convert("RGB") for p in pages]
    total_h = sum(p.height for p in converted)
    long_img = Image.new("RGB", (width, total_h), "white")
    y = 0
    for img in converted: long_img.paste(img, (0,y)); y += img.height
    long_img.save(out_path, quality=quality, subsampling=0, optimize=True)

def main():
    pages = [page_01(), page_02()]  # add more pages
    for i, p in enumerate(pages, 1):
        p1500, _ = save_page(p, i)
        print(f"  ✓ Page {i:02d} — {p1500.name} ({p.width}×{p.height})")
    merge_long(pages, 1500, OUT_1500 / "FULL_LONG.jpg", 93)
    merge_long(pages, 750, OUT_750 / "FULL_LONG_750.jpg", 91)
    print(f"\n✅ {len(pages)} pages rendered to {OUT}")

if __name__ == "__main__":
    main()
