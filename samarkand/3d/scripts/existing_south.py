"""Existing conditions, south zone (R12-v8.2 base update): kept pergola, demolished items, clashes with the current design.
Plan 1:75 + section through the pergola. Usage: python3 tools/existing_south.py zone.json r12/samarkand-3d-data-R12.json OUT.png"""
import sys, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

Z = json.load(open(sys.argv[1])); D = json.load(open(sys.argv[2])); OUT = sys.argv[3]
F = dict(family='DejaVu Sans')
ex = [[x / 1000, y / 1000] for x, y in Z['layers']['EXIST'][4]]          # pergola outline from the as-built DWG
posts = [Z['layers']['EXIST'][i] for i in range(5, 11)]
posts = [[(x / 1000, y / 1000) for x, y in p] for p in posts]
TER, TOP0, FALL = -0.45, 3.75, 0.035                                      # levels in m, ±0 = hall floor
roof_top = lambda x: TOP0 - FALL * x
PERG_LO, PERG_HI = TER + 3.2, TER + 3.6                                  # measured on site (photo 2)

fig = plt.figure(figsize=(16.5, 11.7), dpi=150)
ax = fig.add_axes([0.02, 0.27, 0.57, 0.70]); ax.set_aspect('equal'); ax.axis('off')
ax.set_xlim(-2.2, 14.6); ax.set_ylim(-1.4, 9.8)

zone = Z['zone']; zone = [[x / 1000, y / 1000] for x, y in zone]
ax.add_patch(Polygon(zone, closed=True, fc='#f4f1ea', ec='#2e9e44', lw=1.2, zorder=1))
ax.add_patch(Rectangle((-2.2, 4.1), 2.2, 9, fc='#e3dfd8', ec='#222', lw=1.0, zorder=1))
ax.text(-1.1, 8.5, 'EXISTING BUILDING\nhall ±0.000', rotation=90, ha='center', va='center', fontsize=8, color='#666', **F)
# south boundary wall (the pergola is attached to it)
z3, z4 = (13.4586, 3.3892), (-0.1675, 0.0)
ax.plot([z4[0], z3[0]], [z4[1], z3[1]], color='#333', lw=4.5, solid_capstyle='butt', zorder=3)
ax.text(1.0, -0.55, 'SOUTH BOUNDARY WALL (existing, kept)', rotation=13.97, fontsize=7.5, color='#333', **F)

# --- current design, faded
for it in D['items']:
    for p in it['poly']:
        xs = [q[0] for q in p]; ys = [q[1] for q in p]
        if max(ys) < 11 and min(xs) > -0.5:
            ax.add_patch(Polygon(p, closed=True, fc='#c9b79c', ec='#a08b6a', lw=.4, alpha=.45, zorder=2))
x0, x1, y0, y1 = D['bbq']
ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='none', ec='#b56a1e', lw=1.0, ls='--', zorder=4))
ax.text((x0 + x1) / 2, y1 + 0.25, 'NEW MANGAL (our design)\nreplaces the existing one', ha='center', fontsize=7, color='#b56a1e', **F)
for y, L in D['beams'][:2]:
    for xa, xb in (((0, 3.77), (9.90, L)) if y < 5 else ((0, L),)):
        ax.plot([xa, xb], [y, y], color='#2f5fb3', lw=1.2, ls=(0, (6, 3)), zorder=5)
ax.text(0.3, 4.22, 'roof beam IPE 300, grid A — ends on the pergola', fontsize=6.5, color='#2f5fb3', **F)
for c in D['cols'][:2] + D['cols'][-2:]:
    ax.add_patch(Rectangle((c[0] - .075, c[1] - .075), .15, .15, fc='#2f5fb3', zorder=6))

# --- existing pergola (KEEP)
ax.add_patch(Polygon(ex, closed=True, fc='#7a4a1e', alpha=.13, ec='#7a4a1e', lw=2.0, zorder=7))
for p in posts:
    ax.add_patch(Polygon(p, closed=True, fc='#7a4a1e', ec='black', lw=.6, zorder=8))
