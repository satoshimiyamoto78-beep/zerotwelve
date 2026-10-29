"""R12 rev. 8 assets: tea service (pakhta choynak with lid, curved spout and handle, footed pialas, brass tray, Rishtan
lagans, non, dried-fruit bowls), Bukhara rotunda collection (kuvshins, kumgans, lagans on easels, khum), draped flying
carpet with fringes and selvedge cords, zardevor frieze with tabs and tassels. Needs kit.py, assets_r12/v3, X, XW, m."""
import math

X8 = dict(pakhta=tex2('pakhta_t', 'pakhta.png', 0.11, rough=0.08, bump=0.05, coat=0.9),
          vcob=tex2('vase_cob_t', 'majcobalt.png', 0.2, rough=0.1, bump=0.15, coat=0.85),
          visf=tex2('vase_isf_t', 'majisfahan.png', 0.28, rough=0.1, bump=0.15, coat=0.85),
          vturq=tex2('vase_turq_t', 'domeglaze.png', 0.3, rough=0.1, bump=0.15, coat=0.85),
          apricot=mat('dried_apricot', (0.72, 0.36, 0.08), rough=0.55), almond=mat('almond', (0.52, 0.34, 0.2), rough=0.7),
          raisin=mat('raisin', (0.22, 0.12, 0.06), rough=0.4), gold=mat('gilt', (0.83, 0.62, 0.28), rough=0.25, metal=1.0))
for k_, sz in (('pakhta', 0.11), ('vcob', 0.2), ('visf', 0.28), ('vturq', 0.3)): register_uv_size(X8[k_], sz)

def _curve(b, pts, r0, r1, mm, n=8):
    """tapered tube through a polyline (overlapping rods, one closed shell each)"""
    L = len(pts) - 1
    for k in range(L): b.rod(pts[k], pts[k + 1], r0 + (r1 - r0) * k / max(1, L - 1), mm, n)

# ---------------------------------------------------------------- TEA SERVICE
def _choynak(b, x, y, z, s=1.0, mm=None):
    """Uzbek pakhta teapot ~0.75 l: body, gilt collar, lid with knob, curved spout (+x), loop handle (-x)"""
    mm = mm or X8['pakhta']; S = lambda v: v * s
    b.lathe(x, y, z, [(0.0, 0), (S(0.042), 0), (S(0.046), S(0.006)), (S(0.068), S(0.03)), (S(0.076), S(0.058)), (S(0.07), S(0.088)),
                      (S(0.05), S(0.108)), (S(0.037), S(0.116)), (0.0, S(0.116))], mm, 28)
    b.lathe(x, y, z + S(0.116), [(0.0, 0), (S(0.04), 0), (S(0.04), S(0.008)), (0.0, S(0.008))], X8['gold'], 28)
    b.lathe(x, y, z + S(0.124), [(0.0, 0), (S(0.036), 0), (S(0.03), S(0.012)), (S(0.012), S(0.02)), (S(0.007), S(0.024)), (S(0.011), S(0.032)), (S(0.0), S(0.036))], mm, 20)
    sp = [(x + S(0.06), y, z + S(0.035)), (x + S(0.09), y, z + S(0.052)), (x + S(0.112), y, z + S(0.076)), (x + S(0.126), y, z + S(0.1)), (x + S(0.136), y, z + S(0.118))]
    _curve(b, sp, S(0.012), S(0.006), mm, 10)
    hd = [(x - S(0.062), y, z + S(0.092)), (x - S(0.096), y, z + S(0.094)), (x - S(0.112), y, z + S(0.072)), (x - S(0.104), y, z + S(0.044)), (x - S(0.07), y, z + S(0.032))]
    _curve(b, hd, S(0.007), S(0.007), mm, 8)
def _piala2(b, x, y, z, mm=None):
    """footed piala d 100, h 50 (open bowl: outer wall up, inner wall down)"""
    b.lathe(x, y, z, [(0.0, 0), (0.022, 0), (0.022, 0.006), (0.03, 0.009), (0.045, 0.03), (0.05, 0.05), (0.046, 0.05), (0.041, 0.032), (0.025, 0.014), (0.0, 0.014)], mm or X8['pakhta'], 24)
def _tray(b, x, y, z, r=0.15):
    b.lathe(x, y, z, [(0.0, 0), (r * 0.9, 0), (r, 0.012), (r * 0.97, 0.014), (r * 0.88, 0.004), (0.0, 0.004)], m['brass'], 36)
