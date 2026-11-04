"""Sample sheet: new standing-seam (Klip-Lok type) roof over the kept pergola — section, clip detail, 6 install steps (isometric).
Schematic: pergola squared to the axes, sizes from the DWG + site photos; final per site survey + structural engineer."""
import sys, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
OUT = sys.argv[1]
F = dict(family='DejaVu Sans')
TER, TOP0, FALL = -0.45, 3.75, 0.035
top = lambda x: TOP0 - FALL * x                    # roof sheet top (m, ±0 = hall floor)
SHEET, PUR, PUR_S = 0.041, 0.20, 0.10              # Klip-Lok rib 41, purlin C200, short purlin C100 over the pergola
PX0, PX1, PY0, PY1, PTOP = 3.3, 10.1, 1.2, 8.2, 3.15  # pergola (schematic), top of its beams
XG = 12.9                                          # street gutter line
C = dict(old='#8a5a2b', new='#2f5fb3', sheet='#9aa4ad', ins='#f2c94c', wall='#d9d4cc', red='#d62728', txt='#1f3a5f')

fig = plt.figure(figsize=(16.5, 11.7), dpi=150)
fig.text(0.02, 0.975, 'SAMARKAND — new roof over the kept pergola (sample, how it is built)', fontsize=16, weight='bold', color=C['txt'], **F)
fig.text(0.02, 0.952, 'Standing-seam roof sheet Klip-Lok / Seamlock type, fall 3.5 % (2°) to the street gutter · one sheet length facade → gutter, no end laps, no screws through the sheet · schematic, levels in m, ±0.000 = hall floor',
         fontsize=8.5, color='#555', **F)

# ------------------------------------------------------------------ A. SECTION
ax = fig.add_axes([0.02, 0.50, 0.64, 0.43]); ax.set_xlim(-1.6, 14.2); ax.set_ylim(-0.9, 4.9); ax.axis('off')
ax.text(-1.5, 4.75, 'A  SECTION THROUGH THE PERGOLA  (building → street)', fontsize=10, weight='bold', **F)
ax.fill_between([-1.6, 14.2], -0.9, TER, color='#e4e1dc'); ax.plot([0, 14.2], [TER, TER], color='#333', lw=1)
ax.add_patch(Rectangle((-1.6, TER), 1.6, 5.3, fc=C['wall'], ec='#333')); ax.text(-0.8, 1.2, 'EXISTING\nBUILDING', ha='center', fontsize=7, color='#666', **F)
ax.add_patch(Rectangle((-1.6, 3.85), 3.1, 0.18, fc='#bbb', ec='#333')); ax.text(0.05, 4.1, 'balcony slab, soffit +3.85', fontsize=6.5, **F)
# pergola
for px in (PX0, (PX0 + PX1) / 2, PX1):
    ax.add_patch(Rectangle((px - .1, TER), .2, PTOP - .2 - TER, fc=C['old'], ec='black', lw=.5))
ax.add_patch(Rectangle((PX0 - .25, PTOP - .2), PX1 - PX0 + .5, .2, fc=C['old'], ec='black', lw=.5))
ax.text((PX0 + PX1) / 2, 1.3, 'EXISTING PERGOLA (kept)\nsteel posts + beams, clad later as Khiva columns', ha='center', fontsize=7.5, color='#5a3510', **F)
ax.text((PX0 + PX1) / 2, PTOP - .45, 'old roof sheet removed', ha='center', fontsize=6.5, color=C['red'], **F)
# new structure
ax.add_patch(Rectangle((0, top(0) - SHEET - PUR - .3), .1, .3, fc=C['new'])); ax.text(.15, top(0) - 1.05, 'ledger C300 on the facade\nchem. anchors M16 @ 600', fontsize=6.3, color=C['new'], **F)
ax.add_patch(Rectangle((XG - .3 - .075, TER), .15, top(XG - .3) - SHEET - PUR - .3 - TER, fc=C['new']))
ax.text(XG - .55, 0.6, 'street column\nSHS 150', ha='right', fontsize=6.3, color=C['new'], **F)
for xa, xb in ((0, PX0 - .25), (PX1 + .25, XG - .3)):
    ax.plot([xa, xb], [top(xa) - SHEET - PUR - .15, top(xb) - SHEET - PUR - .15], color=C['new'], lw=5, alpha=.35)
