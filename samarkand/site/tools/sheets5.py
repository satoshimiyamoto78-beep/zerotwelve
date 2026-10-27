"""Construction drawing sheets R12-v5 from the model line extraction (r3d/drawings.py -> dwg5/lines.json).
Every sheet: A1 landscape, views at true scale, cut lines heavy, visible lines thin, dimensions, levels (relative to the
finished terrace floor = +0.000), notes, member schedule, title block. Output per sheet: SVG + DXF (paper space mm) + PNG.
Usage: python3 sheets5.py lines.json data.json OUTDIR"""
import sys, json, math, os
import ezdxf
LINES, DATA, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
V = json.load(open(LINES)); D = json.load(open(DATA))
TER, SID = -0.45, -1.17
def top(x): return 3.75 - 0.05 * x
W, H = 841.0, 594.0
REV = 'R12-v5'; DATE = '2026-10-27'

class Sheet:
    def __init__(s, code, title):
        s.code, s.title = code, title; s.svg = []; s.doc = ezdxf.new('R2010', setup=True); s.msp = s.doc.modelspace()
        for n, c, lw in (('CUT', 7, 50), ('VIS', 8, 13), ('DIM', 1, 13), ('TXT', 7, 18), ('FRAME', 7, 50), ('HATCH', 8, 9)):
            s.doc.layers.add(n, color=c, lineweight=lw)
    # ---- primitives in sheet mm (origin bottom-left) ----
    def line(s, a, b, layer='VIS', w=0.13, col='#222', dash=None):
        s.svg.append(f'<line x1="{a[0]:.2f}" y1="{H - a[1]:.2f}" x2="{b[0]:.2f}" y2="{H - b[1]:.2f}" stroke="{col}" stroke-width="{w}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
        s.msp.add_line(a, b, dxfattribs={'layer': layer})
    def poly(s, pts, layer='CUT', w=0.5, col='#000', close=False):
        d = ' '.join(f'{x:.2f},{H - y:.2f}' for x, y in pts)
        s.svg.append(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round"/>')
        s.msp.add_lwpolyline(pts, close=close, dxfattribs={'layer': layer})
    def text(s, p, t, size=2.5, anchor='start', layer='TXT', bold=False, col='#111', rot=0):
        tr = f' transform="rotate({-rot} {p[0]:.2f} {H - p[1]:.2f})"' if rot else ''
        s.svg.append(f'<text x="{p[0]:.2f}" y="{H - p[1]:.2f}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" text-anchor="{anchor}"'
                     f'{" font-weight=\"bold\"" if bold else ""} fill="{col}"{tr}>{t.replace("&", "&amp;").replace("<", "&lt;")}</text>')
        al = {'start': 'LEFT', 'middle': 'CENTER', 'end': 'RIGHT'}[anchor]
        e = s.msp.add_text(t, dxfattribs={'layer': layer, 'height': size * 0.8, 'rotation': rot}); e.set_placement(p, align=ezdxf.enums.TextEntityAlignment[al if al != 'CENTER' else 'CENTER'])
    def rect(s, x0, y0, x1, y1, layer='FRAME', w=0.35):
        s.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], layer, w, '#000', True)
    # ---- views ----
    def view(s, name, crop, scale, at, title, note=None, rot=False):
        """place view `name` cropped to crop=(u0, v0, u1, v1) (metres, in the drawn orientation) at sheet position `at` (lower-left mm),
        scale 1:scale; rot = quarter turn (drawn u = view v, drawn v = -view u)"""
        v = V[name]; u0, v0, u1, v1 = crop; k = 1000.0 / scale
        R = (lambda p: (p[1], -p[0])) if rot else (lambda p: p)
        def M(p): q = R(p); return (at[0] + (q[0] - u0) * k, at[1] + (q[1] - v0) * k)
        M.k = k
        def clip(a, b):
            (x0, y0), (x1, y1) = a, b; t0, t1 = 0.0, 1.0; dx, dy = x1 - x0, y1 - y0
            for p_, q_ in ((-dx, x0 - u0), (dx, u1 - x0), (-dy, y0 - v0), (dy, v1 - y0)):
                if abs(p_) < 1e-12:
                    if q_ < 0: return None
                    continue
                r = q_ / p_
                if p_ < 0: t0 = max(t0, r)
                else: t1 = min(t1, r)
                if t0 > t1: return None
            return (x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy)
        g = ['<g stroke-linecap="round">']
        for a, b in v['vis']:
            c = clip(R(a), R(b))
            if c: A, B = (at[0] + (c[0][0] - u0) * k, at[1] + (c[0][1] - v0) * k), (at[0] + (c[1][0] - u0) * k, at[1] + (c[1][1] - v0) * k); g.append(f'<line x1="{A[0]:.2f}" y1="{H - A[1]:.2f}" x2="{B[0]:.2f}" y2="{H - B[1]:.2f}" stroke="#333" stroke-width="0.12"/>'); s.msp.add_line(A, B, dxfattribs={'layer': 'VIS'})
        for pl in v['cut']:
            seg = []
            for a, b in zip(pl, pl[1:]):
                c = clip(R(a), R(b))
                if c: seg.append(((at[0] + (c[0][0] - u0) * k, at[1] + (c[0][1] - v0) * k), (at[0] + (c[1][0] - u0) * k, at[1] + (c[1][1] - v0) * k)))
            for A, B in seg: g.append(f'<line x1="{A[0]:.2f}" y1="{H - A[1]:.2f}" x2="{B[0]:.2f}" y2="{H - B[1]:.2f}" stroke="#000" stroke-width="0.45"/>'); s.msp.add_line(A, B, dxfattribs={'layer': 'CUT'})
        g.append('</g>'); s.svg += g
        w_, h_ = (u1 - u0) * k, (v1 - v0) * k
        s.text((at[0], at[1] - 7), f'{title}   1:{scale}', 4.0, bold=True); s.line((at[0], at[1] - 8.2), (at[0] + max(60, len(title) * 2.6), at[1] - 8.2), 'TXT', 0.35, '#000')
        if note: s.text((at[0], at[1] - 12.5), note, 2.4, col='#444')
        return M, k
    # ---- annotation in view coordinates ----
    def dim(s, M, a, b, off, txt=None, horiz=None):
        """linear dimension between view points a, b (metres); off = offset in mm perpendicular (+ = up / right)"""
        A, B = M(a), M(b); hz = abs(A[1] - B[1]) < abs(A[0] - B[0]) if horiz is None else horiz
        L = (abs(B[0] - A[0]) if hz else abs(B[1] - A[1])) / M.k; txt = txt or f'{L * 1000:.0f}'
        if hz:
            y = max(A[1], B[1]) + off if off > 0 else min(A[1], B[1]) + off
            for P in (A, B): s.line(P, (P[0], y + (1.5 if off > 0 else -1.5)), 'DIM', 0.1, '#b00')
            s.line((A[0], y), (B[0], y), 'DIM', 0.13, '#b00')
            for P in (A, B): s.line((P[0] - 1, y - 1), (P[0] + 1, y + 1), 'DIM', 0.25, '#b00')
            s.text(((A[0] + B[0]) / 2, y + 1.0), txt, 2.2, 'middle', 'DIM', col='#b00')
        else:
            x = max(A[0], B[0]) + off if off > 0 else min(A[0], B[0]) + off
            for P in (A, B): s.line(P, (x + (1.5 if off > 0 else -1.5), P[1]), 'DIM', 0.1, '#b00')
            s.line((x, A[1]), (x, B[1]), 'DIM', 0.13, '#b00')
            for P in (A, B): s.line((x - 1, P[1] - 1), (x + 1, P[1] + 1), 'DIM', 0.25, '#b00')
            s.text((x - 1.0, (A[1] + B[1]) / 2), txt, 2.2, 'middle', 'DIM', col='#b00', rot=90)
    def level(s, M, p, label, side=1):
        """level mark: triangle + line + label (heights relative to the terrace floor)"""
        A = M(p); x = A[0] + side * 12
        s.line(A, (x, A[1]), 'DIM', 0.1, '#06c')
        s.poly([(x - 1.6, A[1] + 2.2), (x + 1.6, A[1] + 2.2), (x, A[1]), (x - 1.6, A[1] + 2.2)], 'DIM', 0.15, '#06c')
        s.text((x + side * 2.5, A[1] + 0.8), label, 2.3, 'start' if side > 0 else 'end', 'DIM', col='#06c')
    def note(s, M, p, dxy, txt, size=2.3):
        A = M(p); B = (A[0] + dxy[0], A[1] + dxy[1])
        s.line(A, B, 'TXT', 0.1, '#444'); s.svg.append(f'<circle cx="{A[0]:.2f}" cy="{H - A[1]:.2f}" r="0.5" fill="#444"/>')
        lines = txt.split('\n')
        for i, t in enumerate(lines): s.text((B[0] + (1 if dxy[0] >= 0 else -1), B[1] + 0.8 - i * (size + 0.8)), t, size, 'start' if dxy[0] >= 0 else 'end', col='#222')
    def table(s, x, y, rows, widths, size=2.3, head=True):
        rh = size + 2.2
        for i, r in enumerate(rows):
            yy = y - i * rh; cx = x
            for j, (c, w_) in enumerate(zip(r, widths)):
                s.text((cx + 1.2, yy - rh + 1.6), str(c), size, bold=(i == 0 and head)); cx += w_
            s.line((x, yy - rh), (x + sum(widths), yy - rh), 'TXT', 0.1 if i else 0.3, '#000')
        s.line((x, y), (x + sum(widths), y), 'TXT', 0.3, '#000')
        cx = x
        for w_ in widths + [0]:
            s.line((cx, y), (cx, y - len(rows) * rh), 'TXT', 0.1, '#000'); cx += w_
    def notes_block(s, x, y, title, lines, width=150, size=2.4):
        s.text((x, y), title, 3.0, bold=True); yy = y - 5
        for t in lines:
            words = t.split(' '); cur = ''
            for w_ in words:
                if len(cur) + len(w_) + 1 > width / (size * 0.52): s.text((x, yy), cur, size); yy -= size + 1.2; cur = '   ' + w_
                else: cur = (cur + ' ' + w_).strip() if cur else w_
            s.text((x, yy), cur, size); yy -= size + 1.6
        return yy
    def finish(s):
        s.rect(10, 10, W - 10, H - 10, w=0.5)
        x0, y0 = W - 10 - 190, 10                                                     # title block
        s.rect(x0, y0, W - 10, y0 + 46, w=0.35)
        for yy in (y0 + 34, y0 + 24, y0 + 14): s.line((x0, yy), (W - 10, yy), 'FRAME', 0.2, '#000')
        s.text((x0 + 3, y0 + 38), 'SAMARKAND — Uzbek / Tajik restaurant terrace · 254 Vo Nguyen Giap, Da Nang', 3.0, bold=True)
        s.text((x0 + 3, y0 + 27.5), s.title, 3.4, bold=True)
        s.text((x0 + 3, y0 + 17.5), 'Drawn from the 3D model (closed-shell, QA-clean); dimensions in mm, levels in m from the finished terrace floor ±0.000', 2.2)
        s.text((x0 + 3, y0 + 5), f'Sheet {s.code}    Rev {REV}    {DATE}    A1    Construction set — verify on site before fabrication', 2.6)
        body = ''.join(s.svg)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>{body}</svg>'
        base = os.path.join(OUT, f'{s.code}')
        open(base + '.svg', 'w').write(svg); s.doc.saveas(base + '.dxf')
        return base

