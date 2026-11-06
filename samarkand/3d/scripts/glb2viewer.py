"""Split a GLB for the artifact viewer: textures -> m/texNN.<ext>, geometry buffer (compacted, no images) -> base64 text parts
m/geoN.txt (< 12 MB each), glTF JSON -> m/model.json with extras.geo_parts.  Usage: python3 glb2viewer.py IN.glb OUTDIR"""
import sys, os, json, struct, base64
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out, f))
b = open(src, 'rb').read(); assert b[:4] == b'glTF'
jl = struct.unpack('<I', b[12:16])[0]; g = json.loads(b[20:20 + jl]); off = 20 + jl
bl_ = struct.unpack('<I', b[off:off + 4])[0]; BIN = b[off + 8:off + 8 + bl_]
img_views = set()
for i, im in enumerate(g.get('images', [])):
    v = g['bufferViews'][im['bufferView']]; data = BIN[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]
    ext = 'png' if im.get('mimeType') == 'image/png' else 'jpg'; name = f'tex{i:02d}.{ext}'
    open(os.path.join(out, name), 'wb').write(data); img_views.add(im.pop('bufferView')); im.pop('mimeType', None); im['uri'] = name
new, remap = bytearray(), {}
for i, v in enumerate(g['bufferViews']):
    if i in img_views: continue
    while len(new) % 4: new.append(0)
    o = v.get('byteOffset', 0); d = BIN[o:o + v['byteLength']]; v2 = dict(v); v2['byteOffset'] = len(new); new += d; remap[i] = (len(remap), v2)
g['bufferViews'] = [v for _, (k, v) in sorted(remap.items())]
idx = {i: k for i, (k, _) in remap.items()}
for a in g.get('accessors', []):
    if 'bufferView' in a: a['bufferView'] = idx[a['bufferView']]
g['buffers'] = [{'byteLength': len(new)}]
s = base64.b64encode(bytes(new)).decode(); n = 12 * 1024 * 1024 // 4 * 4; parts = []
for k in range(0, len(s), n):
    nm = f'geo{len(parts) + 1}.txt'; open(os.path.join(out, nm), 'w').write(s[k:k + n]); parts.append(nm)
g.setdefault('extras', {})['geo_parts'] = parts
json.dump(g, open(os.path.join(out, 'model.json'), 'w'))
print('parts', parts, 'textures', len(g.get('images', [])), 'geo MB', round(len(new) / 1e6, 1))
