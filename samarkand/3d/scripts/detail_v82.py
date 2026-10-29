"""R12 rev. 8.2 (owner review): SAMARKAND channel letters on the mangal, advertising display on the aivan end screen, carved
jali aivan screens, draped-tunnel alley (crossing velvet swags, layered rugs, terracotta jar clusters, pillar candles),
majolica planters + real shrubs on the aivan, tapchan per the owner's reference (balustrade, tiled posts, finials, red
kurpacha, turned-leg table), majlis floor seating + octagonal inlaid tables in the tents, richer booth portals.
Executed at the end of detail_r12.py (same namespace)."""
import math
from mathutils import Matrix, Vector

def _rm(*prefixes):
    for o_ in [o for o in bpy.data.objects if o.name.startswith(prefixes)]: bpy.data.objects.remove(o_)
def _bb(o_):
    bpy.context.view_layer.update(); cs_ = [o_.matrix_world @ Vector(c) for c in o_.bound_box]
    return [min(c[i] for c in cs_) for i in range(3)], [max(c[i] for c in cs_) for i in range(3)]

X82 = dict(green=mat('logo_green', (0.0, 0.42, 0.12), emit=(0.0, 1.0, 0.22), strength=2.2),
           yellow=mat('logo_yellow', (0.75, 0.42, 0.0), emit=(1.0, 0.62, 0.0), strength=1.8),
           greenday=mat('logo_green_day', (0.0, 0.26, 0.06), rough=0.3, coat=0.5, emit=(0.0, 1.0, 0.2), strength=0.35),
           yellowday=mat('logo_yellow_day', (0.62, 0.36, 0.0), rough=0.3, coat=0.5, emit=(1.0, 0.6, 0.0), strength=0.3),
           black=mat('screen_bezel', (0.02, 0.02, 0.025), rough=0.25, coat=0.6),
           screen=uvmat('ad_screen_uv', 'ad_screen.png', rough=0.15, sheen=0.0),
           majlis=tex2('majlis_t', 'majlis_kilim.png', 0.55, rough=0.85, bump=0.4),
           inlay=uvmat('octa_inlay_uv', 'octa_inlay.png', rough=0.3, sheen=0.0),
           candle=mat('pillar_wax', (0.93, 0.88, 0.78), rough=0.6),
           flame=mat('pillar_glow', (1, .8, .5), emit=(1.0, 0.62, 0.30), strength=12.0),
           clayred=mat('terracotta_amphora', (0.36, 0.14, 0.065), rough=0.8, bump=0.3, noise_var=0.08))
register_uv_size(X82['majlis'], 0.55)
sb_ = X82['screen'].node_tree.nodes['Principled BSDF']; it_ = [n_ for n_ in X82['screen'].node_tree.nodes if n_.type == 'TEX_IMAGE'][0]
X82['screen'].node_tree.links.new(it_.outputs['Color'], sb_.inputs['Emission Color']); sb_.inputs['Emission Strength'].default_value = 1.6

# =============== 1. SAMARKAND channel letters ===============
FONT_ = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
def channel_text(body, size, depth, mm, origin, xdir, name, cname='Mangal'):
    """extruded letters standing on a wall: reading direction xdir (unit, horizontal), face normal = xdir x Z;
    origin = baseline centre on the wall surface; letters grow out of the wall by `depth`"""
    cu = bpy.data.curves.new(name + '_c', 'FONT'); cu.body = body; cu.font = bpy.data.fonts.load(FONT_, check_existing=True)
    cu.size = size; cu.extrude = depth / 2; cu.align_x = 'CENTER'; cu.fill_mode = 'BOTH'
    tmp = bpy.data.objects.new(name + '_t', cu); bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg)); bpy.data.objects.remove(tmp)
    xd = Vector(xdir).normalized(); zn = xd.cross(Vector((0, 0, 1)))                                 # outward normal (X x Y = Z)
    R = Matrix(((xd.x, 0, zn.x), (xd.y, 0, zn.y), (xd.z, 1, zn.z))).to_4x4()
    me.transform(Matrix.Translation(Vector(origin) + zn * (depth / 2)) @ R)
    me.materials.clear(); me.materials.append(mm)
    o_ = bpy.data.objects.new(name, me); coll(cname).objects.link(o_); return o_
