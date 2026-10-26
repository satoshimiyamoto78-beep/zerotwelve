# Samarkand terrace: 3D base model (R12, LOD 200; R9 kept for reference)

This model is built automatically from the floor plan: current R12 (`samarkand/site/tools/layout_r12.py` → `export3d_r12.py` → `scripts/base3d_r12.py`), earlier R9. When the plan changes, rebuild the model rather than editing it by hand.

## Files
| File | Purpose |
|---|---|
| `samarkand-base3d-R9.blend` | Blender 5.x source. Textures are packed into the file and the materials are procedural. Objects are grouped into collections. |
| `samarkand-base3d-R9.fbx` | For D5 Render, 3ds Max and SketchUp (via plugin). Units are metres, Y-up. |
| `samarkand-base3d-R9.obj` + `.mtl` | For SketchUp Pro (File → Import → OBJ, units: metres). |
| `samarkand-base3d-R9.glb` | Web, AR and quick preview. |
| `viewer.html` + `samarkand-base3d-R9-web.json` | Interactive viewer (online version: https://claude.ai/artifact/7NGDiBpaXwuSr9gytuvAtm). |
| `samarkand-3d-data-R9.json` | Plan geometry in metres (input for the builder). |
| `scripts/base3d.py`, `bl.py`, `bl2.py` | The builder. |

The FBX, OBJ and GLB exports use flat colours, one per material. In D5 or SketchUp, swap them for real materials: tile, wood, majolica, fabric.

## Coordinates and levels
- Origin: axis 6 × axis A' (south-east corner of the main hall). X points east toward the street, Y points north, units are metres.
- Hall and aivan ±0.000. Terrace −0.450. Sidewalk −1.170.
- Balcony slab soffit +3.850. The top of the roof skin is +3.750 at the façade, falling 5% to the street (about +3.16 at the edge).
- Open courts over the trees: south x 3.6–7.6 / y 10.4–15.0, north x 4.7–7.4 / y 25.8–29.0.

## Collections (layers)
Context · Building · Floors · Aivan · Booths · Furniture · Bar · Service · Mangal · Photo_lounge · Corridor · Tapchans_tent · Fountain · Trees · Planting · Kids · Street_facade · Roof_structure · Roof_skin · Lights

## Rebuild
```
python3 samarkand/site/tools/export3d_r9.py zone.json samarkand-zone-base.dxf OUT       # → OUT/samarkand-3d-data-R9.json
bvenv/bin/python samarkand/3d/scripts/base3d.py OUT/samarkand-3d-data-R9.json OUT 1 1600 1000 96   # model + exports + 4 renders
```

## R12 (2026-10-28)
- Three roof domes. South Ø6.0 and north Ø4.4 sit over the chinars, with open oculi Ø3.6 / Ø2.4; the crowns grow out through them. A closed central dome Ø5.6 with a glazed lantern sits between them. Each dome has 12 ribs, a drum with jali windows from the roof skin up to a level ring at +3.900, a terracotta outer skin and an inner girih brick-slip finish.
- "Bukhara dome" rotunda (museum vitrine + shop) at the head of the aryk; Khiva gate 4.1 m; two tents 2.6 m wide; 8 themed booths; R11 linear mangal kitchen; kids corner with its fence.
- Files: `samarkand-base3d-R12.*`, `samarkand-3d-data-R12.json`, web viewer data `samarkand-base3d-R12-web.json`, renders `renders/samarkand-base3d-R12-*.png`.
- Rebuild:
  ```
  python3 samarkand/site/tools/export3d_r12.py zone.json samarkand-zone-base.dxf OUT
  bvenv/bin/python samarkand/3d/scripts/base3d_r12.py OUT/samarkand-3d-data-R12.json OUT 1 1600 1000 96
  ```
