import json, math, re, sys
import numpy as np

class CAD:
    def __init__(self, path):
        db = json.load(open(path))
        self.db = db
        self.blocks = {b['name']: b for b in db['tables']['BLOCK_RECORD']['entries']}
        self.model = db['entities']
        self.layers = {l['name']: l for l in db['tables']['LAYER']['entries']}

    @staticmethod
    def clean(t):
        t = t or ''
        t = re.sub(r'\\[ACFHQTWfLlOoKk][^;\\{}]*;?', '', t)
        t = re.sub(r'\\P', ' ', t); t = re.sub(r'[{}]', '', t)
        return t.strip()

    def explode(self, ents=None, M=np.eye(3), depth=0, layer_override=None):
        """yield (kind, data, layer, entity) in world coords"""
        if ents is None: ents = self.model
        for e in ents:
            lay = e.get('layer', '0')
            if lay == '0' and layer_override: lay = layer_override
            if not e.get('isVisible', True): continue
            t = e['type']
            if t == 'LINE':
                yield 'seg', self.tf(M, [(e['startPoint']['x'], e['startPoint']['y']), (e['endPoint']['x'], e['endPoint']['y'])]), lay, e
            elif t == 'LWPOLYLINE':
                pts = self.lw_points(e)
                yield 'poly', self.tf(M, pts), lay, e
            elif t in ('POLYLINE2D', 'POLYLINE'):
                vs = e.get('vertices', [])
                pts = [(v['x'], v['y']) for v in vs]
                if e.get('flag', 0) & 1 and pts: pts.append(pts[0])
                yield 'poly', self.tf(M, pts), lay, e
            elif t == 'ARC':
                c = e['center']; r = e['radius']; a0 = e['startAngle']; a1 = e['endAngle']
                if a1 < a0: a1 += 2 * math.pi
                n = max(6, int((a1 - a0) / (math.pi / 36)))
                pts = [(c['x'] + r * math.cos(a0 + (a1 - a0) * i / n), c['y'] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
                if e.get('extrusionDirection', {}).get('z', 1) < 0: pts = [(-x, y) for x, y in pts]
                yield 'poly', self.tf(M, pts), lay, e
            elif t == 'CIRCLE':
                c = e['center']; r = e['radius']
                pts = [(c['x'] + r * math.cos(2 * math.pi * i / 48), c['y'] + r * math.sin(2 * math.pi * i / 48)) for i in range(49)]
                yield 'poly', self.tf(M, pts), lay, e
            elif t in ('TEXT', 'MTEXT', 'ATTRIB'):
                p = e.get('insertionPoint') if t == 'MTEXT' else e.get('startPoint')
                if p: yield 'text', (self.tf(M, [(p['x'], p['y'])])[0], self.clean(e.get('text')), e.get('textHeight', 0) * self.scale(M)), lay, e
            elif t == 'DIMENSION':
                yield 'dim', e, lay, e
                b = self.blocks.get(e.get('name'))
                if b and depth < 6: yield from self.explode(b.get('entities', []), M, depth + 1, lay)
            elif t == 'INSERT':
                b = self.blocks.get(e['name'])
                if not b or depth > 8: continue
                bp = b.get('basePoint', {'x': 0, 'y': 0})
                ip = e['insertionPoint']; sx = e.get('xScale', 1); sy = e.get('yScale', 1); r = e.get('rotation', 0)
                ex = e.get('extrusionDirection', {}).get('z', 1)
                if ex < 0: sx = -sx; ip = {'x': -ip['x'], 'y': ip['y']}
                T = np.array([[1, 0, ip['x']], [0, 1, ip['y']], [0, 0, 1]]) @ np.array([[math.cos(r), -math.sin(r), 0], [math.sin(r), math.cos(r), 0], [0, 0, 1]]) @ np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]]) @ np.array([[1, 0, -bp['x']], [0, 1, -bp['y']], [0, 0, 1]])
                yield from self.explode(b.get('entities', []), M @ T, depth + 1, lay)

    @staticmethod
    def scale(M): return math.hypot(M[0, 0], M[1, 0])
    @staticmethod
    def tf(M, pts):
        a = np.array([[x, y, 1] for x, y in pts]).T
        r = M @ a
        return [(float(r[0, i]), float(r[1, i])) for i in range(r.shape[1])]
    @staticmethod
    def lw_points(e):
        vs = e.get('vertices', [])
        closed = e.get('flag', 0) & 1
        out = []
        n = len(vs)
        for i in range(n if closed else n - 1 if n else 0):
            a = vs[i]; b = vs[(i + 1) % n]
            out.append((a['x'], a['y']))
            bu = a.get('bulge', 0) or 0
            if abs(bu) > 1e-9:
                th = 4 * math.atan(bu); dx = b['x'] - a['x']; dy = b['y'] - a['y']; ch = math.hypot(dx, dy)
                if ch > 0:
                    r = ch / (2 * math.sin(th / 2)); mx = (a['x'] + b['x']) / 2; my = (a['y'] + b['y']) / 2
                    d = r * math.cos(th / 2); nx, ny = -dy / ch, dx / ch
                    cx, cy = mx + nx * d, my + ny * d
                    a0 = math.atan2(a['y'] - cy, a['x'] - cx)
                    k = max(4, int(abs(th) / (math.pi / 36)))
                    for j in range(1, k): out.append((cx + abs(r) * math.cos(a0 + th * j / k) * (1 if r > 0 else 1), cy + abs(r) * math.sin(a0 + th * j / k)))
        if vs:
            if closed: out.append((vs[0]['x'], vs[0]['y']))
            else: out.append((vs[-1]['x'], vs[-1]['y']))
        return out

def render(cad, bbox, out, w_px=3000, skip_layers=(), texts=True, dims=True, highlight=None, grid=None, title=None):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    x0, y0, x1, y1 = bbox
    def inb(pts): return any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in pts)
    segs = []; cols = []; tx = []
    for kind, d, lay, e in cad.explode():
        if lay in skip_layers: continue
        if kind in ('seg', 'poly'):
            if len(d) >= 2 and inb(d):
                segs.append(d); cols.append('k' if not (highlight and lay in highlight) else highlight[lay])
        elif kind == 'text' and texts:
            (p, s, h) = d
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and s: tx.append((p, s, h, e.get('rotation', 0) if e['type'] != 'MTEXT' else 0))
    H = w_px * (y1 - y0) / (x1 - x0)
    fig = plt.figure(figsize=(w_px / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.axis('off')
    ax.add_collection(LineCollection(segs, colors=cols, linewidths=0.35))
    k = w_px / (x1 - x0)
    for p, s, h, r in tx:
        fs = max(3, h * k * 0.75)
        if fs > 2.5: ax.text(p[0], p[1], s[:60], fontsize=fs, rotation=math.degrees(r), color='#b00', va='bottom', ha='left')
    if grid:
        import numpy as np
        for gx in np.arange(math.ceil(x0 / grid) * grid, x1, grid): ax.axvline(gx, color='#0a0', lw=.3, alpha=.5); ax.text(gx, y1, f'{gx:.0f}', fontsize=6, color='g', va='top')
        for gy in np.arange(math.ceil(y0 / grid) * grid, y1, grid): ax.axhline(gy, color='#0a0', lw=.3, alpha=.5); ax.text(x0, gy, f'{gy:.0f}', fontsize=6, color='g')
    fig.savefig(out, facecolor='white'); plt.close(fig)
    return len(segs)
