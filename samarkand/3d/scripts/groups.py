"""viewer layer tags (owner 2026-11-05): every object gets o['grp']; the viewer hides by tag with dependencies
(structure off -> roof + everything hung from it off; roof off -> roof-hung carpets/swags/pendants off; domes off -> dome chandelier off)."""
import re
COLG = {'Roof_skin': 'skin', 'Roof_structure': 'structure', 'Pergola_existing': 'structure', 'Domes': 'domes', 'Carpet_ceiling': 'hung',
        'Furniture': 'furniture', 'Planting': 'planting', 'Trees': 'planting', 'Building': 'building', 'Street_facade': 'facade', 'Columns': 'facade',
        'People': 'people', 'Kids': 'kids', 'Context': 'context', 'Floors': 'floors', 'North_gate': 'facade',
        'Aivan': 'aivan', 'Booths': 'booths', 'Mangal': 'mangal', 'Corridor': 'corridor', 'Bar': 'bar', 'Service': 'bar', 'Fountain': 'fountain',
        'Tapchans_tent': 'tents', 'Photo_lounge': 'majlis', 'Bukhara_dome': 'decor', 'Lights': 'decor'}
NAMEG = [(r'^(flashing_|gutter_pergola|gutter_downpipe|roof_panel)', 'skin'), (r'^Skylight_(glass|panjara)', 'skin'), (r'^Skylight_frame', 'structure'), (r'^(Chandelier_dome|Dome_alem)', 'domes'),
         (r'^(Aivan_ceiling_rod|Aivan_tie_cleat|Corridor_frame|column_steel|dome_curb|dome_ring_girder|roof_|purlin|facade_ledger|gutter_street)', 'structure'),
         (r'^(Ceiling_carpet|Flying_carpet|Rod_carpet|Velvet_swag|Pendant_cluster|Bar_drum_pendant|Booth\d_pendant|Rattan_pendant|Corridor_swag)', 'hung'),
         (r'^(Chair|Table|Tableset|Boothset|Booth\d_(table|tableset|banquette)|Aivan_(table|tableset|banquette)|Tent\d_(majlis|tray)|Tent_octatable|Tapchan_(lowtable|tableset|soft)|Barstool|Majlis_(bench|cushion|pouf|table))', 'furniture'),
         (r'^(Olive_|Croton_|Areca|Banana|Bougainvillea|Herbs|Jasmine|Planter_shrub|Plumeria|Pomegranate|Street_palm|Chinar_|Aivan_vase)', 'planting'),
         (r'^Person', 'people'), (r'^(Kids_|play_)', 'kids')]
def tag_groups():
    n = {}
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'EMPTY'): continue
        g = None
        for pat, gg in NAMEG:
            if re.match(pat, o.name): g = gg; break
        if g is None and o.users_collection: g = COLG.get(o.users_collection[0].name, 'decor')
        o['grp'] = g or 'decor'; n[o['grp']] = n.get(o['grp'], 0) + 1
    print('viewer groups', n)
