# Site: design zone (base plan R0, 2026-10-22)

Address: 254 Võ Nguyên Giáp, P. Phước Mỹ, Q. Sơn Trà, Đà Nẵng. The east forecourt of the existing restaurant building, between the façade and Võ Nguyên Giáp road (15 m).

Files in `samarkand/site/`:
- `samarkand-zone-base.dxf` — base drawing, mm, 1:1, layers `SMK-*`. Import into SketchUp (File → Import, units mm) or AutoCAD.
- `samarkand-zone-base-plan.pdf/.png` — A3 sheet at 1:200.
- `samarkand-zone-data.json` — vertices, grid, levels, measurements.
- `source-extract/` — the original as-built DWG + PDF (Long House, 10-07-2024) and the full extracted geometry.
- `tools/` — the extraction pipeline (`cad.py`, `build_zone.py`, `draw_zone.py`). It reads the DWG through `@mlightcad/libredwg-web` (npm) into JSON.

## Coordinate system
- Origin (0,0) = axis 6 × axis A'. x points east, y points north (plan up = north per site plan). Units mm.
- Grid: axis 6 = façade line x=0, axis 5 at x=−7250. Axes A'=0, A=4100, B=9850, C=15600, D=21350, E=27100, F=32100, G=37100.
- The source DWG has the sheets in one model space. Offsets onto the site plan: F1 plan +(41530, 120147), F2 plan +(41530, 183668). Our origin is site (1006949, −259352).

## Zone polygon (mm)
Z1 (0, 42340) NW at north boundary · Z2 (9656, 41965) NE lot corner · Z3 (13459, 3389) on east boundary · Z4 (−168, 0) · Z5 (−7250, 0) · Z6 (−7250, 4100) · Z7 (0, 4100) building SE corner.
- Area 499.9 m². Without the car ramp: 446.5 m². Bay 5–6/A–A': 7250 × 4100 = 29.7 m².
- Façade length A→G 33 000. Depth from façade to boundary: G 10 136 · F 10 629 · E 11 121 · D 11 688 · C 12 255 · B 12 822 · A 13 389.
- East boundary is straight, 5.63° off north. Edges: Z1–Z2 9663 · Z2–Z3 38 763 · Z3–Z4 14 041 (14.0°).

## Existing conditions inside the zone
- North strip Z1–Z2 down to about G (5.2 m): **car ramp 8% to the rear parking**, 53.4 m².
- Wheelchair ramp + rail along the façade, from axis G down to about E (projects about 2.45 m).
- Entrance canopy above (F1 plan): 4404 × 7638 from the façade, between G and E. The site plan shows 5000 × 9200, so verify.
- Floor-2 balcony above: up to 1502 m beyond the façade, from about B to F, curved edge.
- Glass façade with outward-opening doors. Entrance steps ±0.000 → −0.470 at C–D (3 risers, 4.7 m wide).
- Planter walls on the east boundary (about 1.5 m wide). Entrance stairs from the sidewalk −1.170 → −0.470, 4940 wide, near C–D.
- Two round elements Ø2.0 (concentric Ø1.6) at (5999, 27097) and (5999, 12722). What they are is unknown.
- Pergola about 6.0 × 5.8 with 6 posts 200×200 near the south edge, rotated 14°.
- Gate pillar at the SE corner, outside the zone.
- Levels: hall ±0.000, forecourt −0.470, sidewalk −1.170.

## Open questions (ask the client or verify on site)
Canopy size · balcony soffit height · what the round elements are · keep or remove the pergola · bay 5–6/A–A' open to sky above F2? · keep the car ramp · drainage, power and water points.