ax.text(0.15, 2.0, 'roof beam IPE 300 — runs only outside\nthe pergola; on grid A it stops\nand bears on the pergola post', fontsize=6.3, color=C['new'], **F)
for x in [0.8 + i for i in range(13)]:
    if x > XG: break
    over = PX0 - .25 <= x <= PX1 + .25
    h = PUR_S if over else PUR
    zt = top(x) - SHEET
    ax.add_patch(Rectangle((x - .05, zt - h), .1, h, fc='white' if not over else '#cfe0ff', ec=C['new'], lw=.8))
    if over:
        ax.add_patch(Rectangle((x - .07, PTOP), .14, zt - h - PTOP, fc='#999', ec='none'))
# insulation + sheet
xs = [0, XG]
ax.fill_between(xs, [top(0) - SHEET - .05, top(XG) - SHEET - .05], [top(0) - SHEET, top(XG) - SHEET], color=C['ins'])
ax.plot(xs, [top(0), top(XG)], color='#555', lw=2.2)
ax.annotate('', (6.5, top(6.5) + .35), (4.5, top(4.5) + .35 + .07), arrowprops=dict(arrowstyle='->', color=C['new'], lw=1.4))
ax.text(5.5, top(5.5) + .45, 'water → 3.5 %', ha='center', fontsize=8, color=C['new'], **F)
# gutter
g = XG
ax.add_patch(Polygon([(g, top(g) - .05), (g + .3, top(g) - .05), (g + .3, top(g) - .3), (g, top(g) - .3)], closed=True, fc='#ccc', ec='#333'))
ax.plot([g + .15, g + .15], [top(g) - .3, TER], color='#777', lw=2, ls=(0, (3, 2)))
ax.text(g + .35, top(g) - .2, f'box gutter 250\nroof +{top(XG):.3f}', fontsize=6.3, **F)
# levels
def lev(x, z, s, side=1):
    ax.plot([x - .15, x + .15], [z, z], color='#333', lw=.8); ax.plot([x, x - .08, x + .08, x], [z, z + .1, z + .1, z], color='#333', lw=.8)
    ax.text(x + .2 * side, z + .02, s, fontsize=6.8, ha='left' if side > 0 else 'right', color='#c0392b', **F)
lev(0.5, top(0), f'+{top(0):.3f} roof top at facade', 1)
lev(PX1 + .5, top(PX1), f'+{top(PX1):.3f}', 1)
ax.text(PX0 + .3, PTOP - .42, f'▽ +{PTOP:.2f} top of pergola beams', fontsize=6.8, color='#c0392b', **F)
lev(13.6, TER, f'{TER:+.3f} terrace', -1)
gap = top(PX1) - SHEET - PUR_S - PTOP
ax.add_patch(Circle((PX1, PTOP + .12), .45, fill=False, ec=C['red'], lw=1.3, ls='--'))
ax.text(PX1 + .55, PTOP + .52, f'≈ {gap * 1000:.0f} mm free at the street edge\nshort purlins C100 on packers bolted\nto the pergola beams (confirm levels on site)', fontsize=6.5, color=C['red'], **F)

# ------------------------------------------------------------------ B. CLIP DETAIL
bx = fig.add_axes([0.68, 0.53, 0.30, 0.40]); bx.set_xlim(0, 12.5); bx.set_ylim(0, 8); bx.axis('off'); bx.set_aspect('equal')
bx.text(0, 7.7, 'B  DETAIL — how the sheet is fixed (no holes in the roof)', fontsize=10, weight='bold', **F)
bx.add_patch(Rectangle((1, 1.0), 8, .35, fc='white', ec=C['new'], lw=1.5)); bx.add_patch(Rectangle((4.6, .2), .35, 1.15, fc='white', ec=C['new'], lw=1.5))
bx.text(9.1, 1.0, 'purlin C200 (C100\nover the pergola)', fontsize=7, color=C['new'], **F)
bx.add_patch(Rectangle((1, 1.35), 8, .55, fc=C['ins'], ec='none')); bx.text(9.1, 1.5, 'insulation blanket\nfoil-faced 50 mm', fontsize=7, **F)
for cx in (2.6, 6.6):
    bx.add_patch(Polygon([(cx - .5, 1.9), (cx + .5, 1.9), (cx + .25, 3.4), (cx - .25, 3.4)], closed=True, fc='#7d8a96', ec='black', lw=.6))
    bx.plot([cx, cx], [1.9, 1.0], color='black', lw=1.5)
