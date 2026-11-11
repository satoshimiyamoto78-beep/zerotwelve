import bpy,re
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
n=lambda p:[o for o in bpy.data.objects if re.match(p,o.name) and not o.name.endswith('_real')]
ch=len(n(r'Chair_')); bs=len(n(r'Barstool')); bo=len(n(r'Booth\d_settee_'))*2; av=len(n(r'Aivan_settee_'))*3
print('chairs',ch,'barstools',bs,'booth seats',bo,'aivan seats',av,'tents 16 majlis 10 tapchan 6 -> total',ch+bs+bo+av+32)
