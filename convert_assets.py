"""
One-time script to convert .jfif images to .png and copy them to assets/.
Run: python convert_assets.py
"""
import os
from PIL import Image

os.makedirs("assets", exist_ok=True)

mapping = {
    "Rice.jfif":    "assets/rice.png",
    "EGGS.jfif":    "assets/egg.png",
    "chicken.jfif": "assets/chicken.png",
    "beef.jfif":    "assets/beef.png",
    "fish.jfif":    "assets/fish.png",
}

for src, dst in mapping.items():
    if os.path.exists(src):
        img = Image.open(src).convert("RGBA")
        img.save(dst, "PNG")
        print(f"Converted {src} -> {dst}")
    else:
        print(f"WARNING: {src} not found, skipping.")

print("Done.")