sheets = []
# ======================================================================= S-01 ROOF FRAMING PLAN
s = Sheet('S-01', 'Roof framing plan — steel structure, dome ring girders')
v = V['S01_roof_framing_plan']
M, k = s.view('S01_roof_framing_plan', (-0.5, -14.0, 37.5, 0.6), 50, (32, 262), 'ROOF FRAMING PLAN (looking down, roof skin removed; street at the bottom)', rot=True, note=
              'IPE 300 roof beams on the column lines · C200 purlins @ 1000 · facade ledger C300 on the existing building (top) · dome ring girders IPE 300 rolled')
# The plan is 14 x 37.8 m: at 1:100 it is 141 x 378 mm.
ybs = sorted(y for y, _ in D['beams'])
for i, y in enumerate(ybs):
    A = M((-0.3, y)); s.svg.append(f'<circle cx="{A[0]:.2f}" cy="{H - A[1] - 7:.2f}" r="3.2" fill="none" stroke="#000" stroke-width="0.25"/>'); s.text((A[0], A[1] + 6), str(i + 1), 2.6, 'middle', bold=True)
for a, b in zip(ybs, ybs[1:]): s.dim(M, (13.6, a), (13.6, b), -8)
s.dim(M, (13.6, ybs[0]), (13.6, ybs[-1]), -18)
for d in D['domes']:
    cx, cy = d['c']; A = M((cx, cy))
    s.note(M, (cx - d['r'] - 0.06, cy - 0.6), (8, 26), f"Dome {d['key']}: ring girder IPE 300 rolled R{(d['r'] + 0.06) * 1000:.0f}\ncurb C200 ring R{d['r'] * 1000:.0f}-{(d['r'] + 0.12) * 1000:.0f} · dome R{d['r'] * 1000:.0f}, rise {d['rise'] * 1000:.0f}")