def _armudu(b, x, y, z):
    """pear-shaped tea glass on a saucer"""
    b.lathe(x, y, z, [(0.0, 0), (0.05, 0), (0.052, 0.006), (0.0, 0.006)], X8['pakhta'], 20)
    b.lathe(x, y, z + 0.006, [(0.0, 0), (0.022, 0), (0.03, 0.02), (0.02, 0.05), (0.028, 0.085), (0.0, 0.085)], m['glass'], 16)
def _dryfruit(b, x, y, z):
    """pakhta bowl heaped with dried apricots, almonds and raisins"""
    b.lathe(x, y, z, [(0.0, 0), (0.03, 0), (0.07, 0.04), (0.068, 0.042), (0.0, 0.03)], X8['pakhta'], 24)
    for k in range(9):
        a = 2 * math.pi * k / 9; rr = 0.04 if k % 3 else 0.015
        px, py = x + rr * math.cos(a), y + rr * math.sin(a)
        mm = (X8['apricot'], X8['almond'], X8['raisin'])[k % 3]
        b.lathe(px, py, z + 0.03 + (0.006 if k % 3 == 0 else 0), [(0.0, 0), (0.012, 0.003), (0.013, 0.008), (0.0, 0.013)], mm, 8)
def _non(b, x, y, z, r=0.1):
    """Samarkand non: raised rim, stamped centre (picture top)"""
    lathe_pic(b, x, y, z, [(0.0, 0), (r * 0.95, 0), (r, 0.018), (r * 0.9, 0.034), (r * 0.62, 0.026), (r * 0.55, 0.014), (0.0, 0.012)], X['bread'], 2 * r, 32)
@cached
def a_tableset2(n):
    """rev. 8 table setting on a carved table (top +0.76), origin = table centre: per seat a Rishtan plate + piala;
    down the kilim runner: lagan of plov, non, dried fruit, brass tray with the choynak and spare pialas"""
    b = MB(); Lx = 0.7 * n; z = 0.76
    b.picture_box(-Lx / 2 + 0.06, -0.13, z, Lx / 2 - 0.06, 0.13, z + 0.003, X['kilim2'], '+z')
    for j in range(n):
        cx = -Lx / 2 + 0.35 + 0.7 * j
        for sy in (-1, 1): _plate_r(b, cx, sy * 0.265, z, 0.11); _piala2(b, cx + 0.19, sy * 0.3, z)
    zt = z + 0.003
    if n == 1:
        _non(b, -0.13, 0.0, zt, 0.085); _tray(b, 0.15, 0.0, zt, 0.12); _choynak(b, 0.13, 0.0, zt + 0.004, 0.85)
    elif n == 2:
        _lagan_plov(b, -0.33, 0.0, zt); _non(b, 0.04, 0.0, zt, 0.09); _tray(b, 0.38, 0.0, zt, 0.14)
        _choynak(b, 0.35, 0.0, zt + 0.004); _piala2(b, 0.47, 0.07, zt + 0.004)
    else:
        _lagan_plov(b, -0.58, 0.0, zt); _non(b, -0.18, 0.0, zt, 0.095); _dryfruit(b, 0.13, 0.0, zt)
        _tray(b, 0.55, 0.0, zt, 0.15); _choynak(b, 0.52, 0.0, zt + 0.004); _piala2(b, 0.64, 0.08, zt + 0.004); _piala2(b, 0.64, -0.08, zt + 0.004)
    return b.mesh(f'Tableset2_{2 * n}p')
@cached
def a_boothset2():
    """booth table set (booth-local coordinates, table x 0.15..1.05, y 0.73..1.43, top +0.76)"""
    b = MB(); z = 0.76
    for px, py in ((0.33, 0.88), (0.87, 0.88), (0.33, 1.28), (0.87, 1.28)): _plate_r(b, px, py, z, 0.105)
    for px, py in ((0.52, 0.86), (0.68, 1.3)): _piala2(b, px, py, z)
    _lagan_plov(b, 0.6, 1.08, z); _tray(b, 0.3, 1.08, z, 0.11); _choynak(b, 0.28, 1.08, z + 0.004, 0.8); _non(b, 0.9, 1.08, z, 0.075)
    return b.mesh('Boothset2')

# ---------------------------------------------------------------- CERAMICS / METALWORK for the Bukhara rotunda
def _kuvshin(b, x, y, z, mm, s=1.0):
    """jug with a neck, lip and handle (+x spout lip is implied by the flared rim)"""
    S = lambda v: v * s
    b.lathe(x, y, z, [(0.0, 0), (S(0.045), 0), (S(0.05), S(0.01)), (S(0.085), S(0.08)), (S(0.08), S(0.16)), (S(0.045), S(0.215)), (S(0.03), S(0.25)),
                      (S(0.034), S(0.29)), (S(0.046), S(0.31)), (S(0.04), S(0.312)), (S(0.026), S(0.29)), (S(0.0), S(0.27))], mm, 28)
    _curve(b, [(x - S(0.03), y, z + S(0.28)), (x - S(0.08), y, z + S(0.27)), (x - S(0.1), y, z + S(0.22)), (x - S(0.085), y, z + S(0.15))], S(0.008), S(0.008), mm, 8)
