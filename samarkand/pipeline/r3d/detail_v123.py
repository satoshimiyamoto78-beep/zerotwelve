"""rev. 12.0 block 4 — PHOTO ZONE, WAITER STATION, BOOTHS:
  * photo zone (majlis): a pointed walnut arch with pierced star spandrels frames the hanging carpet, centred on the drape; a carved
    3-seat settee with the sewn cushions under it (the plain bench is gone); one larger cascade chandelier centred on the axis (the
    two off-centre ones are removed); the low table, floor cushions and poufs are re-set symmetrically about the same axis
  * waiter station: the bare steel counter becomes a walnut pass counter with a fluted front (as the bar), white stone top, POS
    terminal, cutlery caddies, tray stack, water jugs, a lower shelf for folded linen
  * booths: brass shoes on the posts and a walnut cornice cap over the lintel line (the frame reads as a finished joinery piece)"""
from shapely.geometry import Polygon as _P23, box as _B23
_W = XW['wd']; _BRS3 = m['brass']
# ---------------- photo zone
dr = bpy.data.objects.get('Majlis_drape_1'); lo_, hi_ = _bb(dr); XC = round((lo_[0] + hi_[0]) / 2, 3); YF = hi_[1] + 0.03
_rmp('Majlis_bench_1', 'Pergola_chandelier_2', 'Pergola_chandelier_3')
WOP, ZS3, ZA3 = 2.3, TER + 1.55, TER + 2.5; ZT3 = TER + 2.72; HWF = WOP / 2 + 0.16
pts = arch_left(XC, WOP, ZS3, ZA3, 16)
inner = _P23([(XC - WOP / 2, TER - 0.1)] + pts + [(2 * XC - u, z) for u, z in pts[::-1][1:]] + [(XC + WOP / 2, TER - 0.1)])
outer = _B23(XC - HWF, TER, XC + HWF, ZT3)
b = MB()
fr = outer.difference(inner)
ring = inner.buffer(0.13, join_style=1).intersection(outer).difference(inner)                       # the arch band itself (solid)
for g in (getattr(ring, 'geoms', None) or [ring]):
    if g.geom_type == 'Polygon': ext_safe(b, g.simplify(0.001), YF, YF + 0.12, _W, 'xz')
sp = fr.difference(inner.buffer(0.13, join_style=1))                                                 # spandrels: pierced star lattice
for g in (getattr(sp, 'geoms', None) or [sp]):
    if g.geom_type != 'Polygon' or g.area < 0.01: continue
    bx = g.bounds
    for q in lattice_poly(bx[0], bx[1], bx[2], bx[3], 'star', 0.14, 0.014, 0.0):
        c = q.intersection(g)
        for h in (getattr(c, 'geoms', None) or [c]):
            if h.geom_type == 'Polygon' and h.area > 1e-4: ext_safe(b, h.simplify(0.0005), YF + 0.04, YF + 0.08, _W, 'xz')
b.box(XC - HWF - 0.02, YF - 0.01, ZT3, XC + HWF + 0.02, YF + 0.14, ZT3 + 0.07, _W, 0.004)                       # cornice
for sx in (-1, 1):
    x = XC + sx * (WOP / 2 + 0.08); b.box(x - 0.09, YF - 0.005, TER, x + 0.09, YF + 0.125, TER + 0.12, _BRS3, 0.003)
inst(b.mesh('Photo_arch'), 'Photo_arch', (0, 0, 0), 0, 'Photo_lounge')
st = bpy.data.objects.get('Aivan_settee_1a')
if st:
    sl, sh = _bb(st); o_ = inst(st.data, 'Photo_settee', (0, 0, 0), 0, 'Photo_lounge')
    o_.location = (st.location.x + XC - (sl[0] + sh[0]) / 2, st.location.y + (YF + 0.22) - sl[1], st.location.z + TER - sl[2]); o_.rotation_euler = st.rotation_euler
def _mv(nm, x, y):
    o_ = bpy.data.objects.get(nm)
    if o_:
        bpy.context.view_layer.update(); l, h = _bb(o_); o_.location.x += x - (l[0] + h[0]) / 2; o_.location.y += y - (l[1] + h[1]) / 2
_mv('Majlis_table_low_1', XC, 4.25)                                                   # the rug stays where the floor was laid around it
for nm, dx, yy in (('Majlis_cushion_1', -1.0, 3.75), ('Majlis_cushion_2', 1.0, 3.75), ('Majlis_cushion_3', -1.0, 4.75), ('Majlis_cushion_4', 1.0, 4.75),
                   ('Majlis_pouf_1', -1.75, 4.25), ('Majlis_pouf_2', 1.75, 4.25), ('Majlis_pouf_3', -0.45, 5.45), ('Majlis_pouf_4', 0.45, 5.45)):
    _mv(nm, XC + dx, yy)
