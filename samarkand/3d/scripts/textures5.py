"""Samarkand (Shah-i-Zinda / Gur-e-Amir / Registan) surface textures, seamless tiles -> r3d/tex2/
bannai      buff fired brick, running bond, turquoise glazed crosses in the bed joints   (1.2 m tile)
kufic       glazed-brick square-kufic labyrinth band: turquoise / cobalt / white / black  (0.6 m tile)
majcobalt   cobalt majolica: white + yellow arabesque scrolls, flowers, turquoise contour (0.6 m tile)
girihstar   white glazed field with cobalt 8-point stars + crosses, turquoise-edged medallions (0.6 m)
epigraph    white pseudo-thuluth on cobalt, turquoise borders (horizontal band, 1.2 x 0.3 m)
brickpave   herringbone fired-brick paving (1.0 m tile)
stone       light limestone with soft veining (1.0 m tile)"""
import math, random, os
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex2')
R = random.Random(7)
BUFF = [(214, 178, 128), (205, 166, 116), (222, 188, 140), (196, 158, 108), (210, 172, 122)]
TURQ, TURQ2, COB, COB2, WHITE, YEL, BLACK, GREEN = (38, 168, 176), (64, 190, 196), (24, 44, 140), (34, 62, 168), (238, 236, 226), (232, 186, 52), (26, 30, 40), (54, 150, 84)

def jitter(c, k=10): return tuple(max(0, min(255, v + R.randint(-k, k))) for v in c)
def grain(im, k=6):
    px = im.load(); W, H = im.size
    for y in range(H):
        for x in range(W):
            if R.random() < 0.5: c = px[x, y]; d = R.randint(-k, k); px[x, y] = tuple(max(0, min(255, v + d)) for v in c[:3])
    return im
def glaze(d, box, col, edge=None):
    """glazed tile/brick: base colour, lighter top-left bevel, darker bottom-right"""
    x0, y0, x1, y1 = box; c = jitter(col, 8)
    d.rectangle(box, fill=c)
    hi = tuple(min(255, v + 34) for v in c); lo = tuple(max(0, v - 34) for v in c)
    d.line([(x0, y1), (x0, y0), (x1, y0)], fill=hi, width=2); d.line([(x0, y1), (x1, y1), (x1, y0)], fill=lo, width=2)
    if edge: d.rectangle(box, outline=edge, width=1)

