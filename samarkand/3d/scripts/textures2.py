"""Second texture set for the R12 detailing pass: carpets, kilim, tent stripes, velvet, 8 epoch panels, brick-girih dome lining,
terracotta dome tiles, hammered copper, carved wood. All seamless-ish 512/1024 PNGs. Usage: python3 textures2.py OUTDIR"""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]; R = random.Random(11)
LAP, TUR, CRE, TERC, GOLD, WAL, RED, IND, OCH = (31, 63, 138), (42, 157, 168), (239, 230, 216), (181, 101, 58), (217, 162, 58), (90, 58, 34), (142, 31, 36), (28, 30, 70), (196, 140, 62)
def grain(im, a=8, n=40000):
    px = im.load(); w, h = im.size
    for _ in range(n):
        x, y = R.randrange(w), R.randrange(h); c = px[x, y]; v = R.randint(-a, a); px[x, y] = tuple(max(0, min(255, q + v)) for q in c)
    return im
def star(d, cx, cy, r, fill, k=8, inner=.6, rot=0):
    d.polygon([(cx + (r if i % 2 == 0 else r * inner) * math.cos(rot + i * math.pi / k), cy + (r if i % 2 == 0 else r * inner) * math.sin(rot + i * math.pi / k)) for i in range(2 * k)], fill=fill)
def diamond(d, cx, cy, rx, ry, fill): d.polygon([(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)], fill=fill)
def save(im, n, blur=.5): grain(im).filter(ImageFilter.GaussianBlur(blur)).save(f'{out}/{n}.png')

# carpets: 4 colourways, medallion + border (one carpet = whole image, mapped per carpet)
for k, (fld, med, brd, acc) in enumerate([(RED, IND, IND, GOLD), (IND, RED, RED, CRE), ((120, 30, 40), (210, 170, 110), (40, 40, 80), TUR), ((150, 60, 30), (30, 60, 110), (70, 30, 20), CRE)]):
    W, H = 512, 768; im = Image.new('RGB', (W, H), brd); d = ImageDraw.Draw(im)
    d.rectangle([30, 30, W - 30, H - 30], fill=acc); d.rectangle([44, 44, W - 44, H - 44], fill=fld)
    for y in range(52, H - 52, 34):
        for x in (37, W - 37): diamond(d, x, y, 7, 12, fld)
    diamond(d, W / 2, H / 2, 170, 250, med); diamond(d, W / 2, H / 2, 120, 180, acc); diamond(d, W / 2, H / 2, 90, 140, fld); star(d, W / 2, H / 2, 70, med); star(d, W / 2, H / 2, 34, acc)
    for cx, cy in ((90, 110), (W - 90, 110), (90, H - 110), (W - 90, H - 110)): star(d, cx, cy, 38, med); star(d, cx, cy, 18, acc)
    for i in range(10):
        y = 60 + i * 66
        for x in (130, W - 130): diamond(d, x, y, 10, 14, acc)
    save(im, f'carpet{k + 1}', .7)
# kilim stripes
im = Image.new('RGB', (512, 512), RED); d = ImageDraw.Draw(im)
cols = [RED, CRE, IND, GOLD, RED, TUR, CRE, IND]
for i, y in enumerate(range(0, 512, 64)):
    d.rectangle([0, y, 512, y + 64], fill=cols[i % len(cols)])
    for x in range(0, 512, 64): diamond(d, x + 32, y + 32, 26, 26, cols[(i + 3) % len(cols)]); diamond(d, x + 32, y + 32, 12, 12, cols[(i + 5) % len(cols)])
save(im, 'kilim', .6)
# tent stripes (red / cream / indigo, like the majlis reference)
im = Image.new('RGB', (512, 512), CRE); d = ImageDraw.Draw(im)
for i, x in enumerate(range(0, 512, 32)): d.rectangle([x, 0, x + 32, 512], fill=[RED, CRE, (176, 40, 45), IND, CRE, RED, GOLD, CRE][i % 8])
for x in range(0, 512, 64): d.rectangle([x + 14, 0, x + 18, 512], fill=GOLD)
save(im, 'tentstripe', .8)
# velvet (deep terracotta with soft folds)
im = Image.new('RGB', (512, 512)); px = im.load()
for x in range(512):
    f = 0.75 + 0.25 * math.sin(x / 512 * 2 * math.pi * 6) ** 2
    for y in range(512): px[x, y] = (int(120 * f), int(34 * f), int(22 * f))
save(im, 'velvet', 1.2)
# brick-girih dome lining (buff bricks in a radial/star bond, like the reference)
S = 1024; im = Image.new('RGB', (S, S), (150, 112, 70)); d = ImageDraw.Draw(im)
for row, y in enumerate(range(0, S, 32)):
    off = 32 if row % 2 else 0
    for x in range(-64 + off, S, 64): v = R.randint(-12, 12); d.rectangle([x + 3, y + 3, x + 61, y + 29], fill=(206 + v, 168 + v, 116 + v))
for cx, cy in ((S / 2, S / 2), (0, 0), (S, 0), (0, S), (S, S)):
    for r, c in ((300, (120, 86, 52)), (290, None)):
        pts = [(cx + r * math.cos(i * math.pi / 8 + math.pi / 16) * (1 if i % 2 == 0 else .62), cy + r * math.sin(i * math.pi / 8 + math.pi / 16) * (1 if i % 2 == 0 else .62)) for i in range(16)]
        d.line(pts + [pts[0]], fill=(110, 78, 46), width=10)
    for i in range(8):
        a = i * math.pi / 4; d.line([(cx, cy), (cx + 290 * math.cos(a), cy + 290 * math.sin(a))], fill=(120, 86, 52), width=6)
