"""Samarkand surface textures from the owner's reference photographs (Shah-i-Zinda, Ulugbek madrasa, Isfahan):
crop one pattern period, level the light, make the tile seamless (half-offset cross-fade), upscale.
Usage: python3 textures6.py REFDIR  ->  r3d/tex2/{bannai,bannai2,kufic,hazarbaf,majcobalt,majisfahan,girihstar,epigraph,brickpave}.png"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter, ImageOps
REF = sys.argv[1]; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex2')
FB, UL, IS = (Image.open(os.path.join(REF, f)).convert('RGB') for f in ('fb2d8a22-image.jpg', '982896a7-image.jpg', '27e2774d-image.jpg'))

def level(im, sigma=60):
    """remove large-scale light falloff: divide by a heavy blur, keep the mean colour"""
    a = np.asarray(im).astype(np.float32); lo = np.asarray(im.filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)
    m = a.reshape(-1, 3).mean(0); b = a / np.maximum(lo, 1) * m
    return Image.fromarray(np.clip(b, 0, 255).astype(np.uint8))
def seamless(im, frac=0.18):
    """classic half-offset cross-fade: edges come from the rolled copy (whose borders wrap continuously)"""
    a = np.asarray(im).astype(np.float32); H, W = a.shape[:2]
    r = np.roll(np.roll(a, W // 2, 1), H // 2, 0)
    wx = np.minimum(np.arange(W), W - 1 - np.arange(W)) / (W * frac); wy = np.minimum(np.arange(H), H - 1 - np.arange(H)) / (H * frac)
    m = np.clip(np.minimum(wx[None, :], wy[:, None]), 0, 1)[..., None]
    return Image.fromarray((a * m + r * (1 - m)).astype(np.uint8))
def crop(im, box, size, mode='period', lev=True):
    c = im.crop(box)
    if lev: c = level(c, max(20, min(c.size) // 3))
    if mode == 'blend': c = seamless(c)
    if mode == 'hmirror': w, h = c.size; m = Image.new('RGB', (2 * w, h)); m.paste(c, (0, 0)); m.paste(ImageOps.mirror(c), (w, 0)); c = m
    if mode == 'mirror': w, h = c.size; m = Image.new('RGB', (2 * w, 2 * h)); m.paste(c, (0, 0)); m.paste(ImageOps.mirror(c), (w, 0)); m.paste(ImageOps.flip(c), (0, h)); m.paste(ImageOps.flip(ImageOps.mirror(c)), (w, h)); c = m
    return c.resize(size, Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
def square(im):
    """repeat the (seamless) tile along its short side until near-square, then resample to a square power of two"""
    w, h = im.size
    if w < h: n = max(1, round(h / w)); t = Image.new('RGB', (w * n, h)); [t.paste(im, (k * w, 0)) for k in range(n)]
    else: n = max(1, round(w / h)); t = Image.new('RGB', (w, h * n)); [t.paste(im, (0, k * h)) for k in range(n)]
    return t.resize((1024, 1024), Image.LANCZOS)
def save(im, name, sq=True):
    if sq: im = square(im)
    im.save(os.path.join(OUT, name + '.png')); print(name, im.size)

# bannai: buff brick with turquoise glazed crosses — exact period (2 x 145 px across, 4 x 80 px up)
save(crop(FB, (12, 20, 306, 352), (1024, 1156)), 'bannai')          # measured period 147 x 83 px
# bannai2: recessed panel, larger crosses on long bricks (3 x 152 across, 3 x 92 up)
save(crop(FB, (151, 650, 609, 926), (1024, 618)), 'bannai2')
# kufic: frame stack as on the Shah-i-Zinda wall — kufic band / turquoise-buff brick row / kufic band / cobalt flower strip
band = FB.crop((101, 494, 513, 602)); row = FB.crop((101, 404, 513, 482)); dots = FB.crop((101, 1140, 513, 1174)); band2 = FB.crop((101, 1010, 513, 1118))   # period 103 px
st = Image.new('RGB', (412, 108 + 78 + 108 + 34)); y = 0
for p in (band, row, band2, dots): st.paste(p, (0, y)); y += p.size[1]
save(crop(st, (0, 0) + st.size, (1024, 756), 'period', lev=False), 'kufic')
# hazarbaf: buff brick with cobalt / turquoise glazed bricks (Ulugbek pilaster)
save(crop(UL, (240, 40, 392, 900), (512, 2896 // 2), 'blend'), 'hazarbaf')
# majcobalt: Samarkand cobalt arabesque with white flowers (Ulugbek panel)
save(crop(UL, (8, 500, 228, 800), (1024, 1396), 'mirror'), 'majcobalt')
# majisfahan: cobalt with yellow arabesques (Isfahan) for the column shafts and the frieze ground
save(crop(IS, (204, 792, 418, 912), (1024, 624), 'mirror'), 'majisfahan')
# girihstar: turquoise / cobalt / white glazed-brick lattice (Shah-i-Zinda jamb)
save(crop(FB, (596, 100, 686, 278), (512, 1012), 'hmirror'), 'girihstar')       # 2 vertical periods (89 px), mirrored across
# epigraph frieze: Isfahan floral band between kufic borders (picture texture, 4:1)
fl = crop(IS, (204, 792, 418, 912), (772, 376), 'mirror', lev=True); bd = FB.crop((101, 494, 545, 602)).resize((772, 94), Image.LANCZOS)
ep = Image.new('RGB', (1544, 376 + 2 * 94)); ep.paste(bd, (0, 0)); ep.paste(bd, (772, 0))
ep.paste(fl, (0, 94)); ep.paste(ImageOps.mirror(fl), (772, 94)); ep.paste(bd, (0, 470)); ep.paste(bd, (772, 470))
save(ep.resize((2048, 746), Image.LANCZOS), 'epigraph', False)
# brickpave: plain buff brick (wall base) as floor pavers
save(crop(FB, (10, 1190, 726, 1306), (1024, 166 * 1024 // 716 * 1), 'blend'), 'brickpave')
# domeglaze: long turquoise glazed bricks (Shah-i-Zinda jamb) for the dome shells
save(crop(FB, (553, 96, 584, 400), (256, 2510), 'blend'), 'domeglaze')
# the base kit's generated majolica / girih textures are replaced by the photographic ones
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex')
Image.open(os.path.join(OUT, 'majcobalt.png')).save(os.path.join(TEX, 'majolica.png'))
Image.open(os.path.join(OUT, 'girihstar.png')).save(os.path.join(TEX, 'girih.png'))
print('tex/majolica.png + tex/girih.png replaced')