cols = [c for c in D['cols'] if not (c[1] < 0.6 and c[0] < 0)]
for x, y in cols: s.note(M, (x, y), (3, -10), 'C1 SHS 150')
s.note(M, (0.09, 33.5), (10, 10), 'facade ledger C300, chem. anchors M16 @ 600')
# member schedule
beams_len = []
for y, xe in D['beams']:
    segs = [(0.18, xe)]
    for d in D['domes']:
        dy = abs(y - d['c'][1]); rt = d['r'] + 0.135; dye = max(0.0, dy - 0.075)
        if dye < rt:
            h = math.sqrt(rt ** 2 - dye ** 2); c0, c1 = d['c'][0] - h, d['c'][0] + h
            segs = [(p, min(q, c0)) for p, q in segs if p < c0] + [(max(p, c1), q) for p, q in segs if q > c1]
    beams_len += [q - p for p, q in segs]
pur = 0.0; npur = 0
for x, y0, y1 in D['purlins']: pur += y1 - y0; npur += 1
rows = [('Mark', 'Member', 'Section', 'Qty', 'Total length / note')]
rows.append(('C1', 'Column', 'SHS 150x150x8, S355', str(len(cols) - 2), 'TER to beam underside; 2 more encased in the portal pylons'))
rows.append(('B1', 'Roof beam', 'IPE 300, S355', str(len(beams_len)), f'{sum(beams_len):.1f} m (cut at the dome girders)'))
rows.append(('P1', 'Purlin', 'C200x75x20x2.5 galv.', str(npur), f'~{pur:.0f} m (trimmed at domes)'))
rows.append(('R1', 'Dome ring girder', 'IPE 300 rolled (minor axis)', '3', ' / '.join(f"R{(d['r'] + 0.06) * 1000:.0f}" for d in D['domes'])))
rows.append(('R2', 'Drum curb', 'C200 rolled ring', '3', 'carries the drum studs + roof skin edge'))
rows.append(('L1', 'Facade ledger', 'C300, chem. anchors M16@600', '1', '37.1 m'))
rows.append(('K1', 'Purlin cleat', 'L80x80x8, 2xM12', str(sum(1 for x, y0, y1 in D['purlins'] for yb in ybs if y0 + 0.05 < yb < y1 - 0.05)), 'at every purlin / beam crossing'))
s.table(32, 245, rows, [14, 34, 50, 10, 120])
s.notes_block(300, 245, 'NOTES', [
    'Roof: insulated sandwich panel 50 mm on the purlins, fall 5 % to the street gutter (box gutter 250 wide on the street edge, outlets every 6 m).',
    'Beams IPE 300 bear on the facade ledger (end plate 10 mm, 4xM16 8.8) and on the columns (cap plate 15 mm, 4xM16). At the domes the beams frame into the ring girders (fin plate 10 mm, 3xM16).',
    'Ring girders IPE 300 rolled about the minor axis, 4 splices each (full-strength end plates), set in the 5 % roof plane; drum curb C200 ring welded on top.',
    'Columns SHS 150x150x8 on base plates 300x300x20, 4 chemical anchors M20 into the slab; clad by the majolica columns (sheet S-04).',
    'All steel: blast Sa 2.5, zinc-rich primer + 2 coats, colour RAL 8019 (exposed). Fire / structural check by the local engineer before fabrication.',
], 330)
sheets.append(s.finish())