# (a) dining side: walnut sign board on the mangal flue, above the hood
mb = MB(); mb.box(11.06, 3.85, TER + 2.48, 11.1, 7.35, TER + 3.2, XW['wd'], 0.004)
mb.box(11.055, 3.85, TER + 2.48, 11.06, 7.35, TER + 2.5, m['brass']); mb.box(11.055, 3.85, TER + 3.18, 11.06, 7.35, TER + 3.2, m['brass'])
inst(mb.mesh('Mangal_signboard'), 'Mangal_signboard', (0, 0, 0), 0, 'Mangal')
channel_text('Samarkand', 0.52, 0.03, X82['green'], (11.06, 5.6, TER + 2.76), (0, -1, 0), 'Logo_Samarkand_W')
channel_text('TAJIK AND UZBEK NATIONAL CUISINE', 0.105, 0.015, X82['yellow'], (11.06, 5.6, TER + 2.56), (0, -1, 0), 'Logo_subtitle_W')
# (b) street side: letters on the firewall's back (x = 12.3), read from the sidewalk
channel_text('Samarkand', 0.64, 0.035, X82['greenday'], (12.3, 6.1, TER + 1.2), (0, 1, 0), 'Logo_Samarkand_E')
channel_text('TAJIK AND UZBEK NATIONAL CUISINE', 0.135, 0.02, X82['yellowday'], (12.3, 6.1, TER + 0.94), (0, 1, 0), 'Logo_subtitle_E')

# =============== 2. AIVAN END SCREENS: carved jali panels; the one facing the alley carries a 65" display ===============
@cached
def a_aivan_screen(L, H, ad=False):
    """screen in the x-z plane, local x 0..L, y 0..0.06, z 0..H: walnut frame, pierced star jali (or solid carved board + display),
    brass cap rail; ad: 65" landscape display 1.45 x 0.82 on the -y face"""
    b = MB(); F = 0.07
    b.box(0, 0, 0, F, 0.06, H, XW['wd'], 0.003); b.box(L - F, 0, 0, L, 0.06, H, XW['wd'], 0.003)
    b.box(F, 0, 0, L - F, 0.06, 0.12, XW['wd'], 0.003); b.box(F, 0, H - 0.07, L - F, 0.06, H, XW['wd'], 0.003)
    if ad: b.box(F, 0.01, 0.12, L - F, 0.05, H - 0.07, XW['cv'])
    else:
        for poly in jali(F, 0.12, L - F, H - 0.07, 0.15, 0.02): ext_holes(b, poly, 0.015, 0.045, XW['wd'], 'xz')
    b.box(-0.01, -0.01, H, L + 0.01, 0.07, H + 0.025, m['brass'], 0.003)
    if ad:
        cx, w, h, z0 = L / 2, 1.45, 0.82, 0.2
        b.box(cx - w / 2 - 0.012, -0.03, z0 - 0.012, cx + w / 2 + 0.012, 0.01, z0 + h + 0.012, X82['black'], 0.004)
        b.picture_box(cx - w / 2, -0.032, z0, cx + w / 2, -0.03, z0 + h, X82['screen'], '-y')
    return b.mesh(f'Aivan_screen_{int(L * 1000)}{"_ad" if ad else ""}')
asc_ = sorted([bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'ascreen'], key=lambda b_: b_[1])
_rm('ascreen')
for i_, (x0, y0, x1, y1) in enumerate(asc_):
    inst(a_aivan_screen(round(x1 - x0, 3), 1.2, i_ == 0), f'Aivan_screen_{i_ + 1}', (x0, y0, 0.0), 0, 'Aivan')
# ad image landscape: re-render the ad layout 16:9 is done in textures; the portrait one is cropped by the picture box UVs

# =============== 3. ALLEY = draped tunnel (owner ref.): crossing swags, layered rugs, jars, pillar candles ===============
e0, e1 = D['ent']; t0, t1 = D['tun']; ya, yb = e0 + 0.08, e1 - 0.08; Wc = round(yb - ya, 3)
xs = [t0 + 0.2 + 0.9 * i for i in range(int((t1 - t0 - 0.3) / 0.9) + 1)]
def swag(b, p0, p1, sag, width, mm, folds=5, n=16):
    """gathered velvet swag from p0 to p1 (ends gathered to 0.08 m), width along Y (ends stay in their x-planes), sagging `sag`"""
    rows = []
    for k in range(n + 1):
        t = k / n; c = Vector(p0).lerp(Vector(p1), t); c.z -= sag * math.sin(math.pi * t)
        w = 0.08 + (width - 0.08) * math.sin(math.pi * t) ** 0.7; row = []
        for j in range(folds * 2 + 1):
            u = -w / 2 + w * j / (folds * 2); row.append((c.x, c.y + u, c.z + (0.035 if j % 2 else 0.0) * math.sin(math.pi * t) ** 0.5))
        rows.append(row)
    b.sheet(rows, mm, 0.006, picture=False)