save(im, 'gajbrick', .6)
# terracotta dome tiles (fish-scale)
im = Image.new('RGB', (512, 512), (140, 64, 36)); d = ImageDraw.Draw(im)
for row, y in enumerate(range(-32, 544, 32)):
    for x in range(-32 + (32 if row % 2 else 0), 544, 64):
        v = R.randint(-14, 14); d.ellipse([x, y, x + 64, y + 56], fill=(170 + v, 82 + v // 2, 46 + v // 3), outline=(110, 50, 28), width=3)
save(im, 'dometile', .5)
# hammered copper
im = Image.new('RGB', (512, 512), (176, 98, 52)); d = ImageDraw.Draw(im)
for _ in range(900):
    x, y, r = R.randrange(512), R.randrange(512), R.randint(6, 16); v = R.randint(-30, 30); d.ellipse([x - r, y - r, x + r, y + r], fill=(176 + v, 98 + v // 2, 52 + v // 3))
save(im, 'copper', 1.0)
# carved wood panel (pointed arches + rosettes)
im = Image.new('RGB', (512, 512), (78, 46, 24)); d = ImageDraw.Draw(im)
for x in range(0, 512, 128):
    d.rectangle([x + 10, 10, x + 118, 502], fill=(110, 68, 36)); d.pieslice([x + 20, 20, x + 108, 150], 180, 360, fill=(62, 36, 18)); d.rectangle([x + 20, 85, x + 108, 490], fill=(62, 36, 18))
    for y in range(160, 480, 80): star(d, x + 64, y, 30, (130, 84, 44)); star(d, x + 64, y, 12, (70, 40, 20))
save(im, 'carved', .5)
# 8 epoch panels for the themed booths (motif language of each epoch, stylised)
def panel(name, bg, draw):
    im = Image.new('RGB', (512, 512), bg); d = ImageDraw.Draw(im); draw(d); d.rectangle([0, 0, 511, 511], outline=GOLD, width=14); save(im, 'ep_' + name, .6)
panel('sogd', (196, 120, 70), lambda d: [d.ellipse([60 + 130 * i, 120, 160 + 130 * i, 400], fill=(120, 50, 30)) or d.ellipse([85 + 130 * i, 140, 135 + 130 * i, 190], fill=(230, 190, 140)) for i in range(3)] + [d.rectangle([20, 440, 492, 470], fill=LAP)])
panel('sasan', RED, lambda d: [(d.ellipse([x - 90, y - 90, x + 90, y + 90], fill=GOLD), d.ellipse([x - 76, y - 76, x + 76, y + 76], fill=IND), star(d, x, y, 60, GOLD, 6, .45)) for x in (128, 384) for y in (128, 384)])
panel('saman', (238, 226, 205), lambda d: [d.ellipse([60, 60, 452, 452], outline=(70, 40, 25), width=26), d.ellipse([130, 130, 382, 382], outline=RED, width=10)] + [d.rectangle([250 + 150 * math.cos(a) - 8, 250 + 150 * math.sin(a) - 30, 250 + 150 * math.cos(a) + 8, 250 + 150 * math.sin(a) + 30], fill=(70, 40, 25)) for a in [i * math.pi / 6 for i in range(12)]])
panel('khorezm', (235, 238, 240), lambda d: [(star(d, x, y, 70, LAP, 6, .5), star(d, x, y, 30, TUR, 6, .5)) for x in (85, 256, 427) for y in (85, 256, 427)])
panel('timur', LAP, lambda d: [(star(d, x, y, 120, TUR, 8, .62, math.pi / 8), star(d, x, y, 80, CRE, 8, .62, math.pi / 8), star(d, x, y, 40, GOLD, 8, .62, math.pi / 8)) for x, y in ((128, 128), (384, 128), (128, 384), (384, 384))])
panel('shahr', (36, 96, 70), lambda d: [d.rectangle([40, 40, 472, 472], outline=GOLD, width=10)] + [star(d, 256, 256, 180, GOLD, 12, .7), star(d, 256, 256, 110, (36, 96, 70), 12, .7), star(d, 256, 256, 60, CRE, 12, .7)])
def _ikat(d):
    for i, x in enumerate(range(0, 512, 64)):
        c = [RED, GOLD, IND, CRE][i % 4]
        for y in range(0, 512, 96): d.polygon([(x + 32, y), (x + 62, y + 48), (x + 32, y + 96), (x + 2, y + 48)], fill=c); d.polygon([(x + 32, y + 22), (x + 46, y + 48), (x + 32, y + 74), (x + 18, y + 48)], fill=[IND, RED, GOLD, LAP][i % 4])
panel('margil', CRE, _ikat)
panel('pamir', (200, 40, 40), lambda d: [(d.polygon([(x, y - 60), (x + 60, y), (x, y + 60), (x - 60, y)], fill=CRE), d.polygon([(x, y - 30), (x + 30, y), (x, y + 30), (x - 30, y)], fill=(20, 20, 20))) for x in (96, 256, 416) for y in (96, 256, 416)])
print('textures ok')