# ======================================================================= S-02 CENTRAL DOME
dC = [d for d in D['domes'] if d['key'] == 'C'][0]; cx, cy = dC['c']; ZR = D.get('dome_ring', 3.9); r = dC['r']
s = Sheet('S-02', 'Central dome C — section, ring plan, build-up')
M, k = s.view('S02a_domeC_section', (cx - 4.0, -0.6, cx + 4.0, 7.3), 25, (30, 120), 'SECTION A-A THROUGH THE CENTRAL DOME', 'karbandi interior shell hung from the steel ribs · lantern · chandelier')
fl = lambda z: f'{z - TER:+.3f}'
s.level(M, (cx + 3.6, TER), fl(TER) + ' terrace floor', 1); s.level(M, (cx + r + 0.15, ZR), fl(ZR) + ' springing / ring beam top', 1)
s.level(M, (cx + r + 0.2, top(cx + r) - 0.25), fl(top(cx + r) - 0.25) + ' ring girder top (5 % roof plane)', 1)
lz = ZR + (dC['rise'] + 0.12) * math.cos(math.asin(min(0.999, dC['lantern'] / r)))
s.level(M, (cx + 0.6, lz), fl(lz) + ' lantern base', 1); s.level(M, (cx + 0.3, lz + 1.45), fl(lz + 1.45) + ' finial top', 1)
s.level(M, (cx - 1.2, TER + 3.65), fl(TER + 3.65) + ' chandelier hoop', -1)
s.dim(M, (cx - r, ZR), (cx + r, ZR), -8, f'Ø inside {2 * r * 1000:.0f}')
s.dim(M, (cx - r - 0.12, ZR), (cx - r - 0.12, ZR + dC['rise'] + 0.12), -14, f'{(dC["rise"] + 0.12) * 1000:.0f}')
s.note(M, (cx - r * 0.7, ZR + dC['rise'] * 0.72), (-30, 12), 'karbandi GRC shell 20 mm, glazed tile finish\nhung on 24 rods M10 from the ribs')
s.note(M, (cx + r * 0.75, ZR + dC['rise'] * 0.66), (28, 14), 'dome: 24 rolled ribs T80 + GRC 25 mm\nturquoise glazed brick tiles, ribbed')
s.note(M, (cx + r + 0.06, ZR - 0.4), (30, -6), 'drum: GRC panels on SHS 60 studs @ 600\nkufic glazed brick facing')
s.note(M, (cx - r + 0.05, ZR - 0.12), (-26, -10), 'ring beam UPN 240 rolled + LED cove')
s.note(M, (cx, TER + 3.6), (24, -18), f'chandelier R950, 12+6 pierced brass lanterns\nhung from the crown hook (SWL 150 kg)')
M2, k2 = s.view('S02b_domeC_plan_cut', (cx - 3.6, cy - 3.6, cx + 3.6, cy + 3.6), 50, (400, 340), 'PLAN CUT AT +4.300 (springing) — RING STRUCTURE', 'ring beam + drum cut; curb, ring girder, beams and purlins below')
s.dim(M2, (cx - r - 0.135, cy - 3.4), (cx + r + 0.135, cy - 3.4), -6, f'girder outer Ø {2 * (r + 0.135) * 1000:.0f}')
s.notes_block(560, 330, 'BUILD-UP & ASSEMBLY SEQUENCE', [
    '1. Erect the ring girder (IPE 300 rolled, 4 segments) on temporary props; bolt the beam fin plates; check level against the 5 % roof plane.',
    '2. Weld the C200 curb ring on the girder top flange; fix SHS 60 drum studs @ 600 (base plates 8 mm, 2xM12) and the top ring UPN 240 at +4.350.',
    '3. Set the 24 rolled T80 ribs from the ring beam to the lantern ring (CHS 1016x10), bolted 2xM16 each end; brace with 2 hoops (L60).',
    '4. Hang the karbandi GRC interior panels (precast from the 3D mould file) on M10 rods from the ribs; joint grout + tile touch-up.',
    '5. Close the shell: GRC 25 mm segments on the ribs, waterproof membrane, glazed brick tiles in the ribbed pattern; lantern glazing and copper cap, finial.',
    '6. Drum facing (kufic glazed brick), LED cove in the ring beam, chandelier hook test-loaded to 2 x SWL before hanging.',
], 270)
sheets.append(s.finish())

