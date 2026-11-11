"""rev. 11.8 (owner): 'the bar is oversized and not ergonomic — no shelves, no equipment; organise it properly (non-alcoholic:
coffee, cold drinks, mocktails; staff enter from the side of the station shelves / kids area); the Bukhara dome blocks the last
booth — replace it with a suspended installation of curved pierced panels (owner sketch), panels in brass, the lower part in wood'.
BAR (stools and length kept):
  * the 570 mm sculpted back wall becomes a thin bannai brick wall with three walnut shelves (+1.45/+1.85/+2.25, warm LED under each)
  * back bar 550 deep, worktop +0.90: ice maker, 2+2 under-counter fridges, walnut cabinets, glass bottle cooler at the north end;
    on top: 2-group espresso machine + 2 grinders, 2 blenders, citrus juicer, cups
  * working aisle 920 (was 740); staff enter from the south end, between the station cabinets and the service counter
  * front counter 0.97 -> 0.80 deep, two levels: walnut guest top +1.05, stainless work shelf +0.90 with POS, bins, ice well +
    syrup speed rail, glass washer, double sink, hand sink, fridge; fluted terracotta front, brass foot rail
BUKHARA INSTALLATION (replaces the rotunda + vitrines; floor in front of booth 7 is now free):
  * 7 curved pierced-brass panels (girih star perforation, laser cut 2 mm sheet) on a 1.8 m circle + an inner half-cylinder,
    staggered heights, lowest edge +2.15, hung on 8 mm brass rods from the purlins; the carpet coffers over it are removed so the
    piece rises into the roof void
  * a walnut hoop at +2.80 carrying 8 warm spots; one pierced ribbon spirals down on the hall side onto a walnut drum podium
    (samovar on top)"""
import math as _m
_BRS = mat('brass_sheet_patina', (0.74, 0.54, 0.25), rough=0.32, metal=1.0)
_WD = XW['wd']; _STEEL = mat('stainless_brushed', (0.62, 0.63, 0.64), rough=0.28, metal=1.0)
_GLASSD = mat('fridge_glass_dark', (0.04, 0.05, 0.06), rough=0.08)
_TERRA = mat('terracotta_flute', (0.6, 0.31, 0.18), rough=0.8)
_ICE = mat('ice_cubes', (0.86, 0.92, 0.95), rough=0.15)
_LEDW = mat('led_warm', (1.0, 0.72, 0.42), emit=(1.0, 0.72, 0.42), strength=6.0)
_BLACK = m['black']; _BRICK = X['bannai']

def _rm(pref):
    for o_ in [o for o in bpy.data.objects if o.name == pref or o.name.startswith(pref + '_real') or o.name.startswith(pref + '.')]:
        bpy.data.objects.remove(o_)

# ================= BAR =================
for p_ in ('Bar_backwall', 'Bar_counter', 'Bar_cornice', 'Bar_espresso', 'Bar_wallcarpet'): _rm(p_)
F0 = TER; Y0b, Y1b = 8.62, 14.28
b = MB()
# thin brick back wall + cornice
b.box(0.14, 8.6, F0, 0.22, 14.3, 3.10, _BRICK)
b.box(0.22, 8.6, 2.86, 0.36, 14.3, 3.06, _WD, 0.004)
b.box(0.22, 8.6, 2.84, 0.38, 14.3, 2.86, m['brass'])
# back-bar under-counter units (front face at x 0.70)
def unit(y0, y1, kind):
    if kind == 'fridge':
        b.box(0.16, y0 + 0.005, F0 + 0.1, 0.69, y1 - 0.005, F0 + 0.86, _STEEL, 0.003)
        b.box(0.69, y0 + 0.04, F0 + 0.16, 0.705, y1 - 0.04, F0 + 0.8, _GLASSD)
        b.rod((0.715, y0 + 0.08, F0 + 0.74), (0.715, y1 - 0.08, F0 + 0.74), 0.008, _STEEL)
    elif kind == 'ice':
        b.box(0.16, y0 + 0.005, F0 + 0.1, 0.69, y1 - 0.005, F0 + 0.86, _STEEL, 0.003)
        b.box(0.69, y0 + 0.06, F0 + 0.45, 0.705, y1 - 0.06, F0 + 0.8, _STEEL)
        b.box(0.69, y0 + 0.06, F0 + 0.2, 0.705, y1 - 0.06, F0 + 0.26, _BLACK)
    else:
        n_ = max(1, round((y1 - y0) / 0.6)); w_ = (y1 - y0) / n_
        b.box(0.16, y0, F0 + 0.1, 0.69, y1, F0 + 0.86, _WD, 0.003)
        for k in range(n_):
            ya = y0 + k * w_
            b.box(0.69, ya + 0.01, F0 + 0.12, 0.70, ya + w_ - 0.01, F0 + 0.84, _WD, 0.002)
            b.rod((0.715, ya + w_ / 2 - 0.08, F0 + 0.72), (0.715, ya + w_ / 2 + 0.08, F0 + 0.72), 0.007, m['brass'])
    b.box(0.18, y0, F0, 0.66, y1, F0 + 0.1, _BLACK)                                     # recessed plinth
