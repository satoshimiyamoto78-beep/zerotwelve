"""R12 rev. 8 textiles: woven, not printed. Every rug is designed at KNOT resolution and rendered knot by knot (abrash
bands, per-knot colour scatter, pile shading, wear); kilims get weft ribs and slits; suzani is embroidered (chain-stitch
relief on a linen ground); adras ikat gets the warp-feathered edges of real resist dyeing. Writes tex2/*.png.
Usage: python3 textures8.py"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex2')
BASE = os.path.dirname(os.path.abspath(__file__))

def lowfreq(h, w, cells, seed):
    """smooth noise 0..1 (bilinear upsampled random grid)"""
    r = np.random.default_rng(seed); g = r.random((cells + 1, int(cells * w / h) + 2))
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255.0

def abrash(h, seed, amp=0.07):
    """per-row multiplier: yarn lots dyed slightly differently -> horizontal bands of 4..30 rows"""
    r = random.Random(seed); f = np.ones(h, np.float32); y = 0
    while y < h:
        n = r.randint(4, 30); f[y:y + n] = 1 + r.uniform(-amp, amp); y += n
    return np.convolve(f, np.ones(3) / 3, 'same')

def pile(design, k=6, seed=1, wear=0.12, warp=(150, 120, 100)):
    """design: (H, W, 3) uint8 at knot resolution -> pile rug image (H*k, W*k)"""
    d = design.astype(np.float32); H, W, _ = d.shape; r = np.random.default_rng(seed)
    sat = (d.max(2) - d.min(2)) / 255.0
    d *= (1 + (abrash(H, seed)[:, None] - 1) * (0.4 + sat))[:, :, None]                           # abrash shows on dyed yarn
    d *= (1 + r.normal(0, 0.035, (H, W)))[:, :, None]                                              # knot-to-knot scatter
    wf = lowfreq(H, W, 6, seed + 7); wm = np.clip((wf - (1 - wear)) / wear, 0, 1)[:, :, None]     # worn patches: pile low, warp shows
    d = d * (1 - 0.18 * wm) + np.array(warp, np.float32) * 0.18 * wm
    big = np.repeat(np.repeat(d, k, 0), k, 1)
    yy, xx = np.mgrid[0:k, 0:k] / (k - 1)                                                          # one knot: lit top, shadowed foot
    cell = 1.04 - 0.14 * yy ** 2 - 0.06 * (2 * xx - 1) ** 2
    big *= np.tile(cell, (H, W))[:, :, None]
    big *= (1 + r.normal(0, 0.04, big.shape[:2]))[:, :, None]                                       # fibre noise
    im = Image.fromarray(np.clip(big, 0, 255).astype(np.uint8))
    return im.filter(ImageFilter.GaussianBlur(0.7))

def flatweave(design, kx=4, ky=3, seed=1):
    """kilim: weft ribs, warp ridges, slits where the colour changes along a row"""
    d = design.astype(np.float32); H, W, _ = d.shape; r = np.random.default_rng(seed)
    d *= (1 + (abrash(H, seed, 0.05)[:, None] - 1))[:, :, None]
    d *= (1 + r.normal(0, 0.03, (H, W)))[:, :, None]
    slit = np.zeros((H, W), bool); slit[:, 1:] = np.abs(design[:, 1:].astype(int) - design[:, :-1].astype(int)).sum(2) > 60
    big = np.repeat(np.repeat(d, ky, 0), kx, 1)
    yy, xx = np.mgrid[0:ky, 0:kx]
    cell = 1.0 + 0.10 * np.cos(2 * math.pi * yy / ky) - 0.06 * (xx == 0)
    big *= np.tile(cell, (H, W))[:, :, None]
    s = np.repeat(np.repeat(slit, ky, 0), kx, 1); s[:, 1:] &= ~s[:, :-1]
    big[s] *= 0.45
    big *= (1 + r.normal(0, 0.03, big.shape[:2]))[:, :, None]
    return Image.fromarray(np.clip(big, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5))

def handwarp(a, amp=5.0, seed=1):
    """hand-drawn irregularity: smooth displacement of the design (no ruler-perfect circles)"""
    H, W = a.shape[:2]; dx = (lowfreq(H, W, 10, seed) - 0.5) * 2 * amp; dy = (lowfreq(H, W, 10, seed + 1) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:H, 0:W]
    return a[np.clip((yy + dy).astype(int), 0, H - 1) % H, np.clip((xx + dx).astype(int), 0, W - 1) % W]

def embroider(img, ground, seed=1, tol=40):
    """suzani: linen ground (slubby plain weave); motifs in tambour chain stitch: rows of stitches run parallel to each
    colour field's outline (distance-to-edge rings), each row a chain of loops; thread dye mottling; raised-edge shadow"""
    a = handwarp(np.asarray(img.convert('RGB')), 4.0, seed).astype(np.float32); H, W, _ = a.shape; r = np.random.default_rng(seed)
    gm = (np.abs(a - np.array(ground, np.float32)).sum(2) < tol)
    yy, xx = np.mgrid[0:H, 0:W]
    lin = 1 + 0.04 * np.sign(np.sin(xx * math.pi / 2)) * np.sign(np.sin(yy * math.pi / 2)) + r.normal(0, 0.03, (H, W))
    lin += 0.06 * (np.repeat(r.random((H, 1)), W, 1) > 0.96) * lowfreq(H, W, 60, seed)
    q = (a // 24).astype(np.int32); key = q[:, :, 0] * 10000 + q[:, :, 1] * 100 + q[:, :, 2]
    edge = np.zeros((H, W), bool); edge[:, 1:] |= key[:, 1:] != key[:, :-1]; edge[1:, :] |= key[1:, :] != key[:-1, :]
    dist = np.full((H, W), 14.0, np.float32); cur = Image.fromarray((edge * 255).astype(np.uint8))
    for d in range(14):                                                    # distance to the nearest colour change (0..13 px)
        m = np.asarray(cur) > 0; dist[m & (dist > d)] = d; cur = cur.filter(ImageFilter.MaxFilter(3))
    row = np.abs(np.sin(dist * math.pi / 3.2))                             # stitch rows ~3 px apart, parallel to the outline
    loop = 0.5 + 0.5 * np.sin((xx + yy) * math.pi / 2.2 + dist * 1.7)      # chain loops along the row
    ch = 0.80 + 0.22 * row * (0.7 + 0.3 * loop) + r.normal(0, 0.045, (H, W))
    ch *= 0.92 + 0.12 * lowfreq(H, W, 24, seed + 3)                         # thread-lot mottling
    out = a * np.where(gm, lin, ch)[:, :, None]
    sh = np.asarray(Image.fromarray(((edge & ~gm) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255.0
    out *= (1 - 0.25 * sh)[:, :, None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.45))

# ---------------------------------------------------------------- BUKHARA (TEKKE) RUG, 170 x 260 knots
RED, DRED, IVORY, NAVY, ORANGE, BROWN, BLUEG = (128, 24, 26), (78, 14, 18), (226, 210, 178), (30, 34, 58), (196, 98, 40), (60, 30, 22), (52, 88, 104)
def tekke():
    W_, H_ = 170, 260; im = Image.new('RGB', (W_, H_), RED); dr = ImageDraw.Draw(im)
    def rect(x0, y0, x1, y1, c): dr.rectangle((x0, y0, x1 - 1, y1 - 1), fill=c)
    # borders: outer guard, main border (stepped octagons on dark), inner guard; elems at both ends
    rect(0, 0, W_, H_, DRED); rect(3, 3, W_ - 3, H_ - 3, RED)
    for x in range(4, W_ - 4, 4): dr.point((x, 4), IVORY); dr.point((x, H_ - 5), IVORY)
    for y in range(4, H_ - 4, 4): dr.point((4, y), IVORY); dr.point((W_ - 5, y), IVORY)
    rect(7, 7, W_ - 7, H_ - 7, DRED); rect(9, 9, W_ - 9, H_ - 9, BROWN); rect(21, 21, W_ - 21, H_ - 21, DRED)
    def star(cx, cy, c1, c2):
        for dy in range(-4, 5):
            w = 4 - abs(dy); dr.line((cx - w, cy + dy, cx + w, cy + dy), fill=c1)
        dr.point((cx, cy), c2); dr.line((cx - 1, cy, cx + 1, cy), fill=c2)
    for i, x in enumerate(range(15, W_ - 10, 12)): star(x, 15, (IVORY, ORANGE, BLUEG)[i % 3], RED); star(x, H_ - 16, (IVORY, ORANGE, BLUEG)[i % 3], RED)
    for i, y in enumerate(range(27, H_ - 20, 12)): star(15, y, (ORANGE, IVORY, BLUEG)[i % 3], RED); star(W_ - 16, y, (ORANGE, IVORY, BLUEG)[i % 3], RED)
    rect(23, 23, W_ - 23, H_ - 23, RED)
    # field: 4 x 7 primary guls (quartered octagons) on a lattice of dark lines, chemche minor guls between
    fx0, fy0, fx1, fy1 = 25, 25, W_ - 25, H_ - 25; nx, ny = 4, 7; gw, gh = (fx1 - fx0) / nx, (fy1 - fy0) / ny
    for i in range(nx + 1): dr.line((fx0 + i * gw, fy0, fx0 + i * gw, fy1), fill=DRED)
    for j in range(ny + 1): dr.line((fx0, fy0 + j * gh, fx1, fy0 + j * gh), fill=DRED)
    for j in range(ny):
        for i in range(nx):
            cx, cy = fx0 + (i + 0.5) * gw, fy0 + (j + 0.5) * gh; a_, b_ = gw * 0.44, gh * 0.40
            oct_ = [(cx - a_ * 0.55, cy - b_), (cx + a_ * 0.55, cy - b_), (cx + a_, cy - b_ * 0.4), (cx + a_, cy + b_ * 0.4),
                    (cx + a_ * 0.55, cy + b_), (cx - a_ * 0.55, cy + b_), (cx - a_, cy + b_ * 0.4), (cx - a_, cy - b_ * 0.4)]
            dr.polygon(oct_, fill=DRED); s = 0.86
            dr.polygon([(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in oct_], fill=IVORY); s = 0.78
            inner = [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in oct_]
            dr.polygon(inner, fill=RED)
            for q, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):              # quarters, colours alternate diagonally
                c = NAVY if q % 2 == 0 else ORANGE
                qx, qy = cx + sx * a_ * 0.36, cy + sy * b_ * 0.36
                dr.polygon([(qx, qy - b_ * 0.22), (qx + a_ * 0.24, qy), (qx, qy + b_ * 0.22), (qx - a_ * 0.24, qy)], fill=c)
                dr.point((int(qx), int(qy)), IVORY); dr.point((int(qx) + 1, int(qy)), IVORY)
            dr.line((cx - a_ * 0.75, cy, cx + a_ * 0.75, cy), fill=DRED, width=1); dr.line((cx, cy - b_ * 0.7, cx, cy + b_ * 0.7), fill=DRED, width=1)
            dr.rectangle((cx - 1, cy - 1, cx + 1, cy + 1), fill=IVORY)
    for j in range(ny + 1):
        for i in range(nx + 1):
            cx, cy = fx0 + i * gw, fy0 + j * gh
            if fx0 < cx < fx1 and fy0 < cy < fy1:
                dr.polygon([(cx, cy - 6), (cx + 5, cy), (cx, cy + 6), (cx - 5, cy)], fill=NAVY); dr.polygon([(cx, cy - 3), (cx + 2, cy), (cx, cy + 3), (cx - 2, cy)], fill=IVORY)
    return np.asarray(im)

# ---------------------------------------------------------------- PALAS (kilim-woven version of a flat design)
def palas_from(path, w=180, h=180):
    im = Image.open(path).convert('RGB').resize((w, h), Image.NEAREST)
    return np.asarray(im.quantize(10, dither=Image.Dither.NONE).convert('RGB'))

# ---------------------------------------------------------------- SUZANI (Nurata / Bukhara type): rosettes, leaves, vines on linen
LIN = (226, 214, 186)
def suzani(N=1024, seed=3, big=True):
    r = random.Random(seed); im = Image.new('RGB', (N, N), LIN); dr = ImageDraw.Draw(im)
    CR, CR2, PINK, GOLD, GRN, IND, BLK = (166, 30, 34), (122, 18, 30), (196, 84, 92), (204, 150, 52), (58, 92, 58), (40, 44, 92), (40, 26, 24)
    def vine(x0, y0, x1, y1):
        pts = [(x0 + (x1 - x0) * t / 20 + 14 * math.sin(t * 0.9), y0 + (y1 - y0) * t / 20 + 14 * math.cos(t * 0.7)) for t in range(21)]
        dr.line(pts, fill=GRN, width=5)
        for k, (px, py) in enumerate(pts[2:-2:3]):
            a = r.uniform(0, 2 * math.pi); L = 28
            lx, ly = px + L * math.cos(a), py + L * math.sin(a)
            dr.polygon([(px, py), ((px + lx) / 2 + 9 * math.sin(a), (py + ly) / 2 - 9 * math.cos(a)), (lx, ly), ((px + lx) / 2 - 9 * math.sin(a), (py + ly) / 2 + 9 * math.cos(a))], fill=GRN)
    def rosette(cx, cy, R):
        for k in range(16):                                                           # petal ring
            a = 2 * math.pi * k / 16; px, py = cx + R * 0.86 * math.cos(a), cy + R * 0.86 * math.sin(a)
            dr.ellipse((px - R * 0.2, py - R * 0.2, px + R * 0.2, py + R * 0.2), fill=CR2)
        dr.ellipse((cx - R * 0.86, cy - R * 0.86, cx + R * 0.86, cy + R * 0.86), fill=CR)
        dr.ellipse((cx - R * 0.66, cy - R * 0.66, cx + R * 0.66, cy + R * 0.66), fill=LIN)
        for k in range(12):
            a = 2 * math.pi * k / 12; px, py = cx + R * 0.52 * math.cos(a), cy + R * 0.52 * math.sin(a)
            dr.polygon([(cx + R * 0.3 * math.cos(a - 0.2), cy + R * 0.3 * math.sin(a - 0.2)), (px, py), (cx + R * 0.3 * math.cos(a + 0.2), cy + R * 0.3 * math.sin(a + 0.2))], fill=(IND, PINK)[k % 2])
        dr.ellipse((cx - R * 0.32, cy - R * 0.32, cx + R * 0.32, cy + R * 0.32), fill=CR)
        dr.ellipse((cx - R * 0.18, cy - R * 0.18, cx + R * 0.18, cy + R * 0.18), fill=GOLD)
        dr.ellipse((cx - R * 0.07, cy - R * 0.07, cx + R * 0.07, cy + R * 0.07), fill=BLK)
    cs = [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)] if big else [(0.5, 0.5)]
    for cx, cy in cs:                                                               # vines first, under the rosettes (wrap-around tiling)
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                X0, Y0 = (cx + ox) * N, (cy + oy) * N
                vine(X0, Y0, X0 + N * 0.5, Y0 + N * 0.5) if (ox, oy) == (0, 0) else None
    for cx, cy in cs:
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                rosette((cx + ox) * N, (cy + oy) * N, N * (0.17 if big else 0.3))
    for cx, cy in ((0.5, 0.5), (0.0, 0.5), (0.5, 0.0), (0.0, 0.0)) if big else ((0.0, 0.0),):  # small flower heads between
        for ox in (0, 1):
            for oy in (0, 1):
                x_, y_ = (cx + ox) * N, (cy + oy) * N; R = N * 0.05
                for k in range(6):
                    a = 2 * math.pi * k / 6; dr.ellipse((x_ + R * math.cos(a) - R * 0.5, y_ + R * math.sin(a) - R * 0.5, x_ + R * math.cos(a) + R * 0.5, y_ + R * math.sin(a) + R * 0.5), fill=PINK)
                dr.ellipse((x_ - R * 0.5, y_ - R * 0.5, x_ + R * 0.5, y_ + R * 0.5), fill=GOLD)
    return embroider(im, LIN, seed)

# ---------------------------------------------------------------- ZARDEVOR (suzani frieze hung under the eaves), tile = 0.8 x 0.55 m
def zardevor(W=1600, H=1100):
    im = Image.new('RGB', (W, H), LIN); dr = ImageDraw.Draw(im)
    CR, GRN, IND, GOLD, PINK = (150, 26, 32), (58, 92, 58), (40, 44, 92), (204, 150, 52), (196, 84, 92)
    dr.rectangle((0, 0, W, 230), fill=CR)                                           # top band 0.115 m: red with a running vine
    for x in range(0, W, 100):
        dr.ellipse((x + 30, 80, x + 70, 120), fill=GOLD); dr.arc((x - 20, 60, x + 80, 170), 200, 340, fill=GRN, width=10)
    dr.line((0, 30, W, 30), fill=IND, width=12); dr.line((0, 205, W, 205), fill=IND, width=12)
    for k in range(2):                                                               # main field: 2 rosettes + 2 lancet medallions
        cx = 200 + 800 * k; cy = 520; R = 210
        for j in range(16):
            a = 2 * math.pi * j / 16; px, py = cx + R * 0.86 * math.cos(a), cy + R * 0.86 * math.sin(a)
            dr.ellipse((px - 40, py - 40, px + 40, py + 40), fill=(110, 16, 28))
        dr.ellipse((cx - R * .86, cy - R * .86, cx + R * .86, cy + R * .86), fill=CR); dr.ellipse((cx - R * .6, cy - R * .6, cx + R * .6, cy + R * .6), fill=LIN)
        dr.ellipse((cx - R * .42, cy - R * .42, cx + R * .42, cy + R * .42), fill=IND); dr.ellipse((cx - R * .25, cy - R * .25, cx + R * .25, cy + R * .25), fill=GOLD)
        mx = 600 + 800 * k
        dr.polygon([(mx, 290), (mx + 120, 520), (mx, 760), (mx - 120, 520)], fill=GRN); dr.polygon([(mx, 360), (mx + 70, 520), (mx, 690), (mx - 70, 520)], fill=PINK)
        for sx in (-1, 1): dr.arc((mx + sx * 130 - 90, 420, mx + sx * 130 + 90, 640), 0, 360, fill=GRN, width=12)
    dr.rectangle((0, 820, W, 860), fill=IND)
    for k in range(4):                                                                # 4 pointed tabs (geometry cuts the points)
        x0 = 400 * k; dr.polygon([(x0, 860), (x0 + 400, 860), (x0 + 200, H)], fill=CR)
        dr.polygon([(x0 + 60, 880), (x0 + 340, 880), (x0 + 200, H - 70)], fill=(110, 16, 28))
        dr.ellipse((x0 + 160, 900, x0 + 240, 980), fill=GOLD)
    return embroider(im, LIN, 9)

# ---------------------------------------------------------------- ADRAS (silk-cotton warp ikat), warp-feathered edges
def adras(N=1024, seed=5):
    r = np.random.default_rng(seed); im = Image.new('RGB', (N, N), (92, 22, 60)); dr = ImageDraw.Draw(im)
    cols = [(226, 178, 40), (232, 222, 196), (36, 112, 84), (190, 40, 50), (40, 50, 120)]
    cw = N // 4
    for i in range(4):
        cx = i * cw + cw // 2
        for j in range(4):
            cy = j * N // 4 + N // 8; c1, c2 = cols[(i + j) % 5], cols[(i + j + 2) % 5]
            dr.polygon([(cx, cy - 120), (cx + 100, cy), (cx, cy + 120), (cx - 100, cy)], fill=c1)            # comb-diamond
            dr.polygon([(cx, cy - 70), (cx + 55, cy), (cx, cy + 70), (cx - 55, cy)], fill=c2)
            dr.polygon([(cx, cy - 26), (cx + 20, cy), (cx, cy + 26), (cx - 20, cy)], fill=(92, 22, 60))
            for sy in (-1, 1): dr.rectangle((cx - 8, cy + sy * 120 - (14 if sy < 0 else 0), cx + 8, cy + sy * 120 + (14 if sy > 0 else 0)), fill=c1)
        dr.rectangle((i * cw - 6, 0, i * cw + 6, N), fill=cols[i % 5])                 # warp stripe between the columns
    a = np.asarray(im).copy(); out = np.empty_like(a)
    off = 0; x = 0
    while x < N:                                                                      # warp bundles shifted vertically: the ikat "bleed"
        w = int(r.integers(3, 9)); off = int(np.clip(off + r.integers(-5, 6), -14, 14))
        out[:, x:x + w] = np.roll(a[:, x:x + w], off, 0); x += w
    f = out.astype(np.float32)
    xx = np.arange(N); f *= (1 + 0.05 * np.sin(xx * math.pi / 1.5))[None, :, None]     # fine warp ribs
    f *= (1 + r.normal(0, 0.025, f.shape[:2]))[:, :, None]
    return Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))