# ======================================================================= S-03 OCULUS DOME
dS = [d for d in D['domes'] if d['key'] == 'S'][0]; sx, sy = dS['c']; rS = dS['r']
s = Sheet('S-03', 'Oculus domes S / N — section through the tree opening')
M, k = s.view('S03_domeS_section', (sx - 4.2, -0.6, sx + 4.2, 6.6), 25, (30, 140), 'SECTION B-B THROUGH THE SOUTH DOME (oculus around the plane tree)', 'same structure as dome C without the lantern; open oculus R%d' % (dS['oc'] * 1000))
s.level(M, (sx + 3.9, TER), '+0.000 terrace floor', 1); s.level(M, (sx + rS + 0.15, ZR), fl(ZR) + ' springing', 1)
s.dim(M, (sx - dS['oc'], ZR + dS['rise'] * math.cos(math.asin(dS['oc'] / rS)) + 0.12), (sx + dS['oc'], ZR + dS['rise'] * math.cos(math.asin(dS['oc'] / rS)) + 0.12), 10, f'oculus Ø {2 * dS["oc"] * 1000:.0f}')
s.dim(M, (sx - rS, ZR), (sx + rS, ZR), -8, f'Ø inside {2 * rS * 1000:.0f}')
s.note(M, (sx + dS['oc'] + 0.05, ZR + 0.9), (30, 10), 'oculus ring CHS 168x8 rolled + copper drip edge\nrainwater falls on the tree pit (soil + gravel drain)')
s.note(M, (sx, TER + 1.5), (-34, 6), 'plane tree (chinar) trunk; pit 2 m, root barrier, ring bench')
s.notes_block(380, 140, 'NOTES', [
    'Oculus domes S (R3000, oculus R1800) and N (R2200, oculus R1200): ring girder / curb / drum / ring beam as dome C (S-02).',
    'Ribs end on the oculus ring (CHS 168x8 rolled); interior face of the shell in Samarkand glazed brick (bannai pattern), exterior turquoise ribbed tiles.',
    'Keep 300 mm clear between the canopy and the oculus ring; canopy pruning annually. Uplights in the pit (3 per tree).',
], 300)
sheets.append(s.finish())

