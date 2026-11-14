"""rev. 11.9 (owner): 'on the carved wooden screen on the street write Samarkand too — the logo, in a beautiful oriental script'.
A walnut name board (1.90 x 0.60, 30 thick) with brass edge strips on the street face of the jali screen (sarch, y 25.95..27.95),
'Samarkand' in raised brushed-brass letters (Aladin, an oriental display face, 420 mm body), an 8-point brass star at each end.
(The aryk removal + the two 2-top tables are data edits in base3d_r12.py.)"""
import math as _m9
_FONT_KEEP = FONT_; FONT_ = os.path.join(HERE, 'Aladin-Regular.ttf')
_BRL = mat('brass_letters', (0.83, 0.62, 0.3), rough=0.25, metal=1.0)
def _fx(y): return 10.6848 - 0.0985693 * (y - 25.95)                    # street face of the screen
_dir = Vector((-0.0985693, 1.0, 0.0)).normalized(); _nrm = Vector((_dir.y, -_dir.x, 0.0))   # reading dir / outward normal (+x)
YC9, Z0, Z1 = 26.95, TER + 1.62, TER + 2.22; L9 = 1.90
_ang = _m9.atan2(_dir.y, _dir.x); _c = Vector((_fx(YC9), YC9, 0.0))
b = MB()
c_ = _c + _nrm * 0.015; b.obox(c_.x, c_.y, Z0, Z1, L9, 0.03, _ang, XW['wd'], 0.004)
for z0_, z1_ in ((Z0 - 0.005, Z0 + 0.012), (Z1 - 0.012, Z1 + 0.005)):
    c_ = _c + _nrm * 0.02; b.obox(c_.x, c_.y, z0_, z1_, L9 + 0.01, 0.042, _ang, m['brass'])
for s_ in (-1, 1):                                                          # 8-point stars
    c_ = _c + _dir * (s_ * 0.875) + _nrm * 0.036
    for a_ in (0.0, _m9.pi / 4):
        p0 = c_; zc = (Z0 + Z1) / 2; h = 0.045
        b.obox(p0.x, p0.y, zc - h, zc + h, 0.09, 0.008, _ang, _BRL) if a_ == 0 else None
    # the rotated square as a diamond made of a rod cross (visual 8-point star)
    for k in range(4):
        th = k * _m9.pi / 4; dv = _dir * _m9.cos(th) * 0.065; dz = _m9.sin(th) * 0.065; zc = (Z0 + Z1) / 2
        b.rod((c_.x - dv.x, c_.y - dv.y, zc - dz), (c_.x + dv.x, c_.y + dv.y, zc + dz), 0.012, _BRL, 4)
inst(b.mesh('Street_nameboard'), 'Street_nameboard', (0, 0, 0), 0, 'Street_facade')
o_ = channel_text('Samarkand', 0.42, 0.018, _BRL, tuple(_c + _nrm * 0.03 + Vector((0, 0, TER + 1.775))), tuple(_dir), 'Logo_Samarkand_street', 'Street_facade')
FONT_ = _FONT_KEEP
print('rev 11.9: street name board placed')