# ---------------------------------------------------------------- canvas weave for the tent stripe, pile for velvet
def canvas(path, seed=2):
    a = np.asarray(Image.open(path).convert('RGB').resize((1024, 1024), Image.NEAREST), np.float32); r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:1024, 0:1024]
    a *= (1 + 0.05 * np.sign(np.sin(xx * math.pi / 2)) * np.sign(np.sin(yy * math.pi / 2)) + r.normal(0, 0.03, (1024, 1024)))[:, :, None]
    a *= (0.94 + 0.06 * lowfreq(1024, 1024, 8, seed))[:, :, None]                    # weathering
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5))
def velvet(path, seed=4):
    a = np.asarray(Image.open(path).convert('RGB').resize((1024, 1024), Image.BILINEAR), np.float32); r = np.random.default_rng(seed)
    a *= (0.88 + 0.16 * lowfreq(1024, 1024, 14, seed))[:, :, None]                   # crushed-pile shading
    a *= (1 + r.normal(0, 0.03, (1024, 1024)))[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))


# ---------------------------------------------------------------- PAKHTA (cotton-boll) porcelain: cobalt net, white bolls, gold dots
def pakhta(N=512):
    S_ = 4; im = Image.new('RGB', (N * S_, N * S_), (244, 244, 240)); dr = ImageDraw.Draw(im); c = (18, 40, 128); g = (196, 150, 60)
    n = 4; st = N * S_ / n
    for i in range(-1, n + 2):
        for j in range(-1, n + 2):
            cx, cy = (i + (0.5 if j % 2 else 0)) * st, j * st
            R = st * 0.36
            dr.polygon([(cx, cy - R), (cx + R, cy), (cx, cy + R), (cx - R, cy)], fill=c)                   # cobalt boll husk
            for a in range(4):
                an = a * math.pi / 2 + math.pi / 4; px, py = cx + R * 0.32 * math.cos(an), cy + R * 0.32 * math.sin(an)
                dr.ellipse((px - R * 0.3, py - R * 0.3, px + R * 0.3, py + R * 0.3), fill=(250, 250, 248), outline=c, width=S_ * 2)
            dr.ellipse((cx - R * 0.12, cy - R * 0.12, cx + R * 0.12, cy + R * 0.12), fill=g)
            dr.line((cx + R, cy, cx + st - R, cy), fill=c, width=S_ * 5)
    im = im.resize((N, N), Image.LANCZOS)
    a = np.asarray(im, np.float32) * (1 + np.random.default_rng(1).normal(0, 0.012, (N, N)))[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

if __name__ == '__main__':
    pakhta().save(os.path.join(OUT, 'pakhta.png'))
    pile(tekke(), 6, 11).save(os.path.join(OUT, 'rug_tekke.png')); print('rug_tekke')
    for i, src in enumerate(('carpet1', 'carpet2', 'carpet3', 'carpet4')):
        flatweave(palas_from(os.path.join(OUT, src + '.png')), 5, 4, 20 + i).save(os.path.join(OUT, f'palas{i + 1}.png')); print('palas', i + 1)
    for src in ('kilim', 'kilim2'):
        flatweave(palas_from(os.path.join(OUT, src + '.png'), 200, 200), 5, 4, 3).save(os.path.join(OUT, src + '_w.png')); print(src)
    suzani().save(os.path.join(OUT, 'suzani_w.png')); suzani(1024, 7, False).save(os.path.join(OUT, 'suzani_one.png')); print('suzani')
    zardevor().save(os.path.join(OUT, 'zardevor.png')); print('zardevor')
    adras().save(os.path.join(OUT, 'adras.png')); print('adras')
    canvas(os.path.join(OUT, 'tentstripe.png')).save(os.path.join(OUT, 'tentstripe_w.png'))
    velvet(os.path.join(OUT, 'velvet.png')).save(os.path.join(OUT, 'velvet_w.png'))
    for c_ in ('terra', 'navy', 'emerald', 'wine'): velvet(os.path.join(OUT, f'velvet_{c_}.png')).save(os.path.join(OUT, f'velvet_{c_}_w.png'))
    print('done')