def _kumgan(b, x, y, z, s=1.0):
    """copper ewer: pear body, long neck, domed lid with finial, S-spout (+x), tall handle (-x)"""
    S = lambda v: v * s; cu = X['copper']
    b.lathe(x, y, z, [(0.0, 0), (S(0.05), 0), (S(0.05), S(0.012)), (S(0.035), S(0.022)), (S(0.07), S(0.07)), (S(0.075), S(0.12)), (S(0.05), S(0.17)),
                      (S(0.022), S(0.21)), (S(0.02), S(0.28)), (S(0.032), S(0.3)), (S(0.0), S(0.3))], cu, 28)
    b.lathe(x, y, z + S(0.3), [(0.0, 0), (S(0.032), 0), (S(0.02), S(0.03)), (S(0.006), S(0.05)), (S(0.012), S(0.06)), (S(0.0), S(0.075))], m['brass'], 16)
    _curve(b, [(x + S(0.06), y, z + S(0.09)), (x + S(0.11), y, z + S(0.13)), (x + S(0.12), y, z + S(0.2)), (x + S(0.15), y, z + S(0.27)), (x + S(0.18), y, z + S(0.3))], S(0.011), S(0.005), cu, 10)
    _curve(b, [(x - S(0.02), y, z + S(0.29)), (x - S(0.09), y, z + S(0.31)), (x - S(0.12), y, z + S(0.24)), (x - S(0.1), y, z + S(0.15)), (x - S(0.068), y, z + S(0.11))], S(0.007), S(0.007), cu, 8)
def _lagan_easel(b, x, y, z, R=0.15, ang=0.0):
    """Rishtan lagan standing on a brass easel, picture facing `ang` (about Z)"""
    c, s_ = math.cos(ang), math.sin(ang)
    P = lambda u, w: (x + u * c, y + u * s_, z + w)
    pl = [(R * math.cos(2 * math.pi * k / 40), R * math.sin(2 * math.pi * k / 40) + R + 0.03) for k in range(40)]
    fs = b.extrude(pl, -0.006, 0.008, X['rishtan'], 'xz')                         # disc in local x-z, thin along y
    for f in fs:
        for lp in f.loops:
            v = lp.vert.co
            if abs(f.normal.y) > 0.9: lp[b.uv].uv = (0.5 + v.x / (2 * R), 0.5 + (v.z - R - 0.03) / (2 * R)); b.fixed.add(f)
    for v in {v for f in fs for v in f.verts}:                                        # tilt back 12 deg, rotate, move
        lx, ly, lz = v.co.x, v.co.y, v.co.z; t = math.radians(12)
        ly, lz = ly + lz * math.sin(t), lz * math.cos(t)
        v.co = (x + lx * math.cos(ang + math.pi / 2) - ly * math.sin(ang + math.pi / 2), y + lx * math.sin(ang + math.pi / 2) + ly * math.cos(ang + math.pi / 2), z + lz)
    for sx in (-1, 1):                                                                 # easel: two legs + ledge + back strut
        u = sx * R * 0.55; a_ = (x + u * math.cos(ang + math.pi / 2), y + u * math.sin(ang + math.pi / 2))
        b.rod((a_[0] + 0.03 * c, a_[1] + 0.03 * s_, z), (a_[0] + 0.006 * c, a_[1] + 0.006 * s_, z + 0.06), 0.004, m['brass'], 6)
    b.rod((x - 0.055 * c, y - 0.055 * s_, z), (x - 0.03 * c, y - 0.03 * s_, z + 0.16), 0.004, m['brass'], 6)
def _khum(b, x, y, z, mm):
    """big storage khum (glazed shoulder), h 0.62"""
    b.lathe(x, y, z, [(0.0, 0), (0.1, 0), (0.17, 0.12), (0.2, 0.3), (0.18, 0.45), (0.11, 0.55), (0.09, 0.58), (0.105, 0.6), (0.1, 0.62), (0.0, 0.6)], mm, 32)