# ---------------- bannai: buff brick with turquoise crosses ----------------
S = 1024; im = Image.new('RGB', (S, S), (168, 140, 104)); d = ImageDraw.Draw(im)
bw, bh, j = 128, 32, 6                                          # 1.2 m / 1024 px -> brick 150 x 37 mm + joints
for r in range(S // bh):
    off = (bw // 2) * (r % 2)
    for c in range(-1, S // bw + 1):
        x0 = c * bw + off; box = (x0 + j // 2, r * bh + j // 2, x0 + bw - j // 2, r * bh + bh - j // 2)
        col = jitter(R.choice(BUFF), 8); d.rectangle(box, fill=col)
        d.line([(box[0], box[3]), (box[2], box[3])], fill=tuple(v - 22 for v in col), width=2)
for r in range(1, S // bh, 2):                                   # crosses every other course, staggered
    for c in range(S // bw):
        cx = c * bw + (bw // 2 if (r // 2) % 2 else 0); cy = r * bh
        for bx_ in ((cx - 10, cy - 22, cx + 10, cy + 22), (cx - 22, cy - 10, cx + 22, cy + 10)): glaze(d, bx_, TURQ)
        glaze(d, (cx - 9, cy - 9, cx + 9, cy + 9), TURQ2)
grain(im.filter(ImageFilter.GaussianBlur(0.6))).save(f'{OUT}/bannai.png')

# ---------------- kufic: glazed-brick square kufic labyrinth ----------------
S = 512; N = 16; u = S // N; im = Image.new('RGB', (S, S), (200, 168, 120)); d = ImageDraw.Draw(im)
def kufic_cell(ox, oy, n, palette):
    """concentric square spiral 'Allah'-like key pattern in an n x n module"""
    g = [[0] * n for _ in range(n)]
    for k in range(0, n // 2, 2):
        for i in range(k, n - k):
            g[k][i] = g[n - 1 - k][i] = g[i][k] = g[i][n - 1 - k] = 1
        if k + 1 < n // 2: g[k + 1][k] = 0; g[k][k + 1] = 0 if k else 1
    g[n // 2][n // 2 - 1] = g[n // 2 - 1][n // 2] = 1
    for yy in range(n):
        for xx in range(n):
            col = palette[0] if g[yy][xx] else palette[1]
            glaze(d, (ox + xx * u + 1, oy + yy * u + 1, ox + (xx + 1) * u - 2, oy + (yy + 1) * u - 2), col)
for qx in range(2):
    for qy in range(2):
        pal = [(COB, WHITE), (TURQ, BLACK), (TURQ, BLACK), (COB, WHITE)][qx * 2 + qy]
        kufic_cell(qx * 8 * u, qy * 8 * u, 8, pal)
grain(im).save(f'{OUT}/kufic.png')

# ---------------- majcobalt: cobalt majolica with white / yellow arabesques ----------------
S = 1024; im = Image.new('RGB', (S, S), COB); d = ImageDraw.Draw(im)
def scroll(cx, cy, r, a0, turns, col, w):
    pts = []
    for t in range(60):
        a = a0 + turns * 2 * math.pi * t / 59; rr = r * (1 - 0.75 * t / 59); pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.line(pts, fill=col, width=w, joint='curve')
def flower(cx, cy, r, petal, centre, n=6):
    for k in range(n):
        a = 2 * math.pi * k / n; px_, py_ = cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a)
        d.ellipse((px_ - r * 0.42, py_ - r * 0.42, px_ + r * 0.42, py_ + r * 0.42), fill=petal, outline=COB2)
    d.ellipse((cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35), fill=centre)
for tx in (0, S):
    for ty in (0, S):
        pass
cells = [(x, y) for x in range(0, S, 256) for y in range(0, S, 256)]
for x, y in cells:                                               # yellow main scrolls (wrapping copies keep it seamless)
    for dx in (-S, 0, S):
        for dy in (-S, 0, S):
            scroll(x + 128 + dx, y + 128 + dy, 110, (x + y) / 300, 1.3, YEL, 9)
            scroll(x + dx, y + dy, 70, 2.0 + (x - y) / 300, 1.1, WHITE, 6)
for x, y in cells:
    for dx in (-S, 0, S):
        for dy in (-S, 0, S):
            flower(x + 128 + dx, y + 128 + dy, 34, WHITE, YEL, 8); flower(x + dx, y + dy, 24, TURQ2, WHITE, 6)
            for k in range(4):
                a = math.pi / 4 + k * math.pi / 2; fx, fy = x + 128 + dx + 80 * math.cos(a), y + 128 + dy + 80 * math.sin(a)
                d.ellipse((fx - 9, fy - 9, fx + 9, fy + 9), fill=WHITE); d.ellipse((fx - 4, fy - 4, fx + 4, fy + 4), fill=(200, 60, 60))
for _ in range(260):                                             # dense ground: tendrils, leaves, buds
    x, y = R.randint(0, S), R.randint(0, S); a = R.uniform(0, 6.28)
    for dx in (-S, 0, S):
        for dy in (-S, 0, S):
            scroll(x + dx, y + dy, R.randint(18, 40), a, 0.8, R.choice([WHITE, WHITE, TURQ2, YEL]), 3)
            lx, ly = x + dx + 22 * math.cos(a), y + dy + 22 * math.sin(a)
            d.polygon([(lx, ly), (lx + 14 * math.cos(a + 0.5), ly + 14 * math.sin(a + 0.5)), (lx + 26 * math.cos(a), ly + 26 * math.sin(a)), (lx + 14 * math.cos(a - 0.5), ly + 14 * math.sin(a - 0.5))], fill=R.choice([TURQ2, GREEN, WHITE]))
            if R.random() < 0.3: d.ellipse((x + dx - 5, y + dy - 5, x + dx + 5, y + dy + 5), fill=R.choice([WHITE, YEL, (200, 60, 60)]))
for k in range(0, S, 256):                                       # tile joints (glazed tiles 0.15 m)
    d.line([(k, 0), (k, S)], fill=(14, 26, 90), width=3); d.line([(0, k), (S, k)], fill=(14, 26, 90), width=3)
grain(im.filter(ImageFilter.GaussianBlur(0.8)), 5).save(f'{OUT}/majcobalt.png')

# ---------------- girihstar: white field, cobalt stars + crosses (ref: Shah-i-Zinda / Mashhad portal) ----------------
S = 1024; im = Image.new('RGB', (S, S), (236, 232, 222)); d = ImageDraw.Draw(im)
def star8(cx, cy, r, fill, outline=None, w=0):
    pts = [(cx + (r if k % 2 == 0 else r * 0.72) * math.cos(k * math.pi / 8), cy + (r if k % 2 == 0 else r * 0.72) * math.sin(k * math.pi / 8)) for k in range(16)]
    d.polygon(pts, fill=fill, outline=outline, width=w)
P = 128
for x in range(0, S + P, P):
    for y in range(0, S + P, P):
        star8(x, y, 44, COB2, TURQ, 3); star8(x, y, 18, (230, 150, 50))
        cx, cy = x + P // 2, y + P // 2                           # cross between stars
        d.polygon([(cx - 14, cy - 40), (cx + 14, cy - 40), (cx + 14, cy - 14), (cx + 40, cy - 14), (cx + 40, cy + 14), (cx + 14, cy + 14), (cx + 14, cy + 40),
                   (cx - 14, cy + 40), (cx - 14, cy + 14), (cx - 40, cy + 14), (cx - 40, cy - 14), (cx - 14, cy - 14)], fill=(242, 240, 232), outline=COB, width=4)
        d.rectangle((cx - 6, cy - 6, cx + 6, cy + 6), fill=TURQ)
for x in range(0, S, 512):                                       # turquoise-edged cobalt medallions (cartouches)
    for y in range(0, S, 512):
        cx, cy = x + 256, y + 256; pts = []
        for k in range(12):
            a = k * math.pi / 6; rr = 120 if k % 3 else 150; pts.append((cx + rr * math.cos(a), cy + 0.62 * rr * math.sin(a)))
        d.polygon(pts, fill=COB, outline=TURQ2, width=8)
        for k in range(5):
            scroll(cx - 60 + 30 * k, cy, 26, k, 1.0, YEL if k % 2 else WHITE, 4)
        flower(cx, cy, 22, WHITE, (210, 70, 60), 8)
for k in range(0, S, 64):
    d.line([(k, 0), (k, S)], fill=(205, 200, 190), width=1); d.line([(0, k), (S, k)], fill=(205, 200, 190), width=1)
grain(im.filter(ImageFilter.GaussianBlur(0.7)), 5).save(f'{OUT}/girihstar.png')

# ---------------- epigraph: white pseudo-thuluth on cobalt ----------------
W, H = 2048, 512; im = Image.new('RGB', (W, H), COB); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 34), fill=TURQ); d.rectangle((0, H - 34, W, H), fill=TURQ); d.line([(0, 36), (W, 36)], fill=WHITE, width=4); d.line([(0, H - 38), (W, H - 38)], fill=WHITE, width=4)
x = 20
while x < W - 60:                                                # tall alif strokes + curved bowls + dots: reads as monumental thuluth
    kind = R.random()
    if kind < 0.45:
        h = R.randint(230, 330); d.line([(x, H - 90), (x + 12, H - 90 - h)], fill=WHITE, width=22); x += 46
    elif kind < 0.8:
        w = R.randint(90, 170); d.arc((x, H - 230, x + w, H - 70), 10, 170, fill=WHITE, width=20); x += w // 2 + 20
    else:
        d.ellipse((x, 120, x + 26, 146), fill=WHITE); d.polygon([(x + 40, 200), (x + 70, 180), (x + 64, 214)], fill=WHITE); x += 50
for k in range(0, W, 120):                                       # small floral ground
    d.ellipse((k + 40, 70, k + 56, 86), fill=TURQ2); d.ellipse((k + 90, H - 120, k + 104, H - 106), fill=YEL)
grain(im.filter(ImageFilter.GaussianBlur(1.0)), 4).save(f'{OUT}/epigraph.png')

# ---------------- brickpave: herringbone fired brick ----------------
S = 1024; im = Image.new('RGB', (S, S), (150, 120, 90)); d = ImageDraw.Draw(im); L, Wb = 128, 64
for i in range(-S // Wb - 2, S // Wb + 3):
    for j in range(-2, S // L + 3):
        x0, y0 = i * Wb + j * Wb, j * Wb * 2 - i * Wb
        for (bx_, by_, bw_, bh_) in ((x0, y0, L, Wb), (x0 + L - Wb, y0 + Wb, Wb, L)):
            col = jitter(R.choice([(184, 120, 82), (170, 108, 74), (196, 132, 92), (160, 102, 70)]), 8)
            for ox in (-S, 0, S):
                for oy in (-S, 0, S):
                    d.rectangle((bx_ + 3 + ox, by_ + 3 + oy, bx_ + bw_ - 3 + ox, by_ + bh_ - 3 + oy), fill=col)
grain(im.filter(ImageFilter.GaussianBlur(0.6)), 7).save(f'{OUT}/brickpave.png')

# ---------------- stone: limestone ----------------
S = 512; im = Image.new('RGB', (S, S), (222, 212, 192)); d = ImageDraw.Draw(im)
for _ in range(40):
    x, y = R.randint(0, S), R.randint(0, S); pts = [(x, y)]
    for k in range(12): x += R.randint(-30, 30); y += R.randint(-6, 18); pts.append((x, y))
    d.line(pts, fill=(200, 188, 166), width=R.randint(1, 3))
for k in range(0, S, 256): d.line([(0, k), (S, k)], fill=(176, 164, 144), width=3); d.line([(k, 0), (k, S)], fill=(176, 164, 144), width=3)
grain(im.filter(ImageFilter.GaussianBlur(1.2)), 6).save(f'{OUT}/stone.png')
print('textures5 ok')
