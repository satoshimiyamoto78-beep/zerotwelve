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
fig.text(0.02, 0.975, 'SAMARKAND — new roof round the kept pergola + room above (sample, how it is built)', fontsize=16, weight='bold', color=C['txt'], **F)
fig.text(0.02, 0.952, 'Standing-seam roof sheet Klip-Lok / Seamlock type, fall 3.5 % (2°) to the street gutter · one sheet length facade → gutter, no end laps, no screws through the sheet · schematic, levels in m, ±0.000 = hall floor',
         fontsize=8.5, color='#555', **F)

# ------------------------------------------------------------------ A. SECTION
RH = 2.8; RT = PTOP + 0.12 + RH + 0.12; GAP = 0.3
W0, W1 = PX0 - .25, PX1 + .25                     # room walls (on the pergola outline)
ax = fig.add_axes([0.02, 0.50, 0.64, 0.43]); ax.set_xlim(-1.6, 14.2); ax.set_ylim(-0.9, 6.9); ax.axis('off')
ax.text(-1.5, 6.75, 'A  SECTION THROUGH THE PERGOLA + ROOM ABOVE  (building → street)', fontsize=10, weight='bold', **F)
ax.fill_between([-1.6, 14.2], -0.9, TER, color='#e4e1dc'); ax.plot([0, 14.2], [TER, TER], color='#333', lw=1)
ax.add_patch(Rectangle((-1.6, TER), 1.6, 7.2, fc=C['wall'], ec='#333')); ax.text(-0.8, 1.2, 'EXISTING\nBUILDING', ha='center', fontsize=7, color='#666', **F)
ax.add_patch(Rectangle((-1.6, 3.85), 3.1, 0.18, fc='#bbb', ec='#333')); ax.text(0.05, 4.1, 'balcony slab, soffit +3.85', fontsize=6.5, **F)
# pergola + room (existing, untouched)
for px in (PX0, (PX0 + PX1) / 2, PX1):
    ax.add_patch(Rectangle((px - .1, TER), .2, PTOP - .4 - TER, fc=C['old'], ec='black', lw=.5))
ax.add_patch(Rectangle((W0, PTOP - .4), W1 - W0, .4, fc=C['old'], ec='black', lw=.5))
ax.add_patch(Rectangle((W0, PTOP), W1 - W0, RT - PTOP, fc='#efe9df', ec='#333', lw=1))
ax.text((W0 + W1) / 2, PTOP + 1.4, 'EXISTING CLOSED ROOM ON THE PERGOLA\nown roof — not touched, not loaded', ha='center', fontsize=8, weight='bold', color='#5a3510', **F)
ax.text((PX0 + PX1) / 2, 1.3, 'EXISTING PERGOLA (kept)\nsteel posts + beams, clad later as Khiva columns', ha='center', fontsize=7.5, color='#5a3510', **F)
# new structure: west field facade -> room, east field room -> street
ax.add_patch(Rectangle((0, top(0) - SHEET - PUR - .3), .1, .3, fc=C['new'])); ax.text(.15, top(0) - 1.05, 'ledger C300 on the facade\nchem. anchors M16 @ 600', fontsize=6.3, color=C['new'], **F)
ax.add_patch(Rectangle((XG - .3 - .075, TER), .15, top(XG - .3) - SHEET - PUR - .3 - TER, fc=C['new']))
ax.text(XG - .55, 0.6, 'street column\nSHS 150', ha='right', fontsize=6.3, color=C['new'], **F)
for xa, xb in ((0, W0 - GAP - .08), (W1 + GAP + .08, XG - .3)):
    ax.plot([xa, xb], [top(xa) - SHEET - PUR - .15, top(xb) - SHEET - PUR - .15], color=C['new'], lw=5, alpha=.35)
for xt in (W0 - GAP - .04, W1 + GAP + .04):          # trimmers UPN 200
    ax.add_patch(Rectangle((xt - .04, top(xt) - SHEET - PUR), .08, PUR, fc=C['new'], ec='black', lw=.4))
ax.text(0.15, 2.0, 'roof beam IPE 300 on grid A ends\non the trimmer UPN 200 round the room', fontsize=6.3, color=C['new'], **F)
for x in [0.8 + i for i in range(13)]:
    if x > XG or W0 - GAP - .1 < x < W1 + GAP + .1: continue
    ax.add_patch(Rectangle((x - .05, top(x) - SHEET - PUR), .1, PUR, fc='white', ec=C['new'], lw=.8))
for xa, xb in ((0, W0 - GAP), (W1 + GAP, XG)):
    ax.fill_between([xa, xb], [top(xa) - SHEET - .05, top(xb) - SHEET - .05], [top(xa) - SHEET, top(xb) - SHEET], color=C['ins'])
    ax.plot([xa, xb], [top(xa), top(xb)], color='#555', lw=2.2)