@cached
def a_rotunda2():
    """rev. 8 Bukhara rotunda: same frame as a_rotunda (lattice drum r 0.45, shelves at 0.75 / 1.45, copper cap, 4 posts + ring canopy)
    with a curated collection: khum on the plinth, lagans on easels, cobalt / Isfahan / turquoise kuvshins, copper kumgans,
    brass-edged glass shelves, a lit plinth ring; origin = centre on the podium top (posts stand at z = -0.15)"""
    b = MB(); W = XW['wd']; H = 2.15
    for k in range(16):                                                               # 16 slim slats: the collection reads through the drum
        a = 2 * math.pi * k / 16; b.obox(0.45 * math.cos(a), 0.45 * math.sin(a), 0.06, H - 0.06, 0.03, 0.026, a + math.pi / 2, W)
    b.ring(0, 0, 0.0, [(0.43, 0), (0.5, 0), (0.5, 0.06), (0.43, 0.06)], m['brass'], 48)
    b.ring(0, 0, H - 0.06, [(0.43, 0), (0.5, 0), (0.5, 0.06), (0.43, 0.06)], m['brass'], 48)
    b.cyl(0, 0, 0.0, 0.02, 0.43, X['carved'], 40)                                     # carved plinth disc inside the drum
    for zz in (0.75, 1.45):
        b.cyl(0, 0, zz, zz + 0.012, 0.43, m['glass'], 40)
        b.ring(0, 0, zz - 0.006, [(0.43, 0), (0.465, 0), (0.465, 0.024), (0.43, 0.024)], m['brass'], 48)
    _khum(b, 0, 0, 0.02, X8['vturq'])
    zs = 0.762
    for k in range(5):                                                                  # shelf 1: lagans face outward + kuvshins
        a = 2 * math.pi * k / 5 + 0.3
        if k % 2 == 0: _lagan_easel(b, 0.27 * math.cos(a), 0.27 * math.sin(a), zs, 0.13, a)
        else: _kuvshin(b, 0.25 * math.cos(a), 0.25 * math.sin(a), zs, (X8['vcob'], X8['visf'])[k // 2 % 2], 0.85)
    _kumgan(b, 0, 0, zs, 0.9)
    zs = 1.462
    for k in range(6):                                                                  # shelf 2: kumgans, kuvshins, choynak
        a = 2 * math.pi * k / 6
        px, py = 0.27 * math.cos(a), 0.27 * math.sin(a)
        if k % 3 == 0: _kumgan(b, px, py, zs, 0.75)
        elif k % 3 == 1: _kuvshin(b, px, py, zs, (X8['vturq'], X8['vcob'])[k // 3], 0.8)
        else: _choynak(b, px, py, zs, 1.2)
    _lagan_easel(b, 0.0, 0.0, zs, 0.17, 0.0)
    b.cyl(0, 0, H - 0.03, H, 0.43, X['lampglow'], 32)
    b.lathe(0, 0, H, [(0.0, 0), (0.55, 0), (0.52, 0.12), (0.4, 0.3), (0.2, 0.42), (0.05, 0.47), (0.05, 0.6), (0.0, 0.62)], X['copper'], 40)
    b.lathe(0, 0, H + 0.6, [(0.0, 0), (0.035, 0.0), (0.05, 0.05), (0.02, 0.1), (0.008, 0.16), (0.0, 0.18)], X8['gold'], 16)      # finial
    for k in range(4):
        a = k * math.pi / 2; b.cyl(0.96 * math.cos(a), 0.96 * math.sin(a), -0.15, 2.2, 0.03, m['bronze'], 12)
        b.lathe(0.96 * math.cos(a), 0.96 * math.sin(a), -0.15, [(0.0, 0), (0.05, 0), (0.05, 0.04), (0.03, 0.07), (0.0, 0.07)], m['brass'], 12)
    b.ring(0, 0, 2.2, [(0.85, 0), (1.05, 0), (1.05, 0.12), (0.85, 0.12)], m['brass'], 64)
    return b.mesh('Bukhara_rotunda2')
@cached
def a_vitrine2(k):
    """lit vitrine 300 x 300 (as a_vitrine) holding one masterpiece: 0 lagan, 1 kumgan, 2 cobalt kuvshin, 3 pakhta choynak"""
    b = MB(); h = 0.15
    b.box(-h, -h, 0, h, h, 0.4, XW['wd'], 0.003)
    b.box(-h + 0.012, -h + 0.012, 0.06, h - 0.012, h - 0.012, 0.34, X['carved'])        # carved panel band
    b.box(-h + 0.025, -h + 0.025, 0.4, h - 0.025, h - 0.025, 0.9, m['glass'])
    for sx in (-1, 1):
        for sy in (-1, 1): b.box(sx * h - (0.025 if sx > 0 else 0), sy * h - (0.025 if sy > 0 else 0), 0.4, sx * h + (0 if sx > 0 else 0.025), sy * h + (0 if sy > 0 else 0.025), 0.9, m['brass'])
    b.box(-h, -h, 0.9, h, h, 0.93, m['brass'])
    b.box(-0.1, -0.1, 0.4, 0.1, 0.1, 0.41, X['lampglow'])
    if k == 0: _lagan_easel(b, 0, 0.02, 0.41, 0.1, -math.pi / 2)
    elif k == 1: _kumgan(b, 0, 0, 0.41, 0.95)
    elif k == 2: _kuvshin(b, 0, 0, 0.41, X8['vcob'], 1.0)
    else: _choynak(b, 0, 0, 0.41, 1.3)
    return b.mesh(f'Vitrine2_{k}')

# ---------------------------------------------------------------- FLYING CARPET: draped between 4 hangers, selvedge cords, fringes
FC_W, FC_L = 1.25, 1.9
FC_U = (-0.625, -0.55, -0.42, -0.21, 0.0, 0.21, 0.42, 0.55, 0.625)
FC_V = (-0.95, -0.85, -0.68, -0.45, -0.22, 0.0, 0.22, 0.45, 0.68, 0.85, 0.95)
def fc_z(u, v):
    """top surface height of the draped carpet (0 at the hangers' level)"""
    return -0.075 * math.cos(math.pi * u / FC_W) * math.cos(math.pi * v / FC_L) + 0.012 * math.sin(2 * math.pi * v / FC_L) + 0.0026
@cached
def a_flycarpet2(img):
    b = MB(); mm = X[img]; w, l = FC_W, FC_L
    rows = [[(u, v, fc_z(u, v)) for u in FC_U] for v in FC_V]
    fs = b.sheet(rows, mm, 0.014, picture=True)
    for f in fs:
        for lp in f.loops: c = lp.vert.co; lp[b.uv].uv = ((c.x + w / 2) / w, (c.y + l / 2) / l)
    for sx in (-1, 1):                                                               # selvedge cords along the long sides
        pts = [(sx * (w / 2 + 0.006), v, fc_z(sx * w / 2, v) - 0.007) for v in FC_V]
        _curve(b, pts, 0.006, 0.006, X['tassel_red'], 6)
    for sy in (-1, 1):                                                               # warp fringes at the ends
        for k in range(40):
            u = -w / 2 + 0.02 + (w - 0.04) * k / 39; z0 = fc_z(u, sy * l / 2) - 0.007
            b.rod((u, sy * l / 2, z0), (u + 0.004 * math.sin(k * 1.7), sy * (l / 2 + 0.07), z0 - 0.03), 0.0028, X['fringe'], 4)
    return b.mesh(f'Flying_carpet2_{img}')

# ---------------------------------------------------------------- ZARDEVOR frieze (texture tile = 4 tabs; band 0.43 + tabs 0.12)
@cached
def a_zardevor(L, n_tabs=None):
    """embroidered frieze in the y-z plane (x 0..0.008 local), y 0..L, z 0 = tab tips .. 0.55 top; brass rod on top, tassels"""
    n = n_tabs or max(1, round(L / 0.2)); tw = L / n; tile = 4 * tw
    b = MB(); top_, mid_ = 0.55, 0.12
    ys = [tw * k / 2 for k in range(2 * n + 1)]
    bot = [(0.0, y, (0.0 if k % 2 else mid_ - 0.004)) for k, y in enumerate(ys)]
    rows = [bot, [(0.0, y, mid_) for y in ys], [(0.0, y, top_) for y in ys]]
    fs = b.sheet(rows, X['zardevor'], 0.008, picture=True)
    for f in fs:
        for lp in f.loops: c = lp.vert.co; lp[b.uv].uv = (c.y / tile, c.z / top_)
    xc = min(v.co.x for f in fs for v in f.verts); xc2 = max(v.co.x for f in fs for v in f.verts); xm = (xc + xc2) / 2
    b.rod((xm, 0.004, top_ + 0.012), (xm, L - 0.004, top_ + 0.012), 0.012, m['brass'], 10)     # hanging rod on the hem, tight under the ledger
    for k in range(n):
        y = tw * (k + 0.5)
        b.lathe(xm, y, -0.016, [(0.0, 0), (0.008, 0.002), (0.012, 0.008), (0.008, 0.014), (0.0, 0.016)], X8['gold'], 10)
        b.lathe(xm, y, -0.09, [(0.0, 0), (0.016, 0), (0.012, 0.04), (0.006, 0.07), (0.0, 0.074)], X['tassel_red'], 10)
    return b.mesh(f'Zardevor_{int(L * 1000)}')
