"""white Carrara-type marble, veins only (no grid): one 1024 px image, UV'd per slab with its own rotation / offset"""
import numpy as np, math, sys
from PIL import Image
N = 1024; rng = np.random.default_rng(5)
def fbm(n, seed, octaves=6):
    g = np.random.default_rng(seed); out = np.zeros((n, n), np.float32); amp = 1.0
    for o in range(octaves):
        k = 4 * 2 ** o; z = g.normal(0, 1, (k + 1, k + 1)).astype(np.float32); z[-1, :] = z[0, :]; z[:, -1] = z[:, 0]
        up = np.asarray(Image.fromarray(((z + 4) * 30).clip(0, 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)).astype(np.float32) / 30 - 4
        out += amp * up; amp *= 0.5
    return out
u, v = np.meshgrid(np.arange(N) / N, np.arange(N) / N)
F = fbm(N, 11); F2 = fbm(N, 12)
x = (u * math.cos(0.6) + v * math.sin(0.6)) * 14
v1 = np.exp(-np.abs(np.sin(x + 3.6 * F)) * 22); v2 = np.exp(-np.abs(np.sin(x * 2.1 + 5.5 * F2 + 1)) * 40); v3 = np.exp(-np.abs(np.sin(x * 0.7 + 2.5 * F2 + 2.0 * F)) * 9)
mv = (0.5 * v1 + 0.3 * v2 + 0.12 * v3).clip(0, 0.75)
base = np.array([238, 236, 231], np.float32); vc = np.array([125, 128, 136], np.float32)
img = base[None, None] * (1 + 0.015 * F[..., None]) * (1 - mv[..., None]) + vc[None, None] * mv[..., None]
Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(sys.argv[1])
