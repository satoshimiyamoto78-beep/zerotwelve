"""fabric micro-structure for the flat textile textures: upscale, soften vector edges, weave / weft ribs / stitch grain, dye mottling"""
import sys, os, numpy as np
from PIL import Image, ImageFilter
T = sys.argv[1]; B = sys.argv[2]
rng = np.random.default_rng(11)
def lowfreq(h, w, sc, seed):
    r = np.random.default_rng(seed).random((max(2, h // sc), max(2, w // sc)))
    return np.asarray(Image.fromarray((r * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
def treat(fn, kind, target=2048):
    src = os.path.join(B, fn) if os.path.exists(os.path.join(B, fn)) else os.path.join(T, fn)
    im = Image.open(src).convert('RGB')
    if not os.path.exists(os.path.join(B, fn)): im.save(os.path.join(B, fn))
    k = target / max(im.size); im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.1))
    a = np.asarray(im, np.float32); h, w = a.shape[:2]; y, x = np.mgrid[0:h, 0:w]
    if kind == 'kilim':      # weft-faced flat weave: horizontal ribs + warp ticks + slight line jitter
        rib = 0.5 + 0.5 * np.sin(2 * np.pi * y / 5.0 + 0.6 * np.sin(2 * np.pi * x / 41.0))
        warp = 0.5 + 0.5 * np.sin(2 * np.pi * x / 3.2)
        m = 0.82 + 0.22 * rib + 0.05 * warp
    elif kind == 'suzani':   # cotton ground weave + satin-stitch grain on the motifs
        weave = (0.5 + 0.5 * np.sin(2 * np.pi * x / 3.0)) * (0.5 + 0.5 * np.sin(2 * np.pi * y / 3.0))
        lum = a.mean(2); motif = lum < 175
        stitch = 0.5 + 0.5 * np.sin(2 * np.pi * (x * 0.7 + y * 0.7) / 3.4)
        m = np.where(motif, 0.84 + 0.24 * stitch, 0.92 + 0.12 * weave)
    else:                    # canvas / cotton / silk-cotton: plain weave
        weave = (0.5 + 0.5 * np.sin(2 * np.pi * x / 3.6)) * (0.5 + 0.5 * np.sin(2 * np.pi * y / 3.6))
        m = 0.88 + 0.18 * weave
    fib = np.asarray(Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255
    mott = 0.93 + 0.14 * lowfreq(h, w, 90, len(fn))
    a = a * (m * (0.92 + 0.16 * fib) * mott)[:, :, None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(T, fn))
for fn in ('majlis_kilim.png', 'kilim.png', 'kilim2.png', 'kilim_w.png', 'kilim2_w.png', 'palas1.png', 'palas2.png', 'palas3.png', 'palas4.png'): treat(fn, 'kilim')
for fn in ('suzani_w.png', 'suzani2.png', 'suzani_one.png', 'quilt.png'): treat(fn, 'suzani')
for fn in ('tentstripe.png', 'tentstripe_w.png', 'adras.png', 'cloth_silk_ikat.png', 'cloth_terra.png', 'cloth_linen.png', 'cloth_sand.png', 'cloth_rose.png', 'cloth_olive.png', 'beadikat.jpg'): treat(fn, 'canvas', 1536)
print('fabrics ok')
