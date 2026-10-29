"""R12 rev. 8.2 textures: red majlis kilim (moodboard floor seating), mother-of-pearl inlay for the octagonal tent table.
Usage: python3 textures82.py"""
import os, math
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'tex2')
__file__ = os.path.join(HERE, 'textures8.py'); exec(open(os.path.join(HERE, 'textures8.py')).read().split("if __name__")[0])

def majlis(N=128):
    """cushion-sized kilim tile (one medallion per tile): red ground, black + ivory stepped diamond, small hooked stars, side stripes"""
    RED, DK, IV, GR, OR = (150, 22, 24), (30, 18, 16), (226, 210, 178), (40, 92, 60), (200, 110, 40)
    im = Image.new('RGB', (N, N), RED); d = ImageDraw.Draw(im); c = N / 2
    for x0, col in ((0, DK), (5, IV), (8, DK)):
        d.rectangle((x0, 0, x0 + 2, N), fill=col); d.rectangle((N - x0 - 3, 0, N - x0 - 1, N), fill=col)
    for k, (r, col) in enumerate(((44, DK), (38, IV), (33, RED), (27, DK), (20, OR), (13, IV), (7, DK))):
        pts = []
        for i in range(4 * r // 3 + 1):                                               # stepped (woven) diamond outline
            pass
        d.polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=col)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = c + sx * 46, c + sy * 46
            d.polygon([(x, y - 7), (x + 7, y), (x, y + 7), (x - 7, y)], fill=IV); d.rectangle((x - 2, y - 2, x + 2, y + 2), fill=GR)
    return np.asarray(im)

def inlay(N=1024):
    """walnut top with mother-of-pearl: 8-point star rosette, girih ring, border band"""
    S_ = 2; M = N * S_; im = Image.new('RGB', (M, M), (70, 40, 22)); d = ImageDraw.Draw(im); c = M / 2
    MOP, MOP2, BR = (236, 228, 214), (206, 214, 222), (184, 140, 64)
    def star(r, rot, col):
        pts = []
        for k in range(16):
            a = rot + math.pi * k / 8; rr = r if k % 2 == 0 else r * 0.72
            pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
        d.polygon(pts, fill=col)
    for r, col in ((0.47, BR), (0.455, (70, 40, 22)), (0.44, MOP2), (0.425, (70, 40, 22))):
        d.ellipse((c - r * M, c - r * M, c + r * M, c + r * M), fill=col)
    for k in range(16):
        a = math.pi * k / 8; x, y = c + 0.34 * M * math.cos(a), c + 0.34 * M * math.sin(a); r = 0.055 * M
        d.polygon([(x + r * math.cos(a + j * math.pi / 2), y + r * math.sin(a + j * math.pi / 2)) for j in range(4)], fill=MOP if k % 2 else MOP2)
    star(0.27 * M, 0, MOP); star(0.2 * M, math.pi / 8, (70, 40, 22)); star(0.16 * M, 0, MOP2); star(0.09 * M, math.pi / 8, BR)
    d.ellipse((c - 0.03 * M, c - 0.03 * M, c + 0.03 * M, c + 0.03 * M), fill=MOP)
    a = np.asarray(im.resize((N, N), Image.LANCZOS), np.float32) * (1 + np.random.default_rng(3).normal(0, 0.03, (N, N)))[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

if __name__ == '__main__':
    flatweave(majlis(), 6, 5, 31).save(os.path.join(OUT, 'majlis_kilim.png'))
    inlay().save(os.path.join(OUT, 'octa_inlay.png')); print('ok')
