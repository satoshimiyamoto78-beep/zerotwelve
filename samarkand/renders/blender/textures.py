import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]; R = random.Random(3)
LAP, TUR, CRE, TER, GOLD, WAL, RED = (31,63,138), (42,157,168), (239,230,216), (181,101,58), (217,162,58), (90,58,34), (142,31,36)
def star(d, cx, cy, r, fill, rot=0):
    pts=[]
    for i in range(16):
        a = rot + i*math.pi/8; rr = r if i%2==0 else r*0.62
        pts.append((cx+rr*math.cos(a), cy+rr*math.sin(a)))
    d.polygon(pts, fill=fill)
# 1 floor: large cream tile 600 with lapis cabochon at corners (1 tile = 512 px)
S=1024; im=Image.new('RGB',(S,S),(232,214,186)); d=ImageDraw.Draw(im)
for i in range(2):
    for j in range(2):
        x0,y0=i*512,j*512; v=R.randint(-8,8)
        d.rectangle([x0+3,y0+3,x0+509,y0+509], fill=(234+v,216+v,188+v))
for (x,y) in [(0,0),(512,0),(1024,0),(0,512),(512,512),(1024,512),(0,1024),(512,1024),(1024,1024)]:
    d.polygon([(x,y-60),(x+60,y),(x,y+60),(x-60,y)], fill=TER); d.polygon([(x,y-30),(x+30,y),(x,y+30),(x-30,y)], fill=LAP)
for k in range(30000):
    x,y=R.randrange(S),R.randrange(S); c=im.getpixel((x,y)); n=R.randint(-10,10); im.putpixel((x,y),tuple(max(0,min(255,v+n)) for v in c))
im.filter(ImageFilter.GaussianBlur(.6)).save(f'{out}/floor.png')
# 2 girih alley tile (one tile 600 = 1024 px)
im=Image.new('RGB',(S,S),TER); d=ImageDraw.Draw(im)
d.rectangle([6,6,S-6,S-6], fill=(201,139,98))
star(d,S/2,S/2,420,LAP,math.pi/8); star(d,S/2,S/2,300,CRE,math.pi/8); star(d,S/2,S/2,210,TUR,math.pi/8); d.ellipse([S/2-70,S/2-70,S/2+70,S/2+70], fill=GOLD)
for (x,y) in [(0,0),(S,0),(0,S),(S,S)]: star(d,x,y,190,LAP,math.pi/8); star(d,x,y,110,CRE,math.pi/8)
im.filter(ImageFilter.GaussianBlur(.8)).save(f'{out}/girih.png')
# 3 majolica (islimi-like) tile
im=Image.new('RGB',(S,S),LAP); d=ImageDraw.Draw(im)
def motif(cx,cy,s):
    for k in range(4):
        a=k*math.pi/2
        for t in range(6):
            ang=a+t*0.25; r=s*(0.25+t*0.07)
            x,y=cx+r*math.cos(ang),cy+r*math.sin(ang); d.ellipse([x-s*.05,y-s*.05,x+s*.05,y+s*.05], fill=CRE)
        x,y=cx+s*.62*math.cos(a+math.pi/4),cy+s*.62*math.sin(a+math.pi/4); d.ellipse([x-s*.09,y-s*.05,x+s*.09,y+s*.05], fill=TUR)
    star(d,cx,cy,s*.32,TUR,math.pi/8); star(d,cx,cy,s*.18,CRE,math.pi/8); d.ellipse([cx-s*.07,cy-s*.07,cx+s*.07,cy+s*.07], fill=RED)
