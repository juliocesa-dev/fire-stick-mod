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

src = Image.open(SRC).convert("RGBA").resize((B, B), Image.LANCZOS)
mask = Image.new("L", (B, B), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, B - 1, B - 1], R, fill=255)
out = Image.new("RGBA", (B, B), (0, 0, 0, 0))
out.paste(src, (0, 0), mask)
out.resize((S, S), Image.LANCZOS).save(OUT / "dock_prime.png")
print("wrote dock_prime.png to", OUT)
