"""rev. 10.6 (owner marked 4 spots on the plan: 'seating 155 must be inside'): new tables in the owner's spots, same carved family
(carved table with zellige inlay, carved chairs with the sewn cushions, fitted table set); one more bar stool at the free counter end.
 m1 between the south rows (y 23.6..26.0): 4-top turned 90 deg -> the aisle to the booths stays 0.6+
 m2 east of the dome 4-top: 2-top (a 4-top would close Booth 1's front)
 m3 between the bar stools and the tree planter: 4-top (0.56 behind the stools, chairs clear of the planter ring)
 m4 between the north row and the tree planter: 4-top turned 90 deg"""
_ch = {k: next(o.data for o in bpy.data.objects if o.name.startswith('Chair_') and o.data.name.startswith(f'Carvedchair2_{k}')) for k in ('k1', 'k2')}
_ts = {n: next((o.data for o in bpy.data.objects if o.name.startswith('Tableset_') and o.data.name.startswith(f'Tableset2_{n}p')), None) for n in (1, 2)}
_ts[1] = next((o.data for o in bpy.data.objects if o.name.startswith('Tableset_') and '2p' in o.data.name), None)
_ts[2] = next((o.data for o in bpy.data.objects if o.name.startswith('Tableset_') and '4p' in o.data.name), None)
NEW = [('m1', 6.0, 24.8, 2, True), ('m3', 4.6, 13.25, 1, False), ('m4', 5.95, 10.45, 2, True)]
_rm('Table_m', 'Tableset_m', 'Chair_m')
nseat = 0
for tag, cx, cy, n, rot in NEW:
    rz = math.pi / 2 if rot else 0.0
    inst(a_carvedtable(n), f'Table_{tag}', (cx, cy, TER), rz, 'Furniture')
    ts = _ts[n]
    if ts:
        inst(ts, f'Tableset_{tag}', (cx, cy, TER), rz, 'Furniture')
    offs = [(-0.35 * (n - 1) + 0.7 * i, s * 0.66) for i in range(n) for s in (-1, 1)]
    for k, (ox, oy) in enumerate(offs):
        if rot: ox, oy = -oy, ox                                              # turned table: chairs on the long x sides
        fx, fy = ((-math.copysign(1, ox), 0) if rot else (0, -math.copysign(1, oy)))   # chair faces the table side square-on
        a = math.atan2(fy, fx) - math.pi / 2
        inst(_ch['k1' if k % 3 else 'k2'], f'Chair_{tag}{k}', (cx + ox, cy + oy, TER), a, 'Furniture'); nseat += 1
st = bpy.data.objects.get('Barstool')
if st:
    o = st.copy(); o.name = 'Barstool_end'; o.location.y = st.location.y - 0.62; (st.users_collection[0]).objects.link(o); nseat += 1
print('rev 10.6 seats added', nseat)
# owner: 'the tree stays under the roof, just shorter' -> chinar (trunk + crown) scaled to 89 % height about the floor
_tr = bpy.data.objects.get('Chinar_trained_1'); Z0_ = _bb(_tr)[0][2] if _tr else TER          # trunk foot in the soil stays put
for n_ in ('Chinar_crown_1', 'Chinar_trained_1'):
    o_ = bpy.data.objects.get(n_)
    if o_:
        f_ = (2.55 - Z0_) / (2.92 - Z0_); o_.location.z = Z0_ + (o_.location.z - Z0_) * f_; o_.scale.z *= f_
        bpy.context.view_layer.update()
        if n_ == 'Chinar_trained_1': o_.location.z += Z0_ - _bb(o_)[0][2]
print('rev 10.6 chinar shortened')
