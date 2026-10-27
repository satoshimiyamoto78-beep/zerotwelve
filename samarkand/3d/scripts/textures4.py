"""Texture set 4: velvet (terracotta, navy, emerald), pierced brass (with an emission mask), zellige table inlay,
skin-free clothing fabrics (linen, denim, silk). Usage: python3 textures4.py OUTDIR"""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]; R = random.Random(9)
def velvet(name, base):
    S = 256; im = Image.new('RGB', (S, S), base); px = im.load()
    for y in range(S):
        for x in range(S):
            n = R.randint(-6, 6) + int(8 * math.sin((x + y * 0.3) / 9.0))
            px[x, y] = tuple(max(0, min(255, c + n)) for c in base)
    im.filter(ImageFilter.GaussianBlur(1.2)).save(f'{out}/{name}.png')
velvet('velvet_terra', (150, 62, 38)); velvet('velvet_navy', (32, 44, 82)); velvet('velvet_emerald', (28, 84, 70)); velvet('velvet_wine', (110, 28, 40))
# pierced brass: dark brass with a star/dot perforation pattern; the mask is the light that shines through
S = 512; col = Image.new('RGB', (S, S), (150, 108, 46)); msk = Image.new('L', (S, S), 0); dc, dm = ImageDraw.Draw(col), ImageDraw.Draw(msk)
for j in range(0, S, 32):
    for i in range(0, S, 32):
        ox = 16 if (j // 32) % 2 else 0; x, y = i + ox, j + 16
        pts = [(x + (9 if k % 2 == 0 else 4) * math.cos(k * math.pi / 4), y + (9 if k % 2 == 0 else 4) * math.sin(k * math.pi / 4)) for k in range(8)]
        dc.polygon(pts, fill=(255, 210, 140)); dm.polygon(pts, fill=255)
        dc.ellipse([x + 14, y - 2, x + 18, y + 2], fill=(255, 210, 140)); dm.ellipse([x + 14, y - 2, x + 18, y + 2], fill=255)
col.filter(ImageFilter.GaussianBlur(.6)).save(f'{out}/pierced.png'); msk.filter(ImageFilter.GaussianBlur(.6)).save(f'{out}/pierced_mask.png')
# zellige inlay for table tops (one 8-point star rosette panel)
S = 512; im = Image.new('RGB', (S, S), (238, 230, 214)); d = ImageDraw.Draw(im)
def star(cx, cy, r, fill, inner=.62, rot=math.pi / 8):
    d.polygon([(cx + (r if k % 2 == 0 else r * inner) * math.cos(rot + k * math.pi / 8), cy + (r if k % 2 == 0 else r * inner) * math.sin(rot + k * math.pi / 8)) for k in range(16)], fill=fill)
for cx, cy in ((0, 0), (256, 256), (512, 0), (0, 512), (512, 512), (256, 0), (0, 256), (512, 256), (256, 512)):
    star(cx, cy, 120, (30, 70, 140)); star(cx, cy, 82, (238, 230, 214)); star(cx, cy, 52, (40, 150, 160)); star(cx, cy, 22, (214, 160, 60))
for x in range(0, S, 64):
    for y in range(0, S, 64): d.rectangle([x, y, x + 63, y + 63], outline=(200, 190, 170), width=2)
im.filter(ImageFilter.GaussianBlur(.5)).save(f'{out}/zellige.png')
# clothing fabrics
for name, base, stripe in (('cloth_linen', (226, 218, 200), None), ('cloth_denim', (52, 66, 98), None), ('cloth_silk_ikat', (150, 30, 50), (230, 180, 60)), ('cloth_white', (236, 234, 228), None), ('cloth_olive', (92, 98, 66), None), ('cloth_black', (34, 32, 34), None)):
    S = 256; im = Image.new('RGB', (S, S), base); d = ImageDraw.Draw(im)
    if stripe:
        for x in range(0, S, 32): d.polygon([(x + 16, 0), (x + 28, 64), (x + 16, 128), (x + 4, 64)], fill=stripe); d.polygon([(x + 16, 128), (x + 28, 192), (x + 16, 256), (x + 4, 192)], fill=stripe)
    px = im.load()
    for y in range(S):
        for x in range(S):
            if (x + y) % 3 == 0: c = px[x, y]; px[x, y] = tuple(max(0, q - 8) for q in c)
    im.filter(ImageFilter.GaussianBlur(.4)).save(f'{out}/{name}.png')
print('textures4 ok')
