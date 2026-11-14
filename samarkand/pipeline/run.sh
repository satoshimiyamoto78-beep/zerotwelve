#!/bin/bash
# Build the Samarkand 3D model (mode 0 = no render) and run QA. Run from samarkand/pipeline.
# Needs: python3.13 venv with bpy 5.2.x, shapely 2.x, numpy, pillow  ->  python3 -m venv bvenv && bvenv/bin/pip install bpy==5.2.3 shapely numpy pillow
set -e; cd "$(dirname "$0")"; mkdir -p out
bvenv/bin/python r3d/base3d_r12.py r12/samarkand-3d-data-R12.json out 0 > out/build.log 2>&1 || true
grep -v "WARNING: Cannot register" out/build.log | grep -A8 "Traceback" | tail -8 || true
bvenv/bin/python r3d/qa.py out/samarkand-base3d-R12.blend out/qa.json Furniture,Booths,Aivan,Tapchans_tent,Lights,Corridor,Mangal,Bukhara_dome,North_gate,Fountain,Carpet_ceiling,Kids,Floors,Columns,Street_facade,Bar,People,Photo_lounge,Planting,Trees,Pergola_existing 2>&1 | tail -1
python3 -c "import json; r=json.load(open('out/qa.json')); print('penetrations', r['n_penetrations'], r['penetrations'][:20]); print('floating', r['n_floating'], r['floating'][:20])"
# viewer data:  python3 tools/glb2viewer.py out/samarkand-base3d-R12.glb viewer/m   (then publish viewer/index.html + viewer/m/* in <64 MB parts)