# ======================================================================= S-04 MAJOLICA COLUMN
s = Sheet('S-04', 'Majolica column — cladding of the steel columns')
col = D['cols'][1]
M, k = s.view('S04a_column_elevation', (col[1] - 0.6, TER - 0.05, col[1] + 0.6, top(col[0] - 0.3) - 0.2), 10, (40, 160), 'ELEVATION', 'view from the street')
zt = top(col[0] + 0.36) - 0.55 - 0.002; H_ = zt - TER
for z, lab in ((0.0, 'plinth'), (0.06, 'die'), (0.40, 'cap'), (0.46, 'shaft'), (H_ - 0.5, 'capital'), (H_, 'beam')):
    s.level(M, (col[1] + 0.4, TER + z), f'+{z:.3f} {lab}', 1)
s.dim(M, (col[1] - 0.27, TER), (col[1] + 0.27, TER), -10, '540 (octagon)')
M2, _ = s.view('S04b_column_section', (col[1] - 0.6, TER - 0.05, col[1] + 0.6, top(col[0] - 0.3) - 0.2), 10, (240, 160), 'SECTION', 'steel core and cladding layers')
s.note(M2, (col[1] - 0.14, TER + 1.5), (-30, 20), 'GRC tube 25 mm, majolica tiles 10 mm\non spacer rings @ 600 to the SHS core')
s.note(M2, (col[1] + 0.0, TER + 1.0), (34, 10), 'SHS 150x150x8 steel column')
s.note(M2, (col[1] + 0.3, TER + H_ - 0.25), (30, 8), 'muqarnas capital: 4 tiers glazed GRC\n(turquoise / girih), stone abacus')
M3, _ = s.view('S04c_column_plan_cut', (col[0] - 0.32, col[1] - 0.32, col[0] + 0.32, col[1] + 0.32), 5, (440, 300), 'PLAN AT +0.200', 'octagonal stone plinth around the base plate')
s.notes_block(440, 250, 'NOTES', [
    'Plinth: limestone octagon 540 across, 3 courses (60 / 340 / 60), dowelled to the slab, open core around the base plate (grout after levelling).',
    'Shaft: 2 GRC half-shells per storey, mechanically fixed to spacer rings; joints on the column axis; tiles: Samarkand cobalt majolica + kufic bands.',
    'Capital: 4 GRC tiers (100 mm each) stepping 40 mm, glazed; stone abacus 720 octagon under the beam (20 mm clear above the sloped flange).',
    'Columns inside the street portal pylons are encased by the pylon brickwork (S-05).',
], 330)
sheets.append(s.finish())