cx = sum(p[0] for p in ex) / 4; cy = sum(p[1] for p in ex) / 4
ax.text(cx, cy + 0.5, 'EXISTING PERGOLA — KEEP', ha='center', fontsize=11, weight='bold', color='#7a4a1e', rotation=13.97, **F)
ax.text(cx, cy - 0.35, 'steel posts 200×200 (6) + beams kept\nDWG 6.0 × 5.8 · site 6.4 × 5.9 (roof edge)\nunderside +3.2 · top +3.6 above the terrace\nattached to the boundary wall',
        ha='center', va='top', fontsize=7.5, color='#5a3510', rotation=13.97, **F)
# dims along the pergola sides
def dim(a, b, off, txt):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * off, dx / L * off
    A, B = (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)
    ax.annotate('', A, B, arrowprops=dict(arrowstyle='<->', lw=.7, color='#c0392b'))
    ax.text((A[0] + B[0]) / 2 + nx * .5, (A[1] + B[1]) / 2 + ny * .5, txt, ha='center', va='center', fontsize=7, color='#c0392b',
            rotation=math.degrees(math.atan2(dy, dx)) % 180 if abs(dx) > abs(dy) else math.degrees(math.atan2(dy, dx)) - 90 if dy > 0 else 0, **F)
dim(ex[0], ex[1], 0.45, '6 000 (DWG) / 6 400 (site)')
dim(ex[2], ex[1], -0.45, '5 800 / 5 900')

# --- clashes
CL = '#d62728'
def clash(x, y, n, txt, dx=0.6, dy=0.6):
    ax.add_patch(plt.Circle((x, y), .28, fc='none', ec=CL, lw=1.6, zorder=9))
    ax.text(x, y, str(n), ha='center', va='center', fontsize=8, weight='bold', color=CL, zorder=10, **F)
clash(6.0, 4.1, 1, '')
clash(4.2, 6.9, 2, '')
clash(3.6, 3.0, 3, '')
clash(9.6, 4.5, 4, '')

