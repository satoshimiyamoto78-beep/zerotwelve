"""minimal Autodesk .3ds -> .obj/.mtl converter (meshes, UVs, per-face materials, diffuse colour + texture map name)
usage: python3 max3ds2obj.py IN.3ds OUT.obj"""
import struct, sys, os
data = open(sys.argv[1], 'rb').read(); out = sys.argv[2]
def cstr(p):
    e = data.index(b'\0', p); return data[p:e].decode('latin-1'), e + 1
objs, mats = [], {}
def walk(p, end, ctx):
    while p + 6 <= end:
        cid, ln = struct.unpack_from('<HI', data, p); body, nxt = p + 6, p + ln
        if ln < 6: break
        if cid in (0x4D4D, 0x3D3D): walk(body, nxt, ctx)
        elif cid == 0x4000:
            nm, q = cstr(body); o = dict(name=nm, v=[], f=[], uv=[], fm=[]); objs.append(o); walk(q, nxt, o)
        elif cid == 0x4100: walk(body, nxt, ctx)
        elif cid == 0x4110:
            n, = struct.unpack_from('<H', data, body); ctx['v'] = [struct.unpack_from('<3f', data, body + 2 + 12 * i) for i in range(n)]
        elif cid == 0x4140:
            n, = struct.unpack_from('<H', data, body); ctx['uv'] = [struct.unpack_from('<2f', data, body + 2 + 8 * i) for i in range(n)]
        elif cid == 0x4120:
            n, = struct.unpack_from('<H', data, body); ctx['f'] = [struct.unpack_from('<4H', data, body + 2 + 8 * i)[:3] for i in range(n)]
            walk(body + 2 + 8 * n, nxt, ctx)
        elif cid == 0x4130:
            nm, q = cstr(body); n, = struct.unpack_from('<H', data, q); ctx['fm'].append((nm, struct.unpack_from(f'<{n}H', data, q + 2)))
        elif cid == 0xAFFF:
            m = dict(name='', kd=(0.7, 0.7, 0.7), tex=None); walk(body, nxt, m); mats[m['name']] = m
        elif cid == 0xA000: ctx['name'], _ = cstr(body)
        elif cid == 0xA020: walk(body, nxt, ctx); ctx['kd'] = ctx.get('_col', ctx['kd'])
        elif cid == 0x0011: ctx['_col'] = tuple(c / 255 for c in data[body:body + 3])
        elif cid == 0x0010: ctx['_col'] = struct.unpack_from('<3f', data, body)
        elif cid == 0xA200: walk(body, nxt, ctx)
        elif cid == 0xA300: ctx['tex'], _ = cstr(body)
        p = nxt
walk(0, len(data), None)
base = os.path.splitext(out)[0]
with open(base + '.mtl', 'w') as f:
    for m in mats.values():
        f.write(f"newmtl {m['name'].replace(' ', '_')}\nKd {m['kd'][0]:.4f} {m['kd'][1]:.4f} {m['kd'][2]:.4f}\n")
        if m['tex']: f.write(f"map_Kd {m['tex']}\n")
with open(out, 'w') as f:
    f.write(f"mtllib {os.path.basename(base)}.mtl\n"); vo = 1
    for o in objs:
        if not o['v'] or not o['f']: continue
        f.write(f"o {o['name'].replace(' ', '_')}\n")
        for x, y, z in o['v']: f.write(f"v {x:.5f} {z:.5f} {-y:.5f}\n")          # 3ds Z-up -> obj Y-up
        has_uv = len(o['uv']) == len(o['v'])
        if has_uv:
            for u, v in o['uv']: f.write(f"vt {u:.5f} {v:.5f}\n")
        fmat = {}
        for nm, idx in o['fm']:
            for i in idx: fmat[i] = nm
        cur = None
        for i, (a, b, c) in enumerate(o['f']):
            mm = fmat.get(i)
            if mm != cur: f.write(f"usemtl {(mm or 'default').replace(' ', '_')}\n"); cur = mm
            if has_uv: f.write(f"f {a+vo}/{a+vo} {b+vo}/{b+vo} {c+vo}/{c+vo}\n")
            else: f.write(f"f {a+vo} {b+vo} {c+vo}\n")
        vo += len(o['v'])
print(os.path.basename(sys.argv[1]), 'objects', len(objs), 'verts', sum(len(o['v']) for o in objs), 'faces', sum(len(o['f']) for o in objs), 'mats', {k: v['tex'] for k, v in mats.items()})