for (cx,cy) in [(256,256),(768,256),(256,768),(768,768)]: motif(cx,cy,300)
for (cx,cy) in [(0,0),(512,0),(1024,0),(0,512),(512,512),(1024,512),(0,1024),(512,1024),(1024,1024)]: star(d,cx,cy,70,GOLD,math.pi/8)
d.line([(0,0),(S,0)],fill=(15,30,70),width=8); d.line([(0,0),(0,S)],fill=(15,30,70),width=8); d.line([(512,0),(512,S)],fill=(15,30,70),width=4); d.line([(0,512),(S,512)],fill=(15,30,70),width=4)
im.filter(ImageFilter.GaussianBlur(.7)).save(f'{out}/majolica.png')
# 4 ikat fabric
im=Image.new('RGB',(512,512),CRE); d=ImageDraw.Draw(im)
cols=[RED,LAP,GOLD,RED]
for c in range(4):
    cx=c*128+64
    for y in range(0,512,3):
        ph=(y%256)/256; half=(ph if ph<.5 else 1-ph)*2; hw=10+half*52+R.uniform(-5,5)
        d.rectangle([cx-hw,y,cx+hw,y+3], fill=cols[c]); iw=max(0,hw-20+R.uniform(-3,3)); d.rectangle([cx-iw,y,cx+iw,y+3], fill=CRE)
        cw=max(0,iw-12); d.rectangle([cx-cw,y,cx+cw,y+3], fill=cols[(c+1)%4])
im.save(f'{out}/ikat.png')
# 5 suzani
im=Image.new('RGB',(512,512),(241,229,208)); d=ImageDraw.Draw(im)
for (cx,cy) in [(128,128),(384,384),(384,128),(128,384)]:
    for k in range(12):
        a=k*math.pi/6; x,y=cx+70*math.cos(a),cy+70*math.sin(a); d.ellipse([x-22,y-22,x+22,y+22], fill=(184,50,58))
    d.ellipse([cx-58,cy-58,cx+58,cy+58], fill=(184,50,58)); d.ellipse([cx-34,cy-34,cx+34,cy+34], fill=GOLD); d.ellipse([cx-14,cy-14,cx+14,cy+14], fill=(42,111,74))
for (cx,cy) in [(256,0),(0,256),(256,256),(512,256),(256,512)]: d.ellipse([cx-24,cy-24,cx+24,cy+24], fill=(42,111,74))
im.save(f'{out}/suzani.png')
# 6 girih band (frieze) 4:1
im=Image.new('RGB',(2048,512),LAP); d=ImageDraw.Draw(im)
d.rectangle([0,0,2048,40],fill=TUR); d.rectangle([0,472,2048,512],fill=TUR)
for i in range(8):
    cx=i*256+128; star(d,cx,256,170,CRE,math.pi/8); star(d,cx,256,120,LAP,math.pi/8); star(d,cx,256,60,GOLD,math.pi/8)
    d.polygon([(cx+128,150),(cx+190,256),(cx+128,362),(cx+66,256)], fill=TUR)
im.filter(ImageFilter.GaussianBlur(.7)).save(f'{out}/band.png')
print('ok')
# 7 jali: carved walnut lattice (8-point star grid)
im=Image.new('RGB',(512,512),(70,42,22)); d=ImageDraw.Draw(im)
for cx in range(0,513,128):
    for cy in range(0,513,128):
        star(d,cx,cy,58,(28,16,8),math.pi/8); star(d,cx,cy,40,(120,78,44),math.pi/8); star(d,cx,cy,26,(20,12,6),math.pi/8)
for cx in range(64,513,128):
    for cy in range(64,513,128):
        d.polygon([(cx,cy-40),(cx+40,cy),(cx,cy+40),(cx-40,cy)], fill=(22,13,7)); d.polygon([(cx,cy-24),(cx+24,cy),(cx,cy+24),(cx-24,cy)], fill=(110,70,40))
im.filter(ImageFilter.GaussianBlur(1.0)).save(f'{out}/jali.png')
# 8 sea/sky backdrop (vertical gradient + sea band)
im=Image.new('RGB',(64,512)); px=im.load()
for y in range(512):
    t=y/511
    if t<0.62: c=tuple(int(a+(b-a)*(t/0.62)**1.2) for a,b in zip((38,58,110),(250,170,110)))
    else: c=tuple(int(a+(b-a)*((t-0.62)/0.38)) for a,b in zip((60,95,125),(20,40,60)))
    for x in range(64): px[x,y]=c
im.save(f'{out}/sky.png')
print('ok2')