_rl, _rh = _bb(bpy.data.objects['Majlis_rug_1'])
for nm in ('Majlis_pouf_1', 'Majlis_pouf_2', 'Majlis_pouf_3', 'Majlis_pouf_4', 'Floor_socket_05'):
    o_ = bpy.data.objects.get(nm)
    if not o_: continue
    if nm == 'Floor_socket_05': _mv(nm, XC, 4.95)
    bpy.context.view_layer.update(); l, h = _bb(o_)
    if h[0] > _rl[0] and l[0] < _rh[0] and h[1] > _rl[1] and l[1] < _rh[1]: o_.location.z += _rh[2] - l[2] + 0.0005   # standing on the rug
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); dg.update()
zc = ceil_at(XC, 4.25)
if zc: mini_cascade('Photo_chandelier', XC, 4.25, zc, TER + 1.95, 'Lights', 0.3)
# ---------------- waiter station pass counter
old = bpy.data.objects.get('counter')
if old and old.users_collection[0].name == 'Service':
    l, h = _bb(old); bpy.data.objects.remove(old)
    b = MB(); F0 = TER; x0, x1, y0, y1 = l[0], h[0], l[1], h[1]; _ST3 = mat('cap_stone_white2', (0.9, 0.89, 0.86), rough=0.3)
    _TE = bpy.data.materials.get('terracotta_flute') or _W; _BK3 = m['black']; _PO3 = mat('porcelain_white', (0.93, 0.93, 0.9), rough=0.15)
    b.box(x0 + 0.02, y0 + 0.02, F0 + 0.08, x1 - 0.02, y1 - 0.02, F0 + 0.90, _W); b.box(x0 + 0.05, y0 + 0.05, F0, x1 - 0.05, y1 - 0.05, F0 + 0.08, _BK3)
    n = int((y1 - y0 - 0.1) / 0.06)
    for k in range(n + 1): b.rod((x1 - 0.015, y0 + 0.05 + k * (y1 - y0 - 0.1) / n, F0 + 0.1), (x1 - 0.015, y0 + 0.05 + k * (y1 - y0 - 0.1) / n, F0 + 0.88), 0.022, _TE, 8)
    b.box(x0 - 0.02, y0 - 0.02, F0 + 0.90, x1 + 0.03, y1 + 0.02, F0 + 0.94, _ST3, 0.006)
    for k in range(4):                                                                              # doors on the staff side
        ya = y0 + 0.04 + k * (y1 - y0 - 0.08) / 4; yb = ya + (y1 - y0 - 0.08) / 4
        b.box(x0 + 0.005, ya + 0.008, F0 + 0.1, x0 + 0.02, yb - 0.008, F0 + 0.88, _W, 0.003); b.rod((x0 - 0.01, yb - 0.06, F0 + 0.45), (x0 - 0.01, yb - 0.06, F0 + 0.6), 0.006, _BRS3)
    ZT = F0 + 0.94; xm = (x0 + x1) / 2
    b.box(xm - 0.1, y0 + 0.25, ZT, xm + 0.1, y0 + 0.45, ZT + 0.02, _BK3); b.box(xm - 0.02, y0 + 0.33, ZT + 0.02, xm + 0.02, y0 + 0.37, ZT + 0.2, _BK3)   # POS
    b.box(xm - 0.14, y0 + 0.22, ZT + 0.2, xm + 0.14, y0 + 0.235, ZT + 0.4, _BK3, 0.004)
    for k in range(3):                                                                              # cutlery caddies
        yy = y0 + 0.85 + k * 0.22; b.cyl(xm, yy, ZT, ZT + 0.14, 0.06, _BRS3, 16)
        for j in range(6): b.rod((xm + 0.03 * math.cos(j), yy + 0.03 * math.sin(j), ZT + 0.02), (xm + 0.045 * math.cos(j), yy + 0.045 * math.sin(j), ZT + 0.24), 0.004, mat('stainless_brushed', (0.62, 0.63, 0.64), rough=0.28, metal=1.0), 5)
    for k in range(6): b.cyl(xm, y0 + 1.75, ZT + k * 0.012, ZT + k * 0.012 + 0.008, 0.2, _BRS3, 28)   # tray stack
    for k in range(2): b.lathe(xm, y0 + 2.25 + k * 0.22, ZT, [(0.0, 0.0), (0.05, 0.0), (0.07, 0.1), (0.045, 0.2), (0.04, 0.26), (0.0, 0.26)], _PO3, 16)   # water jugs
    inst(b.mesh('Station_counter'), 'Station_counter', (0, 0, 0), 0, 'Service')
# ---------------- booths: brass shoes + cornice cap
b = MB(); nsh = 0
for k in range(1, 8):
    sh_ = bpy.data.objects.get(f'Booth{k}_shell')
    if not sh_: continue
    l, h = _bb(sh_); xa = l[0]                                                                      # aisle face
    for yy in (l[1], h[1]):
        b.box(xa - 0.012, yy - 0.06, TER, xa + 0.07, yy + 0.06, TER + 0.1, _BRS3, 0.003); nsh += 1
    b.box(xa - 0.03, l[1] - 0.06, h[2] + 0.006, xa + 0.12, h[1] + 0.06, h[2] + 0.05, _W, 0.004)       # cornice cap over the lintel
inst(b.mesh('Booth_frame_trim'), 'Booth_frame_trim', (0, 0, 0), 0, 'Booths')
print('rev 12.0 block 4: photo zone, station, booth trim; shoes', nsh)
