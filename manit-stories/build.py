import base64, re
src = open('manit-stories.html').read()
head = src[:src.index('<body>')]
cover = src[src.index('<!-- ============ 1. COVER'):src.index('<!-- ============ 2. MANICURE')]
head = head.replace('</style>', '''  .photo{left:220px;top:150px;width:640px;height:640px;object-fit:cover}
  .photo-shade{left:220px;top:520px;width:640px;height:270px;background:linear-gradient(180deg,rgba(28,4,9,0) 0%,rgba(28,4,9,.72) 100%)}
  .frame{left:204px;top:134px;width:672px;height:672px;border:1px solid rgba(246,236,230,.5)}
  .ph-logo{font-family:"cormorant-garamond",serif;font-weight:500;font-size:84px;letter-spacing:10px;line-height:1;color:#fff}
  .ph-sub{font-family:"montserrat",sans-serif;font-weight:300;font-size:18px;letter-spacing:9px;color:#fff}
  .script{font-family:"cormorant-garamond",serif;font-style:italic;font-weight:400;font-size:150px;line-height:1}
  .colh{font-family:"cormorant-garamond",serif;font-style:italic;font-size:30px;line-height:1.05;text-align:center;color:var(--soft)}
  .svc{font-family:"cormorant-garamond",serif;font-weight:400;font-size:38px;line-height:1.15}
  .pr{font-family:"cormorant-garamond",serif;font-weight:400;font-size:42px;line-height:1;text-align:center}
  .box{border:1px solid rgba(246,236,230,.6)}
  .boxnote{font-family:"cormorant-garamond",serif;font-style:italic;font-size:32px;line-height:1.3;text-align:center}
</style>''')

def b64(p): return 'data:image/jpeg;base64,'+base64.b64encode(open(p,'rb').read()).decode()
STAR='<svg class="abs" style="left:{x}px;top:{y}px" width="30" height="30" viewBox="0 0 40 40"><path d="M20 2 Q22 18 38 20 Q22 22 20 38 Q18 22 2 20 Q18 18 20 2Z" fill="#f6ece6"/></svg>'

def story(title, img, rows, step, note, note_h, arcs):
    o=['<section class="slide" data-canvas-width="1080" data-canvas-height="1920">',
       '  <div class="abs g1"></div><div class="abs g2"></div>',
       f'  <svg class="arcs" width="1080" height="1920" viewBox="0 0 1080 1920">{arcs}</svg>',
       '  <div class="abs kicker" style="top:62px"><span></span>MANIT NAIL STUDIO<span></span></div>',
       '  <div class="abs frame"></div>',
       (f'  <img class="abs photo" src="{img}" alt="">' if img else '  <div class="abs photo" style="background:#5a1a26"></div>'),
       '  <div class="abs photo-shade"></div>',
       '  <div class="abs center ph-logo" style="top:668px">MÁNIT</div>',
       '  <div class="abs center ph-sub" style="top:758px">NAIL STUDIO</div>',
       f'  <div class="abs center script" style="top:815px">{title}</div>',
       '  <div class="abs colh" style="left:650px;top:968px;width:170px">топ<br>мастер</div>',
       '  <div class="abs colh" style="left:830px;top:968px;width:190px">ведущий<br>мастер</div>']
    y=1065
    for i,(name,p1,p2) in enumerate(rows):
        if i: o.append(f'  <div class="abs rule" style="left:90px;top:{y-step//2-2}px;width:900px;background:rgba(246,236,230,.25)"></div>')
        o.append(f'  <div class="abs svc" style="left:90px;top:{y}px;width:540px">{name}</div>')
        o.append(f'  <div class="abs pr" style="left:650px;top:{y+2}px;width:170px">{p1}</div>')
        o.append(f'  <div class="abs pr" style="left:840px;top:{y+2}px;width:170px">{p2}</div>')
        y+=46*(name.count('<br>')+1)+step
    by=y-step+70
    o.append('  '+STAR.format(x=525,y=by-50))
    o.append(f'  <div class="abs box" style="left:150px;top:{by}px;width:780px;height:{note_h}px"></div>')
    o.append(f'  <div class="abs center boxnote" style="left:190px;width:700px;top:{by+28}px">{note}</div>')
    o.append('</section>')
    return '\n'.join(o)

ARC_A='<path d="M1080 330 C 960 260, 920 140, 900 0" fill="none" stroke="rgba(246,236,230,.55)" stroke-width="1.5"/><path d="M0 1640 C 160 1700, 230 1820, 250 1920" fill="none" stroke="rgba(246,236,230,.55)" stroke-width="1.5"/>'
ARC_B='<path d="M0 330 C 120 260, 160 140, 180 0" fill="none" stroke="rgba(246,236,230,.55)" stroke-width="1.5"/><path d="M1080 1640 C 920 1700, 850 1820, 830 1920" fill="none" stroke="rgba(246,236,230,.55)" stroke-width="1.5"/>'

def build(imgsrc):
    man = story('маникюр', imgsrc('photo-manicure-s.jpg'), [
        ('Маникюр + покрытие гель лак<br>(всё включено)','250 с','000 с'),
        ('Маникюр Френч (всё включено)','280 с','000 с'),
        ('Наращивание ногтей до 4 длины','320 с','000 с'),
        ('Маникюр без покрытия','000 с','000 с'),
        ('Японский маникюр','180 с','000 с')], 48,
        '***В наши услуги входит всё, чтобы ваши ногти выглядели безупречно, поэтому мы не берём доплат за снятие покрытия, укрепление, исправления и ремонт!', 215, ARC_A)
    ped = story('педикюр', imgsrc('photo-pedicure-s.jpg'), [
        ('Полный smart педикюр<br>с покрытием гель лак','000 с','000 с'),
        ('Полный педикюр без покрытия','000 с','000 с'),
        ('Express педикюр с покрытием<br>гель лак/лак','000 с','000 с'),
        ('Express педикюр без покрытия','000 с','000 с')], 64,
        '***SPA ритуал включён в программу<br>любого педикюра', 150, ARC_B)
    return head+'<body>\n\n'+cover+'<!-- ============ 2. MANICURE ============ -->\n'+man+'\n\n<!-- ============ 3. PEDICURE ============ -->\n'+ped+'\n\n</body>\n</html>\n'

open('manit-stories-v3.html','w').write(build(lambda p:p))
open('manit-stories-v3-embedded.html','w').write(build(b64))
open('manit-stories-v3-express.html','w').write(build(lambda p:''))
