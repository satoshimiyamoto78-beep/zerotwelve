# Samarkand terrace: 3D base model (R9, LOD 200)

This model is built automatically from the R9 floor plan (`samarkand/site/tools/layout_r9.py`). When the plan changes, rebuild the model rather than editing it by hand.

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
