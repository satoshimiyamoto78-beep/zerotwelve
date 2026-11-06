"""straight-grain American walnut, quarter/rift sawn: long fibre lines, slow colour drift across boards, open pores, no waves"""
import numpy as np, sys
from PIL import Image, ImageFilter
N = 1024; rng = np.random.default_rng(7)
y = np.arange(N)[:, None] / N; x = np.arange(N)[None, :] / N
# grain runs along x (texture u). Fibre lines: 1-D noise across y, very slightly drifting along x
def noise1(n, octaves):
    out = np.zeros(n)
    for f, a in octaves:
        k = rng.normal(size=f + 3); t = np.linspace(0, f, n, endpoint=False)
        i = t.astype(int); fr = t - i; out += a * (k[i] * (1 - fr) + k[i + 1] * fr)
    return out
drift = 0.004 * np.sin(2 * np.pi * (x * 1.0 + 0.3)) + 0.002 * np.sin(2 * np.pi * x * 3.0)
yy = (y + drift) % 1.0
lines = noise1(4096, [(8, 1.0), (40, 0.5), (160, 0.35), (700, 0.25), (2000, 0.15)])
g = lines[(yy * 4095).astype(int)]
g = (g - g.min()) / (g.max() - g.min())
board = noise1(N, [(3, 1.0), (9, 0.4)])[:, None]; board = (board - board.min()) / (board.max() - board.min())
base = np.array([0.30, 0.19, 0.12]); dark = np.array([0.16, 0.09, 0.055]); warm = np.array([0.40, 0.26, 0.16])
t = np.clip(0.75 * g ** 1.6 + 0.35 * board, 0, 1)
col = dark[None, None] * (1 - t[..., None]) + base[None, None] * t[..., None]
col = col + (warm - base)[None, None] * (np.clip(board - 0.6, 0, 1)[..., None] * 0.8)
pores = (rng.random((N, N)) < 0.006).astype(float)
pores = np.array(Image.fromarray((pores * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).resize((N, N))) / 255.0
streak = np.repeat(pores[:, :1], 1, axis=1)
col *= (1 - 0.45 * pores[..., None])
col *= (0.96 + 0.04 * rng.random((N, 1, 1)))
img = Image.fromarray((np.clip(col * 1.05, 0, 1) * 255).astype(np.uint8))
img = img.filter(ImageFilter.GaussianBlur(0.4))
img.save(sys.argv[1])
