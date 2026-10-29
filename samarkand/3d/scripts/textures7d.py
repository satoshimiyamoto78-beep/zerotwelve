"""Plane-tree (chinar) leaf atlas with alpha (2 x 2 leaves, 5-lobed, veins, colour variation) and mottled chinar bark.
Usage: python3 textures7d.py -> tex2/platanleaf.png (RGBA), tex2/platanbark.png"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex2'); R = random.Random(5)
N = 1024; atlas = Image.new('RGBA', (N, N), (60, 90, 40, 0))
TIPS = (0.0, 0.85, -0.85, 1.75, -1.75)
def leaf(cx, cy, s, col, ang):
    im = Image.new('RGBA', (N // 2, N // 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = N // 4
    pts = []
    for k in range(361):                                      # 5 pointed lobes: r(t) with sharp tips
        t = math.radians(k); dt_ = [((t - (math.pi / 2 + o) + math.pi) % (2 * math.pi)) - math.pi for o in TIPS]
        lob = max(math.exp(-(d_ / 0.24) ** 2) * w_ for d_, w_ in zip(dt_, (1, .9, .9, .62, .62)))
        r = s * (0.38 + 0.62 * lob + 0.02 * math.sin(48 * t))
        pts.append((c + r * math.cos(t), c - r * math.sin(t)))
    d.polygon(pts, fill=col + (255,))
    for k in range(5):                                        # palmate veins from the petiole
        t = math.pi / 2 + TIPS[k]; d.line([(c, c + s * 0.15), (c + s * 0.95 * math.cos(t), c - s * 0.95 * math.sin(t))], fill=tuple(min(255, v + 38) for v in col) + (255,), width=3)
    d.line([(c, c + s * 0.15), (c, c + s * 0.55)], fill=(110, 120, 60, 255), width=4)          # petiole
    a = np.asarray(im).astype(np.float32); n = np.random.default_rng(R.randint(0, 99)).normal(0, 9, a.shape[:2])
    a[..., :3] += n[..., None] * (a[..., 3:4] > 0)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).rotate(ang, resample=Image.BICUBIC)
cols = [(58, 98, 38), (74, 112, 44), (52, 86, 34), (88, 120, 52)]
for i in range(2):
    for j in range(2):
        L = leaf(0, 0, N * 0.21, cols[i * 2 + j], R.uniform(-10, 10)); atlas.alpha_composite(L, (i * N // 2, j * N // 2))
atlas.save(os.path.join(OUT, 'platanleaf.png')); print('platanleaf')
# bark: grey-olive base with cream / ochre flaking patches (Platanus orientalis)
M = 1024; rng = np.random.default_rng(11)
def fbm(n, oct_=5, seed=0):
    g = np.random.default_rng(seed); out = np.zeros((n, n), np.float32); amp = 1
    for o in range(oct_):
        k = 4 * 2 ** o; z = g.normal(0, 1, (k + 1, k + 1)).astype(np.float32); z[-1] = z[0]; z[:, -1] = z[:, 0]
        out += amp * np.asarray(Image.fromarray(((z + 4) * 30).clip(0, 255).astype(np.uint8)).resize((n + n // k, n + n // k), Image.BICUBIC)).astype(np.float32)[:n, :n] / 30; amp *= .5
    return out
f1, f2, f3 = fbm(M, seed=1), fbm(M, seed=2), fbm(M, 6, seed=3)
base = np.array([118, 112, 92], np.float32); cream = np.array([206, 194, 158], np.float32); ochre = np.array([170, 146, 96], np.float32); dark = np.array([86, 84, 70], np.float32)
img = base + (f3 - f3.mean())[..., None] * 6
img = np.where((f1 > np.percentile(f1, 62))[..., None], cream + (f3 - f3.mean())[..., None] * 4, img)
img = np.where((f2 > np.percentile(f2, 78))[..., None], ochre, img)
edge = (np.abs(f1 - np.percentile(f1, 62)) < 0.04) | (np.abs(f2 - np.percentile(f2, 78)) < 0.04)
img[edge] = dark
Image.fromarray(img.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)).save(os.path.join(OUT, 'platanbark.png')); print('platanbark')

# ---- narrow-leaf atlas (pomegranate / plumeria / jasmine / herbs): lanceolate leaves, midrib, 4 tints
nl = Image.new('RGBA', (N, N), (0, 0, 0, 0))
for i in range(2):
    for j in range(2):
        im = Image.new('RGBA', (N // 2, N // 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = N // 4; col = [(54, 96, 40), (70, 118, 46), (44, 84, 36), (84, 126, 52)][i * 2 + j]
        for k, (ang, L, W) in enumerate(((0, 0.98, 0.12), (58, 0.62, 0.1), (-58, 0.62, 0.1))):   # a sprig of three leaves
            pts = []
            for t in range(41):
                u = t / 40; w = W * math.sin(math.pi * u) ** 0.8
                pts.append((u * L, w))
            pts = pts + [(u, -w) for u, w in reversed(pts)]
            a = math.radians(90 + ang); ca, sa = math.cos(a), math.sin(a)
            P_ = [(c + (x * ca - y * sa) * c * 1.75, c + c * 0.92 - (x * sa + y * ca) * c * 1.75) for x, y in pts]
            d.polygon(P_, fill=col + (255,))
            d.line([P_[0], (c + L * ca * c * 1.75, c + c * 0.92 - L * sa * c * 1.75)], fill=tuple(min(255, v + 45) for v in col) + (255,), width=3)
        nl.alpha_composite(im, (i * N // 2, j * N // 2))
nl.save(os.path.join(OUT, 'narrowleaf.png')); print('narrowleaf')
# ---- flower atlas: plumeria (cream, yellow eye), bougainvillea bracts (magenta), jasmine (white star), pomegranate flower (scarlet)
fl = Image.new('RGBA', (N, N), (0, 0, 0, 0))
def flower(ox, oy, petals, rr, col, eye, shape='round'):
    d = ImageDraw.Draw(fl); c = (ox + N // 4, oy + N // 4)
    for k in range(petals):
        a = 2 * math.pi * k / petals + (0.3 if shape == 'twist' else 0)
        px, py = c[0] + rr * 0.55 * math.cos(a), c[1] + rr * 0.55 * math.sin(a)
        if shape == 'star': d.polygon([c, (c[0] + rr * math.cos(a - .25), c[1] + rr * math.sin(a - .25)), (c[0] + rr * 1.05 * math.cos(a), c[1] + rr * 1.05 * math.sin(a)), (c[0] + rr * math.cos(a + .25), c[1] + rr * math.sin(a + .25))], fill=col)
        else: d.ellipse([px - rr * 0.48, py - rr * 0.48, px + rr * 0.48, py + rr * 0.48], fill=col)
    d.ellipse([c[0] - rr * 0.2, c[1] - rr * 0.2, c[0] + rr * 0.2, c[1] + rr * 0.2], fill=eye)
flower(0, 0, 5, N * 0.2, (246, 238, 214, 255), (238, 190, 60, 255), 'twist')
flower(N // 2, 0, 3, N * 0.22, (196, 30, 112, 255), (236, 226, 190, 255))
flower(0, N // 2, 6, N * 0.18, (250, 250, 246, 255), (236, 226, 170, 255), 'star')
flower(N // 2, N // 2, 6, N * 0.18, (214, 52, 30, 255), (240, 170, 60, 255))
fl.save(os.path.join(OUT, 'flowers.png')); print('flowers')

# ---- kids corner soft floor: EPDM granules, terracotta field with a turquoise / saffron 8-point star grid (2.0 m tile)
K = 1024; g = np.random.default_rng(21)
base = np.array([178, 88, 58], np.float32); img = np.ones((K, K, 3), np.float32) * base
kim = Image.new('L', (K, K), 0); dk = ImageDraw.Draw(kim); kim2 = Image.new('L', (K, K), 0); dk2 = ImageDraw.Draw(kim2)
for i in range(2):
    for j in range(2):
        cx, cy = (i + .5) * K / 2, (j + .5) * K / 2; R0 = K * 0.17
        dk.polygon([(cx + (R0 if k % 2 == 0 else R0 * .55) * math.cos(math.radians(22.5 * k)), cy + (R0 if k % 2 == 0 else R0 * .55) * math.sin(math.radians(22.5 * k))) for k in range(16)], fill=255)
        dk2.ellipse([cx - R0 * .3, cy - R0 * .3, cx + R0 * .3, cy + R0 * .3], fill=255)
for k in range(5): dk.line([(k * K / 2 - 6, 0), (k * K / 2 - 6, K)], fill=255, width=10); dk.line([(0, k * K / 2 - 6), (K, k * K / 2 - 6)], fill=255, width=10)
m1 = np.asarray(kim, np.float32)[..., None] / 255; m2 = np.asarray(kim2, np.float32)[..., None] / 255
img = img * (1 - m1) + np.array([46, 140, 146], np.float32) * m1
img = img * (1 - m2) + np.array([232, 170, 60], np.float32) * m2
gran = g.random((K, K)) ; img *= (0.86 + 0.28 * gran)[..., None]
Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(os.path.join(OUT, 'kidsfloor.png')); print('kidsfloor')

# ---- dark walnut grain (quarter-sawn: long streaks, ray flecks), 1.0 m tile, stretched along u
W_ = 1024; g = np.random.default_rng(31)
def fb1(n, oct_, seed):
    gg = np.random.default_rng(seed); out = np.zeros((n, n), np.float32); amp = 1
    for o in range(oct_):
        k = 4 * 2 ** o; z = gg.normal(0, 1, (k + 1, k + 1)).astype(np.float32); z[-1] = z[0]; z[:, -1] = z[:, 0]
        out += amp * np.asarray(Image.fromarray(((z + 4) * 30).clip(0, 255).astype(np.uint8)).resize((n + n // k, n + n // k), Image.BICUBIC)).astype(np.float32)[:n, :n] / 30; amp *= .5
    return out
f = fb1(W_, 6, 41); yy = np.arange(W_)[:, None] / W_
streak = np.sin((yy * 60 + f * 1.5) * math.pi) * 0.5 + 0.5
streak = 0.75 * streak ** 3 + 0.3 * (np.sin((yy * 230 + f * 2.5) * math.pi) * 0.5 + 0.5) ** 6
base = np.array([62, 36, 20], np.float32); dark = np.array([34, 19, 11], np.float32); light = np.array([92, 58, 34], np.float32)
img = base[None, None] * (1 - streak[..., None]) + dark[None, None] * streak[..., None]
fl_ = fb1(W_, 6, 43); img += (light - base)[None, None] * np.clip(fl_ - fl_.mean() - 0.25, 0, 1)[..., None] * 0.35
img *= (0.94 + 0.12 * g.random((W_, W_)))[..., None] ** 0.3
im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((W_, W_ // 4)).resize((W_, W_))   # stretch along u
im.save(os.path.join(OUT, 'walnutgrain.png')); print('walnutgrain')
# ---- light oak / elm grain (same figure, honey tones) for decks, tapchans, booth frames
base = np.array([146, 100, 60], np.float32); dark = np.array([100, 64, 36], np.float32); light = np.array([178, 128, 80], np.float32)
img = base[None, None] * (1 - streak[..., None]) + dark[None, None] * streak[..., None]
img += (light - base)[None, None] * np.clip(fl_ - fl_.mean() - 0.25, 0, 1)[..., None] * 0.35
img *= (0.94 + 0.12 * g.random((W_, W_)))[..., None] ** 0.3
Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((W_, W_ // 4)).resize((W_, W_)).save(os.path.join(OUT, 'oakgrain.png')); print('oakgrain')
