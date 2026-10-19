"""Bake the real Prime Video icon (captured via AppAdapter's debug export, which renders it with
Drawable.draw() at fixed square bounds - no ImageView centerCrop scaling quirk) into a squircle dock
tile PNG, matching the style of the hand-drawn icons.

Usage:
    tools/iconvenv/Scripts/python.exe -I tools/bake_prime_icon.py prime_icon_debug.png \
        launcher/app/src/main/res/drawable-nodpi
"""
import sys, pathlib
from PIL import Image, ImageDraw

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
S, K = 256, 4
B = S * K
R = int(B * 0.225)
SCALE = 0.68   # shrink the wordmark+smile well below full-bleed so it has real breathing room
LOGO_COLOR = (64, 196, 255)   # the light Prime blue used on the current dark app icon
BG = (10, 16, 26)             # near-black, matching the current Prime Video app icon


def shape_mask():
    m = Image.new("L", (B, B), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, B - 1, B - 1], R, fill=255)
    return m


def fill(color):
    img = Image.new("RGBA", (B, B), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (B, B), color + (255,)), (0, 0), shape_mask())
    return img


# Isolate the wordmark+smile from the captured icon (white on a blue gradient): anything close to white
# becomes opaque logo-colour, everything else becomes transparent, so it composites cleanly onto a fresh
# dark tile with no seam, matching the current Prime Video app icon style.
src = Image.open(SRC).convert("RGBA").resize((B, B), Image.LANCZOS)
px = src.load()
logo = Image.new("RGBA", (B, B), (0, 0, 0, 0))
lpx = logo.load()
for y in range(B):
    for x in range(B):
        r, g, b, a = px[x, y]
        whiteness = min(r, g, b)   # 255 on pure white, lower near the blue background
        if whiteness > 120:
            alpha = int(255 * min(1.0, (whiteness - 120) / 80))
            lpx[x, y] = LOGO_COLOR + (alpha,)

logo_small = logo.resize((int(B * SCALE), int(B * SCALE)), Image.LANCZOS)
out = fill(BG)
off = (B - logo_small.width) // 2
out.alpha_composite(logo_small, (off, off))
out.resize((S, S), Image.LANCZOS).save(OUT / "dock_prime.png")
print("wrote dock_prime.png to", OUT)