for k_, (xa_, xb_) in enumerate(zip(xs[:-1], xs[1:])):
    mb = MB(); x0s, x1s = xa_ + 0.092, xb_ - 0.012                     # 12 mm off the arch faces (sheet thickness tilts at the ends)
    swag(mb, (x0s, ya + 0.32, TER + 2.36), (x1s, yb - 0.32, TER + 2.36), 0.22, 0.5, X['velvet_terra'])
    swag(mb, (x0s, yb - 0.32, TER + 2.43), (x1s, ya + 0.32, TER + 2.43), 0.2, 0.46, X['velvet_wine'])
    inst(mb.mesh(f'Corridor_swag_{k_ + 1}'), f'Corridor_swag_{k_ + 1}', (0, 0, 0), 0, 'Corridor')
run_ = next((bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'runner'), None)
zr_ = TER + 0.012 if run_ else TER
RUGS_ = []
for k_, (cx_, cy_, ang_, img_) in enumerate(((8.3, (ya + yb) / 2 + 0.05, 0.06, 'carpet1'), (9.05, (ya + yb) / 2 - 0.08, -0.05, 'carpet2'), (9.8, (ya + yb) / 2 + 0.04, 0.04, 'carpet1'))):
    mb = MB(); hw, hl = 0.6, 0.68; zb = zr_ + 0.008 * k_
    fs = mb.picture_box(-hl, -hw, zb, hl, hw, zb + 0.008, X[img_], '+z')
    for v in {v for f in fs for v in f.verts}:
        x_, y_ = v.co.x, v.co.y; v.co.x, v.co.y = cx_ + x_ * math.cos(ang_) - y_ * math.sin(ang_), cy_ + x_ * math.sin(ang_) + y_ * math.cos(ang_)
    inst(mb.mesh(f'Corridor_rug_{k_ + 1}'), f'Corridor_rug_{k_ + 1}', (0, 0, 0), 0, 'Corridor'); RUGS_.append((cx_, cy_, ang_, hl, hw, zb + 0.008))
def floor_z(x, y, base):
    """top of the highest corridor rug under (x, y) (rugs are stacked), else `base`"""
    z = base
    for cx, cy, a, hl, hw, zt in RUGS_:
        u = (x - cx) * math.cos(a) + (y - cy) * math.sin(a); v = -(x - cx) * math.sin(a) + (y - cy) * math.cos(a)
        if abs(u) <= hl + 0.06 and abs(v) <= hw + 0.06: z = max(z, zt)
    return z
@cached
def a_amphora(h):
    """terracotta amphora with two loop handles, height h, origin = bottom centre"""
    b = MB(); s = h / 0.8
    b.lathe(0, 0, 0, [(0.0, 0), (0.07 * s, 0), (0.09 * s, 0.03 * s), (0.19 * s, 0.25 * s), (0.2 * s, 0.4 * s), (0.15 * s, 0.6 * s), (0.08 * s, 0.7 * s), (0.065 * s, 0.75 * s),
                      (0.085 * s, 0.79 * s), (0.08 * s, 0.8 * s), (0.055 * s, 0.77 * s), (0.0, 0.74 * s)], X82['clayred'], 28)
    for sg in (-1, 1): _curve(b, [(sg * 0.07 * s, 0, 0.72 * s), (sg * 0.13 * s, 0, 0.73 * s), (sg * 0.16 * s, 0, 0.66 * s), (sg * 0.155 * s, 0, 0.6 * s)], 0.012 * s, 0.012 * s, X82['clayred'], 8)
    return b.mesh(f'Amphora_{int(h * 100)}')
@cached
def a_pillar_candle(h):
    b = MB(); b.cyl(0, 0, 0, h, 0.05, X82['candle'], 20); b.cyl(0, 0, h, h + 0.004, 0.044, X82['flame'], 20); return b.mesh(f'Pillar_candle_{int(h * 100)}')
