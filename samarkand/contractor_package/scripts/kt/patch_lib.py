import re
p='kt/lib.py'; s=open(p).read()
s=s.replace("OUT = os.path.join(os.path.dirname(__file__), 'out')","OUT = os.path.join(os.path.dirname(__file__), '..', 'cd', 'out'); HOUT = os.path.join(os.path.dirname(__file__), '..', 'hlr', 'out'); KOUT = os.path.join(os.path.dirname(__file__), 'out'); os.makedirs(KOUT, exist_ok=True)")
s=s.replace("PAPER = '#f6f1e6'; GREEN = '#a9d18e'; GREEN_D = '#2f5d23'; INK = '#1b1b1b'; RED = '#9b1c1c'; BLUE = '#1f3f8a'; MUTED = '#6b5d4c'",
            "PAPER = '#ffffff'; GREEN = '#e8e8e8'; GREEN_D = '#111111'; INK = '#111111'; RED = '#b3261e'; BLUE = '#1f3f8a'; MUTED = '#666666'")
s=s.replace("SERIF = 'DejaVu Serif'","SERIF = 'DejaVu Sans'")
a=s.index("        ax.add_patch(Rectangle((0, 0), 420, 297, color=PAPER, zorder=-10))"); b=s.index("    def save(self, pdf):")
s=s[:a]+'''        ax.add_patch(Rectangle((0, 0), 420, 297, color=PAPER, zorder=-10))
        ax.add_patch(Rectangle((8, 8), 404, 281, fc='none', ec=INK, lw=0.7, zorder=1))
        ax.text(13, 283.2, title_vi.upper(), fontweight='bold', fontsize=12.5, color=INK, va='center', zorder=2)
        ax.text(407, 283.2, title_en, fontsize=8, color=MUTED, va='center', ha='right', zorder=2)
        ax.plot([8, 412], [278, 278], color=INK, lw=0.4)
        ax.plot([8, 412], [16, 16], color=INK, lw=0.4)
        ax.text(13, 12, 'SAMARKAND', fontweight='bold', fontsize=9, va='center')
        ax.text(42, 12, 'Đà Nẵng  ·  R12-v12.1  ·  11/2026  ·  kích thước mm / dimensions in mm  ·  cao độ m / levels in m', fontsize=5.6, color=MUTED, va='center')
        ax.text(407, 12, f'{code}    {num}/{total}', fontsize=10, fontweight='bold', ha='right', va='center', color=INK, zorder=2)
'''+s[b:]
a=s.index("def line_image("); b=s.index("    def P(self, x, y, z):")
s=s[:a]+'''from matplotlib.path import Path as MPath
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
    def __init__(self, page, name, x_mm, y_mm, scale, crop=None, flip=False, dmax=None, lw=0.2, poche='#cfcfcf', **kw):
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
                        ax.fill(x_, y_, fc=poche, ec='none', zorder=1)
            except Exception as e: print('poche', name, e)
        p = seg_patch(V, ec='#000000', lw=lw, zorder=2, capstyle='round')
        if p is not None: ax.add_patch(p)
        p = seg_patch(C_, ec='#000000', lw=max(0.55, lw * 3), zorder=3, capstyle='round')
        if p is not None: ax.add_patch(p)
        self.box = (x_mm, y_mm, w_mm, h_mm); self.mpu = 1000 / scale       # mm on paper per metre
'''+s[b:]
s=s.replace("ax.add_patch(Circle((x + 4, y), 4, fc=GREEN_D, ec='none', zorder=4)); ax.text(x + 4, y, str(n), color='white'","ax.add_patch(Circle((x + 4, y), 4, fc='white', ec=INK, lw=0.7, zorder=4)); ax.text(x + 4, y, str(n), color=INK")
s=s.replace("boxstyle='round,pad=0,rounding_size=1.5', fc='white', ec='#b9ab92', lw=0.5","boxstyle='square,pad=0', fc='white', ec='#111111', lw=0.35")
s=s.replace("ax.add_patch(Rectangle((x, y + h - 6), w, 6, fc=GREEN_D, ec='none', zorder=3))","ax.add_patch(Rectangle((x, y + h - 6), w, 6, fc='#e8e8e8', ec='#111111', lw=0.35, zorder=3))")
s=s.replace("head, color='white', fontsize=6.2","head, color=INK, fontsize=6.2")
s=s.replace("head_bg='#e7efe0'","head_bg='#e8e8e8'").replace("color='#c9bea9', lw=0.3","color='#999999', lw=0.25")
open(p,'w').write(s)
