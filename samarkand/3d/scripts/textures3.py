"""Texture set 3 (R12 client renders): richer carpets (Bukhara gul, Persian medallion, suzani rosettes, kilim runner),
Rishtan plate, quilted suzani patchwork, turquoise dome glaze, lime plaster, rattan weave, plov, lepyoshka.
Usage: python3 textures3.py OUTDIR"""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]; R = random.Random(5)
RED, DRED, IND, NAVY, CRE, GOLD, TUR, LAP, IVORY, GRN, OCH = (150, 28, 34), (96, 18, 24), (34, 38, 92), (22, 26, 58), (236, 222, 196), (214, 160, 60), (44, 160, 168), (30, 62, 140), (244, 236, 220), (46, 98, 70), (196, 132, 58)
def grain(im, a=10, n=None):
    px = im.load(); w, h = im.size
    for _ in range(n or w * h // 6):
        x, y = R.randrange(w), R.randrange(h); c = px[x, y]; v = R.randint(-a, a); px[x, y] = tuple(max(0, min(255, q + v)) for q in c)
    return im
def weave(im, s=3, a=10):
    px = im.load(); w, h = im.size
    for y in range(h):
        for x in range(w):
            if (x // s + y // s) % 2: c = px[x, y]; px[x, y] = tuple(max(0, q - a) for q in c)
    return im
def star(d, cx, cy, r, fill, k=8, inner=.6, rot=0):
    d.polygon([(cx + (r if i % 2 == 0 else r * inner) * math.cos(rot + i * math.pi / k), cy + (r if i % 2 == 0 else r * inner) * math.sin(rot + i * math.pi / k)) for i in range(2 * k)], fill=fill)
def oct_(d, cx, cy, rx, ry, fill):
    d.polygon([(cx + rx * math.cos(math.pi / 8 + i * math.pi / 4), cy + ry * math.sin(math.pi / 8 + i * math.pi / 4)) for i in range(8)], fill=fill)
def dia(d, cx, cy, rx, ry, fill): d.polygon([(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)], fill=fill)
def flower(d, cx, cy, r, petal, center, n=8):
    for i in range(n):
        a = 2 * math.pi * i / n; d.ellipse([cx + r * .55 * math.cos(a) - r * .38, cy + r * .55 * math.sin(a) - r * .38, cx + r * .55 * math.cos(a) + r * .38, cy + r * .55 * math.sin(a) + r * .38], fill=petal)
    d.ellipse([cx - r * .35, cy - r * .35, cx + r * .35, cy + r * .35], fill=center)
def borders(d, W, H, specs):
    o = 0
    for wdt, col in specs: d.rectangle([o, o, W - 1 - o, H - 1 - o], outline=col, width=wdt); o += wdt
    return o
def save(im, n, blur=.6, wv=True):
    if wv: weave(im)
    grain(im).filter(ImageFilter.GaussianBlur(blur)).save(f'{out}/{n}.png')

# 1 Bukhara (Tekke) carpet: rows of guls on madder red
W, H = 768, 1152; im = Image.new('RGB', (W, H), DRED); d = ImageDraw.Draw(im)
o = borders(d, W, H, [(18, NAVY), (8, CRE), (30, RED), (8, CRE)])
for x in range(30, W, 40):
    for y in (24, H - 24): dia(d, x, y, 10, 8, CRE)
for gy in range(o + 90, H - o - 40, 170):
    for gx in range(o + 90, W - o - 40, 190):
        oct_(d, gx, gy, 80, 62, RED); oct_(d, gx, gy, 72, 54, NAVY)
        for q in range(4): d.pieslice([gx - 64, gy - 48, gx + 64, gy + 48], q * 90, q * 90 + 90, fill=[RED, CRE, RED, CRE][q])
        dia(d, gx, gy, 26, 20, NAVY); dia(d, gx, gy, 12, 9, GOLD)
    for gx in range(o + 185, W - o - 40, 190): dia(d, gx, gy + 85, 14, 22, NAVY)
save(im, 'rug_bukhara', .7)
# 2 Persian medallion carpet: indigo field, crimson medallion, floral sprigs
im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
o = borders(d, W, H, [(14, GOLD), (36, RED), (6, CRE)])
for k in range(0, H, 46):
    for x in (o // 2 + 2, W - o // 2 - 2): flower(d, x, k + 20, 12, CRE, GOLD, 6)
for _ in range(220):
    x, y = R.randrange(o + 20, W - o - 20), R.randrange(o + 20, H - o - 20); flower(d, x, y, R.randint(6, 12), [RED, CRE, TUR, GOLD][R.randrange(4)], NAVY, 6)
for s, c in ((1.0, RED), (.82, CRE), (.66, IND), (.5, RED), (.3, GOLD)):
    d.ellipse([W / 2 - 230 * s, H / 2 - 330 * s, W / 2 + 230 * s, H / 2 + 330 * s], fill=c)
star(d, W / 2, H / 2, 70, NAVY, 12, .7); flower(d, W / 2, H / 2, 40, CRE, RED, 10)
for cx, cy in ((o + 90, o + 120), (W - o - 90, o + 120), (o + 90, H - o - 120), (W - o - 90, H - o - 120)):
    d.pieslice([cx - 150, cy - 150, cx + 150, cy + 150], 0, 360, fill=RED); flower(d, cx, cy, 60, CRE, GOLD, 8)
save(im, 'rug_persian', .7)
# 3 Suzani: cream ground with big crimson rosettes and vines
S = 1024; im = Image.new('RGB', (S, S), IVORY); d = ImageDraw.Draw(im)
for cx, cy in ((256, 256), (768, 256), (256, 768), (768, 768), (512, 512), (0, 512), (1024, 512), (512, 0), (512, 1024)):
    d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=RED); d.ellipse([cx - 118, cy - 118, cx + 118, cy + 118], fill=IVORY)
    for i in range(12):
        a = 2 * math.pi * i / 12; flower(d, cx + 134 * math.cos(a), cy + 134 * math.sin(a), 22, [RED, OCH][i % 2], IVORY, 6)
    d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=DRED); star(d, cx, cy, 70, GOLD, 8, .55); d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=RED)
