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

# ================= BUKHARA INSTALLATION =================
for o_ in [o for o in bpy.data.collections['Bukhara_dome'].all_objects]: bpy.data.objects.remove(o_)
CX, CY = 6.0, 35.15
import bmesh as _bmesh
HS = 1.15                                                                                      # open the coffers above it: square cut, capped
for o_ in [o for o in bpy.data.collections['Carpet_ceiling'].all_objects if o.type == 'MESH']:
    bm = _bmesh.new(); bm.from_mesh(o_.data); bm.transform(o_.matrix_world)
    for co_, no_ in (((CX - HS, 0, 0), (1, 0, 0)), ((CX + HS, 0, 0), (1, 0, 0)), ((0, CY - HS, 0), (0, 1, 0)), ((0, CY + HS, 0), (0, 1, 0))):
        _bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co_, plane_no=no_)
    def _in(c): return abs(c.x - CX) < HS - 1e-4 and abs(c.y - CY) < HS - 1e-4 and c.z > 2.2
    dead = [f for f in bm.faces if _in(f.calc_center_median())]
    if dead:
        _bmesh.ops.delete(bm, geom=dead, context='FACES')
        bnd = [e for e in bm.edges if e.is_boundary and all(abs(abs(v.co.x - CX) - HS) < 2e-3 or abs(abs(v.co.y - CY) - HS) < 2e-3 for v in e.verts)]
        if bnd: _bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
        bm.transform(o_.matrix_world.inverted()); bm.to_mesh(o_.data); o_.data.update()
    bm.free()
dg = bpy.context.evaluated_depsgraph_get(); dg.update()
hit = bpy.context.scene.ray_cast(dg, (CX, CY, TER + 0.3), (0, 0, -1), distance=0.5)
if not hit[0] or abs(hit[1].z - TER) > 0.02:                                                   # floor patch where the rotunda base was
    prism('terrace_floor_fill_bk', [[(CX + 1.1 * _m.cos(a), CY + 1.1 * _m.sin(a)) for a in [k * _m.pi / 24 for k in range(48)]]], TER - 0.2, TER, XW['marble'], 'Floors')
    o_ = bpy.data.objects.get('terrace_floor_fill_bk')
    if o_: _uv_top(o_, CX - 1.1, CY - 1.1, CX + 1.1, CY + 1.1)
ZR = 3.27                                                                                      # purlin underside
PAN = [(10, 70, 0.90, 2.15, 3.45), (65, 60, 0.98, 2.55, 3.60), (115, 65, 0.90, 2.30, 3.35), (170, 55, 0.98, 2.70, 3.55),
       (215, 65, 0.90, 2.20, 3.50), (270, 60, 0.98, 2.60, 3.40), (320, 60, 0.90, 2.35, 3.60), (100, 200, 0.45, 2.45, 3.30)]
TH = 0.004
def _slice(pb, L, step=0.05):                                                                  # densify along u before bending
    k = 1
    while k * step < L - 1e-3:
        g = pb.bm.verts[:] + pb.bm.edges[:] + pb.bm.faces[:]
        _bmesh.ops.bisect_plane(pb.bm, geom=g, plane_co=(k * step, 0, 0), plane_no=(1, 0, 0)); k += 1
for i_, (a0, span, R, zb, zt) in enumerate(PAN):
    L = R * _m.radians(span); pb = MB()
    for q in lattice_poly(0.0, TER + zb, L, TER + zt, 'star', 0.09, 0.013, 0.025): ext_holes(pb, q, 0.0, TH, _BRS, 'xz')
    for u in (0.004, L - 0.004): pb.rod((u, TH / 2, TER + zb), (u, TH / 2, TER + zt), 0.008, _BRS, 8)     # tube edges
    _slice(pb, L)
    me = pb.mesh(f'Bk_panel_{i_ + 1}')
    for v in me.vertices:
        th = _m.radians(a0) + v.co.x / R; r = R + v.co.y
        v.co.x, v.co.y = CX + r * _m.cos(th), CY + r * _m.sin(th)
    me.update(); inst(me, f'Bukhara_panel_{i_ + 1}', (0, 0, 0), 0, 'Bukhara_dome')
    rb = MB()
    for f in (0.15, 0.5, 0.85):                                                               # hanging rods to the purlins
        th = _m.radians(a0 + span * f); x, y = CX + (R + TH / 2) * _m.cos(th), CY + (R + TH / 2) * _m.sin(th)
        if TER + zt < ZR - 0.01: rb.rod((x, y, TER + zt - 0.02), (x, y, ZR), 0.004, m['brass'], 6)
    if rb.bm.verts: inst(rb.mesh(f'Bk_rods_{i_ + 1}'), f'Bukhara_rods_{i_ + 1}', (0, 0, 0), 0, 'Bukhara_dome')
