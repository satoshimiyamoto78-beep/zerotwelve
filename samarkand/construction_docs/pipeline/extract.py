import bpy, json, re
from mathutils import Vector
from collections import defaultdict
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
def bb(o):
    w=[o.matrix_world@Vector(v) for v in o.bound_box]; return [round(min(p[i] for p in w),3) for i in range(3)],[round(max(p[i] for p in w),3) for i in range(3)]
D={}
pat={'sam_col':r'^Sam_column_\d+$','steel_col':r'^column_steel','dome_col':r'^Dome_column(\.\d+)?$','khiva_col':r'^Khiva_column_\d+$','beam':r'^roof_beam_y','purlin':r'^purlin(\.\d+)?$',
 'booth':r'^Booth\d_shell$','booth_table':r'^Booth\d_table$','table':r'^Table_','chair':r'^Chair_[0-9m]+$','aivan_table':r'^Aivan_table_\d$','aivan_settee':r'^Aivan_settee','booth_settee':r'^Booth\d_settee',
 'barstool':r'^Barstool','bar':r'^Bar_(counter|backwall)$','tent':r'^Tent_\d$','tapchan':r'^Tapchan_v82$','majlis':r'^Majlis_(bench|cushion|pouf)','pishtaq':r'^Street_pishtaq$','sebil':r'^Street_sebil$',
 'corridor':r'^Corridor_arches$','dome':r'^dome_(shell|drum|ring_girder)_C$','planter':r'^Tree_planter_ring','hauz':r'^Hauz_star_wall$','mangal':r'^Mangal_(west_wall|hood|display_base)$|^firewall$|^kazanblock$|^tandoorblock$',
 'kids':r'^kids_rubber$','aivan_deck':r'^aivan_deck$','steps':r'^steps[AB]_flight$|^barsteps_flight$','ramp':r'^ramp$','rotunda':r'^Bukhara_rotunda$','gate':r'^Khiva_gate$','doors':r'^Hall_door','lift':r'^Lift_portal$',
 'street_bench':r'^Street_bench_plaster','socket':r'^Floor_socket','chandelier':r'chandelier|Chandelier|lantern_hang','globe':r'globes','skylight':r'^Skylight_frame$','coffers':r'^Ceiling_(coffers|grid)$',
 'clay_wall':r'^Boundary_clay_wall','pergola':r'^Pergola_existing$','facade':r'^facade_glass$','terrace':r'^terrace_floor$','tree':r'^Chinar_trained','framed':r'^Wall_framed_carpet'}
for k,p in pat.items():
    D[k]=[[o.name]+list(bb(o)) for o in bpy.data.objects if o.type=='MESH' and re.search(p,o.name) and not o.name.endswith('_real')]
json.dump(D,open('cd/model_data.json','w'))
print({k:len(v) for k,v in D.items()})
