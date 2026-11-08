"""Samarkand construction drawing set — page template + true-scale views + annotation helpers (matplotlib, mm on an A3 page)."""
import json, os, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon as MPoly
from PIL import Image
OUT = os.path.join(os.path.dirname(__file__), 'out')
TER = -0.45                                   # model z of the terrace finished floor = ±0.000
PAPER = '#f6f1e6'; GREEN = '#a9d18e'; GREEN_D = '#2f5d23'; INK = '#1b1b1b'; RED = '#9b1c1c'; BLUE = '#1f3f8a'; MUTED = '#6b5d4c'
SERIF = 'DejaVu Serif'; SANS = 'DejaVu Sans'
plt.rcParams.update({'font.family': SANS, 'font.size': 7, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
PROJECT = 'Dự án «SAMARKAND» — Nhà hàng ẩm thực Trung Á · Đà Nẵng'
SETNAME = 'HỒ SƠ THIẾT KẾ THI CÔNG NỘI THẤT · CONSTRUCTION DRAWINGS · R12-v11.7 · 11/2026'
MM = 1 / 25.4

class Page:
    """A3 landscape, coordinates in mm (0..420 x 0..297)."""
    def __init__(self, title_vi, title_en, code, num, total):
        self.fig = plt.figure(figsize=(420 * MM, 297 * MM), dpi=300)
        ax = self.fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis('off'); self.ax = ax
        ax.add_patch(Rectangle((0, 0), 420, 297, color=PAPER, zorder=-10))
        ax.add_patch(Rectangle((10, 280), 400, 11, color=GREEN, zorder=1))
        ax.text(14, 285.5, title_vi.upper(), fontfamily=SERIF, fontweight='bold', fontsize=15, color=GREEN_D, va='center', zorder=2)
        ax.text(406, 285.5, title_en.upper(), fontsize=8, color=GREEN_D, va='center', ha='right', zorder=2)
        ax.plot([10, 410], [14, 14], color=INK, lw=1.6)
        ax.text(10, 9.5, PROJECT, fontfamily=SERIF, fontsize=8.5, va='center')
        ax.text(10, 5.2, SETNAME, fontsize=5.6, color=MUTED, va='center')
        ax.add_patch(Rectangle((372, 3.5), 38, 9, color=GREEN, zorder=1))
        ax.text(391, 8, f'{code}', fontsize=10, fontweight='bold', ha='center', va='center', color=GREEN_D, zorder=2)
        ax.text(368, 8, f'{num}/{total}', fontsize=8, ha='right', va='center', color=INK)
        ax.plot([300, 300], [3.5, 12.5], color=INK, lw=0.4)
        ax.text(303, 10, 'Thiết kế / Design: Samarkand design team', fontsize=5.2, va='center')
        ax.text(303, 6.2, 'Kiểm tra / Checked: —   ·   Ngày / Date: 11/2026', fontsize=5.2, va='center')
    def save(self, pdf):
        pdf.savefig(self.fig, facecolor=PAPER); plt.close(self.fig)

# ------------------------------------------------------------------ views
def line_image(name, dz=0.05, ang=0.45, thick=1, fill='#ffffff', cap='#262626', tone=False, dmax=None):
    n = np.asarray(Image.open(f'{OUT}/{name}_n.png').convert('RGB')).astype(np.float32) / 255 * 2 - 1
    o = np.asarray(Image.open(f'{OUT}/{name}_o.png').convert('RGB')).astype(np.int32)
    d = np.asarray(Image.open(f'{OUT}/{name}_d.png')).astype(np.float32); d = d / (65535.0 if d.max() > 255 else 255.0) * 120.0
    c = np.asarray(Image.open(f'{OUT}/{name}_c.png').convert('L')).astype(np.float32) / 255
    bg = (d >= 119.5) | (d < 1.0)                               # <1: world colour leaking into the plan passes
    if dmax: bg |= d > 0.5875 * dmax - 1.3                  # depth pass is colour-managed: calibrated reading ≈ 0.5875·m − 1.3
    E = np.zeros(d.shape, bool)
    nl = np.linalg.norm(n, axis=2) + 1e-6
    for sh in ((0, 1), (1, 0), (1, 1), (1, -1)):
        d2 = np.roll(d, sh, (0, 1)); n2 = np.roll(n, sh, (0, 1)); o2 = np.roll(o, sh, (0, 1)); b2 = np.roll(bg, sh, (0, 1))
        rel = np.abs(d - d2) > dz
        nn = (n * n2).sum(2) / (nl * np.roll(nl, sh, (0, 1))) < np.cos(ang)
        oo = (np.abs(o - o2) > 6).any(2)
        E |= ((rel | nn | oo) & ~(bg & b2)) | (bg != b2)
    E[0, :] = E[-1, :] = E[:, 0] = E[:, -1] = False
    if thick > 1:
        F = E.copy()
        for dy in range(-(thick // 2), thick // 2 + 1):
            for dx in range(-(thick // 2), thick // 2 + 1): F |= np.roll(E, (dy, dx), (0, 1))
        E = F
    img = np.zeros(d.shape + (4,), np.uint8)
    fc = tuple(int(fill[i:i + 2], 16) for i in (1, 3, 5)); img[~bg] = (*fc, 255)
    if tone:                                                    # faint shading from the normals so masses read
        sh_ = np.clip(0.55 + 0.45 * (n[..., 2] * 0.6 + n[..., 0] * 0.3 + n[..., 1] * 0.1) / nl, 0, 1)
        g = (200 + 55 * sh_).astype(np.uint8); img[~bg, 0] = g[~bg]; img[~bg, 1] = g[~bg]; img[~bg, 2] = (g[~bg] * 0.98).astype(np.uint8)
    cc = tuple(int(cap[i:i + 2], 16) for i in (1, 3, 5)); img[(c > 0.5) & ~bg] = (*cc, 255)
    img[E] = (25, 25, 25, 255)
    return img

class View:
    """a rendered view placed on the page at a true scale. view metres: h (right), v (up), origin = camera centre."""
    def __init__(self, page, name, x_mm, y_mm, scale, crop=None, flip=False, **kw):
        J = json.load(open(f'{OUT}/{name}.json')); self.J = J
        self.C = np.array(J['cam']); self.R = np.array(J['right']); self.U = np.array(J['up'])
        if flip: self.U = -self.U
        s = J['scale']; Hm = s * J['H'] / J['W']
        h0, h1, v0, v1 = crop or (-s / 2, s / 2, -Hm / 2, Hm / 2)
        self.scale = scale
        w_mm, h_mm = (h1 - h0) * 1000 / scale, (v1 - v0) * 1000 / scale
        fig = page.fig
        self.ax = fig.add_axes([x_mm / 420, y_mm / 297, w_mm / 420, h_mm / 297]); ax = self.ax
        ax.set_xlim(h0, h1); ax.set_ylim(v0, v1); ax.axis('off'); ax.set_zorder(3); ax.patch.set_alpha(0)
        img = line_image(name, **kw)
        if flip: img = img[::-1]
        ax.imshow(img, extent=(-s / 2, s / 2, -Hm / 2, Hm / 2), interpolation='lanczos', zorder=1)
        self.box = (x_mm, y_mm, w_mm, h_mm); self.mpu = 1000 / scale       # mm on paper per metre
    def P(self, x, y, z):
        q = np.array([x, y, z]) - self.C; return float(q @ self.R), float(q @ self.U)

# ------------------------------------------------------------------ annotation (in view metres; sizes in paper mm via v.mpu)
def _k(v): return 1 / v.mpu                                  # metres per paper-mm
def dim(v, a, b, off, text=None, side=1, col=RED, fs=5.2, ext=True):
    """dimension line between view points a, b (tuples h,v), offset 'off' paper-mm perpendicular"""
    ax = v.ax; k = _k(v); a = np.array(a, float); b = np.array(b, float); d = b - a; L = np.linalg.norm(d)
    if L < 1e-6: return
    t = d / L; nrm = np.array([-t[1], t[0]]) * side; o = nrm * off * k
    pa, pb = a + o, b + o
    ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color=col, lw=0.45, zorder=6)
    if ext:
        for p, q in ((a, pa), (b, pb)): ax.plot([p[0] + nrm[0] * 0.6 * k, q[0] + nrm[0] * 1.2 * k], [p[1] + nrm[1] * 0.6 * k, q[1] + nrm[1] * 1.2 * k], color=col, lw=0.3, zorder=6)
    for p in (pa, pb):                                      # architectural ticks
        tk = (t + nrm) / np.linalg.norm(t + nrm) * 1.0 * k
        ax.plot([p[0] - tk[0], p[0] + tk[0]], [p[1] - tk[1], p[1] + tk[1]], color=col, lw=0.8, zorder=6)
    txt = text if text is not None else f'{L * 1000:,.0f}'.replace(',', '.')
    m = (pa + pb) / 2 + nrm * 1.3 * k
    ang = np.degrees(np.arctan2(t[1], t[0]))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    ax.text(m[0], m[1], txt, fontsize=fs, color=col, ha='center', va='center', rotation=ang, zorder=7,
            bbox=dict(boxstyle='square,pad=0.08', fc=PAPER, ec='none', alpha=0.85))
def chain(v, pts, off, side=1, **kw):
    for a, b in zip(pts[:-1], pts[1:]): dim(v, a, b, off, side=side, **kw)
def level(v, h, vv, text, side=1, col=BLUE, fs=5.2):
    """level mark (triangle + line + text) at view point"""
    ax = v.ax; k = _k(v)
    ax.add_patch(MPoly([[h, vv], [h - 1.3 * k, vv + 1.6 * k], [h + 1.3 * k, vv + 1.6 * k]], closed=True, fc=col, ec=col, lw=0.3, zorder=7))
    ax.plot([h, h + side * 18 * k], [vv + 1.6 * k] * 2, color=col, lw=0.4, zorder=7)
    ax.text(h + side * 2 * k, vv + 2.4 * k, text, fontsize=fs, color=col, ha='left' if side > 0 else 'right', va='bottom', zorder=7)
def bubble(v, h, vv, txt, r=3.2, col=INK, fs=6.5):
    ax = v.ax; k = _k(v)
    ax.add_patch(Circle((h, vv), r * k, fc='white', ec=col, lw=0.6, zorder=8))
    ax.text(h, vv, txt, fontsize=fs, ha='center', va='center', fontweight='bold', color=col, zorder=9)
def gridline(v, a, b, txt, ends=(True, True)):
    ax = v.ax; k = _k(v)
    ax.plot([a[0], b[0]], [a[1], b[1]], color='#8a8a8a', lw=0.35, ls=(0, (8, 2, 1, 2)), zorder=5)
    d = np.array(b) - np.array(a); d = d / np.linalg.norm(d)
    if ends[0]: bubble(v, a[0] - d[0] * 3.2 * k, a[1] - d[1] * 3.2 * k, txt)
    if ends[1]: bubble(v, b[0] + d[0] * 3.2 * k, b[1] + d[1] * 3.2 * k, txt)
def tag(v, xy, text, dxy=(8, 8), fs=5.0, col=INK, ha=None, num=None):
    """leader label: point xy (view m) -> text offset dxy (paper mm)"""
    ax = v.ax; k = _k(v); tx = xy[0] + dxy[0] * k; ty = xy[1] + dxy[1] * k
    ax.plot([xy[0], tx], [xy[1], ty], color=col, lw=0.35, zorder=8); ax.add_patch(Circle(xy, 0.5 * k, color=col, zorder=8))
    ha = ha or ('left' if dxy[0] >= 0 else 'right')
    if num is not None:
        bubble(v, tx + (2.2 if ha == 'left' else -2.2) * k, ty, str(num), r=2.2, col=BLUE, fs=5.2)
    else:
        ax.text(tx + (0.8 if ha == 'left' else -0.8) * k, ty, text, fontsize=fs, ha=ha, va='center', color=col, zorder=8,
                bbox=dict(boxstyle='square,pad=0.15', fc=PAPER, ec='none', alpha=0.9))
def title(page, x, y, n, vi, en, scale_txt, w=120):
    ax = page.ax
    ax.add_patch(Circle((x + 4, y), 4, fc=GREEN_D, ec='none', zorder=4)); ax.text(x + 4, y, str(n), color='white', fontsize=8, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(x + 10, y + 1.3, vi.upper(), fontsize=8.2, fontweight='bold', va='center', fontfamily=SERIF)
    ax.text(x + 10, y - 2.6, f'{en}  ·  {scale_txt}', fontsize=5.6, va='center', color=MUTED)
    ax.plot([x + 10, x + w], [y - 0.6, y - 0.6], color=INK, lw=0.5)
def scalebar(page, x, y, scale, metres=5):
    ax = page.ax; L = metres * 1000 / scale
    for i in range(metres):
        ax.add_patch(Rectangle((x + i * L / metres, y), L / metres, 1.6, fc=INK if i % 2 == 0 else 'white', ec=INK, lw=0.3))
    ax.text(x, y + 2.6, '0', fontsize=5); ax.text(x + L, y + 2.6, f'{metres} m', fontsize=5, ha='center')
def north(page, x, y, ang=90):
    """north arrow; ang = direction of model +y on paper (deg from paper +x)"""
    ax = page.ax; a = np.radians(ang)
    ax.add_patch(Circle((x, y), 6, fc='none', ec=INK, lw=0.5))
    tip = (x + 5.5 * np.cos(a), y + 5.5 * np.sin(a)); l = (x + 2.5 * np.cos(a + 2.4), y + 2.5 * np.sin(a + 2.4)); r = (x + 2.5 * np.cos(a - 2.4), y + 2.5 * np.sin(a - 2.4))
    ax.add_patch(MPoly([tip, l, (x, y), r], closed=True, fc=INK))
    ax.text(x + 8.5 * np.cos(a), y + 8.5 * np.sin(a), 'B / N', fontsize=6, ha='center', va='center', fontweight='bold')
def panel(page, x, y, w, h, head=None):
    ax = page.ax; ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=1.5', fc='white', ec='#b9ab92', lw=0.5, zorder=2))
    if head:
        ax.add_patch(Rectangle((x, y + h - 6), w, 6, fc=GREEN_D, ec='none', zorder=3))
        ax.text(x + 2.5, y + h - 3, head, color='white', fontsize=6.2, fontweight='bold', va='center', zorder=4)
def table(page, x, y, cols, rows, widths, fs=5.0, rh=4.2, head_bg='#e7efe0'):
    """simple ruled table, top-left at (x, y)"""
    ax = page.ax; yy = y
    def row(cells, bg=None, bold=False):
        nonlocal yy
        if bg: ax.add_patch(Rectangle((x, yy - rh), sum(widths), rh, fc=bg, ec='none', zorder=3))
        cx = x
        for c, w in zip(cells, widths):
            ax.text(cx + 1, yy - rh / 2, str(c), fontsize=fs, va='center', fontweight='bold' if bold else 'normal', zorder=4, clip_on=False)
            cx += w
        ax.plot([x, x + sum(widths)], [yy - rh, yy - rh], color='#c9bea9', lw=0.3, zorder=4); yy -= rh
    row(cols, head_bg, True)
    for r in rows: row(r)
    return yy
def text_block(page, x, y, lines, fs=5.6, lh=3.6, col=INK, bold_first=False):
    for i, l in enumerate(lines):
        page.ax.text(x, y - i * lh, l, fontsize=fs, color=col, va='top', fontweight='bold' if (bold_first and i == 0) else 'normal', zorder=4)
    return y - len(lines) * lh
