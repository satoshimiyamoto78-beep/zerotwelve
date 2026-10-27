"""Pierced-brass lantern sheet (refs: Moroccan pierced brass pendants / lanterns): black = brass, warm white = holes, coloured = glass jewels.
Rosette per cell: 8-point star cut-out (some with a coloured jewel), radial slots, a ring of drilled dots, dotted cell borders, corner stars."""
import os, math, random
from PIL import Image, ImageDraw
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex2'); R = random.Random(9)
N = 2048; P = N // 4; im = Image.new('RGB', (N, N), (0, 0, 0)); d = ImageDraw.Draw(im); H = (255, 214, 150)
J = [(220, 20, 30), (20, 170, 70), (240, 150, 20), (30, 80, 220)]
def pol(cx, cy, r, a): return (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
def dot(x, y, r, c=H): d.ellipse([x - r, y - r, x + r, y + r], fill=c)
for i in range(4):
    for j in range(4):
        cx, cy = (i + 0.5) * P, (j + 0.5) * P
        d.polygon([pol(cx, cy, 0.19 * P if k % 2 == 0 else 0.09 * P, k * 22.5) for k in range(16)], fill=H)
        if (i * 4 + j) % 3 == 1: dot(cx, cy, 0.075 * P, J[(i + 2 * j) % 4])
        else: d.polygon([pol(cx, cy, 0.05 * P, k * 45) for k in range(8)], fill=(0, 0, 0))
        for k in range(8):                                                       # radial slots
            a = k * 45 + 22.5; p0, p1 = pol(cx, cy, 0.215 * P, a), pol(cx, cy, 0.30 * P, a)
            d.line([p0, p1], fill=H, width=int(0.024 * P)); dot(*p1, 0.012 * P); dot(*p0, 0.012 * P)
        for k in range(16): dot(*pol(cx, cy, 0.37 * P, k * 22.5), 0.02 * P)     # drilled ring
        for k in range(32): dot(*pol(cx, cy, 0.44 * P, k * 11.25), 0.011 * P)
for i in range(5):
    for j in range(5):
        cx, cy = i * P, j * P
        d.polygon([pol(cx, cy, 0.09 * P if k % 2 == 0 else 0.035 * P, k * 45) for k in range(8)], fill=H)
        for k in range(1, 8):
            if k != 4: dot(cx + k * P / 8, cy, 0.01 * P); dot(cx, cy + k * P / 8, 0.01 * P)
im = im.resize((1024, 1024), Image.LANCZOS); im.save(os.path.join(OUT, 'piercedbrass.png')); print('piercedbrass', im.size)