bx.text(2.6, 0.45, 'clip screwed\nto the purlin', ha='center', fontsize=7, **F)
pts = [(1, 1.9), (2.0, 1.9), (2.15, 3.6), (3.05, 3.6), (3.2, 1.9), (6.0, 1.9), (6.15, 3.6), (7.05, 3.6), (7.2, 1.9), (9, 1.9)]
bx.plot(*zip(*pts), color='#333', lw=2.2)
bx.text(4.6, 2.3, 'sheet pan (water runs here)', ha='center', fontsize=7, **F)
bx.text(6.6, 4.1, 'rib snaps over the clip →\nnext sheet locks the ribs', ha='center', fontsize=7, color=C['txt'], **F)
bx.text(0, 5.6, '• sheet roll-formed ON SITE in one length (≈ 13 m) — no end laps\n• rib 41 mm keeps water in the pans even at 2°\n• clips: more of them at edges/corners (typhoon) — engineer sets spacing\n• walk only on the purlin lines; soft shoes', fontsize=7.5, **F)

# ------------------------------------------------------------------ C. INSTALL STEPS (isometric)
c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
def P(x, y, z): return ((x - y) * c30, (x + y) * s30 + z * 1.0)
def box(a, x0, y0, z0, x1, y1, z1, fc, ec='black', lw=.3, alpha=1):
    v = lambda x, y, z: P(x, y, z)
    faces = [[v(x0, y0, z1), v(x1, y0, z1), v(x1, y1, z1), v(x0, y1, z1)],
             [v(x0, y0, z0), v(x1, y0, z0), v(x1, y0, z1), v(x0, y0, z1)],
             [v(x0, y0, z0), v(x0, y1, z0), v(x0, y1, z1), v(x0, y0, z1)]]
    for f, sh in zip(faces, (1.0, .8, .65)):
        col = matplotlib.colors.to_rgb(fc); col = tuple(min(1, c * sh) for c in col)
        a.add_patch(Polygon(f, closed=True, fc=col, ec=ec, lw=lw, alpha=alpha))
def plane(a, x0, x1, y0, y1, zf, fc, alpha=1, ec='#444'):
    a.add_patch(Polygon([P(x0, y0, zf(x0)), P(x1, y0, zf(x1)), P(x1, y1, zf(x1)), P(x0, y1, zf(x0))], closed=True, fc=fc, ec=ec, lw=.4, alpha=alpha))