for y0, y1, k in ((8.62, 9.22, 'ice'), (9.22, 9.82, 'fridge'), (9.82, 10.42, 'fridge'), (10.42, 12.22, 'cab'),
                  (12.22, 12.82, 'fridge'), (12.82, 13.42, 'fridge')): unit(y0, y1, k)
b.box(0.14, 8.62, F0 + 0.86, 0.72, 13.42, F0 + 0.90, _WD, 0.004)                         # walnut worktop +0.90
# glass bottle cooler, full height, north end
b.box(0.16, 13.44, F0, 0.70, 14.28, F0 + 2.0, _STEEL, 0.004)
b.box(0.70, 13.48, F0 + 0.12, 0.712, 14.24, F0 + 1.92, _GLASSD)
GLS = mat('cooler_glass', (0.75, 0.85, 0.9), rough=0.05)
cols_ = [(0.8, 0.25, 0.1), (0.95, 0.6, 0.1), (0.25, 0.55, 0.2), (0.85, 0.82, 0.7), (0.55, 0.1, 0.25)]
for r_, zz in enumerate((0.3, 0.75, 1.2, 1.62)):
    b.box(0.2, 13.5, F0 + zz - 0.02, 0.66, 14.22, F0 + zz, _STEEL)
    for k in range(9):
        cm = mat(f'drink_{r_ % 5}', cols_[(r_ + k) % 5], rough=0.15)
        b.cyl(0.6, 13.56 + k * 0.08, F0 + zz, F0 + zz + 0.24, 0.03, cm, 10)
