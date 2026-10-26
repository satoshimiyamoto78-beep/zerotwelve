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

## Layout R1 (2026-10-22)
`samarkand/layout/samarkand-terrace-layout-R1.*`, script `samarkand/site/tools/layout.py`. The script checks that furniture is clear of planters, columns, the ramp, the steps and the door swing.
Zoning comes from the owner's red markup:
- North entrance (from parking) and east entrance (street stair 13300–18300). The alley runs y 16300–19700 into the hall doors C–D.
- Bar on the façade, y 8600–15200, under the balcony, 10 stools.
- BBQ along the planter in the SE corner: tandoor, mangal 2.4 m, kazan, prep and pass counters.
- Photo zone on the south edge with a pishtaq backdrop. Kids zone in bay 5–6/A–A'.
- Dining: 4-tops N and S, 4 hybrid tapchans under the canopy, banquette along the planter. 112 seats in total.
- Roof columns: mid row x=6300 on the grid axes, east row in the planter centreline, west row on brackets to the building.

Project log (Claude Doc): https://claude.ai/artifact/J1QKYY82544U1DqaET49jN. Add a timeline row after every step.

## Layout R6 (2026-10-22, current)
Script `samarkand/site/tools/layout_r6.py` → `samarkand/layout/samarkand-terrace-layout-R6-{ru,en}.{svg,pdf,png}` + DXF/JSON. Sheet A2 at 1:100, with axes, dimensions, table numbers, ergonomics table and four details (mangal 1:75, tent 1:75, street-bench section, aivan section).
- Aivan platform (3.3 m): ONE row only. Banquette 550 on the hall wall in front of the closed doors, 4 tables 1200×700, chairs on the aisle side, aisle 1510. In R5 two columns of tables did not physically fit.
- Mangal 4.2 × 4.8 m (x 8100–12300, y 3700–8500), was 3.2 × 6.1. The hot line (tandoor, mangal, kazan) runs along the east fire wall. The pass (2.8 m) faces the entrance tables, with 1710 to the guests.
- Street façade (lot-line strip 1500): outer 550 is a cast concrete bench at +450, then a 150 back wall with majolica, then an 800 planter with the roof columns in it. It also has a sebil fountain south of the entrance, a street photo arch at y 25800–27800, and pishtaq pylons at the entrance. Nothing projects onto the sidewalk.
- Entrance alley: the first 2.8 m from the street is a draped velvet corridor (runner, khum jars, floor lanterns).
- North: 2 tapchans, a majlis tent 3.3×3.6 (U-sofa, 10 seats) in place of the 2 northern tapchans, and 2×2-tops at the north entrance.
- Photo zone: freestanding backlit jali arch 3.2 m, palms in terracotta pots, rug, lanterns and candles.
- Seats: 163, plus about 35 on the street benches. Minimum path 1205 (booths). Chairs back-to-back are at least 450.

## Heights and legal lines from the as-built set (checked 2026-10-26)
Source: BV_HOAN_CONG_GALINA PDF, sheets KT-06 (east elevation A'–H), H–A', roof plan, site plan 1:250.
- Levels (finished): hall ±0.000. Ground at the façade −0.450 on the elevation (the plan spot level says −0.470, so verify on site). Sidewalk −1.170. F2 +4.200, F3 +7.800, roof +11.700, arched roof up to +15.400.
- F2 slab 350 thick, so the balcony soffit is at **+3.850**. The balcony is a curved slab up to about 1.5 m deep (B–F), with a 1000 rail.
- The F1 glazing is 2600 doors plus a 600 transom. A decorative wavy louver screen hangs from the balcony edge, dropping as low as about +3.2.
- Existing entrance canopy at E–G: 4400 deep (y 28662–36300), soffit about +3.650, 1260 fascia. The GALINA sign pylon at the F–G corner rises to +12.150.
- **Building line (chỉ giới xây dựng)**: dashed line about **4.0 m inside the lot line / red line** (chỉ giới đường đỏ = our east boundary xb). Local x at y=20000: lot line 11820, building line 7800. Any permanent roof east of it needs the authority's OK. Fallback: a fixed roof up to the building line, and a retractable or demountable cover (awning, retractable-fabric pergola) over the outer 4 m.
- The roof can only go under the balcony. At the façade, the top of the roof structure is ≤ +3.850. With a 5–8% fall to the street over 10–13 m, the street eave sits at about +2.9…+3.3, which is 3.3–3.7 m above the terrace. That is a strong reason to keep the terrace at −0.450.

## Layout R7 + roof + estimate (2026-10-26, current)
The owner said: legal setback is not a concern, so the roof goes to the street. Remove the wave louvers. Keep both trees, open to the sky. Budget "normal, no waste". The north driveway stays for cars and scooters. The mangal kitchen has all utilities.
- Tables: every loose table is built from 700 × 800 modules (1 = 2 seats, 2 = 4, 3 = 6, 4 = 8). There are 36 modules and 64 chairs. Rows are aligned so pairs push together into tables for 8.
- Tapchans: two of 2.0 × 2.2 m for 6 guests each, with kurpacha on 3 sides, open to the east. The hauz fountain is in front of them at (6000, 30800). The aryk was removed and a planting bed sits behind.
- Majlis tent: 3.3 × 3.2 m, entered from the east (1.8 m opening).
- Photo lounge "Ochag": draped portal, carpets, LED fire bowl, 3 low tables with 9 poufs.
- Courts open to the sky: south x3600–7600 / y10400–15000, north x4700–7400 / y25800–29000.
- Seats: 164, plus about 35 on the street benches.
- Roof (`roof_r7.py`): beams on the column lines 4100/9850/15300/18300/21350/25600/29100/32100/36300. Steel ledger under the balcony slab (top of skin +3.750), 5% fall to the street (eave about +3.16). PU 50 mm sandwich panel with a wood-look underside, box gutter along the street, downpipes in the columns. About 9.8 t of steel, 419.5 m² of roof.
- Estimate (`samarkand/estimate/samarkand-estimate-R7.xlsx`, live formulas): about 3.67 bn VND (~141k USD at 26,000) including 10% contingency. The all-economy option is about 3.2 bn VND. Prices are Da Nang 2026 indicative, ±20%.
