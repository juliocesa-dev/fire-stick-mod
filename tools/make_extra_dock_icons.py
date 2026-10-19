"""Draw square dock icons for Crunchyroll and HBO Max, matching the style of make_dock_icons.py
(flat color squircle tile, simplified mark - not a pixel trace of the trademarked logo).

Usage:
    tools/iconvenv/Scripts/python.exe -I tools/make_extra_dock_icons.py \
        launcher/app/src/main/res/drawable-nodpi launcher/app/src/main/res/font/open_sans.ttf
"""
import sys, pathlib
from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path(sys.argv[1])
FONT = sys.argv[2]
S, K = 256, 4
B = S * K
R = int(B * 0.225)


def canvas():
    return Image.new("RGBA", (B, B), (0, 0, 0, 0))


def shape_mask():
    m = Image.new("L", (B, B), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, B - 1, B - 1], R, fill=255)
    return m


def fill(color):
    img = canvas()
    img.paste(Image.new("RGBA", (B, B), color), (0, 0), shape_mask())
    return img


def vgradient(top, bottom):
    g = Image.new("RGBA", (1, B))
    for y in range(B):
        t = y / (B - 1)
        g.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,))
    img = canvas()
    img.paste(g.resize((B, B)), (0, 0), shape_mask())
    return img


def save(img, name):
    img.resize((S, S), Image.LANCZOS).save(OUT / name)


def centered_text(img, text, font_path, color, target_w_ratio):
    size = int(B * 0.5)
    font = ImageFont.truetype(font_path, size)
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    scale = (target_w_ratio * B) / w
    font = ImageFont.truetype(font_path, int(size * scale))
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((B - w) / 2 - bbox[0], (B - h) / 2 - bbox[1]), text, font=font, fill=color)


# Crunchyroll: brand orange tile, bold white "CR" monogram
img = fill((244, 117, 33, 255))
centered_text(img, "CR", FONT, (255, 255, 255, 255), 0.60)
save(img, "dock_crunchyroll.png")

# HBO Max: deep purple gradient tile, white "max" wordmark
img = vgradient((78, 36, 157), (40, 14, 90))
centered_text(img, "max", FONT, (255, 255, 255, 255), 0.72)
save(img, "dock_hbomax.png")

print("wrote dock_crunchyroll.png, dock_hbomax.png to", OUT)