nj_ = 0
for k_, (xa_, xb_) in enumerate(zip(xs[:-1], xs[1:])):
    for side_, yw_ in ((1, ya), (-1, yb)):
        base_ = (xa_ + 0.08 + xb_) / 2
        for dx_, dy_, h_ in ((-0.205, 0.24, 0.78), (0.135, 0.2, 0.55), (0.34, 0.33, 0.36)):
            nj_ += 1; z_ = zr_ if run_ and run_[1] - 1e-6 <= yw_ + side_ * dy_ <= run_[3] + 1e-6 else TER
            inst(a_amphora(h_ if (k_ + (side_ > 0)) % 2 else [0.62, 0.42, 0.3][[0.78, 0.55, 0.36].index(h_)]), f'Corridor_amphora_{nj_}', (base_ + dx_, yw_ + side_ * dy_, z_), 0.4 * nj_, 'Corridor')
for x_ in xs:
    for side_, yw_ in ((1, ya), (-1, yb)):
        for dx_, h_ in ((0.04, 0.42), ):
            y_ = yw_ + side_ * 0.5; z_ = floor_z(x_ + dx_, y_, zr_ if run_ and run_[1] - 1e-6 <= y_ <= run_[3] + 1e-6 else TER)
            inst(a_pillar_candle(h_), 'Corridor_candle', (x_ + dx_, y_, z_), 0, 'Corridor')
            point_light = bpy.data.lights.new('cand', 'POINT'); point_light.energy = 6; point_light.color = (1.0, 0.62, 0.3); point_light.shadow_soft_size = 0.03
            lo_ = bpy.data.objects.new('Corridor_candle_light', point_light); lo_.location = (x_ + dx_, y_, z_ + h_ + 0.06); coll('Lights').objects.link(lo_)

# =============== 4. PLANTERS + PLANTS: alley pots, aivan arcade bays ===============
@cached
def a_urn(R, H):
    """glazed majolica planter (Rishtan cobalt), footed urn, soil flush with the rim at H; origin = bottom centre"""
    b = MB()
    b.lathe(0, 0, 0, [(0.0, 0), (R * 0.55, 0), (R * 0.58, 0.04), (R * 0.5, 0.08), (R * 0.82, H * 0.35), (R, H * 0.72), (R * 0.93, H * 0.9), (R * 1.0, H * 0.95), (R * 0.97, H), (0.0, H)], X8['vcob'], 32)
    b.ring(0, 0, H * 0.9, [(R * 0.93, 0), (R * 1.01, 0), (R * 1.01, H * 0.05), (R * 0.93, H * 0.05)], X8['gold'], 32)
    return b.mesh(f'Urn_{int(R * 100)}_{int(H * 100)}')
for o_ in [o for o in bpy.data.objects if o.name.split('.')[0] == 'pot']:
    lo, hi = _bb(o_); cx_, cy_ = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2; R_ = (hi[0] - lo[0]) / 2; H_ = hi[2] - lo[2]
    o_.data = a_urn(round(R_, 3), round(H_, 3)); o_.location = (cx_, cy_, lo[2]); o_.rotation_euler = (0, 0, 0); o_.scale = (1, 1, 1)
nsh_ = 0; bays_ = [o for o in bpy.data.objects if o.name.startswith('Khiva_arcade_bay') and 'lotus' in [m_.name for m_ in o.data.materials]]
spots_ = []
for o_ in bays_:                                                     # positions first: the bays share mesh data
    me_ = o_.data; li_ = [i for i, m_ in enumerate(me_.materials) if m_.name == 'lotus'][0]; mw_ = o_.matrix_world
    pts_ = [mw_ @ me_.vertices[v].co for p_ in me_.polygons if p_.material_index == li_ for v in p_.vertices]
    if pts_: spots_.append((sum(p.x for p in pts_) / len(pts_), sum(p.y for p in pts_) / len(pts_), min(p.z for p in pts_)))
for me_ in {o_.data for o_ in bays_}:
    li_ = [i for i, m_ in enumerate(me_.materials) if m_.name == 'lotus'][0]
    bm_ = bmesh.new(); bm_.from_mesh(me_); bmesh.ops.delete(bm_, geom=[f for f in bm_.faces if f.material_index == li_], context='FACES'); bm_.to_mesh(me_); bm_.free(); me_.update()
