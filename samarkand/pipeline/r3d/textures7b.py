"""Chair textures cut from the owner's chair photo (ref7/chair.jpg): kilim cushion cloth and the carved interlace rail.
Usage: python3 textures7b.py REF7DIR"""
import sys, os
from PIL import Image, ImageOps
import numpy as np
from PIL import ImageFilter
_t6 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textures6.py')).read(); exec(_t6[_t6.index('def level'):_t6.index('# bannai:')])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex2')
CH = Image.open(os.path.join(sys.argv[1], 'chair.jpg')).convert('RGB')
k = crop(CH, (356, 332, 664, 412), (1024, 266), 'hmirror'); k = k.resize((1024, 266))
t = Image.new('RGB', (1024, 1064)); [t.paste(k if j % 2 == 0 else ImageOps.flip(k), (0, j * 266)) for j in range(4)]
t.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, 'kilimref.png')); print('kilimref')
k2 = crop(CH, (420, 236, 600, 296), (768, 256), 'hmirror')
t = Image.new('RGB', (1536, 1024)); [t.paste(k2 if j % 2 == 0 else ImageOps.flip(k2), (i * 768, j * 256)) for i in range(2) for j in range(4)]
t.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, 'kilimref2.png')); print('kilimref2')
c = crop(CH, (78, 284, 292, 344), (1024, 288), 'blend')
t = Image.new('RGB', (1024, 1152)); [t.paste(c, (0, j * 288)) for j in range(4)]
t.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, 'carvedref.png')); print('carvedref')

# ---- kilim cloth woven on a grid (ref: the chair cushions) — colours sampled from the photo, motifs as woven: stepped diamonds,
# hooked borders, ram's-horn hooks; every cell is a weft float, so it reads as cloth, not print
def kilim(name, seed, ground_seq):
    import random; R = random.Random(seed)
    P = dict(maroon=(118, 34, 38), olive=(128, 146, 108), cream=(222, 206, 174), brown=(58, 36, 30), blue=(64, 96, 118), tan=(176, 138, 92), rust=(164, 72, 44), dark=(34, 28, 30))
    N = 256; g = [[None] * N for _ in range(N)]
    bands = []; x = 0; k = 0
    while x < N:
        w = 44 if k % 2 == 0 else 10; bands.append((x, min(N, x + w), k)); x += w; k += 1
    for (x0, x1, k) in bands:
        mid = (x0 + x1) / 2
        if k % 2:                                                        # narrow border: ground + zigzag in two colours
            gc, zc = P['cream'], P['maroon'] if (k // 2) % 2 else P['dark']
            for y in range(N):
                for x in range(x0, x1):
                    z = abs(((y % 10) - 5)) + 2; g[y][x] = zc if abs(x - mid) < 1 or abs((x - x0) - z) < 1 else gc
            continue
        gc = P[ground_seq[(k // 2) % len(ground_seq)]]
        a, b2 = (P['cream'], P['maroon']) if gc != P['cream'] else (P['maroon'], P['olive'])
        per = 40
        for y in range(N):
            yy = (y % per) - per / 2
            for x in range(x0, x1):
                dx = abs(x - mid); dy = abs(yy); d = dx + dy
                if d < 16 and d >= 13: c = a                                   # outer diamond outline
                elif d < 13 and d >= 9: c = P['dark']
                elif d < 9 and d >= 6: c = b2
                elif d < 6: c = P['cream'] if d < 2 else (P['rust'] if (dx + dy) % 2 else P['tan'])
                elif d < 21 and ((dx == 17 and dy < 4) or (dy == 17 and dx < 4)): c = a   # hooks off the diamond tips
                else: c = gc
                g[y][x] = c
    a = np.zeros((N * 4, N * 4, 3), np.float32); rng = np.random.default_rng(seed)
    row = rng.normal(1, 0.05, N * 4)[:, None]; col = 1 + 0.04 * np.sin(np.arange(N * 4) * np.pi / 2)[None, :]
    for y in range(N):
        for x in range(N):
            a[y * 4:(y + 1) * 4, x * 4:(x + 1) * 4] = g[y][x]
    a = a * row[..., None] * col[..., None] * (1 + rng.normal(0, 0.035, a.shape[:2]))[..., None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    im.save(os.path.join(OUT, name + '.png')); print(name, im.size)
kilim('kilimref', 3, ('olive', 'maroon', 'cream', 'blue'))
kilim('kilimref2', 5, ('maroon', 'cream', 'olive', 'brown'))
