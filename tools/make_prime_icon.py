"""Draw a square Prime Video dock icon: Amazon's smile swoosh on the blue tile, no wordmark
(avoids cairosvg/cairo, which don't install cleanly on Windows, and avoids text clipping at
this tile size). Matches the style of make_dock_icons.py (squircle tile, supersampled).

Usage:
    tools/iconvenv/Scripts/python.exe -I tools/make_prime_icon.py launcher/app/src/main/res/drawable-nodpi
"""
import sys, pathlib, math
from PIL import Image, ImageDraw

OUT = pathlib.Path(sys.argv[1])
S, K = 256, 4
B = S * K
R = int(B * 0.225)


def canvas():
    return Image.new("RGBA", (B, B), (0, 0, 0, 0))


def shape_mask():
    m = Image.new("L", (B, B), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, B - 1, B - 1], R, fill=255)
    return m


def vgradient(top, bottom):
    g = Image.new("RGBA", (1, B))
    for y in range(B):
        t = y / (B - 1)
        g.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,))
    img = canvas()
    img.paste(g.resize((B, B)), (0, 0), shape_mask())
    return img


img = vgradient((31, 168, 236), (0, 120, 200))
d = ImageDraw.Draw(img)

# The smile: a shallow arc from lower-left to lower-right of a centred band, line width proportional
# to canvas size, rounded caps via overlapping circles at each sampled point.
cx, cy = 0.5 * B, 0.60 * B
rx, ry = 0.30 * B, 0.17 * B
start_deg, end_deg = 200, 340   # bottom arc of the ellipse, a gentle smile
width = int(0.065 * B)
points = []
steps = 1200
for i in range(steps + 1):
    t = start_deg + (end_deg - start_deg) * i / steps
    rad = math.radians(t)
    x = cx + rx * math.cos(rad)
    y = cy + ry * math.sin(rad)
    points.append((x, y))
# Stamp overlapping circles along the path: a perfectly smooth stroke, no segment seams.
r = width / 2
for (x, y) in points:
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))

# The arrowhead at the right end, Amazon-orange, pointing up and to the right.
ex, ey = points[-1]
ang = math.radians(end_deg + 90)  # tangent direction at the end, rotated to point outward/up
head = 0.075 * B
p1 = (ex, ey)
p2 = (ex - head * math.cos(ang - math.radians(28)), ey - head * math.sin(ang - math.radians(28)))
p3 = (ex - head * math.cos(ang + math.radians(28)), ey - head * math.sin(ang + math.radians(28)))
d.polygon([p1, p2, p3], fill=(255, 153, 0, 255))

# "video" wordmark, small and safely inset, under the smile - short enough it never clips.
from PIL import ImageFont
font_path = sys.argv[2] if len(sys.argv) > 2 else None
if font_path:
    size = int(B * 0.17)
    font = ImageFont.truetype(font_path, size)
    text = "video"
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    max_w = 0.80 * B
    if w > max_w:
        font = ImageFont.truetype(font_path, int(size * max_w / w))
        bbox = d.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    ty = 0.74 * B
    d.text(((B - w) / 2 - bbox[0], ty - bbox[1]), text, font=font, fill=(255, 255, 255, 255))

img.resize((S, S), Image.LANCZOS).save(OUT / "dock_prime.png")
print("wrote dock_prime.png to", OUT)