# west: box gutter at the up-slope wall; east: cover flashing
gx = W0 - GAP
ax.add_patch(Polygon([(gx, top(gx) - .05), (W0 - .02, top(gx) - .05), (W0 - .02, top(gx) - .22), (gx, top(gx) - .22)], closed=True, fc='#ccc', ec='#333'))
ax.plot([W0 - .015, W0 - .015], [top(gx) - .1, top(gx) + .25], color='#333', lw=2)
ax.add_patch(Circle((W0 - .15, top(gx) - .05), .55, fill=False, ec=C['red'], lw=1.3, ls='--'))
ax.text(0.3, top(gx) + 1.05, 'box gutter 300 along the room wall\n(falls south → downpipe into the planter)\n+ wall upstand 250, counter-flashing', fontsize=6.5, color=C['red'], **F)
ex = W1 + GAP
ax.plot([W1 + .015, W1 + .015, ex + .02], [top(ex) + .25, top(ex) + .015, top(ex) + .015], color='#333', lw=2)
ax.add_patch(Circle((W1 + .15, top(ex)), .5, fill=False, ec=C['red'], lw=1.3, ls='--'))
ax.text(W1 + .7, top(ex) + .7, 'cover flashing 320 + upstand 250\non the room wall; sheets start here', fontsize=6.5, color=C['red'], **F)
ax.annotate('', (W1 + 2.6, top(W1 + 2.6) + .32), (W1 + 0.8, top(W1 + 0.8) + .32 + .06), arrowprops=dict(arrowstyle='->', color=C['new'], lw=1.4))
ax.text(W1 + 1.7, top(W1 + 1.7) - .55, 'water → 3.5 %', ha='center', fontsize=8, color=C['new'], **F)
g = XG
ax.add_patch(Polygon([(g, top(g) - .05), (g + .3, top(g) - .05), (g + .3, top(g) - .3), (g, top(g) - .3)], closed=True, fc='#ccc', ec='#333'))
ax.plot([g + .15, g + .15], [top(g) - .3, TER], color='#777', lw=2, ls=(0, (3, 2)))
ax.text(g + .35, top(g) - .2, f'box gutter 250\nroof +{top(XG):.3f}', fontsize=6.3, **F)
def lev(x, z, s, side=1):
    ax.plot([x - .15, x + .15], [z, z], color='#333', lw=.8); ax.plot([x, x - .08, x + .08, x], [z, z + .1, z + .1, z], color='#333', lw=.8)
    ax.text(x + .2 * side, z + .02, s, fontsize=6.8, ha='left' if side > 0 else 'right', color='#c0392b', **F)
lev(0.5, top(0), f'+{top(0):.3f} roof top at facade', 1)
ax.text(PX0 + .3, PTOP - .62, f'▽ +{PTOP:.2f} top of pergola beams = room floor', fontsize=6.8, color='#c0392b', **F)
lev(13.6, TER, f'{TER:+.3f} terrace', -1)
gap = GAP


