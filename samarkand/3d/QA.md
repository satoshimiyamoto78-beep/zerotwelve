# 3D model quality (R12, clean geometry)

Audit tool: `scripts/qa.py`. It runs on the .blend. Each mesh datablock is checked once; instances share it.

| Check | Before (detail pass 1) | Now |
|---|---|---|
| Objects / mesh datablocks | 469 / 469 (zones merged into big batches) | 614 / 398 (each piece is its own object; repeated pieces are linked instances) |
| Clean meshes (all checks 0) | 433 of 469 | **398 of 398** |
| Open (boundary) edges | 28 280 | **0** |
| Non-manifold edges | 0 | **0** |
| Inside-out shells | 645 | **0** |
| Coincident vertices within a shell | 12 877 | **0** |
| Zero-area faces / zero-length edges | 31 / 14 222 | **0 / 0** |
| Objects penetrating each other (> 2 mm) | 130 | **0** |
| Standing objects not resting on anything (> 2 mm gap) | 45 | **0** |
| Unapplied rotation / scale | 0 | 0 (only Z rotation on instances; rods scaled along Z) |

## Modelling rules (`scripts/kit.py`, `scripts/assets_r12.py`)
- **Closed shells.** Every part is a closed, outward-facing solid: prisms, solids of revolution with real poles, capped rods, and cloth or carpets made as 6–12 mm solids.
- **Flush joints.** Parts of an asset meet on shared planes and never overlap:
  - chair: legs, aprons, notched seat board, cushion, back rails, carved panel, crest;
  - booth: posts and spandrels, curtain rod running from partition face to partition face;
  - rotunda: slats, rings, shelves.
- **Chamfers.** Wood and metal get 2–4 mm; cushions get softer bevels.
- **UVs.** Box UV at real texel density, or a 0..1 picture UV for carpets and epoch panels. The textures export to GLB as JPEG.
- **Origins.** At the base centre for furniture; at the plan corner for booths and tents. Real-world scale throughout.
- **Floors.** Inlays (girih alley, kids rubber, mangal slate, star mosaic, aryk channel) are cut out of the slab and sit flush. The aryk is a real channel below floor level; the hauz rim is a ring around the water.
- **Rests on its support.**
  - The bridge rests on the aryk edges; trays, dastarkhan and tableware rest on their tables.
  - Sofa cushions rest on the sofas.
  - Lanterns hang on rods that reach the roof panel, the balcony slab or the booth cap.
- **Assets in the library:** chair, module tables 2p/4p, tableware sets, lanterns, cushions, bolster, booth module ×8 themes, stepped partitions, majlis tent, tapchan railing, corridor arch and niche, khum and jars, Bukhara rotunda, vitrine, Khiva gate, flying carpets, tandoor, kazan, firewood wall, hood, heat lamp.

Asset sheet (materials + clay/wireframe): `renders/asset-sheet-wireframe.jpg`.