for cx_, cy_, z0_ in spots_:
    nsh_ += 1; inst(a_shrub(30 + nsh_, ('bou', 'jas', 'green')[nsh_ % 3]), f'Aivan_shrub_foliage_{nsh_}', (cx_, cy_, z0_ + 0.002), 0.7 * nsh_, 'Planting')
print('aivan shrubs', nsh_)

# =============== 5. TAPCHAN per the owner's reference ===============
@cached
def a_tapchan2(W=2.0, Dp=2.2):
    """tapchan W (x) x Dp (y), deck +0.45, open to +x: square posts with majolica inserts + turned finials, carved apron, plank deck,
    turned-baluster railing on the -x, -y, +y sides; origin = (-x, -y) floor corner"""
    b = MB(); WD = XW['wd']; P = 0.12; zd = 0.45
    for px, py in ((0, 0), (W - P, 0), (0, Dp - P), (W - P, Dp - P)):
        b.box(px, py, 0, px + P, py + P, zd + 0.5, WD, 0.004)
        for fx, fy, nx_, ny_ in ((px - 0.004, py + 0.02, 1, 0), (px + P, py + 0.02, 1, 0), (px + 0.02, py - 0.004, 0, 1), (px + 0.02, py + P, 0, 1)):
            if nx_: b.box(fx, fy, 0.08, fx + 0.004, fy + P - 0.04, 0.36, X['majcobalt'])
            else: b.box(fx, fy, 0.08, fx + P - 0.04, fy + 0.004, 0.36, X['majcobalt'])
        b.lathe(px + P / 2, py + P / 2, zd + 0.5, [(0.0, 0), (0.05, 0), (0.05, 0.02), (0.035, 0.03), (0.045, 0.06), (0.02, 0.1), (0.008, 0.13), (0.0, 0.14)], WD, 16)
    for a0, a1, ax in ((P, W - P, 'x'), (P, Dp - P, 'y')):
        for c in (0.01, (Dp if ax == 'x' else W) - 0.03):
            if ax == 'x': b.box(a0, c, 0.06, a1, c + 0.02, zd - 0.05, XW['cv'])
            else: b.box(c, a0, 0.06, c + 0.02, a1, zd - 0.05, XW['cv'])
    b.box(0.01, 0.01, zd - 0.05, W - 0.01, Dp - 0.01, zd, WD, 0.003)
    rails = (((P, 0.03), (W - P, 0.03)), ((P, Dp - 0.06), (W - P, Dp - 0.06)), ((0.03, P), (0.03, Dp - P)))
    for (ax0, ay0), (ax1, ay1) in rails:
        horiz = ay0 == ay1; L = (ax1 - ax0) if horiz else (ay1 - ay0); n = int(L / 0.1)
        if horiz:
            b.box(ax0, ay0, zd, ax1, ay0 + 0.03, zd + 0.04, WD); b.box(ax0, ay0 - 0.005, zd + 0.42, ax1, ay0 + 0.035, zd + 0.47, WD, 0.004)
        else:
            b.box(ax0, ay0, zd, ax0 + 0.03, ay1, zd + 0.04, WD); b.box(ax0 - 0.005, ay0, zd + 0.42, ax0 + 0.035, ay1, zd + 0.47, WD, 0.004)
        for k in range(n):
            t = (k + 0.5) / n; bx_ = ax0 + (ax1 - ax0) * t + (0 if horiz else 0.015); by_ = ay0 + (ay1 - ay0) * t + (0.015 if horiz else 0)
            b.lathe(bx_, by_, zd + 0.04, [(0.0, 0), (0.014, 0), (0.014, 0.03), (0.022, 0.08), (0.012, 0.14), (0.02, 0.22), (0.012, 0.3), (0.014, 0.35), (0.014, 0.38), (0.0, 0.38)], WD, 8)
    return b.mesh('Tapchan_v82')