Y1 = 9.85
def scene(a, step):
    a.set_aspect('equal'); a.axis('off'); a.set_xlim(-10, 13); a.set_ylim(-1.5, 16.5)
    a.add_patch(Polygon([P(0, 0, TER), P(XG, 0, TER), P(XG, Y1, TER), P(0, Y1, TER)], closed=True, fc='#eeeae3', ec='#999', lw=.4))
    box(a, -1.2, 0, TER, 0, Y1, 4.2, C['wall'], lw=.4)                       # building
    box(a, 0, -0.25, TER, XG, 0, 1.6, '#cfc8bd', lw=.4)                       # boundary wall (schematic)
    for px in (PX0, (PX0 + PX1) / 2, PX1):
        for py in (PY0, PY1):
            box(a, px - .1, py - .1, TER, px + .1, py + .1, PTOP - .2, C['old'])
    box(a, PX0 - .2, PY0 - .1, PTOP - .2, PX1 + .2, PY0 + .1, PTOP, C['old']); box(a, PX0 - .2, PY1 - .1, PTOP - .2, PX1 + .2, PY1 + .1, PTOP, C['old'])
    for x in [PX0 + .6 * i for i in range(12)]:
        if x <= PX1: box(a, x - .05, PY0, PTOP - .12, x + .05, PY1, PTOP, C['old'])
    if step == 1:
        plane(a, PX0 - .3, PX1 + .3, PY0 - .2, PY1 + .2, lambda x: PTOP + .02, '#c8a77e', alpha=.55)
        a.text(*P(PX1, PY0, PTOP + 1.4), '✕ old sheet off', fontsize=8, color=C['red'], **F)
    if step >= 2:
        box(a, 0, 0, top(0) - .55, .12, Y1, top(0) - .25, C['new'])
        for c in ((XG - .3, 4.1), (XG - .3, Y1)):
            box(a, c[0] - .08, c[1] - .08, TER, c[0] + .08, c[1] + .08, top(c[0]) - .55, C['new'])
        for yb, xa, xb in ((Y1, 0, XG - .3), (4.1, 0, PX0 - .1), (4.1, PX1 + .1, XG - .3)):
            for i in range(6):
                xx0 = xa + (xb - xa) * i / 6; xx1 = xa + (xb - xa) * (i + 1) / 6
                box(a, xx0, yb - .07, top(xx1) - .55, xx1, yb + .07, top(xx1) - .25, C['new'], lw=.15)
    if step >= 3:
        for x in [0.8 + i for i in range(13)]:
            if x > XG: break
            over = PX0 - .25 <= x <= PX1 + .25
            h = PUR_S if over else PUR
            box(a, x - .05, 0, top(x) - SHEET - h, x + .05, Y1, top(x) - SHEET, '#cfe0ff' if over else '#ffffff', ec=C['new'], lw=.3)
    if step >= 4:
        plane(a, 0, XG, 0, Y1, lambda x: top(x) - SHEET + .005, C['ins'], alpha=.9 if step == 4 else .0)
    if step >= 5:
        n = 24 if step >= 6 else 15
        for i in range(n):
            y0 = i * Y1 / 24; y1 = (i + 1) * Y1 / 24
            plane(a, 0, XG, y0, y1, top, C['sheet'], ec='#5b6670')
        if step == 5:
            a.text(*P(0, 15 * Y1 / 24 + .8, top(0) + .8), '→ next sheet', fontsize=7.5, color=C['txt'], **F)
    if step >= 6:
        box(a, XG, 0, top(XG) - .3, XG + .3, Y1, top(XG) - .05, '#bbbbbb')
        box(a, -0.05, 0, top(0), .1, Y1, top(0) + .12, '#888888')
STEPS = ['1  Remove the old pergola roof sheet.\nKeep posts + beams. Survey levels.',
         '2  Ledger on the facade, beams IPE 300,\nstreet columns. Grid-A beam stops at the pergola.',
         '3  Purlins @ 1.0 m. Over the pergola: short\nC100 purlins bolted to its beams (pale blue).',
         '4  Insulation blanket (foil-faced) laid\nover the purlins, edge to edge.',
         '5  Klip-Lok sheets roll-formed on site,\none length facade → gutter, clipped down.',
         '6  Box gutter + downpipes, facade flashing,\nridge cap. Below: carved cladding / ceiling.']
for i in range(6):
    a = fig.add_axes([0.01 + (i % 3) * 0.33, 0.025 + (1 - i // 3) * 0.225, 0.31, 0.215]); scene(a, i + 1)
    a.text(-9.8, 16.3, STEPS[i], fontsize=7.6, va='top', color=C['txt'], **F)
fig.text(0.02, 0.475, 'C  INSTALLATION SEQUENCE (isometric, schematic)', fontsize=10, weight='bold', **F)
fig.text(0.98, 0.008, 'Legend: brown = existing pergola (kept) · blue = new steel · yellow = insulation · grey = Klip-Lok sheet.  Final sizes: site survey + licensed structural engineer (typhoon clips & spacing).',
         ha='right', fontsize=7, color='#555', **F)
fig.savefig(OUT); print('ok', OUT, 'gap', round(gap * 1000))
