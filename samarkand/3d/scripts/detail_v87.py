"""rev. 8.7 — central dome: gilded alem finial on the lantern cap (owner: 'nothing on the crown'); the dome itself is Ø5.0 now
(layout: clear of the aivan arcade and the booth fronts, centred on the 4-top axis x 6.0)"""
_rm('dome_finial')
GILT = mat('gilt_alem', (0.86, 0.63, 0.24), rough=0.22, metal=1.0)
for o_ in [o for o in bpy.data.objects if o.name.startswith('dome_lantern_cap_')]:
    lo_, hi_ = _bb(o_); cx_, cy_ = (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2
    b = MB()
    b.lathe(0, 0, 0, [(0.0, 0.0), (0.075, 0.0), (0.075, 0.06), (0.05, 0.08), (0.06, 0.1), (0.04, 0.12), (0.035, 0.13)] +
            [(0.035 + 0.11 * math.sin(math.pi * k / 12), 0.13 + 0.22 * k / 12) for k in range(13)] +               # ball 1  (Ø 0.29)
            [(0.03, 0.37), (0.045, 0.39), (0.03, 0.41)] +
            [(0.03 + 0.08 * math.sin(math.pi * k / 12), 0.41 + 0.16 * k / 12) for k in range(13)] +                # ball 2  (Ø 0.22)
            [(0.025, 0.59), (0.04, 0.61), (0.025, 0.63)] +
            [(0.025 + 0.06 * math.sin(math.pi * min(1.0, k / 8)) * (1.0 if k <= 8 else 0.0), 0.63 + 0.02 * k) for k in range(1, 9)] +   # onion
            [(0.022, 0.80), (0.012, 0.9), (0.006, 1.0), (0.0, 1.06)], GILT, 32)                                       # spire
    inst(b.mesh('Dome_alem'), f'Dome_alem_{o_.name[-1]}', (cx_, cy_, hi_[2]), 0, 'Domes')
print('rev 8.7 dome alem ok')