b.box(0.705, 13.47, F0 + 1.75, 0.715, 14.25, F0 + 1.9, _LEDW)
# worktop equipment
def espresso(y):
    b.box(0.22, y, F0 + 0.90, 0.66, y + 0.72, F0 + 1.32, _STEEL, 0.01); b.box(0.24, y + 0.02, F0 + 1.32, 0.62, y + 0.7, F0 + 1.35, m['brass'])
    for k in range(2):
        yy = y + 0.2 + k * 0.32; b.cyl(0.70, yy, F0 + 1.08, F0 + 1.14, 0.04, _BLACK, 12); b.rod((0.70, yy, F0 + 1.11), (0.78, yy, F0 + 1.1), 0.01, _BLACK)
    b.box(0.6, y + 0.05, F0 + 0.92, 0.72, y + 0.67, F0 + 0.94, _STEEL)                       # drip tray
    for k in range(6): b.cyl(0.3 + 0.07 * (k % 3), y + 0.15 + 0.1 * (k // 3), F0 + 1.35, F0 + 1.42, 0.035, m.get('porcelain', _ICE), 10)
espresso(10.5)
for yy in (11.32, 11.58):                                                                  # grinders
    b.box(0.3, yy - 0.09, F0 + 0.90, 0.5, yy + 0.09, F0 + 1.22, _BLACK, 0.01); b.cyl(0.4, yy, F0 + 1.22, F0 + 1.42, 0.08, GLS, 12, r2=0.05)
for yy in (9.55, 9.85):                                                                    # blenders
    b.box(0.32, yy - 0.09, F0 + 0.90, 0.5, yy + 0.09, F0 + 1.05, _BLACK, 0.01); b.cyl(0.41, yy, F0 + 1.05, F0 + 1.35, 0.06, GLS, 12, r2=0.075)
b.cyl(0.42, 12.5, F0 + 0.90, F0 + 1.12, 0.1, _STEEL, 16)                                    # citrus juicer
b.cyl(0.42, 12.9, F0 + 0.90, F0 + 1.15, 0.12, GLS, 16)                                      # lemonade dispenser
b.cyl(0.42, 13.2, F0 + 0.90, F0 + 1.15, 0.12, GLS, 16)
# shelves + LED + dividers + stock
for zz in (1.45, 1.85, 2.25):
    b.box(0.22, 8.7, F0 + zz - 0.03, 0.50, 13.35, F0 + zz, _WD, 0.002)
    b.box(0.46, 8.72, F0 + zz - 0.04, 0.48, 13.33, F0 + zz - 0.03, _LEDW)
    for k in range(30):
        y_ = 8.82 + k * 0.15
        if any(abs(y_ - d) < 0.06 for d in (10.25, 11.8)): continue
        if (k + int(zz * 10)) % 3 == 0: b.cyl(0.36, y_, F0 + zz, F0 + zz + 0.11, 0.045, m.get('porcelain', _ICE), 12)        # cups / jars
        else:
            cm = mat(f'drink_{(k + int(zz * 10)) % 5}', cols_[(k + int(zz * 10)) % 5], rough=0.15)
            b.cyl(0.36, y_, F0 + zz, F0 + zz + 0.22, 0.033, cm, 10); b.cyl(0.36, y_, F0 + zz + 0.22, F0 + zz + 0.27, 0.012, cm, 8)
for yd in (8.7, 10.25, 11.8, 13.35):
    b.box(0.22, yd - 0.015, F0 + 1.42, 0.50, yd + 0.015, F0 + 2.25, _WD, 0.002)
inst(b.mesh('Bar_backbar'), 'Bar_backbar', (0, 0, 0), 0, 'Bar')

# front counter, y 8.10 .. 14.30
YA, YB = 8.10, 14.30
b = MB()
b.box(2.00, YA, F0 + 0.10, 2.28, YB, F0 + 1.01, _TERRA)                                     # body
b.box(2.02, YA + 0.02, F0, 2.26, YB - 0.02, F0 + 0.10, _BLACK)                              # kick
nfl = int((YB - YA - 0.06) / 0.06)
for k in range(nfl + 1):                                                                    # fluted front
    yy = YA + 0.03 + k * (YB - YA - 0.06) / nfl; b.rod((2.285, yy, F0 + 0.12), (2.285, yy, F0 + 0.98), 0.024, _TERRA, 8)
b.box(1.98, YA - 0.02, F0 + 1.01, 2.44, YB, F0 + 1.05, _WD, 0.006)                           # walnut guest top +1.05
b.box(1.98, YA, F0 + 0.90, 2.02, YB, F0 + 1.01, _WD)                                        # riser
b.box(1.64, YA, F0 + 0.86, 2.00, YB, F0 + 0.90, _STEEL, 0.002)                              # stainless work shelf +0.90
b.rod((2.40, YA + 0.1, F0 + 0.22), (2.40, YB - 0.1, F0 + 0.22), 0.024, m['brass'], 12)     # foot rail
for yy in [YA + 0.2 + k * 1.2 for k in range(6)]: b.rod((2.29, yy, F0 + 0.22), (2.40, yy, F0 + 0.22), 0.012, m['brass'])
def under(y0, y1, kind):
    if kind == 'cab':
        b.box(1.66, y0, F0 + 0.1, 2.0, y1, F0 + 0.86, _WD, 0.002); b.box(1.655, y0 + 0.01, F0 + 0.12, 1.665, y1 - 0.01, F0 + 0.84, _WD)
        b.rod((1.645, (y0 + y1) / 2 - 0.07, F0 + 0.75), (1.645, (y0 + y1) / 2 + 0.07, F0 + 0.75), 0.007, m['brass'])
    elif kind in ('fridge', 'washer'):
        b.box(1.66, y0 + 0.005, F0 + 0.1, 2.0, y1 - 0.005, F0 + 0.86, _STEEL, 0.003)
        b.box(1.65, y0 + 0.04, F0 + 0.16, 1.66, y1 - 0.04, F0 + 0.8, _GLASSD if kind == 'fridge' else _STEEL)
        b.rod((1.64, y0 + 0.08, F0 + 0.76), (1.64, y1 - 0.08, F0 + 0.76), 0.008, _STEEL)
    elif kind == 'bins':
        b.box(1.7, y0 + 0.03, F0, 1.98, y1 - 0.03, F0 + 0.62, _BLACK, 0.01)
    b.box(1.68, y0, F0, 1.98, y1, F0 + 0.1, _BLACK)
for y0, y1, k in ((8.10, 8.70, 'cab'), (8.70, 9.30, 'bins'), (9.30, 10.10, 'cab'), (10.10, 10.70, 'washer'), (10.70, 11.70, 'cab'),
                  (11.70, 12.10, 'cab'), (12.10, 12.70, 'fridge'), (12.70, 13.30, 'fridge'), (13.30, 14.30, 'cab')): under(y0, y1, k)
b.box(1.70, 8.30, F0 + 0.90, 1.92, 8.62, F0 + 0.93, _BLACK); b.box(1.86, 8.34, F0 + 0.93, 1.88, 8.58, F0 + 1.15, _BLACK)   # POS
b.box(1.68, 9.32, F0 + 0.90, 1.96, 10.08, F0 + 0.93, _STEEL); b.box(1.7, 9.34, F0 + 0.905, 1.94, 10.06, F0 + 0.935, _ICE)  # ice well
b.rod((1.62, 9.3, F0 + 0.62), (1.62, 10.1, F0 + 0.62), 0.01, _STEEL)                                                       # syrup speed rail
for k in range(6):
    cm = mat(f'drink_{k % 5}', cols_[k % 5], rough=0.15); b.cyl(1.585, 9.38 + k * 0.13, F0 + 0.55, F0 + 0.8, 0.032, cm, 10)
for y0, y1 in ((10.75, 11.18), (11.22, 11.65), (11.75, 12.05)):                                                             # sinks
    b.box(1.68, y0, F0 + 0.90, 1.96, y1, F0 + 0.905, _BLACK)
    b.rod((1.93, (y0 + y1) / 2, F0 + 0.90), (1.93, (y0 + y1) / 2, F0 + 1.15), 0.012, _STEEL); b.rod((1.93, (y0 + y1) / 2, F0 + 1.15), (1.82, (y0 + y1) / 2, F0 + 1.12), 0.01, _STEEL)
for k in range(3): b.box(1.70 + 0.09 * k, 13.5, F0 + 0.90, 1.77 + 0.09 * k, 14.1, F0 + 0.91, _STEEL)                     # glass rack mats
inst(b.mesh('Bar_counter'), 'Bar_counter', (0, 0, 0), 0, 'Bar')

# ================= NORTH END (rev. 11.10, owner: 'remove the whole construction and its decor, keep only a chandelier, make it as
# simple as possible to make / buy; add flowers and pots') =================
for o_ in [o for o in bpy.data.collections['Bukhara_dome'].all_objects]: bpy.data.objects.remove(o_)
CX, CY = 5.68, 33.27                                                              # between the two 4-top tables
dg = bpy.context.evaluated_depsgraph_get(); dg.update()
for px_, py_ in ((6.0, 35.15), (5.3, 34.7), (6.6, 35.6)):                          # floor patch where the rotunda base was
    hit = bpy.context.scene.ray_cast(dg, (px_, py_, TER + 0.3), (0, 0, -1), distance=0.5)
    if not hit[0] or abs(hit[1].z - TER) > 0.02:
        prism('terrace_floor_fill_bk', [[(6.0 + 1.1 * _m.cos(a), 35.15 + 1.1 * _m.sin(a)) for a in [k * _m.pi / 24 for k in range(48)]]], TER - 0.2, TER, XW['marble'], 'Floors')
        o_ = bpy.data.objects.get('terrace_floor_fill_bk')
        if o_: _uv_top(o_, 4.9, 34.05, 7.1, 36.25)
        break
# one plain drum chandelier: rolled pierced-brass band 900 dia x 380, two brass hoops, 3 rods to the ceiling grid, 6 lamps inside
ZC_ = top(CX) - 0.75; ZB = TER + 2.30; HB = 0.38; RD = 0.45; TH = 0.003
L = 2 * _m.pi * RD; pb = MB()
for q in lattice_poly(0.0, ZB, L, ZB + HB, 'star', 0.095, 0.014, 0.03): ext_holes(pb, q, 0.0, TH, _BRS, 'xz')
k = 1
while k * 0.05 < L - 1e-3:
    _bmesh_ = __import__('bmesh'); g = pb.bm.verts[:] + pb.bm.edges[:] + pb.bm.faces[:]
    _bmesh_.ops.bisect_plane(pb.bm, geom=g, plane_co=(k * 0.05, 0, 0), plane_no=(1, 0, 0)); k += 1
me = pb.mesh('Drum_band')
for v in me.vertices:
    th = v.co.x / RD; r = RD + v.co.y; v.co.x, v.co.y = CX + r * _m.cos(th), CY + r * _m.sin(th)
me.update(); inst(me, 'North_chandelier_band', (0, 0, 0), 0, 'Bukhara_dome')
b = MB()
for zz in (ZB - 0.012, ZB + HB - 0.012):
    b.ring(CX, CY, zz, [(RD - 0.012, 0.0), (RD + 0.012, 0.0), (RD + 0.012, 0.024), (RD - 0.012, 0.024)], m['brass'], 48)
for k in range(3):
    a = k * 2 * _m.pi / 3 + 0.5; x, y = CX + RD * _m.cos(a), CY + RD * _m.sin(a); b.rod((x, y, ZB + HB), (x, y, ZC_), 0.005, m['brass'], 6)
    b.rod((CX, CY, ZB + HB - 0.05), (x, y, ZB + HB - 0.002), 0.006, m['brass'], 6)
b.rod((CX, CY, ZB + HB - 0.05), (CX, CY, ZB + 0.2), 0.008, m['brass'], 6)
for k in range(6):
    a = k * _m.pi / 3; x, y = CX + 0.2 * _m.cos(a), CY + 0.2 * _m.sin(a)
    b.rod((CX, CY, ZB + 0.2), (x, y, ZB + 0.17), 0.005, m['brass'], 6); b.cyl(x, y, ZB + 0.09, ZB + 0.17, 0.035, _LEDW, 12)
inst(b.mesh('North_chandelier'), 'North_chandelier', (0, 0, 0), 0, 'Bukhara_dome')
# flower pots: a row of three between the tables, two by the gate
_POT = mat('pot_terracotta', (0.62, 0.33, 0.2), rough=0.85); _SOIL = mat('pot_soil', (0.08, 0.06, 0.04), rough=0.95)
def _pot(nm, x, y, r, h, kind, seed):
    b = MB(); b.lathe(x, y, TER, [(0.0, 0.0), (r * 0.62, 0.0), (r * 0.7, 0.03), (r * 0.98, h * 0.82), (r * 1.06, h * 0.84), (r * 1.06, h), (r * 0.9, h),
                                 (r * 0.88, h - 0.03), (0.0, h - 0.03)], _POT, 28)
    b.cyl(x, y, TER + h - 0.04, TER + h - 0.025, r * 0.87, _SOIL, 20)
    inst(b.mesh(nm), nm, (0, 0, 0), 0, 'Planting')
    inst(a_shrub(seed, kind), nm + '_flowers', (x, y, TER + h - 0.03), seed * 0.7, 'Planting', scale=(r / 0.27,) * 3)
for k, (x, y, r, h, kind) in enumerate(((5.16, 33.27, 0.19, 0.36, 'bou'), (5.68, 33.27, 0.23, 0.48, 'jas'), (6.20, 33.27, 0.19, 0.36, 'bou'),
                                        (4.42, 36.0, 0.22, 0.45, 'bou'), (6.80, 36.0, 0.22, 0.45, 'jas'))):
    _pot(f'North_pot_{k + 1}', x, y, r, h, kind, 70 + k)
print('rev 11.10: bar rebuilt; installation removed, drum chandelier + pots placed')
