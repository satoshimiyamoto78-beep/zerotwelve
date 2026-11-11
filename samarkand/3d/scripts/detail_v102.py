"""rev. 10.2 (owner: 'floor sockets where it is convenient'): power for guests' phones / laptops
  * dining tables: a flush brass floor box 130 x 130 (2 x universal socket + 2 x USB-C, hinged lid, 3 mm rim) under every table centre,
    so a cable never runs more than ~0.8 m to any seat and never across a walkway
  * aivan bays: floor box by the wall end of every table; majlis + tents: floor box beside the low tables
  * booths: wall socket + USB on the parapet inside face, just under table height
  Circuits: 16 A RCD-protected, one radial per zone (dining W / dining E / aivan / booths / majlis+tents), boxes IP44 (floor washing)."""
SOCK = mat('socket_insert', (0.03, 0.03, 0.03), rough=0.4); BRASS_ = m['brass']
@cached
def a_floorbox():
    # rev 12.0 (owner: 'I cannot see the sockets'): pop-up floor box 180 x 180 — brass frame 8 mm proud, lid hinged open, 2 sockets + 2 USB
    b = MB(); b.box(-0.09, -0.09, 0.0, 0.09, 0.09, 0.008, BRASS_, 0.002)
    b.box(-0.075, -0.075, 0.008, 0.075, 0.075, 0.0095, SOCK)
    for dx in (-0.035, 0.035): b.cyl(dx, -0.015, 0.0095, 0.0115, 0.022, BRASS_, 20)
    for dx in (-0.02, 0.02): b.box(dx - 0.008, 0.04, 0.0095, dx + 0.008, 0.047, 0.011, BRASS_)
    b.obox(0.0, 0.098, 0.008, 0.012, 0.18, 0.012, 0.0, BRASS_)                                       # hinge
    b.box(-0.085, 0.092, 0.012, 0.085, 0.1, 0.17, BRASS_, 0.002)                                     # lid, standing open
    return b.mesh('Floor_box_2S2U')
@cached
def a_wallsocket():
    b = MB(); b.box(-0.004, -0.08, -0.04, 0.0, 0.08, 0.04, BRASS_, 0.002)
    for dy in (-0.035, 0.035): b.box(-0.0055, dy - 0.025, -0.025, -0.004, dy + 0.025, 0.025, SOCK)
    return b.mesh('Wall_socket_2S2U')
ns = 0
for o_ in [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(('Table_', 'Aivan_table_', 'Majlis_table', 'Tent_octatable'))]:
    lo_, hi_ = _bb(o_); cx, cy, z = (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2, lo_[2]
    if o_.name.startswith('Aivan_table_'): cx = lo_[0] - 0.02
    elif o_.name.startswith('Majlis_table'): cx = hi_[0] + 0.18
    elif o_.name.startswith('Tent_octatable'):
        if o_.name.endswith(('.001', '.003')): continue
        cx = lo_[0] - 0.14
    rz_ = 0.0
    if o_.name.startswith('Table_'):                                                                  # at the table's end, beside the leg — visible, out of the aisle
        if hi_[0] - lo_[0] >= hi_[1] - lo_[1]: cx = lo_[0] + 0.13; rz_ = math.pi / 2
        else: cy = lo_[1] + 0.13
    ns += 1; inst(a_floorbox(), f'Floor_socket_{ns:02d}', (cx, cy, z), rz_, 'Lights')
for i, (y0, y1, x0, x1, key) in enumerate(D['booths']):
    ns += 1; inst(a_wallsocket(), f'Booth{i + 1}_socket', (x1 - 0.18, (y0 + y1) / 2, TER + 0.15 + 0.45), 0.0, 'Booths')
print('rev 10.2 sockets', ns)