# ======================================================================= S-05 PISHTAQ
e0, e1 = D['ent']; yc = (e0 + e1) / 2
s = Sheet('S-05', 'Street portal (pishtaq, Gur-e-Amir type) + sebil')
M, k = s.view('S05a_pishtaq_elevation', (e0 - 2.5, SID - 0.1, e1 + 1.2, 2.75), 25, (30, 260), 'FRONT ELEVATION FROM THE STREET', 'glazed-brick pylons, kufic frames, majolica panels, epigraphic band, muqarnas half-vault; sebil on the left')
s.dim(M, (e0 - 0.7, SID), (e0, SID), -10); s.dim(M, (e0, SID), (e1, SID), -10); s.dim(M, (e1, SID), (e1 + 0.7, SID), -10)
s.level(M, (e1 + 0.9, SID), f'{SID - TER:+.3f} sidewalk', 1); s.level(M, (e1 + 0.9, TER), '+0.000 terrace', 1)
xp = 0
Hp = min(top(11.387 + 0.75 - t) - 0.55 for t in (0.0, 1.5)) - SID
s.level(M, (e1 + 0.9, SID + Hp), f'{SID + Hp - TER:+.3f} top = beam underside', 1)
M2, _ = s.view('S05b_pishtaq_section', (9.4, SID - 0.3, 13.6, 2.75), 25, (30, 70), 'SECTION C-C ON THE PORTAL AXIS', 'entrance steps 4 x 180, muqarnas half-vault (6 tiers of niche cells)')
M3, _ = s.view('S05c_pishtaq_plan_cut', (10.3, e0 - 0.9, 12.7, e1 + 0.9), 25, (360, 260), 'PLAN AT +1.050 ABOVE THE SIDEWALK', 'pylons follow the street line (sheared 5.6°)')
s.notes_block(560, 260, 'NOTES', [
    'Pylons: RC core 400 + glazed brick facing (hazarbaf), stone plinth 550; they carry the roof beams at gridlines 3 and 4 (encasing columns C1).',
    'Front: kufic glazed-brick frames 100, majolica panels with pointed niches, epigraphic band; turquoise roll on the arch edge.',
    'Muqarnas: 6 tiers of GRC niche cells (cobalt / turquoise glazed), precast from the model, hung on a steel cradle from the lintel.',
    'Sebil: wall fountain, glazed brick + majolica tympanum, bronze spout, stone basin with recirculating pump.',
], 260)
sheets.append(s.finish())

# ======================================================================= S-06 ARCADE
s = Sheet('S-06', 'Khiva arcade — aivan / hall divider')
M, k = s.view('S06a_arcade_elevation', (15.1, -0.1, 28.7, 3.1), 50, (30, 330), 'ELEVATION FROM THE HALL', 'carved elm columns on tiled plinths, carved arch heads, carved frieze beam; jali and myrtle bays')
COLY = [15.45, 18.17] + [18.17 + (24.18 - 18.17) * i / 5 for i in range(1, 5)] + [24.18, 25.92, 27.13, 28.34]
for a, b in zip(COLY, COLY[1:]): s.dim(M, (a, 0.0), (b, 0.0), -9)
s.level(M, (28.5, 0.0), '+0.450 aivan floor', 1); s.level(M, (28.5, 2.78), '+3.230 capital top', 1); s.level(M, (28.5, 3.02), '+3.470 beam top', 1)
M2, _ = s.view('S06b_arcade_section', (2.7, -0.55, 3.75, 3.1), 20, (30, 90), 'SECTION D-D THROUGH A JALI BAY', '')
s.notes_block(250, 200, 'NOTES', [
    'Columns: carved elm, turned rings, kuza base, stepped walnut capital; on Rishtan-tiled plinths 240 sq x 450 fixed to the aivan slab edge (M16 studs).',
    'Bays: tiled parapet 500 + walnut cap; jali screens (CNC birch ply 24, walnut frame) with LED strip in the cap; myrtle planters (terracotta, liner + drip).',
    'Arch heads: carved walnut spandrels 100 thick hung from the frieze beam; a pierced brass lantern at each apex. Steps openings A (2740) and B (1740) keep full height.',
], 330)
sheets.append(s.finish())

