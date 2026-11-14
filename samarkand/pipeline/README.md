# Samarkand 3D build pipeline (rev R12-v11.7)

Everything needed to rebuild the model, run QA and refresh the working viewer.

* `r3d/base3d_r12.py` — entry point (Blender `bpy`). Reads `r12/samarkand-3d-data-R12.json` (booth layout is overridden near the
  top: 7 booths, rev 11.4). It execs `detail_r12.py` → … → `detail_v82.py`, whose tail execs the revision modules in order
  (`detail_v85 … v117`, `struct_v92`). **Add a new revision by appending an `exec(...)` line to the end of `r3d/detail_v82.py`.**
* Key helpers available to every module (shared namespace): `MB` mesh builder (`box, extrude, lathe, ring, rod, cyl`), `inst`,
  `_rm`, `_bb`, `mat`, `XW`, `TILE`, `GLZ`, `BRK`, `BUFF`, `MORTAR`, `rugmat`, `a_settee`, `a_trestle`, `pillow` (v105),
  `realize_all` + `PAT/HORIZ/SIDES/CULL_MINZ/HMINZ` (v107: turns photo-textured faces into real brick/tile/carving pieces),
  `mini_cascade` (v113: small dome-style chandelier), `_free` (v113: collision probe).
* `r3d/qa.py` — QA: penetrations (2 mm inward offset) and floating objects. Target is always **0 / 0**.
* `r3d/place_cache.json` — plant placement cache (first build without it takes ~25 min, with it ~3–5 min).
* `tools/glb2viewer.py` — glb → viewer data (`viewer/m/geo*.txt`, `tex*`, `model.json`). `tools/close2.py`, `tools/top.py` — quick
  Cycles check renders (`bvenv/bin/python tools/close2.py '[["name","Object",[dx,dy,dz],dz_target]]'`).
* `viewer/index.html` — the working viewer page (published at the owner's working artifact; never publish to the frozen shared one).
* Textures: `r3d/tex2` (owner's carpet photos `rug_p01..19`, generated wood/marble grain), plant models in `r3d/plants`.

Run: `./run.sh` (see the venv line inside).
