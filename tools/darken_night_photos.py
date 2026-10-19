"""Darken the night-variant background photos so they stay dim on a TV in a dark room.
Reduces brightness to ~45% and nudges contrast up slightly so shapes stay readable.
"""
import pathlib
from PIL import Image, ImageEnhance

DIR = pathlib.Path(r"C:\Users\User\Documents\fire-tv-cleanup\launcher\app\src\main\res\drawable-nodpi")
BRIGHTNESS = 0.45
CONTRAST = 1.08

names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
for name in names:
    src = DIR / f"bg_{name}_night.jpg"
    img = Image.open(src).convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(BRIGHTNESS)
    img = ImageEnhance.Contrast(img).enhance(CONTRAST)
    img.save(src, quality=88)
    print(f"darkened {src.name}")