# ------------------------------------------------------------------ B. CLIP DETAIL
bx = fig.add_axes([0.68, 0.53, 0.30, 0.40]); bx.set_xlim(0, 12.5); bx.set_ylim(0, 8); bx.axis('off'); bx.set_aspect('equal')
bx.text(0, 7.7, 'B  DETAIL — how the sheet is fixed (no holes in the roof)', fontsize=10, weight='bold', **F)
bx.add_patch(Rectangle((1, 1.0), 8, .35, fc='white', ec=C['new'], lw=1.5)); bx.add_patch(Rectangle((4.6, .2), .35, 1.15, fc='white', ec=C['new'], lw=1.5))
bx.text(9.1, 1.0, 'purlin C200 @ 1000', fontsize=7, color=C['new'], **F)
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
    a.set_aspect('equal'); a.axis('off'); a.set_xlim(-10, 13); a.set_ylim(-1.5, 17.5)
    W0_, W1_, RY1 = PX0 - .25, PX1 + .25, PY1 + .1          # room footprint (schematic, on the boundary wall)
    CX0, CX1, CY1 = W0_ - .3, W1_ + .3, RY1 + .3            # roof cut 300 off its walls
    a.add_patch(Polygon([P(0, 0, TER), P(XG, 0, TER), P(XG, Y1, TER), P(0, Y1, TER)], closed=True, fc='#eeeae3', ec='#999', lw=.4))
    box(a, -1.2, 0, TER, 0, Y1, 4.2, C['wall'], lw=.4)
    box(a, 0, -0.25, TER, XG, 0, 1.6, '#cfc8bd', lw=.4)
    for px in (PX0, (PX0 + PX1) / 2, PX1):
        for py in (PY0, PY1):
            box(a, px - .1, py - .1, TER, px + .1, py + .1, PTOP - .4, C['old'])
    fields_back = [(CX1, XG, 0, Y1), (CX0, CX1, CY1, Y1)]; fields_front = [(0, CX0, 0, Y1)]
    def layer(fields):
        if step >= 2:
            for x0, x1, y0, y1 in fields:
                for yb in (4.1, Y1):
                    if y0 <= yb <= y1:
                        xa, xb = max(x0, 0), min(x1, XG - .3)
                        if xb > xa: box(a, xa, yb - .07, top(xb) - .55, xb, yb + .07, top(xb) - .25, C['new'], lw=.15)
        if step >= 3:
            for x in [0.8 + i for i in range(13)]:
                for x0, x1, y0, y1 in fields:
                    if x0 < x < x1: box(a, x - .05, y0, top(x) - SHEET - PUR, x + .05, y1, top(x) - SHEET, '#ffffff', ec=C['new'], lw=.3)
        if step == 4:
            for x0, x1, y0, y1 in fields: plane(a, x0, x1, y0, y1, lambda x: top(x) - SHEET + .005, C['ins'], alpha=.9)
        if step >= 5:
            for x0, x1, y0, y1 in fields:
                n = max(2, int((y1 - y0) / 0.41))
                for k in range(n): plane(a, x0, x1, y0 + (y1 - y0) * k / n, y0 + (y1 - y0) * (k + 1) / n, top, C['sheet'], ec='#5b6670')
    def trimmers():
        if step >= 2:
            for xt in (CX0 - .04, CX1 + .04): box(a, xt - .04, 0, top(xt) - SHEET - PUR, xt + .04, Y1, top(xt) - SHEET, '#1d4f9a', lw=.3)
            box(a, CX0, CY1, top(CX1) - SHEET - PUR, CX1, CY1 + .08, top(CX0) - SHEET, '#1d4f9a', lw=.3)
    layer(fields_back); trimmers()
    if step >= 2:
        box(a, 0, 0, top(0) - .55, .12, Y1, top(0) - .25, C['new'])
        for c in ((XG - .3, 4.1), (XG - .3, Y1)): box(a, c[0] - .08, c[1] - .08, TER, c[0] + .08, c[1] + .08, top(c[0]) - .55, C['new'])
    box(a, W0_, 0, PTOP - .4, W1_, RY1, PTOP, C['old'])                         # pergola beams
    box(a, W0_, 0, PTOP, W1_, RY1, PTOP + 0.12 + 2.8 + 0.12, '#efe9df', lw=.5)   # closed room on top
    if step == 1: a.text(*P(W1_, 0, PTOP + 3.4), 'room on the pergola\n= kept, own roof', fontsize=7.5, color='#5a3510', **F)
    layer(fields_front)
    if step >= 6:
        box(a, XG, 0, top(XG) - .3, XG + .3, Y1, top(XG) - .05, '#bbbbbb')
        box(a, CX0, 0, top(CX0) - .2, W0_, RY1, top(CX0) - .05, '#bbbbbb')          # box gutter along the up-slope wall
        box(a, -0.05, 0, top(0), .1, Y1, top(0) + .12, '#888888')

STEPS = ['1  Survey. Pergola + the closed room on top stay\nas they are (own roof, not loaded).',
         '2  Ledger, beams IPE 300, street columns, TRIMMERS\nUPN 200 round the room (dark blue).',
         '3  Purlins @ 1.0 m, stopping on the trimmers\n300 off the room walls.',
         '4  Insulation blanket (foil-faced) on the three\nroof fields round the room.',
         '5  Klip-Lok sheets roll-formed on site, clipped;\nwest field ends at the room wall.',
         '6  Box gutter along the room west wall + downpipe,\ncover flashings N/E, street gutter.']
for i in range(6):
    a = fig.add_axes([0.01 + (i % 3) * 0.33, 0.025 + (1 - i // 3) * 0.225, 0.31, 0.215]); scene(a, i + 1)
    a.text(-9.8, 16.3, STEPS[i], fontsize=7.6, va='top', color=C['txt'], **F)
fig.text(0.02, 0.475, 'C  INSTALLATION SEQUENCE (isometric, schematic)', fontsize=10, weight='bold', **F)
fig.text(0.98, 0.008, 'Legend: brown = existing pergola (kept) · blue = new steel · yellow = insulation · grey = Klip-Lok sheet.  Final sizes: site survey + licensed structural engineer (typhoon clips & spacing).',
         ha='right', fontsize=7, color='#555', **F)
fig.savefig(OUT); print('ok', OUT, 'gap', round(gap * 1000))