# ======================================================================= S-07 BAR
s = Sheet('S-07', 'Bar — plan, back wall, counter, section')
M, k = s.view('S07a_bar_plan_cut', (0.0, 7.6, 3.2, 14.45), 25, (30, 60), 'PLAN AT +1.200', '')
s.dim(M, (0.14, 14.35), (0.14 + 0.55, 14.35), 6); s.dim(M, (1.5, 14.35), (2.38, 14.35), 6, '880 incl. 260 overhang')
M2, _ = s.view('S07b_bar_backwall_elevation', (8.5, -0.5, 14.4, 3.2), 25, (190, 360), 'BACK WALL ELEVATION', 'sculpted clay plaster with rounded niches, oak shelves + warm LED, reed fringe, wall carpet')
for nm, (rects, rad) in zip('N1 N2 N3 N4'.split(), [([(0.25, 1.25, 1.25, 2.75)], 0.14), ([(1.55, 1.25, 2.05, 2.62), (1.55, 1.25, 2.6, 1.86)], 0.11),
                                                   ([(2.9, 2.02, 4.45, 2.75), (2.9, 1.25, 3.7, 2.1), (3.55, 1.6, 4.0, 2.2)], 0.12), ([(3.95, 1.25, 4.55, 1.72)], 0.1)]):
    y0 = min(r_[0] for r_ in rects) + 8.6; y1 = max(r_[2] for r_ in rects) + 8.6; z1 = max(r_[3] for r_ in rects) + TER
    s.dim(M2, (y0, z1), (y1, z1), 5, f'{nm} {(y1 - y0) * 1000:.0f}')
s.level(M2, (14.35, TER + 0.96), '+0.960 back counter', 1); s.level(M2, (14.35, TER + 1.25), '+1.250 niche sills', 1); s.level(M2, (14.35, 3.10), '+3.550 wall top', 1)
M3, _ = s.view('S07c_bar_counter_elevation', (7.6, -0.5, 14.4, 0.7), 25, (190, 250), 'COUNTER FRONT ELEVATION', 'terracotta glazed baguettes 46 x 40/75 in 3 checkered rows, toe-kick LED, walnut top 60')
s.level(M3, (14.35, TER + 1.09), '+1.090 bar top', 1)
M4, _ = s.view('S07d_bar_section', (-0.1, -0.55, 3.2, 3.8), 20, (560, 250), 'SECTION E-E', '')
s.notes_block(560, 200, 'NOTES', [
    'Back wall: steel stud + cement board, sculpted clay (tadelakt-type) plaster; niche returns formed in bent board; shelves solid oak 30 on hidden brackets.',
    'Counter: plastered blockwork body, terracotta glazed baguettes on adhesive + mechanical clips, LED strip 2700 K in the toe kick; top walnut 60 with a 260 overhang.',
    'Stools: walnut frame, leather seat at +760, foot rail at +260. Pendants: beaded ikat drums Ø440 h300 on brass rods, bottom at +2.350.',
], 260)
sheets.append(s.finish())

# ======================================================================= S-08 BOOTH
b3 = D['booths'][2]; by0, by1, bxw, bxe, th = b3
s = Sheet('S-08', 'Themed booth (typical) — plan and section')
M, k = s.view('S08a_booth_plan_cut', (bxw - 0.25, by0 - 0.25, bxe + 0.45, by1 + 0.25), 20, (40, 120), 'PLAN AT +1.200 (booth 3 "Saman")', 'niche wall with framed epoch art, two banquettes, tiled table, open to the street')
s.dim(M, (bxw, by0 - 0.2), (bxe, by0 - 0.2), -6); s.dim(M, (bxe + 0.3, by0), (bxe + 0.3, by1), 6)
M2, _ = s.view('S08b_booth_section', (bxw - 0.3, -0.55, bxe + 0.45, 1.85), 20, (300, 120), 'SECTION F-F ACROSS THE BOOTH', '')
s.level(M2, (bxe + 0.35, TER), '+0.000', 1); s.level(M2, (bxe + 0.35, TER + 0.44), '+0.440 seat', 1); s.level(M2, (bxe + 0.35, TER + 0.76), '+0.760 table', 1); s.level(M2, (bxe + 0.35, TER + 2.25), '+2.250 cap', 1)
s.notes_block(560, 380, 'NOTES', [
    'Booth: walnut portal posts + carved arch head, velvet swag and curtains; quilted suzani ceiling panels; parapet 720 with majolica cap to the street.',
    'Banquettes: walnut plinth, emerald velvet, channel-tufted back, kilim lumbar pillows; table: walnut frame with zellige inlay, turned legs.',
    'Niche wall 160: through niche with a vase, framed epoch art panels on both faces.',
], 260)
sheets.append(s.finish())
print('\n'.join(sheets))