# --- legend / notes
nx = fig.add_axes([0.61, 0.02, 0.37, 0.95]); nx.axis('off')
import textwrap
T = lambda y, s, w=88, **k: nx.text(0, y, '\n'.join(textwrap.wrap(s, w, subsequent_indent='      ' if s.startswith('   ') else '')), transform=nx.transAxes, va='top', **F, **{a: b for a, b in k.items() if a != 'wrap'})
T(1.0, 'SAMARKAND — existing conditions, south zone', fontsize=15, weight='bold', color='#1f3a5f')
T(0.965, 'Base plan update R12-v8.3 · from the as-built DWG + site photos 2026-11 · plan approx. 1:75', fontsize=8.5, color='#555')
y = 0.92
T(y, 'DECISIONS (owner)', fontsize=10, weight='bold', color='#1f3a5f'); y -= 0.03
for s in ['KEEP  existing pergola: steel posts + beams stay exactly as built; it is attached to the south boundary wall.',
          'DEMOLISH  existing bar kiosk "SAMARKAND" (4.8 × 2.5, h 3.5) → new bar of our design.',
          'REPLACE  existing mangal + hood (≈ 3.28 wide) → new mangal block of our design, same corner.',
          'JOIN  the new roof to the pergola so that nothing sticks out and no water gets in.']:
    nx.text(0.0, y, '•', transform=nx.transAxes, va='top', fontsize=9); T(y, '   ' + s, fontsize=8.5); y -= 0.022 * (1 + len(s) // 88)
y -= 0.01
T(y, 'CLASHES FOUND IN R12-v8.2 → RESOLVED IN R12-v8.3', fontsize=10, weight='bold', color=CL); y -= 0.03
lo, hi = roof_top(3.1) - 0.55, roof_top(10.3) - 0.55
for n, s in [(1, 'Roof vs pergola: at 5 % the roof was up to 0.47 m below the pergola top. → Roof fall now 3.5 % (Klip-Lok standing seam), short C100 purlins on packers over the pergola beams, ≈ 100 mm clear; grid-A beam ends on the pergola main beams.'),
             (2, 'South 2-tops sat on the north-west post. → Tables moved to x 2.65 / 4.15: the post now stands between them.'),
             (3, 'Photo lounge crossed the mid-west post. → Rug ends west of the post, middle tray table + areca pot moved east (under the pergola).'),
             (4, 'Mangal touched the east posts. → Kitchen west wall (firewood display) wraps the mid-east post; staff lane 1.55 m.')]:
    nx.add_patch(plt.Circle((0.012, y - 0.008), 0.011, transform=nx.transAxes, fc='none', ec=CL, lw=1.2))
    nx.text(0.012, y - 0.008, str(n), transform=nx.transAxes, ha='center', va='center', fontsize=7, color=CL, weight='bold')
    T(y, '      ' + s, fontsize=8.2); y -= 0.02 * (1 + len(s) // 82) + 0.006
y -= 0.005
T(y, 'ROOF AT THE PERGOLA — DECIDED (owner 2026-11-04)', fontsize=10, weight='bold', color='#1f3a5f'); y -= 0.03
for s in ['One roof over everything, including the pergola: Klip-Lok / Seamlock sheet on clips, one length facade → street gutter, fall 3.5 % (2°), insulation blanket under it. '
          'Old pergola roof sheet removed; posts + beams kept and become the support of the new roof in this bay (engineer to confirm). See sheet "roof over the pergola — section + install steps".',
          'Rejected: sandwich panels (need ≥ 4° — not possible under the balcony), separate pergola roof with a step and box gutter (more joints, more leaks).',
          '']:
    T(y, s, fontsize=8.2); y -= 0.02 * (1 + len(s) // 88) + 0.006
T(y, 'Interior of the pergola in both versions: beams clad in carved walnut, posts as Khiva columns (cladding only, steel stays), ceiling in ganch / painted panels.', fontsize=8.2, color='#444'); y -= 0.06
T(y, 'TO MEASURE ON SITE (when convenient)', fontsize=10, weight='bold', color='#1f3a5f'); y -= 0.028
for s in ['1. Exact pergola post positions + section size; beam sizes and spacing (≈ 1.0 m purlins seen).',
          '2. Levels: pergola beam underside and roof top, terrace floor under it, balcony slab soffit at the façade.',
          '3. What is ON TOP of the pergola (room / terrace / roof only) and its load — can new panels bear on it?',
          '4. Boundary wall: height, thickness, owner (ours / neighbour), drainage of the pergola roof today.',
          '5. Existing mangal: hood, flue route, gas line, drain, power — reuse points for the new mangal.',
          '6. Bar kiosk: where its water / drain / power come from before demolition.']:
    T(y, s, fontsize=8); y -= 0.02 * (1 + len(s) // 88)

# --- section through the pergola along x (west → street), at the pergola middle
sx = fig.add_axes([0.04, 0.02, 0.53, 0.22]); sx.set_xlim(-0.8, 13.8); sx.set_ylim(-0.7, 4.3); sx.axis('off')
sx.fill_between([-0.8, 13.8], -0.7, TER, color='#ddd')
xs = [0, 13.4]; sx.plot(xs, [roof_top(x) for x in xs], color='#2f5fb3', lw=2)
sx.plot(xs, [roof_top(x) - .55 for x in xs], color='#2f5fb3', lw=1, ls='--')
sx.text(6.5, roof_top(6.5) + .12, 'new roof top (3.5 % fall, Klip-Lok)', fontsize=6.5, color='#2f5fb3', **F)
sx.text(6.5, roof_top(6.5) - .78, 'underside of new beams (outside the pergola)', fontsize=6.5, color='#2f5fb3', **F)
sx.add_patch(Rectangle((3.5, PERG_LO), 6.6, PERG_HI - PERG_LO, fc='#7a4a1e', alpha=.35, ec='#7a4a1e'))
for px in (3.6, 6.8, 10.0): sx.add_patch(Rectangle((px - .1, TER), .2, PERG_LO - TER, fc='#7a4a1e'))
sx.text(6.8, PERG_LO - .35, 'existing pergola +3.2 / +3.6 above terrace', ha='center', fontsize=6.5, color='#5a3510', **F)
sx.add_patch(Rectangle((-0.8, TER), 0.8, 4.6, fc='#e3dfd8', ec='#222'))
sx.plot([-0.8, 0], [3.85, 3.85], color='#222', lw=2); sx.text(-0.75, 3.95, 'balcony +3.85', fontsize=6, **F)
sx.text(13.6, TER + .1, '−0.450 terrace', ha='right', fontsize=6, **F)
sx.text(-0.8, 4.25, 'SECTION THROUGH THE PERGOLA (schematic, ±0 = hall floor)', fontsize=7.5, weight='bold', **F)
fig.savefig(OUT); print('ok', OUT)
