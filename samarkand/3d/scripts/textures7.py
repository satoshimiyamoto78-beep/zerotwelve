"""Floor tile textures after the owner's floor references (R12-v6):
  marblegrid  - white marble slabs on the diagonal, framed by cobalt + zellige-chip bands (ref: marble with mosaic grid)
  zfield      - Fes zellige: 8-fold rosettes on a navy ground (ref: zellige floor carpet), seamless 2 x 2 rosettes
  zcarpet_*   - framed zellige 'carpets' for the domes / court: cobalt lines, chip band, painted star-tile border (ref: tile border)
  alleyrun    - cream tile runner with the star-tile border for the alley
Everything is drawn as cut / painted tile pieces with grout, glaze jitter per piece and fine speckle (no generated ornament).
Usage: python3 textures7.py  ->  r3d/tex2/*.png"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex2')
rng = random.Random(7)
C = dict(white=(232, 228, 216), cobalt=(26, 42, 108), honey=(190, 128, 56), green=(38, 88, 66), black=(34, 33, 34), turq=(44, 118, 124),
         navy=(36, 44, 74), brown=(122, 70, 38), cream=(228, 216, 192), grout=(196, 190, 176))

def jit(c, a=0.07):
    k = 1 + rng.uniform(-a, a); t = rng.uniform(-a, a) * 40
    return tuple(int(max(0, min(255, v * k + t * (i == 2) * 0.3))) for i, v in enumerate(c))

def speckle(im, amt=5, blur=0.6):
    a = np.asarray(im).astype(np.float32); n = np.random.default_rng(3).normal(0, amt, a.shape[:2])[..., None]
    lo = np.random.default_rng(5).normal(0, 1, (a.shape[0] // 64 + 1, a.shape[1] // 64 + 1)).astype(np.float32)
    lo = np.asarray(Image.fromarray(((lo + 3) * 40).clip(0, 255).astype(np.uint8)).resize((a.shape[1], a.shape[0]), Image.BICUBIC)).astype(np.float32) / 40 - 3
    a = a * (1 + 0.008 * lo[..., None]) + n
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))

def pol(cx, cy, r, deg): return (cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg)))

def piece(d, pts, col, gw):
    d.polygon(pts, fill=jit(col), outline=C['grout'], width=gw)

def rosette(d, cx, cy, c, par, gw):
    """Fes 8-fold rosette: star, 8 white petals, 8 diamonds, 16-piece outer ring"""
    R1, r1, Rp, Rd, Ro = 0.16 * c, 0.085 * c, 0.33 * c, 0.40 * c, 0.47 * c
    ring = []
    for i in range(16):
        a0, a1 = i * 22.5, (i + 1) * 22.5; am = (a0 + a1) / 2
        z0 = pol(cx, cy, Rd if i % 2 == 0 else Rp, a0); z1 = pol(cx, cy, Rd if (i + 1) % 2 == 0 else Rp, a1)
        zm = pol(cx, cy, (Rd + Rp) / 2 + 0.01 * c, am)                              # each ring cell cut in two chips
        piece(d, [z0, zm, pol(cx, cy, Ro, am), pol(cx, cy, Ro, a0)], C['white'] if i % 2 else C['black'], gw)
        piece(d, [zm, z1, pol(cx, cy, Ro, a1), pol(cx, cy, Ro, am)], C['black'] if i % 2 else C['white'], gw)
    for k in range(8):
        th, ph = k * 45 + 22.5, k * 45
        piece(d, [pol(cx, cy, r1, th), pol(cx, cy, R1, th - 22.5), pol(cx, cy, Rp, th), pol(cx, cy, R1, th + 22.5)], C['white'], gw)
        piece(d, [pol(cx, cy, R1, ph), pol(cx, cy, Rp, ph - 22.5), pol(cx, cy, Rd, ph), pol(cx, cy, Rp, ph + 22.5)], C['cobalt'] if (par or k % 2) else C['green'], gw)
    star = [pol(cx, cy, R1 if j % 2 == 0 else r1, j * 22.5) for j in range(16)]
    piece(d, star, C['honey'] if par else C['cobalt'], gw)
    piece(d, [pol(cx, cy, 0.045 * c, j * 45 + 22.5) for j in range(8)], C['white'], max(1, gw // 2))

def corner_star(d, cx, cy, c, gw):
    piece(d, [pol(cx, cy, 0.20 * c if j % 2 == 0 else 0.10 * c, j * 22.5 + 11.25) for j in range(16)], C['white'], gw)
    piece(d, [pol(cx, cy, 0.06 * c, j * 45) for j in range(8)], C['honey'], max(1, gw // 2))

def zellige(d, x0, y0, x1, y1, c, off=(0.5, 0.5), gw=3):
    """rosette lattice clipped to the box (draw on an oversize layer, then the caller crops)"""
    d.rectangle([x0, y0, x1, y1], fill=C['navy'])
    nx0, nx1 = int((x0 - x1) / c) - 2, int((x1 - x0) / c) + 2
    for i in range(-int(x1 / c) - 2, int(x1 / c) + 3):
        for j in range(-int(y1 / c) - 2, int(y1 / c) + 3):
            cx, cy = x0 + (i + off[0]) * c, y0 + (j + off[1]) * c
            if cx < x0 - c or cx > x1 + c or cy < y0 - c or cy > y1 + c: continue
            corner_star(d, cx + c / 2, cy + c / 2, c, gw)
    for i in range(-int(x1 / c) - 2, int(x1 / c) + 3):
        for j in range(-int(y1 / c) - 2, int(y1 / c) + 3):
            cx, cy = x0 + (i + off[0]) * c, y0 + (j + off[1]) * c
            if cx < x0 - c or cx > x1 + c or cy < y0 - c or cy > y1 + c: continue
            rosette(d, cx, cy, c, (i + j) % 2 == 0, gw)

def star_tile(d, x, y, s, gw, rot=0):
    """hand-painted 24 cm border tile (ref: cream tile with cobalt 8-point star and corner quarter rosettes)"""
    piece(d, [(x, y), (x + s, y), (x + s, y + s), (x, y + s)], C['cream'], gw)
    cx, cy = x + s / 2, y + s / 2
    for (qx, qy, a0) in ((x, y, 0), (x + s, y, 90), (x + s, y + s, 180), (x, y + s, 270)):     # corner quarter-diamonds, blue
        pts = [(qx, qy)] + [pol(qx, qy, 0.26 * s, a0 + t) for t in (0, 45, 90)]
        d.polygon(pts, fill=jit(C['cobalt'], 0.04))
    sq1 = [pol(cx, cy, 0.40 * s, 45 + 90 * j) for j in range(4)]; sq2 = [pol(cx, cy, 0.40 * s, 90 * j) for j in range(4)]
    d.polygon(sq1, fill=jit(C['cobalt'], 0.04)); d.polygon(sq2, fill=jit(C['cobalt'], 0.04))
    star_in = [pol(cx, cy, 0.31 * s if j % 2 == 0 else 0.20 * s, j * 22.5) for j in range(16)]
    d.polygon(star_in, fill=jit(C['white'], 0.03))
    d.polygon([pol(cx, cy, 0.16 * s if j % 2 == 0 else 0.07 * s, j * 45 + 22.5 * (j % 2)) for j in range(8)], fill=jit(C['honey'], 0.05))
    for j in range(8):                                                               # brush-line petals
        a = j * 45 + 22.5; d.line([pol(cx, cy, 0.09 * s, a), pol(cx, cy, 0.25 * s, a)], fill=jit(C['cobalt'], 0.05), width=max(1, int(0.012 * s)))
    d.rectangle([x, y, x + s, y + s], outline=C['grout'], width=gw)

def chip_band(d, x0, y0, L, w, horiz, gw):
    """cobalt / zellige chip band (ref 4): cobalt strip, diamond chips alternating colour / white, cobalt strip"""
    cs = 0.16 * w; m0, m1 = cs, w - cs; h = (m1 - m0) / 2
    seq = [C['black'], C['honey'], C['green'], C['brown']]
    def P(s, t): return (x0 + s, y0 + t) if horiz else (x0 + t, y0 + s)
    n = int(L / (6 * cs)) + 1
    for k in range(n):                                                              # cobalt strips cut in 6-chip lengths
        for t0, t1 in ((0, cs), (m1, w)):
            s0, s1 = k * 6 * cs, min(L, (k + 1) * 6 * cs)
            piece(d, [P(s0, t0), P(s1, t0), P(s1, t1), P(s0, t1)], C['cobalt'], gw)
    piece(d, [P(0, m0), P(L, m0), P(L, m1), P(0, m1)], C['white'], gw)
    k = 0; s = h
    while s - h < L:
        col = seq[k % 4] if k % 2 == 0 else C['white']
        pts = [P(max(0, min(L, s - h)), m0 + h), P(max(0, min(L, s)), m0), P(max(0, min(L, s + h)), m0 + h), P(max(0, min(L, s)), m1)]
        piece(d, pts, col, gw); s += 2 * h; k += 1

def frame(d, x0, y0, x1, y1, ppm, gw, tile=0.24):
    """carpet frame from outside in: cobalt 3 cm, chip band 8 cm, cobalt 3 cm, painted star tiles, cobalt 3 cm. returns inner box"""
    def cob(a0, b0, a1, b1):
        L = max(a1 - a0, b1 - b0); n = max(1, int(L / (0.30 * ppm)))
        for k in range(n):
            if a1 - a0 > b1 - b0: piece(d, [(a0 + (a1 - a0) * k / n, b0), (a0 + (a1 - a0) * (k + 1) / n, b0), (a0 + (a1 - a0) * (k + 1) / n, b1), (a0 + (a1 - a0) * k / n, b1)], C['cobalt'], gw)
            else: piece(d, [(a0, b0 + (b1 - b0) * k / n), (a1, b0 + (b1 - b0) * k / n), (a1, b0 + (b1 - b0) * (k + 1) / n), (a0, b0 + (b1 - b0) * (k + 1) / n)], C['cobalt'], gw)
    def ring(w):
        nonlocal x0, y0, x1, y1
        cob(x0, y0, x1, y0 + w); cob(x0, y1 - w, x1, y1); cob(x0, y0 + w, x0 + w, y1 - w); cob(x1 - w, y0 + w, x1, y1 - w)
        x0 += w; y0 += w; x1 -= w; y1 -= w
    ring(0.03 * ppm)
    w = 0.08 * ppm
    chip_band(d, x0 + w, y0, x1 - x0 - 2 * w, w, True, gw); chip_band(d, x0 + w, y1 - w, x1 - x0 - 2 * w, w, True, gw)
    chip_band(d, x0, y0 + w, y1 - y0 - 2 * w, w, False, gw); chip_band(d, x1 - w, y0 + w, y1 - y0 - 2 * w, w, False, gw)
    for (cx, cy) in ((x0, y0), (x1 - w, y0), (x0, y1 - w), (x1 - w, y1 - w)):
        piece(d, [(cx, cy), (cx + w, cy), (cx + w, cy + w), (cx, cy + w)], C['cobalt'], gw)
        piece(d, [(cx + w / 2, cy + w * 0.2), (cx + w * 0.8, cy + w / 2), (cx + w / 2, cy + w * 0.8), (cx + w * 0.2, cy + w / 2)], C['honey'], gw)
    x0 += w; y0 += w; x1 -= w; y1 -= w
    ring(0.03 * ppm)
    s = tile * ppm                                                                  # star tiles: whole tiles at the corners, stretched evenly along
    for side in range(4):
        L = (x1 - x0 - 2 * s) if side < 2 else (y1 - y0 - 2 * s); n = max(1, round(L / s)); st = L / n
        for k in range(n):
            if side == 0: star_tile(d, x0 + s + k * st, y0, st, gw)
            if side == 1: star_tile(d, x0 + s + k * st, y1 - st, st, gw)
            if side == 2: star_tile(d, x0, y0 + s + k * st, st, gw)
            if side == 3: star_tile(d, x1 - st, y0 + s + k * st, st, gw)
    for (cx, cy) in ((x0, y0), (x1 - s, y0), (x0, y1 - s), (x1 - s, y1 - s)): star_tile(d, cx, cy, s, gw)
    x0 += s; y0 += s; x1 -= s; y1 -= s
    ring(0.03 * ppm)
    return x0, y0, x1, y1

def carpet(name, W, H, ppm, field='zellige', c=0.30):
    ppm *= 2
    im = Image.new('RGB', (int(W * ppm), int(H * ppm)), C['grout']); d = ImageDraw.Draw(im); gw = max(2, int(0.0028 * ppm))
    x0, y0, x1, y1 = frame(d, 0, 0, im.width, im.height, ppm, gw)
    if field == 'zellige':
        lay = Image.new('RGB', im.size, C['grout']); dl = ImageDraw.Draw(lay)
        cpx = c * ppm; fx, fy = (x0 + x1) / 2, (y0 + y1) / 2
        zellige(dl, x0, y0, x1, y1, cpx, off=(((fx - x0) / cpx) % 1, ((fy - y0) / cpx) % 1), gw=gw)
        im.paste(lay.crop((int(x0), int(y0), int(x1), int(y1))), (int(x0), int(y0)))
    else:                                                                           # cream 30 cm field tiles, laid straight
        t = 0.30 * ppm; nx = max(1, round((x1 - x0) / t)); ny = max(1, round((y1 - y0) / t))
        for i in range(nx):
            for j in range(ny):
                piece(d, [(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny), (x0 + (x1 - x0) * (i + 1) / nx, y0 + (y1 - y0) * j / ny),
                          (x0 + (x1 - x0) * (i + 1) / nx, y0 + (y1 - y0) * (j + 1) / ny), (x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * (j + 1) / ny)], C['cream'], gw)
    im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    im = speckle(im); im.save(os.path.join(OUT, name + '.png')); print(name, im.size)

def zfield(name, c_px=1024, n=2):
    S_ = c_px * n; lay = Image.new('RGB', (S_ * 3, S_ * 3), C['grout']); d = ImageDraw.Draw(lay)
    zellige(d, 0, 0, S_ * 3, S_ * 3, c_px, off=(0.0, 0.0), gw=6)
    im = lay.crop((S_, S_, 2 * S_, 2 * S_)).resize((S_ // 2, S_ // 2), Image.LANCZOS); im = speckle(im); im.save(os.path.join(OUT, name + '.png')); print(name, im.size)

# ---- marble slabs on the diagonal with chip bands (numpy, per pixel) ----
def fbm(n, octaves=6, seed=0):
    g = np.random.default_rng(seed); out = np.zeros((n, n), np.float32); amp = 1.0
    for o in range(octaves):
        k = 4 * 2 ** o; z = g.normal(0, 1, (k, k)).astype(np.float32)
        z = np.tile(z, (2, 2))[:k + 1, :k + 1]                                       # wrap -> seamless
        up = np.asarray(Image.fromarray(((z + 4) * 30).clip(0, 255).astype(np.uint8)).resize((n + n // k, n + n // k), Image.BICUBIC)).astype(np.float32)[:n, :n] / 30 - 4
        out += amp * up; amp *= 0.5
    return out
def marblegrid(name, N=2048, a=0.50, w=0.09, reps=2):
    p = a + w; T = reps * p * math.sqrt(2); px = T / N
    u, v = np.meshgrid((np.arange(N) + 0.5) * px, (np.arange(N) + 0.5) * px)
    s = (u + v) / math.sqrt(2); t = (v - u) / math.sqrt(2)                          # grid coordinates (45 deg)
    si, ti = np.floor(s / p), np.floor(t / p); ls, lt = s - si * p, t - ti * p        # local; band occupies [a, a + w)
    # marble: turbulence veins, one random orientation / offset per slab
    F = fbm(N, seed=11); F2 = fbm(N, seed=12)
    rnd = np.random.default_rng(4); key = (si.astype(int) * 7 + ti.astype(int) * 13) % 97
    ang = rnd.uniform(0, math.pi, 97)[key]; ph = rnd.uniform(0, 10, 97)[key]; tint = rnd.uniform(-0.04, 0.04, 97)[key]
    x = (ls * np.cos(ang) + lt * np.sin(ang)) * 9 + ph
    v1 = np.exp(-np.abs(np.sin(x + 3.6 * F)) * 22); v2 = np.exp(-np.abs(np.sin(x * 2.1 + 5.5 * F2 + 1)) * 40)
    v3 = np.exp(-np.abs(np.sin(x * 0.7 + 2.5 * F2 + 2.0 * F)) * 9)
    base = np.array([238, 236, 231], np.float32); vc = np.array([128, 130, 138], np.float32)
    mv = (0.55 * v1 + 0.35 * v2 + 0.12 * v3 + 0.03 * (F - F.min()) / (np.ptp(F) + 1e-6)).clip(0, 0.8)
    img = base[None, None] * (1 + tint[..., None] + 0.015 * F[..., None]) * (1 - mv[..., None]) + vc[None, None] * mv[..., None]
    gr = np.array(C['grout'], np.float32); g = 0.003
    def band_pix(q, r, bi):                                                          # q along the band, r across in [0, w)
        cs = 0.16 * w; m0, m1 = cs, w - cs; h = (m1 - m0) / 2
        out = np.zeros(q.shape + (3,), np.float32); grt = np.zeros(q.shape, bool)
        cob = (r < cs) | (r >= m1); out[cob] = C['cobalt']
        grt |= (np.abs(r - cs) < g / 2) | (np.abs(r - m1) < g / 2) | (r < g / 2) | (np.abs(r - w) < g / 2)
        grt |= cob & (np.abs(((q / (6 * cs)) % 1) - 0.5) > 0.5 - g / (12 * cs))
        k = np.floor(q / (2 * h)); dq = q - (k + 0.5) * 2 * h; dr = r - (m0 + h)
        dia = np.abs(dq) + np.abs(dr) < h; mid = ~cob
        seq = np.array([C['black'], C['honey'], C['green'], C['brown']], np.float32)
        colk = ((k.astype(int) + bi.astype(int) * 3) % 4)
        out[mid] = C['white']; sel = mid & dia & (k.astype(int) % 2 == 0); out[sel] = seq[colk[sel]]
        grt |= mid & (np.abs(np.abs(dq) + np.abs(dr) - h) < g * 0.6)
        return out, grt
    inS, inT = ls >= a, lt >= a
    bs, gs = band_pix(t, ls - a, si); bt, gt = band_pix(s, lt - a, ti)
    img = np.where(inS[..., None] & ~inT[..., None], bs, img); img = np.where(inT[..., None] & ~inS[..., None], bt, img)
    cross = inS & inT; cx_, cy_ = ls - a - w / 2, lt - a - w / 2
    img = np.where(cross[..., None], np.array(C['cobalt'], np.float32), img)
    cc = cross & (np.abs(cx_) + np.abs(cy_) < w * 0.32); img[cc] = C['honey']
    grt = (inS & ~inT & gs) | (inT & ~inS & gt) | (cross & ((np.abs(np.abs(cx_) + np.abs(cy_) - w * 0.32) < g * 0.6) | (np.maximum(np.abs(cx_), np.abs(cy_)) > w / 2 - g / 2)))
    grt |= (~inS & ~inT) & ((ls < g / 2) | (lt < g / 2) | (np.abs(ls - a) < g / 2) | (np.abs(lt - a) < g / 2))
    img[grt] = gr
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8)); im = speckle(im, 3, 0.5); im.save(os.path.join(OUT, name + '.png')); print(name, im.size, 'tile m', round(T, 4))
    return T

if __name__ == '__main__':
    import sys
    if 'nomarble' not in sys.argv:
        T = marblegrid('marblegrid'); open(os.path.join(OUT, 'marblegrid.size'), 'w').write(str(T))
        zfield('zfield')                               # 2 x 2 rosettes, c = 0.30 m -> 0.60 m tile
    carpet('zcarpet', 3.6, 3.6, 1000)                  # under the karbandi dome and the south dome
    carpet('alleyrun', 6.31, 2.5, 620, field='cream')
