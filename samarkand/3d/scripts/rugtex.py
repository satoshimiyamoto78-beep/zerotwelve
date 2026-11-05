"""procedural hand-knotted rug textures (owner: "текстура ковров ужасная"): knot grid with per-knot pile shading, dark outlines,
abrash bands, wear, multi-band borders; Persian medallion, Tekke gul and a Bukhara-style allover.
usage: python3 rugtex.py OUTDIR"""
import sys, os, math
import numpy as np
from PIL import Image, ImageFilter
rng = np.random.default_rng(3)
OUT = sys.argv[1]

def noise2(h, w, scale, seed):
    r = np.random.default_rng(seed); g = r.random((int(h / scale) + 3, int(w / scale) + 3))
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((w + int(2 * scale), h + int(2 * scale)), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)[:h, :w] / 255.0

def finish(cls, pal, KH, KW, px=5, seed=0, outline=True, worn=0.25):
    """class map (KH x KW knots) -> RGB image with knot shading"""
    cls = cls.astype(np.int32); col = pal[cls].astype(np.float32)
    if outline:   # dark brown outline where neighbouring knots change class (except within the field ground)
        e = np.zeros(cls.shape, bool)
        e[1:, :] |= cls[1:, :] != cls[:-1, :]; e[:, 1:] |= cls[:, 1:] != cls[:, :-1]
        col[e] = col[e] * 0.35 + np.array([40, 22, 18]) * 0.65
    # abrash: horizontal dye-lot bands along the length
    ab = noise2(KH, 1, 9, seed + 1)[:, :1] * 0.16 - 0.08; col *= (1 + ab)[:, :, None] if ab.ndim == 2 else 1
    col *= (1 + (noise2(KH, KW, 3, seed + 2) - 0.5) * 0.12)[:, :, None]
    wear = noise2(KH, KW, 40, seed + 3); wear = np.clip((wear - 0.55) * 2.5, 0, 1) * worn
    col = col * (1 - wear[:, :, None] * 0.35) + np.array([190, 165, 130]) * wear[:, :, None] * 0.35
    img = np.repeat(np.repeat(col, px, 0), px, 1)
    yy, xx = np.mgrid[0:px, 0:px] / (px - 1) - 0.5
    knot = 1.0 - 0.16 * (np.abs(xx) * 1.6) ** 2 - 0.1 * (yy * 2) ** 2           # each knot a rounded tuft, darker at its edges
    img *= np.tile(knot, (KH, KW))[:, :, None]
    fib = np.asarray(Image.fromarray((rng.random((KH * px, KW * px)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    img *= (0.9 + 0.2 * fib)[:, :, None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

def border_frame(KH, KW, bw):
    """distance-to-edge maps for borders: returns (d, s) d = knots from the outer edge, s = coordinate along the edge"""
    y, x = np.mgrid[0:KH, 0:KW]
    d = np.minimum(np.minimum(x, KW - 1 - x), np.minimum(y, KH - 1 - y)).astype(np.float32)
    along_x = np.minimum(y, KH - 1 - y) < np.minimum(x, KW - 1 - x)
    s = np.where(along_x, x, y).astype(np.float32)
    return d, s

def borders(cls, KH, KW, pal_ids, main=18):
    """outer guard | main border with rosettes + meander vine | inner guard. pal_ids = dict(ground, guard, gdot, rose, vine, mainbg)"""
    d, s = border_frame(KH, KW, main)
    g1 = (d < 5); cls[g1] = pal_ids['guard']
    cls[(d >= 1.5) & (d < 3.5) & ((s.astype(int) // 3) % 2 == 0)] = pal_ids['gdot']
    mb = (d >= 5) & (d < 5 + main); cls[mb] = pal_ids['mainbg']
    t = (d - 5) / main - 0.5                                           # -0.5..0.5 across the main border
    per = main * 1.6; ph = (s % per) / per
    vine = np.abs(t - 0.32 * np.sin(2 * math.pi * s / per)) < 0.07
    cls[mb & vine] = pal_ids['vine']
    rr = np.hypot((ph - 0.5) * per / main, t)                           # rosette every period
    ang = np.arctan2(t, (ph - 0.5) * per / main)
    petal = rr < 0.32 * (0.75 + 0.25 * np.cos(8 * ang))
    cls[mb & petal] = pal_ids['rose']; cls[mb & (rr < 0.1)] = pal_ids['gdot']
    g2 = (d >= 5 + main) & (d < 9 + main); cls[g2] = pal_ids['guard']
    cls[g2 & ((s.astype(int) // 2) % 3 == 0)] = pal_ids['gdot']
    return 9 + main

def persian(KH=540, KW=360, seed=0, red=True):
    # palette: 0 madder red, 1 indigo, 2 ivory, 3 saffron, 4 teal, 5 rose, 6 dark brown, 7 light blue
    pal = np.array([[128, 22, 26], [24, 34, 70], [222, 206, 172], [196, 140, 50], [38, 98, 96], [190, 92, 88], [52, 28, 22], [110, 140, 170]], np.float32)
    if not red: pal[[0, 1]] = pal[[1, 0]]
    cls = np.zeros((KH, KW), np.int32)
    inset = borders(cls, KH, KW, dict(guard=6, gdot=3, rose=0, vine=2, mainbg=1))
    y, x = np.mgrid[0:KH, 0:KW].astype(np.float32)
    u = (x - KW / 2) / (KW / 2 - inset); v = (y - KH / 2) / (KH / 2 - inset)
    field = (np.abs(u) < 1) & (np.abs(v) < 1)
    au, av = np.abs(u), np.abs(v)
    # allover floral: mirrored vine scrolls + small palmettes
    vine = np.abs(np.sin(15.0 * au + 2.6 * np.sin(11.0 * av)) * np.cos(13.0 * av - 2.0 * np.sin(9.0 * au))) < 0.06
    cls[field & vine] = 2
    vine2 = np.abs(np.sin(23.0 * au - 3.0 * np.sin(17.0 * av + 1.0))) < 0.05
    cls[field & vine2 & ~vine] = 5
    pu, pv = (au * 10.0) % 1 - 0.5, (av * 14.0) % 1 - 0.5; pr = np.hypot(pu, pv); pa = np.arctan2(pv, pu)
    palm = pr < 0.22 * (0.7 + 0.3 * np.cos(6 * pa)); cls[field & palm] = 3; cls[field & (pr < 0.07)] = 4
    # corner spandrels
    cr = np.hypot((1 - au) * 1.0, (1 - av) * 0.66); spand = field & (cr < 0.42 + 0.05 * np.cos(10 * np.arctan2(1 - av, 1 - au)))
    cls[spand] = 1; cls[spand & (np.abs(np.sin(30 * cr)) < 0.3)] = 7; cls[spand & (cr < 0.12)] = 3
    # central medallion: lobed layers + radial petals + pendants
    r = np.hypot(u * 1.0, v * 0.66); a = np.arctan2(v * 0.66, u)
    lob = 0.5 * (1 + 0.16 * np.cos(8 * a) + 0.06 * np.cos(16 * a))
    med = field & (r < lob); cls[med] = 2
    cls[field & (r < lob * 0.92) & (r > lob * 0.86)] = 6
    inner = field & (r < lob * 0.84); cls[inner] = 1
    cls[inner & (np.cos(24 * a + 18 * r) > 0.5)] = 4
    cls[inner & (np.abs(np.sin(40 * r)) < 0.15)] = 7
    cls[field & (r < lob * 0.5)] = 0
    cls[field & (r < lob * 0.5) & (np.cos(16 * a) * np.cos(45 * r) > 0.35)] = 3
    cls[field & (r < 0.08)] = 2
    pend = field & (au < 0.09 * (1 - (av - 0.5) / 0.2)) & (av > 0.5) & (av < 0.7); cls[pend] = 2
    return finish(cls, pal, KH, KW, px=4, seed=seed)

def tekke(KH=360, KW=240, seed=5):
    pal = np.array([[118, 18, 22], [30, 20, 26], [214, 196, 160], [168, 62, 38], [36, 60, 92], [92, 14, 18], [52, 28, 22], [196, 140, 60]], np.float32)
    cls = np.zeros((KH, KW), np.int32)
    inset = borders(cls, KH, KW, dict(guard=5, gdot=2, rose=3, vine=7, mainbg=0), main=16)
    y, x = np.mgrid[0:KH, 0:KW].astype(np.float32)
    fx, fy = x - inset, y - inset; FW, FH = KW - 2 * inset, KH - 2 * inset
    field = (fx >= 0) & (fy >= 0) & (fx < FW) & (fy < FH)
    nx, ny = 4, 7; cw, ch = FW / nx, FH / ny
    cu = (fx % cw) / cw - 0.5; cv = (fy % ch) / ch - 0.5
    lat = (np.abs(cu) > 0.47) | (np.abs(cv) > 0.47); cls[field & lat] = 1
    g = np.abs(cu) / 0.42 + np.abs(cv) / 0.36                              # octagonal gul
    oc = np.maximum(np.maximum(np.abs(cu) / 0.4, np.abs(cv) / 0.34), (np.abs(cu) + np.abs(cv)) / 0.52)
    gul = field & (oc < 1); cls[gul] = 2
    cls[field & (oc < 0.9)] = 0
    q = (cu > 0) ^ (cv > 0); cls[field & (oc < 0.88) & q] = 3
    cls[field & (oc < 0.88) & (np.abs(cu) < 0.03)] = 1; cls[field & (oc < 0.88) & (np.abs(cv) < 0.03)] = 1
    cls[field & (oc < 0.42)] = 2; cls[field & (oc < 0.3)] = 4; cls[field & (oc < 0.12)] = 7
    # minor gul at the lattice crossings
    mu = ((fx + cw / 2) % cw) / cw - 0.5; mv = ((fy + ch / 2) % ch) / ch - 0.5
    mg = field & ((np.abs(mu) + np.abs(mv)) < 0.14); cls[mg] = 2; cls[field & ((np.abs(mu) + np.abs(mv)) < 0.07)] = 4
    return finish(cls, pal, KH, KW, seed=seed, worn=0.18)

def runner(KH=600, KW=170, seed=9):
    pal = np.array([[150, 110, 82], [26, 36, 66], [222, 206, 172], [140, 30, 30], [40, 96, 92], [190, 92, 88], [52, 28, 22], [196, 140, 50]], np.float32)
    cls = np.zeros((KH, KW), np.int32)
    inset = borders(cls, KH, KW, dict(guard=3, gdot=2, rose=1, vine=7, mainbg=3), main=14)
    y, x = np.mgrid[0:KH, 0:KW].astype(np.float32)
    u = (x - KW / 2) / (KW / 2 - inset); v = (y - inset) / (KH - 2 * inset)
    field = (np.abs(u) < 1) & (v >= 0) & (v < 1)
    n = 5; t = (v * n) % 1 - 0.5
    dia = np.abs(u) * 0.9 + np.abs(t) * 2.4
    cls[field & (dia < 0.95)] = 1; cls[field & (dia < 0.78)] = 3; cls[field & (dia < 0.6)] = 2
    cls[field & (dia < 0.45) & (np.cos(14 * np.arctan2(t, u)) > 0.3)] = 4; cls[field & (dia < 0.2)] = 7
    hook = field & (dia > 0.95) & (dia < 1.08) & (np.cos(40 * v) > 0.2); cls[hook] = 6
    sm = field & (np.hypot((np.abs(u) - 0.8) * 2, ((v * n * 3) % 1 - 0.5)) < 0.18); cls[sm] = 5
    return finish(cls, pal, KH, KW, seed=seed)

os.makedirs(OUT, exist_ok=True)
persian(seed=1).save(os.path.join(OUT, 'rug_persian.png'))
persian(seed=2, red=False).save(os.path.join(OUT, 'rug_persian_navy.png'))
tekke().save(os.path.join(OUT, 'rug_tekke.png'))
tekke(seed=8).save(os.path.join(OUT, 'rug_bukhara.png'))
runner().save(os.path.join(OUT, 'runner_gen.png'))
print('rugs ok')