# the spiral ribbon down to the podium (hall / tent side, clear of the booth entrance)
PX, PY, PR = 5.35, 34.75, 0.40; HZ = TER + 0.45
H_ = 0.30; t0, t1 = 100.0, 235.0; L = 0.95 * _m.radians(t1 - t0); pb = MB()
for q in lattice_poly(0.0, 0.0, L, H_, 'star', 0.09, 0.013, 0.025): ext_holes(pb, q, 0.0, TH, _BRS, 'xz')
for zz in (0.006, H_ - 0.006): pb.rod((0.0, TH / 2, zz), (L, TH / 2, zz), 0.008, _BRS, 8)
_slice(pb, L, 0.04)
me = pb.mesh('Bk_spiral')
zt0, zt1 = TER + 2.45, HZ + H_
for v in me.vertices:
    t = min(max(v.co.x / L, 0.0), 1.0); s = t * t * (3 - 2 * t); th = _m.radians(t0 + (t1 - t0) * t)
    r = 0.98 - 0.22 * t * t + v.co.y; ztop = zt0 + (zt1 - zt0) * s
    v.co.x, v.co.y, v.co.z = CX + r * _m.cos(th), CY + r * _m.sin(th), ztop - H_ + v.co.z
me.update(); inst(me, 'Bukhara_spiral', (0, 0, 0), 0, 'Bukhara_dome')
# walnut hoop with spots + its rods; walnut podium with samovar
b = MB(); RH = 0.94; ZH = TER + 2.80
b.ring(CX, CY, ZH, [(RH - 0.02, 0.0), (RH + 0.02, 0.0), (RH + 0.02, 0.08), (RH - 0.02, 0.08)], _WD, 64)
for k in range(8):
    a = k * _m.pi / 4 + _m.pi / 8; x, y = CX + RH * _m.cos(a), CY + RH * _m.sin(a)
    b.cyl(x, y, ZH - 0.09, ZH, 0.03, _BLACK, 12); b.cyl(x, y, ZH - 0.095, ZH - 0.09, 0.022, _LEDW, 12)
for k in range(4):
    a = k * _m.pi / 2 + _m.pi / 8; x, y = CX + RH * _m.cos(a), CY + RH * _m.sin(a); b.rod((x, y, ZH + 0.08), (x, y, ZR), 0.005, m['brass'], 6)
inst(b.mesh('Bukhara_hoop'), 'Bukhara_hoop', (0, 0, 0), 0, 'Bukhara_dome')
b = MB()
b.cyl(PX, PY, TER, HZ - 0.03, PR, _WD, 48); b.cyl(PX, PY, HZ - 0.03, HZ, PR + 0.015, _WD, 48)
b.cyl(PX, PY, TER + 0.06, TER + 0.09, PR + 0.004, m['brass'], 48); b.cyl(PX, PY, HZ - 0.06, HZ - 0.045, PR + 0.004, m['brass'], 48)
b.lathe(PX + 0.08, PY + 0.05, HZ, [(0.0, 0.0), (0.09, 0.0), (0.06, 0.04), (0.14, 0.12), (0.15, 0.3), (0.11, 0.38), (0.06, 0.42),
                                   (0.08, 0.47), (0.03, 0.55), (0.0, 0.56)], m['brass'], 32)                 # samovar
b.rod((PX + 0.22, PY + 0.05, HZ + 0.18), (PX + 0.3, PY + 0.05, HZ + 0.16), 0.012, m['brass'])
b.lathe(PX + 0.08, PY + 0.05, HZ + 0.56, [(0.0, 0.0), (0.06, 0.0), (0.07, 0.07), (0.04, 0.12), (0.0, 0.13)], m.get('porcelain', _ICE), 16)
inst(b.mesh('Bukhara_podium'), 'Bukhara_podium', (0, 0, 0), 0, 'Bukhara_dome')
print('rev 11.8: bar rebuilt, Bukhara installation placed')
