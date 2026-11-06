"""rev. 11.1 (owner: 'the marble floor is a photo — real tiles'): the terrace floor laid piece by piece in the same design:
white marble slabs 500 x 500 on the diagonal (each its own stone, veins only, own rotation), 3 mm joints; 90 mm bands between them:
cobalt edge strips, white middle strip with inlaid diamonds (black / honey / green / brown); at every crossing a cobalt square with a
honey diamond. The screed under the pieces is pulled down 6 mm; anything standing through the floor gets the pieces cut around it."""
MARB = uvmat('marble_slab_uv', 'marble_slab.png', rough=0.18, sheen=0.0)
GROUT = mat('grout_grey', (0.55, 0.55, 0.53), rough=0.9)
FC = {'cob': mat('fl_cobalt', (0.03, 0.08, 0.38), rough=0.2, coat=0.6), 'white': mat('fl_white', (0.9, 0.89, 0.86), rough=0.25),
      'honey': mat('fl_honey', (0.72, 0.5, 0.2), rough=0.25), 'black': mat('fl_black', (0.05, 0.05, 0.05), rough=0.25),
      'green': mat('fl_green', (0.1, 0.35, 0.22), rough=0.25), 'brown': mat('fl_brown', (0.35, 0.2, 0.1), rough=0.25)}
A_, W_ = 0.50, 0.09; P_ = A_ + W_; CS = 0.16 * W_; H_ = (W_ - 2 * CS) / 2; G_ = 0.0015
R45 = lambda g: _aff.rotate(g, 45, origin=(0, 0), use_radians=False)
SEQ = ['black', 'honey', 'green', 'brown']
def floor_gen(u0, v0, u1, v1):
    """pieces in world x, y; grid frame s = (x + y)/sqrt2, t = (y - x)/sqrt2 -> generated in (s, t) then rotated 45 deg"""
    cs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    S = [(x + y) / math.sqrt(2) for x, y in cs]; T = [(y - x) / math.sqrt(2) for x, y in cs]
    for i in range(math.floor(min(S) / P_) - 1, math.ceil(max(S) / P_) + 1):
        for j in range(math.floor(min(T) / P_) - 1, math.ceil(max(T) / P_) + 1):
            s0, t0 = i * P_, j * P_
            yield R45(_box(s0 + G_, t0 + G_, s0 + A_ - G_, t0 + A_ - G_)), MARB                       # slab
            for d in (0, 1):                                                                            # band along t (d=0) / along s (d=1)
                def bx(a0, a1, r0, r1):
                    return R45(_box(s0 + A_ + r0, t0 + a0, s0 + A_ + r1, t0 + a1)) if d == 0 else R45(_box(s0 + a0, t0 + A_ + r0, s0 + a1, t0 + A_ + r1))
                yield bx(G_, A_ - G_, G_, CS - G_), FC['cob']
                yield bx(G_, A_ - G_, W_ - CS + G_, W_ - G_), FC['cob']
                dias = []
                for k in range(int(A_ / (2 * H_))):
                    q = (k + 0.5) * 2 * H_; r = CS + H_; hh = H_ - G_
                    dl = _P([(q - hh, r), (q, r - hh), (q + hh, r), (q, r + hh)]) if d == 1 else _P([(r - hh, q), (r, q - hh), (r + hh, q), (r, q + hh)])
                    dl = _aff.translate(dl, s0 if d == 1 else s0 + A_, t0 + A_ if d == 1 else t0)
                    if k % 2 == 0: dias.append(dl); yield R45(dl), FC[SEQ[(k // 2 + i + j) % 4]]
                wst = bx(G_, A_ - G_, CS + G_, W_ - CS - G_)
                if dias: wst = wst.difference(R45(_uu9([dd.buffer(G_, join_style=2) for dd in dias])))
                yield wst, FC['white']
            c = (s0 + A_ + W_ / 2, t0 + A_ + W_ / 2); hd = W_ * 0.3
            dc = _P([(c[0] - hd, c[1]), (c[0], c[1] - hd), (c[0] + hd, c[1]), (c[0], c[1] + hd)])
            yield R45(_box(s0 + A_ + G_, t0 + A_ + G_, s0 + P_ - G_, t0 + P_ - G_).difference(dc.buffer(G_, join_style=2))), FC['cob']   # crossing
            yield R45(dc), FC['honey']
PAT.clear(); PAT['marblegrid_t'] = (GROUT, 0.0018, floor_gen, MARB, 0.3)
HORIZ.clear(); HORIZ.add('marblegrid_t'); SIDES.clear()
UVS = 0.55; CULL_MINZ = TER + 0.001
realize_all(skip=('Booth',)); CULL_MINZ = None
print('rev 11.1 floor pieces: objects', nobj, 'culled', ncull)
# zellige carpets (under the dome and the tree) + the alley runner: real 8-point star tiles on a white glazed field, cobalt border
def zel_gen(P, R, cols, border):
    st = _stars(P, R, cols)
    def gen(u0, v0, u1, v1):
        yield from st(u0, v0, u1, v1)
    return gen
PAT.clear()
PAT['zcarpet_uv'] = (TILE[1], 0.003, _stars(0.2, 0.08, [TILE[0], TILE[2], TILE[3], TILE[0]]), TILE[1], 0.2)
PAT['alleyrun_uv'] = (TILE[1], 0.003, _stars(0.16, 0.065, [TILE[0], TILE[2]]), TILE[1], 0.15)
HORIZ.clear(); HORIZ.update(PAT.keys()); UVS = 1.0; CULL_MINZ = TER + 0.02
realize_all(skip=('Booth',)); CULL_MINZ = None
print('rev 11.1 zellige carpets real: objects', nobj, 'culled', ncull)