@cached
def a_tapchan_soft(W=2.0, Dp=2.2):
    """kurpacha mattresses (wine velvet) on 3 sides, kilim (palas) rug in the middle, adras + suzani pillows, ikat bolsters;
    local frame as a_tapchan2, z 0 = deck top"""
    b = MB(); V = X['velvet_wine']
    b.box(0.07, 0.125, 0, 0.6, Dp - 0.125, 0.1, V, 0.03); b.box(0.6, 0.08, 0, W - 0.125, 0.6, 0.1, V, 0.03); b.box(0.6, Dp - 0.6, 0, W - 0.125, Dp - 0.1, 0.1, V, 0.03)   # clear of the corner posts
    b.picture_box(0.6, 0.6, 0, W - 0.125, Dp - 0.6, 0.006, X['carpet4'], '+z')
    for (x0, y0, x1, y1), mm in (((0.07, 0.5, 0.21, 0.94), m['ikat']), ((0.07, 1.26, 0.21, 1.7), m['suzani']), ((0.7, 0.08, 1.14, 0.22), m['suzani']),
                                 ((1.3, 0.08, 1.74, 0.22), m['ikat']), ((0.7, Dp - 0.24, 1.14, Dp - 0.1), m['ikat']), ((1.3, Dp - 0.24, 1.74, Dp - 0.1), m['suzani'])):
        b.box(x0, y0, 0.1, x1, y1, 0.48, mm, 0.05)
    for yy in (0.24, Dp - 0.26): b.rod((0.12, yy - 0.0, 0.19), (0.52, yy, 0.19), 0.09, m['ikat'], 14)
    return b.mesh('Tapchan_soft')
@cached
def a_lowtable2(L=1.0, Wt=0.66, H=0.32):
    """dastarkhan table per the reference: plain walnut top with a moulded edge, turned legs, plain apron; origin = floor centre"""
    b = MB(); WD = XW['wd']
    b.box(-L / 2, -Wt / 2, H - 0.035, L / 2, Wt / 2, H, WD, 0.006)
    b.box(-L / 2 + 0.06, -Wt / 2 + 0.06, H - 0.1, L / 2 - 0.06, Wt / 2 - 0.06, H - 0.035, WD, 0.003)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.lathe(sx * (L / 2 - 0.08), sy * (Wt / 2 - 0.08), 0, [(0.0, 0), (0.022, 0), (0.016, 0.03), (0.026, 0.08), (0.018, 0.14), (0.03, 0.2), (0.024, H - 0.1), (0.03, H - 0.1), (0.03, H - 0.035), (0.0, H - 0.035)], WD, 12)
    return b.mesh(f'Lowtable2_{int(L * 100)}')
for y0 in D['tap']:
    _rm('tapchan', 'kurpacha', 'Tapchan_railing', 'Tapchan_bolster', 'Tapchan_lowtable', 'Tapchan_dastarkhan')
    inst(a_tapchan2(), 'Tapchan_v82', (2.55, y0, TER), 0, 'Tapchans_tent')
    inst(a_tapchan_soft(), 'Tapchan_soft', (2.55, y0, TER + 0.45), 0, 'Tapchans_tent')
    inst(a_lowtable2(), 'Tapchan_lowtable', (2.55 + 1.3, y0 + 1.1, TER + 0.456), 0, 'Tapchans_tent')
    mb = MB(); zt_ = 0.32
    _lagan_plov(mb, -0.2, 0.0, zt_); _non(mb, 0.15, 0.17, zt_, 0.085); _tray(mb, 0.27, -0.12, zt_, 0.12); _choynak(mb, 0.25, -0.12, zt_ + 0.004, 0.85)
    for px, py in ((-0.38, 0.22), (-0.38, -0.22), (0.05, -0.24)): _piala2(mb, px, py, zt_)
    inst(mb.mesh('Tapchan_set_v82'), 'Tapchan_tableset', (2.55 + 1.3, y0 + 1.1, TER + 0.456), 0, 'Tapchans_tent')

# =============== 6. TENTS: majlis floor seating + octagonal inlaid tables (moodboard) ===============
@cached
def a_majlis(L, Dp):
    """majlis seat L (x) x Dp (y), back at y = 0, sitter faces +y: striped plinth, kilim seat mattress, kilim back cushions,
    end arm cushions; origin = back-left floor corner (same frame as a_banquette)"""
    b = MB(); K = X82['majlis']
    b.box(0, 0, 0, L, Dp, 0.14, X['tent'], 0.006)
    b.box(0.005, 0.005, 0.14, L - 0.005, Dp - 0.005, 0.3, K, 0.03)
    n = max(1, int(round((L - 0.04) / 0.62))); w = (L - 0.04) / n
    for k in range(n): b.box(0.02 + k * w + 0.01, 0.01, 0.3, 0.02 + (k + 1) * w - 0.01, 0.2, 0.78, K, 0.05)
    for k in range(n): b.box(0.02 + k * w + 0.12, 0.2, 0.3, 0.02 + (k + 1) * w - 0.12, 0.33, 0.62, X['carpet4'] if False else m['ikat'], 0.05)
    return b.mesh(f'Majlis_{int(L * 1000)}x{int(Dp * 1000)}')
