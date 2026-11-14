"""Samarkand construction drawing set — page template + true-scale views + annotation helpers (matplotlib, mm on an A3 page)."""
import json, os, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon as MPoly
from PIL import Image
OUT = os.path.join(os.path.dirname(__file__), '..', 'cd', 'out'); HOUT = os.path.join(os.path.dirname(__file__), '..', 'hlr', 'out'); KOUT = os.path.join(os.path.dirname(__file__), 'out'); os.makedirs(KOUT, exist_ok=True)
TER = -0.45                                   # model z of the terrace finished floor = ±0.000
PAPER = '#ffffff'; GREEN = '#e8e8e8'; GREEN_D = '#111111'; INK = '#111111'; RED = '#b3261e'; BLUE = '#1f3f8a'; MUTED = '#666666'
SERIF = 'DejaVu Sans'; SANS = 'DejaVu Sans'
plt.rcParams.update({'font.family': SANS, 'font.size': 7, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
PROJECT = 'Dự án «SAMARKAND» — Nhà hàng ẩm thực Trung Á · Đà Nẵng'
SETNAME = 'HỒ SƠ THIẾT KẾ THI CÔNG NỘI THẤT · CONSTRUCTION DRAWINGS · R12-v12.1 · 11/2026'
MM = 1 / 25.4

class Page:
    """A3 landscape, coordinates in mm (0..420 x 0..297)."""
    def __init__(self, title_vi, title_en, code, num, total):
        self.fig = plt.figure(figsize=(420 * MM, 297 * MM), dpi=300)
        ax = self.fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis('off'); self.ax = ax
        ax.add_patch(Rectangle((0, 0), 420, 297, color=PAPER, zorder=-10))
        ax.add_patch(Rectangle((8, 8), 404, 281, fc='none', ec=INK, lw=0.7, zorder=1))
        ax.text(13, 283.2, title_vi.upper(), fontweight='bold', fontsize=12.5, color=INK, va='center', zorder=2)
        ax.text(407, 283.2, title_en, fontsize=8, color=MUTED, va='center', ha='right', zorder=2)
        ax.plot([8, 412], [278, 278], color=INK, lw=0.4)
        ax.plot([8, 412], [16, 16], color=INK, lw=0.4)
        ax.text(13, 12, 'SAMARKAND', fontweight='bold', fontsize=9, va='center')
        ax.text(42, 12, 'Đà Nẵng  ·  R12-v12.1  ·  11/2026  ·  kích thước mm / dimensions in mm  ·  cao độ m / levels in m', fontsize=5.6, color=MUTED, va='center')
        ax.text(407, 12, f'{code}    {num}/{total}', fontsize=10, fontweight='bold', ha='right', va='center', color=INK, zorder=2)
    def save(self, pdf):
        for t_ in self.fig.findobj(matplotlib.text.Text):                      # v2: small annotation text 22 % larger (readable on an A3 print)
            if t_.get_fontsize() < 7.6: t_.set_fontsize(t_.get_fontsize() * 1.22)
        pdf.savefig(self.fig, facecolor=PAPER); plt.close(self.fig)

# ------------------------------------------------------------------ views
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
_HC = {}
def hload(name):
    if name not in _HC: _HC[name] = json.load(open(f'{HOUT}/{name}.json'))
    return _HC[name]
def seg_patch(S, **kw):
    S = np.asarray(S, float).reshape(-1, 4); n = len(S)
    if n == 0: return None
    verts = S.reshape(-1, 2); codes = np.tile([MPath.MOVETO, MPath.LINETO], n)
    return PathPatch(MPath(verts, codes), fill=False, **kw)
class View:
    """a vector hidden-line view placed on the page at a true scale. view metres: h (right), v (up), origin = camera centre."""
    def __init__(self, page, name, x_mm, y_mm, scale, crop=None, flip=False, dmax=None, lw=0.2, poche='#cfcfcf', col='#000000', cutcol=None, **kw):
        J = hload(name); self.J = J; self.name = name
        self.C = np.array(J['cam']); self.R = np.array(J['right']); self.U = np.array(J['up'])
        sg = -1.0 if flip else 1.0
        if flip: self.U = -self.U
        s = J['scale']; Hm = s * J['H'] / J['W']
        h0, h1, v0, v1 = crop or (-s / 2, s / 2, -Hm / 2, Hm / 2)
        self.scale = scale; self.crop = (h0, h1, v0, v1)
        w_mm, h_mm = (h1 - h0) * 1000 / scale, (v1 - v0) * 1000 / scale
        fig = page.fig
        self.ax = fig.add_axes([x_mm / 420, y_mm / 297, w_mm / 420, h_mm / 297]); ax = self.ax
        ax.set_xlim(h0, h1); ax.set_ylim(v0, v1); ax.axis('off'); ax.set_zorder(3); ax.patch.set_alpha(0)
        V = np.asarray(J['vis'], float).reshape(-1, 5)
        if dmax: V = V[V[:, 4] <= dmax]
        V = V[:, :4].copy(); V[:, 1] *= sg; V[:, 3] *= sg
        m = (np.maximum(V[:, 0], V[:, 2]) >= h0) & (np.minimum(V[:, 0], V[:, 2]) <= h1) & (np.maximum(V[:, 1], V[:, 3]) >= v0) & (np.minimum(V[:, 1], V[:, 3]) <= v1)
        V = V[m]
        V = V[np.hypot(V[:, 2] - V[:, 0], V[:, 3] - V[:, 1]) * 1000 / scale > 0.05]          # drop sub-0.05 mm specks
        self.vis = V
        cs = []
        for nm_, ss in J['cut']:
            a = np.asarray(ss, float).reshape(-1, 4); a[:, 1] *= sg; a[:, 3] *= sg; cs.append(a)
        C_ = np.concatenate(cs) if cs else np.zeros((0, 4))
        self.cutseg = C_
        if poche and len(cs):
            try:
                from shapely.geometry import LineString
                from shapely.ops import polygonize, unary_union
                from matplotlib.patches import PathPatch as PP
                for a in cs:
                    if len(a) < 3 or len(a) > 6000: continue
                    lines = [LineString([(r[0], r[1]), (r[2], r[3])]) for r in np.round(a, 3) if (r[0], r[1]) != (r[2], r[3])]
                    for pg_ in polygonize(unary_union(lines)):
                        if pg_.area < 2e-5: continue
                        x_, y_ = pg_.exterior.xy
                        ax.fill(x_, y_, fc=('#ececec' if pg_.area > 40 else poche), ec='none', zorder=1)
            except Exception as e: print('poche', name, e)
        p = seg_patch(V, ec=col, lw=lw, zorder=2, capstyle='round')
        if p is not None: ax.add_patch(p)
        p = seg_patch(C_, ec=cutcol or col, lw=max(0.55, lw * 3), zorder=3, capstyle='round')
        if p is not None: ax.add_patch(p)
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
    ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color=col, lw=0.45, zorder=6, clip_on=False)
    if ext:
        for p, q in ((a, pa), (b, pb)): ax.plot([p[0] + nrm[0] * 0.6 * k, q[0] + nrm[0] * 1.2 * k], [p[1] + nrm[1] * 0.6 * k, q[1] + nrm[1] * 1.2 * k], color=col, lw=0.3, zorder=6, clip_on=False)
    for p in (pa, pb):                                      # architectural ticks
        tk = (t + nrm) / np.linalg.norm(t + nrm) * 1.0 * k
        ax.plot([p[0] - tk[0], p[0] + tk[0]], [p[1] - tk[1], p[1] + tk[1]], color=col, lw=0.8, zorder=6, clip_on=False)
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
    ax.add_patch(MPoly([[h, vv], [h - 1.3 * k, vv + 1.6 * k], [h + 1.3 * k, vv + 1.6 * k]], closed=True, fc=col, ec=col, lw=0.3, zorder=7, clip_on=False))
    ax.plot([h, h + side * 18 * k], [vv + 1.6 * k] * 2, color=col, lw=0.4, zorder=7, clip_on=False)
    ax.text(h + side * 2 * k, vv + 2.4 * k, text, fontsize=fs, color=col, ha='left' if side > 0 else 'right', va='bottom', zorder=7)
def bubble(v, h, vv, txt, r=3.2, col=INK, fs=6.5):
    ax = v.ax; k = _k(v)
    ax.add_patch(Circle((h, vv), r * k, fc='white', ec=col, lw=0.6, zorder=8, clip_on=False))
    ax.text(h, vv, txt, fontsize=fs, ha='center', va='center', fontweight='bold', color=col, zorder=9)
def gridline(v, a, b, txt, ends=(True, True)):
    ax = v.ax; k = _k(v)
    ax.plot([a[0], b[0]], [a[1], b[1]], color='#8a8a8a', lw=0.35, ls=(0, (8, 2, 1, 2)), zorder=5, clip_on=False)
    d = np.array(b) - np.array(a); d = d / np.linalg.norm(d)
    if ends[0]: bubble(v, a[0] - d[0] * 3.2 * k, a[1] - d[1] * 3.2 * k, txt)
    if ends[1]: bubble(v, b[0] + d[0] * 3.2 * k, b[1] + d[1] * 3.2 * k, txt)
def tag(v, xy, text, dxy=(8, 8), fs=5.0, col=INK, ha=None, num=None):
    """leader label: point xy (view m) -> text offset dxy (paper mm)"""
    ax = v.ax; k = _k(v); tx = xy[0] + dxy[0] * k; ty = xy[1] + dxy[1] * k
    ax.plot([xy[0], tx], [xy[1], ty], color=col, lw=0.35, zorder=8, clip_on=False); ax.add_patch(Circle(xy, 0.5 * k, color=col, zorder=8, clip_on=False))
    ha = ha or ('left' if dxy[0] >= 0 else 'right')
    if num is not None:
        bubble(v, tx + (2.2 if ha == 'left' else -2.2) * k, ty, str(num), r=2.2, col=BLUE, fs=5.2)
    else:
        ax.text(tx + (0.8 if ha == 'left' else -0.8) * k, ty, text, fontsize=fs, ha=ha, va='center', color=col, zorder=8,
                bbox=dict(boxstyle='square,pad=0.15', fc=PAPER, ec='none', alpha=0.9))
def title(page, x, y, n, vi, en, scale_txt, w=120):
    ax = page.ax
    ax.add_patch(Circle((x + 4, y), 4, fc='white', ec=INK, lw=0.7, zorder=4)); ax.text(x + 4, y, str(n), color=INK, fontsize=8, fontweight='bold', ha='center', va='center', zorder=5)
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
    ax = page.ax; ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='square,pad=0', fc='white', ec='#111111', lw=0.35, zorder=2))
    if head:
        ax.add_patch(Rectangle((x, y + h - 6), w, 6, fc='#e8e8e8', ec='#111111', lw=0.35, zorder=3))
        ax.text(x + 2.5, y + h - 3, head, color=INK, fontsize=6.2, fontweight='bold', va='center', zorder=4)
def table(page, x, y, cols, rows, widths, fs=5.0, rh=4.2, head_bg='#e8e8e8'):
    """simple ruled table, top-left at (x, y)"""
    ax = page.ax; yy = y
    def row(cells, bg=None, bold=False):
        nonlocal yy
        if bg: ax.add_patch(Rectangle((x, yy - rh), sum(widths), rh, fc=bg, ec='none', zorder=3))
        cx = x
        for c, w in zip(cells, widths):
            ax.text(cx + 1, yy - rh / 2, str(c), fontsize=fs, va='center', fontweight='bold' if bold else 'normal', zorder=4, clip_on=False)
            cx += w
        ax.plot([x, x + sum(widths)], [yy - rh, yy - rh], color='#999999', lw=0.25, zorder=4); yy -= rh
    row(cols, head_bg, True)
    for r in rows: row(r)
    return yy
def text_block(page, x, y, lines, fs=5.6, lh=3.6, col=INK, bold_first=False):
    for i, l in enumerate(lines):
        page.ax.text(x, y - i * lh, l, fontsize=fs, color=col, va='top', fontweight='bold' if (bold_first and i == 0) else 'normal', zorder=4)
    return y - len(lines) * lh
