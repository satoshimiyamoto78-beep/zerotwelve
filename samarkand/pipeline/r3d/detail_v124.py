"""rev. 12.1 (owner: 'make the entrance portal easy to build — simplify the model, bring it to ideal'; 'the bar counter must be laid
in brick like its wall'):
  PORTAL — one plain, buildable piece instead of the sheared one with a muqarnas vault and merlons:
    * plan square to the entrance axis: two pylons 700 x 1200 (each encases its steel roof column), clear opening as before, a flat
      lintel block over them up to the purlins; steel frame + brick / block infill, flat finishes only
    * pylons: stone plinth 550, then standard 150 x 150 glazed tiles laid as a diagonal cobalt / turquoise / white pattern inside a
      75 mm cobalt border — front, back and passage faces
    * opening: a flat pointed-arch tympanum (white, with a turquoise edge band) in the front plane; behind it a straight passage with
      a flat soffit — no vault
    * lintel: buff facing brick in running bond, brass letters 'Samarkand', white stone coping on top
  BAR COUNTER — front face laid in the same buff brick with glazed headers as the back wall, on the black kick, under the walnut top"""
import random as _r4
from shapely.geometry import Polygon as _P24, box as _B24
_r = _r4.Random(11)
_BUFF4 = [mat(f'brick_face_{k}', c, rough=0.85) for k, c in enumerate(((0.72, 0.56, 0.38), (0.66, 0.5, 0.34), (0.76, 0.61, 0.43)))]
_TQ = mat('glaze_turq_bar', (0.05, 0.5, 0.52), rough=0.12); _CB = mat('glaze_cob_bar', (0.03, 0.1, 0.42), rough=0.12)
_WH = mat('glaze_white_tile', (0.9, 0.9, 0.86), rough=0.15); _MO = mat('mortar_joint', (0.5, 0.46, 0.4), rough=0.95)
_STN = mat('cap_stone_white2', (0.9, 0.89, 0.86), rough=0.3)
# ---------------- bar counter front
b = MB(); F0 = TER; YA, YB = 8.10, 14.30; XF = 2.268; BL, BH, J = 0.23, 0.065, 0.01; row = 0; z = F0 + 0.105
while z + BH <= F0 + 1.005:
    off = (BL + J) / 2 if row % 2 else 0.0; y = YA - off; col = 0
    while y < YB:
        y0, y1 = max(y, YA), min(y + BL, YB)
        if y1 - y0 > 0.03:
            g = ((col * 2 + row) % 8 == 0 or (col * 2 - row) % 8 == 0) and row % 2 == 0
            b.box(XF, y0, z, XF + 0.012 + (0.004 if g else _r.uniform(-0.002, 0.002)), y1, z + BH, (_TQ if (row // 4) % 2 else _CB) if g else _BUFF4[_r.randrange(3)], 0.0015)
        y += BL + J; col += 1
    z += BH + J; row += 1
for (xa, xb_, ya, yb) in ((2.0, XF, YA - 0.012, YA),):                                                # south return of the counter
    zz = F0 + 0.105; r2 = 0
    while zz + BH <= F0 + 1.005:
        b.box(xa + (0.12 if r2 % 2 else 0.0), ya - 0.002, zz, xb_ + 0.012, yb, zz + BH, _BUFF4[_r.randrange(3)], 0.0015); zz += BH + J; r2 += 1
inst(b.mesh('Bar_counter_brick'), 'Bar_counter_brick', (0, 0, 0), 0, 'Bar')
# ---------------- portal
for o_ in [o for o in bpy.data.objects if o.name.startswith('Street_pishtaq')]: bpy.data.objects.remove(o_)
e0, e1 = D['ent']; SIDz = -1.17; PW = 0.70; X0p, X1p = 10.75, 11.95; ZTOP = 3.09; ZL = TER + 2.62          # lintel underside: 2.62 clear over the terrace floor
b = MB(); T = 0.15
def tiles(face, a0, a1, z0, z1, xpos, sgn):
    """150 tiles on a vertical face; face 'x': plane x = xpos, a = y;  face 'y': plane y = xpos, a = x; sgn = outward direction"""
    na = max(1, round((a1 - a0 - 0.15) / T)); nz = max(1, round((z1 - z0 - 0.15) / T)); ta = (a1 - a0 - 0.15) / na; tz = (z1 - z0 - 0.15) / nz
    def put_(aa, ab, za, zb, mm, th=0.012):
        if face == 'x': b.box(min(xpos, xpos + sgn * th), aa, za, max(xpos, xpos + sgn * th), ab, zb, mm, 0.001)
        else: b.box(aa, min(xpos, xpos + sgn * th), za, ab, max(xpos, xpos + sgn * th), zb, mm, 0.001)
    put_(a0, a1, z0, z0 + 0.075, _CB); put_(a0, a1, z1 - 0.075, z1, _CB); put_(a0, a0 + 0.075, z0 + 0.075, z1 - 0.075, _CB); put_(a1 - 0.075, a1, z0 + 0.075, z1 - 0.075, _CB)
    for i in range(na):
        for j in range(nz):
            k = (i + j) % 4; mm = _CB if k == 0 else (_TQ if k == 2 else _WH)
            put_(a0 + 0.075 + i * ta + 0.0015, a0 + 0.075 + (i + 1) * ta - 0.0015, z0 + 0.075 + j * tz + 0.0015, z0 + 0.075 + (j + 1) * tz - 0.0015, mm, 0.010)
for (ya, yb) in ((e0 - PW, e0), (e1, e1 + PW)):
    b.box(X0p - 0.02, ya - 0.02, SIDz, X1p + 0.02, yb + 0.02, SIDz + 0.55, _STN, 0.008)                    # stone plinth
    b.box(X0p, ya, SIDz + 0.55, X1p, yb, ZL, _MO)                                                          # pylon body (frame + infill)
    tiles('x', ya, yb, SIDz + 0.55, ZL, X1p, 1); tiles('x', ya, yb, TER + 0.02, ZL, X0p, -1)               # street face, hall face
    inner = yb if ya < e0 else ya
    tiles('y', X0p, X1p, TER + 0.55, ZL, inner, 1 if ya < e0 else -1)                                       # passage face
    outer = ya if ya < e0 else yb
    tiles('y', X0p, X1p, SIDz + 0.55, ZL, outer, -1 if ya < e0 else 1)                                      # outer side
# lintel block + brick face + coping
YL0, YL1 = e0 - PW, e1 + PW
b.box(X0p, YL0, ZL, X1p, YL1, ZTOP - 0.08, _MO)
for (xpos, sgn) in ((X1p, 1), (X0p, -1)):
    z = ZL + 0.005; row = 0
    while z + BH <= ZTOP - 0.085:
        off = (BL + J) / 2 if row % 2 else 0.0; y = YL0 - off
        while y < YL1:
            y0, y1 = max(y, YL0), min(y + BL, YL1)
            if y1 - y0 > 0.03: b.box(min(xpos, xpos + sgn * 0.012), y0, z, max(xpos, xpos + sgn * 0.012), y1, z + BH, _BUFF4[_r.randrange(3)], 0.0015)
            y += BL + J
        z += BH + J; row += 1
b.box(X0p - 0.04, YL0 - 0.04, ZTOP - 0.08, X1p + 0.04, YL1 + 0.04, ZTOP, _STN, 0.006)
b.box(X0p + 0.02, e0, ZL - 0.02, X1p - 0.02, e1, ZL, _WH)                                                   # flat soffit of the passage
# flat pointed-arch tympanum in the street plane
YC4 = (e0 + e1) / 2; WOP = e1 - e0; ZS4, ZA4 = TER + 1.65, ZL - 0.12
pts = arch_left(YC4, WOP, ZS4, ZA4, 18)
inn = _P24([(e0, ZS4 - 0.01)] + pts + [(2 * YC4 - u, z) for u, z in pts[::-1][1:]] + [(e1, ZS4 - 0.01)])
tym = _B24(e0, ZS4, e1, ZL).difference(inn)
band = inn.buffer(0.09, join_style=1).intersection(_B24(e0, ZS4, e1, ZL)).difference(inn)
for g in (getattr(tym.difference(band), 'geoms', None) or [tym.difference(band)]):
    if g.geom_type == 'Polygon' and g.area > 1e-4: ext_safe(b, g.simplify(0.001), X1p - 0.06, X1p, _WH, 'yz')
for g in (getattr(band, 'geoms', None) or [band]):
    if g.geom_type == 'Polygon' and g.area > 1e-4: ext_safe(b, g.simplify(0.001), X1p - 0.06, X1p + 0.012, _TQ, 'yz')
inst(b.mesh('Street_pishtaq'), 'Street_pishtaq', (0, 0, 0), 0, 'Street_facade')
_FK = FONT_; FONT_ = os.path.join(HERE, 'Aladin-Regular.ttf')
channel_text('Samarkand', 0.30, 0.016, mat('brass_letters', (0.83, 0.62, 0.3), rough=0.25, metal=1.0), (X1p + 0.012, YC4, (ZL + ZTOP - 0.08) / 2 - 0.09), (0, 1, 0), 'Logo_Samarkand_portal', 'Street_facade')
FONT_ = _FK
print('rev 12.1: portal rebuilt (plain), bar counter in brick')