@cached
def a_octatable(R=0.33, H=0.45):
    """octagonal Damascene table: inlaid octagon top, 8 side panels each with a pointed-arch opening, brass edge; origin floor centre"""
    b = MB(); WD = XW['wd']; oc = [(R * math.cos(math.pi / 8 + k * math.pi / 4), R * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    fs = b.extrude(oc, H - 0.03, H, X82['inlay'])
    for f in fs:
        if f.normal.z > 0.9:
            for lp in f.loops: lp[b.uv].uv = (0.5 + lp.vert.co.x / (2 * R), 0.5 + lp.vert.co.y / (2 * R))
            b.fixed.add(f)
    b.ring(0, 0, H - 0.008, [(R * 0.985, 0), (R * 1.01, 0), (R * 1.01, 0.008), (R * 0.985, 0.008)], m['brass'], 8)
    ap = R * math.cos(math.pi / 8) * 0.9; side = 2 * R * 0.9 * math.sin(math.pi / 8)
    for k in range(8):
        a = k * math.pi / 4; pl = arch_apron(-side / 2, 0.0, side / 2, H - 0.03, 0.22, 0.3)
        sfs = []
        for poly in pl:
            sfs += b.extrude(list(poly.exterior.coords)[:-1], ap - 0.022, ap, WD, 'xz')
        for v in {v for f in sfs for v in f.verts}:
            x_, y_ = v.co.x, v.co.y; v.co.x, v.co.y = x_ * math.cos(a + math.pi / 2) - y_ * math.sin(a + math.pi / 2), x_ * math.sin(a + math.pi / 2) + y_ * math.cos(a + math.pi / 2)
    return b.mesh('Octa_table')
for o_ in [o for o in bpy.data.objects if '_banquette_' in o.name and o.name.startswith('Tent')]:
    me_ = o_.data.name; L_, D_ = [int(v) / 1000 for v in me_.split('_')[1].split('x')]
    loc_, rz_ = tuple(o_.location), o_.rotation_euler.z; nm_ = o_.name; bpy.data.objects.remove(o_)
    inst(a_majlis(L_, D_), nm_.replace('banquette', 'majlis'), loc_, rz_, 'Tapchans_tent')
for o_ in [o for o in bpy.data.objects if o.name.startswith('otable')]:
    lo, hi = _bb(o_); cx_, cy_ = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2; bpy.data.objects.remove(o_)
    inst(a_octatable(), 'Tent_octatable', (cx_, cy_, TER + 0.015), 0, 'Tapchans_tent')      # on the tent rug; top +0.465 = the tray

# =============== 7. BOOTH PORTALS: tiled post faces, muqarnas capitals, zardevor valance, tassel tie-backs ===============
@cached
def a_booth_trim():
    """add-on for a_booth_open (same local frame: portal at x = 0, y 0..2.0): majolica panels on the post fronts, stepped
    walnut capitals, an embroidered band (zardevor top border) on the head fascia -- nothing lowers the 2.12 m arch head"""
    b = MB(); Wd = 2.0
    for y0_, y1_ in ((0.0, 0.22), (Wd - 0.22, Wd)):
        b.box(-0.075, y0_ + 0.04, 0.12, -0.07, y1_ - 0.04, 1.35, X['majcobalt'])
        for dz, dd in ((1.66, 0.006), (1.7, 0.012), (1.74, 0.018)): b.box(-0.07 - dd, y0_, dz, -0.07, y1_, dz + 0.04, XW['wd'], 0.002)
    fs = b.box(-0.0935, 0.0, 2.11, -0.09, Wd, 2.23, X['zardevor'])                  # embroidered band on the brass head fascia
    for f in fs:
        if f.normal.x < -0.9:
            for lp in f.loops: c = lp.vert.co; lp[b.uv].uv = (c.y / 0.8, 0.78 + 0.22 * (c.z - 2.11) / 0.12)
            b.fixed.add(f)
    return b.mesh('Booth_trim')
for k_, (y0_, y1_, xw_, xe_, th_) in enumerate(D['booths']):
    inst(a_booth_trim(), f'Booth{k_ + 1}_trim', (xw_, y0_, TER), 0, 'Booths')
print('rev 8.2 detail ok')