for _ in range(40):
    x, y = R.randrange(S), R.randrange(S); d.arc([x - 60, y - 60, x + 60, y + 60], R.randrange(360), R.randrange(360), fill=GRN, width=6); flower(d, x, y, 16, [IND, GRN][R.randrange(2)], OCH, 5)
save(im, 'suzani2', .6)
# 4 kilim runner / cushion (bold stripes with lozenges)
im = Image.new('RGB', (512, 512), RED); d = ImageDraw.Draw(im)
for i, y in enumerate(range(0, 512, 32)):
    c = [RED, NAVY, CRE, GOLD, RED, TUR, CRE, DRED][i % 8]; d.rectangle([0, y, 512, y + 32], fill=c)
    for x in range(0, 512, 48): dia(d, x + 24, y + 16, 18, 12, [CRE, RED, NAVY, RED][(i + x // 48) % 4])
save(im, 'kilim2', .5)
# 5 Rishtan plate (top view, picture-mapped on plates)
S = 512; im = Image.new('RGB', (S, S), (250, 250, 245)); d = ImageDraw.Draw(im); c = S / 2
d.ellipse([4, 4, S - 4, S - 4], fill=(28, 90, 160)); d.ellipse([28, 28, S - 28, S - 28], fill=(245, 244, 236))
for i in range(16):
    a = 2 * math.pi * i / 16; d.ellipse([c + 200 * math.cos(a) - 18, c + 200 * math.sin(a) - 18, c + 200 * math.cos(a) + 18, c + 200 * math.sin(a) + 18], fill=(28, 120, 170))
for i in range(8):
    a = 2 * math.pi * i / 8; d.polygon([(c, c), (c + 150 * math.cos(a - .18), c + 150 * math.sin(a - .18)), (c + 170 * math.cos(a), c + 170 * math.sin(a)), (c + 150 * math.cos(a + .18), c + 150 * math.sin(a + .18))], fill=(40, 120, 180))
d.ellipse([c - 60, c - 60, c + 60, c + 60], fill=(214, 160, 60)); star(d, c, c, 50, (28, 90, 160), 8, .5)
grain(im, 6).filter(ImageFilter.GaussianBlur(.6)).save(f'{out}/rishtan.png')
# 6 quilted suzani patchwork (one tile of 4 x 4 squares, alternating motifs, like ref 03)
S = 512; im = Image.new('RGB', (S, S), RED); d = ImageDraw.Draw(im)
for i in range(4):
    for j in range(4):
        x0, y0 = i * 128, j * 128; bg = [IVORY, (230, 205, 170)][(i + j) % 2]; d.rectangle([x0 + 2, y0 + 2, x0 + 126, y0 + 126], fill=bg)
        flower(d, x0 + 64, y0 + 64, 44, [RED, DRED, OCH][(i * 3 + j) % 3], [GOLD, NAVY][(i + j) % 2], 8)
        for cx, cy in ((x0 + 16, y0 + 16), (x0 + 112, y0 + 16), (x0 + 16, y0 + 112), (x0 + 112, y0 + 112)): d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=GOLD)
save(im, 'quilt', .5)
# 7 turquoise dome glaze (vertical ribs with a lapis lozenge net)
S = 512; im = Image.new('RGB', (S, S), (32, 150, 170)); d = ImageDraw.Draw(im)
for x in range(0, S, 32): d.rectangle([x, 0, x + 3, S], fill=(20, 110, 130))
for y in range(0, S, 64):
    for x in range(0, S, 64): dia(d, x + 32, y + 32, 14, 24, LAP); dia(d, x + 32, y + 32, 6, 10, (240, 236, 220))
save(im, 'domeglaze', .5, wv=False)
# 8 lime plaster (tadelakt-like warm white)
S = 512; im = Image.new('RGB', (S, S), (232, 216, 190))
for _ in range(400):
    x, y, r = R.randrange(S), R.randrange(S), R.randint(20, 60); v = R.randint(-10, 8)
    ImageDraw.Draw(im).ellipse([x - r, y - r, x + r, y + r], fill=(232 + v, 216 + v, 190 + v))
im.filter(ImageFilter.GaussianBlur(14)).save(f'{out}/plaster.png')
# 9 rattan weave
S = 256; im = Image.new('RGB', (S, S), (176, 128, 70)); d = ImageDraw.Draw(im)
for k in range(0, S, 16):
    for j in range(0, S, 16):
        if (k // 16 + j // 16) % 2: d.rectangle([k + 1, j + 1, k + 15, j + 15], fill=(204, 156, 92))
        else: d.rectangle([k + 1, j + 5, k + 15, j + 11], fill=(140, 96, 48))
save(im, 'rattan', .4, wv=False)
# 10 plov (rice with carrot strands) and 11 lepyoshka crust
S = 256; im = Image.new('RGB', (S, S), (226, 186, 110)); d = ImageDraw.Draw(im)
for _ in range(1800):
    x, y = R.randrange(S), R.randrange(S); d.ellipse([x, y, x + 4, y + 2], fill=(240, 214, 150))
for _ in range(120):
    x, y = R.randrange(S), R.randrange(S); d.line([x, y, x + R.randint(-14, 14), y + R.randint(-14, 14)], fill=(214, 100, 30), width=2)
im.filter(ImageFilter.GaussianBlur(.5)).save(f'{out}/plov.png')
im = Image.new('RGB', (S, S), (196, 128, 60)); d = ImageDraw.Draw(im)
d.ellipse([60, 60, 196, 196], fill=(222, 170, 98))
for i in range(24):
    a = 2 * math.pi * i / 24; d.ellipse([128 + 45 * math.cos(a) - 3, 128 + 45 * math.sin(a) - 3, 128 + 45 * math.cos(a) + 3, 128 + 45 * math.sin(a) + 3], fill=(150, 92, 40))
grain(im, 14).filter(ImageFilter.GaussianBlur(1.2)).save(f'{out}/bread.png')
print('textures3 ok')
