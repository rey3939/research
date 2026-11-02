from contextlib import contextmanager
from zipfile import ZipFile
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from pathlib import Path
import math, json
from PIL import Image, ImageDraw, ImageFont
import fitz
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement

BASE=Path('/workspace/slide_redesign'); OUT=Path('/workspace/outputs'); ASSET=BASE/'assets'
SRC=Path('/workspace/attachments/d3682aed-3346-4110-a6e1-ac6360e710ce/2026.10.26_大橋怜倭_日本語版.pdf')
W,H=1600,900; U=914400/120; SCALE=1.5
C={'navy':'142C44','ink':'183046','muted':'617689','teal':'007F86','cyan':'E7F5F4','blue':'2377C5','pale':'EEF3F8','orange':'D86B35','peach':'FFF0E5','white':'FFFFFF','gray':'C1CED8','light':'F7F9FC','red':'BB4560','green':'30846C'}
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'; BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
prs=Presentation(); prs.slide_width=Inches(13.333333); prs.slide_height=Inches(7.5)
prs.core_properties.title='永久磁石エラストマーの曲げ変形による磁場変化｜中間審査会 改良版'
prs.core_properties.author='大橋 怜倭'
prs.core_properties.subject='10分発表用：線形性の意義と弾性領域を図で説明'
slides=[]; alltext=[]; issues=[]; cur=None; im=None; dr=None

def rgb(c):
 c=C.get(c,c);return RGBColor.from_string(c)
def col(c): return '#'+C.get(c,c)
def e(v): return Emu(round(v*U))
def font(sz,b=False):return ImageFont.truetype(BOLD if b else FONT,round(sz*SCALE))
def measure(s,sz,b=False):return font(sz,b).getlength(s)/SCALE

def rect(x,y,w,h,fill='white',line=None,r=0,lw=2):
 sh=cur.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE,e(x),e(y),e(w),e(h))
 sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
 if line:sh.line.color.rgb=rgb(line);sh.line.width=Pt(lw*.6)
 else:sh.line.fill.background()
 if r:
  try:sh.adjustments[0]=min(.12,r/min(w,h))
  except:pass
 xy=[round(x*SCALE),round(y*SCALE),round((x+w)*SCALE),round((y+h)*SCALE)]
 if r:dr.rounded_rectangle(xy,radius=round(r*SCALE),fill=col(fill),outline=col(line) if line else None,width=max(1,round(lw*SCALE)))
 else:dr.rectangle(xy,fill=col(fill),outline=col(line) if line else None,width=max(1,round(lw*SCALE)))
 return sh

def circle(x,y,r,fill='teal',line=None,lw=2):
 sh=cur.shapes.add_shape(MSO_SHAPE.OVAL,e(x-r),e(y-r),e(2*r),e(2*r));sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
 if line:sh.line.color.rgb=rgb(line);sh.line.width=Pt(lw*.6)
 else:sh.line.fill.background()
 dr.ellipse([(x-r)*SCALE,(y-r)*SCALE,(x+r)*SCALE,(y+r)*SCALE],fill=col(fill),outline=col(line) if line else None,width=max(1,round(lw*SCALE)))
 return sh

def poly(points,fill=None,line='ink',lw=3,closed=False):
 if len(points)<2:return
 b=cur.shapes.build_freeform(round(points[0][0]),round(points[0][1]),scale=U)
 b.add_line_segments([(round(x),round(y)) for x,y in points[1:]],close=closed)
 sh=b.convert_to_shape()
 if fill:sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
 else:sh.fill.background()
 if line:sh.line.color.rgb=rgb(line);sh.line.width=Pt(lw*.6)
 else:sh.line.fill.background()
 xy=[(x*SCALE,y*SCALE) for x,y in points]
 if fill:dr.polygon(xy,fill=col(fill))
 if line:dr.line(xy+([xy[0]] if closed else []),fill=col(line),width=max(1,round(lw*SCALE)),joint='curve')
 return sh

def line(x1,y1,x2,y2,c='ink',lw=3,dash=False):
 if dash:
  length=math.hypot(x2-x1,y2-y1);n=max(1,int(length/15))
  for i in range(n):
   if i%2==0:
    a=i/n;b=min((i+1)/n,1);line(x1+(x2-x1)*a,y1+(y2-y1)*a,x1+(x2-x1)*b,y1+(y2-y1)*b,c,lw)
  return
 return poly([(x1,y1),(x2,y2)],line=c,lw=lw)

def arrow(x1,y1,x2,y2,c='teal',lw=5,head=15):
 line(x1,y1,x2,y2,c,lw)
 a=math.atan2(y2-y1,x2-x1);p1=(x2-head*math.cos(a)+head*.52*math.sin(a),y2-head*math.sin(a)-head*.52*math.cos(a));p2=(x2-head*math.cos(a)-head*.52*math.sin(a),y2-head*math.sin(a)+head*.52*math.cos(a))
 poly([(x2,y2),p1,p2],fill=c,line=None,closed=True)

def wrap_text(s,width,sz,bold):
 lines=[]
 for para in s.split('\n'):
  if not para:lines.append('');continue
  st=''
  for ch in para:
   if st and measure(st+ch,sz,bold)>width:lines.append(st);st=ch
   else:st+=ch
  lines.append(st)
 return lines

def text(x,y,w,h,s,sz=32,color='ink',bold=False,align='left',valign='top',wrap=False):
 global alltext
 s=s.translate(str.maketrans('ᵧₛₘₜₒₐₗₙᵢₓ', 'ysmt oalnix'.replace(' ','')))
 ls=wrap_text(s,w,sz,bold) if wrap else s.split('\n')
 line_h=sz*1.28;total=len(ls)*line_h
 if total>h+4:issues.append(f'text height slide {len(slides)+1}: {s[:25]} ({total:.1f}>{h})')
 for ss in ls:
  if measure(ss,sz,bold)>w+3:issues.append(f'text width slide {len(slides)+1}: {ss} ({measure(ss,sz,bold):.1f}>{w})')
 if x<0 or y<0 or x+w>W+2 or y+h>H+2:issues.append('outside text '+s[:20])
 box=cur.shapes.add_textbox(e(x),e(y),e(w),e(h))
 tf=box.text_frame;tf.clear();tf.word_wrap=False;tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0
 tf.vertical_anchor=MSO_ANCHOR.TOP
 from pptx.enum.text import PP_ALIGN
 dy=0
 if valign=='center':dy=(h-total)/2
 elif valign=='bottom':dy=h-total
 for i,ss in enumerate(ls):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=ss
  p.alignment={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}[align]
  p.space_before=Pt(0);p.space_after=Pt(0);p.line_spacing=Pt(line_h*.6)
  for run in p.runs:
   run.font.name='Noto Sans CJK JP';run.font.size=Pt(sz*.6);run.font.bold=bold;run.font.color.rgb=rgb(color)
   rp=run._r.get_or_add_rPr()
   ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK JP');rp.append(ea)
  tw=measure(ss,sz,bold);dx=0 if align=='left' else (w-tw)/2 if align=='center' else w-tw
  dr.text(((x+dx)*SCALE,(y+dy+i*line_h)*SCALE),ss,font=font(sz,bold),fill=col(color),anchor='lt')
 alltext.append(s)
 return box


BASE=Path(__file__).resolve().parent.parent;OUT=BASE;OUT.mkdir(exist_ok=True)
prs=Presentation();prs.slide_width=Inches(13.333333);prs.slide_height=Inches(7.5)
prs.core_properties.title='MCT-2150W：スマホ1台での引張物性測定・撮影と同期の配置案'
prs.core_properties.author='大橋 怜倭'
C.update({'black':'121212','bar':'858585','paper':'F2F2F2','softblue':'EAF3FA','peach2':'FCE9E0','machine':'354858','dark':'233746','sensor':'ECBC80'})
slides=[];alltext=[];issues=[];cur=None;im=None;dr=None;data=[]

@contextmanager
def group(name):
 global cur
 prev=cur;g=cur.shapes.add_group_shape();g.name=name;cur=g
 try:yield g
 finally:g.shapes._recalculate_extents();cur=prev

def new(title,subtitle):
 global slide,root,cur,im,dr,alltext
 slide=prs.slides.add_slide(prs.slide_layouts[6]);root=slide.shapes.add_group_shape();root.name='配置案：図形・テキストで編集可能';cur=root
 im=Image.new('RGB',(2400,1350),'white');dr=ImageDraw.Draw(im);alltext=[]
 text(60,28,1480,80,title,47,'navy',True)
 text(65,125,1460,45,subtitle,27,'muted')
 line(60,820,1540,820,'gray',1)
 text(65,840,1340,34,'MCT-2150W・上下同じ治具・スマートフォン1台を前提とした設計案／縮尺任意',18,'muted')
 text(1450,837,85,35,str(len(data)+1),23,'teal',True,'right')

def save(notes,name):
 root.shapes._recalculate_extents();slide.notes_slide.notes_text_frame.text=notes
 for rp in slide._element.iter(qn('a:rPr')):
  for ch in rp:
   if ch.tag in [qn('a:latin'),qn('a:ea')]:ch.set('typeface','Yu Gothic')
 path=OUT/(name+'.png');im.save(path)
 data.append({'title':alltext[0],'notes':notes,'preview':str(path),'text':alltext.copy()})

def dashbox(x,y,w,h,c='blue',lw=2):
 line(x,y,x+w,y,c,lw,True);line(x+w,y,x+w,y+h,c,lw,True);line(x+w,y+h,x,y+h,c,lw,True);line(x,y+h,x,y,c,lw,True)
def dimh(x1,x2,y,s,c='navy',sz=24):
 arrow(x1,y,x2,y,c,2,9);arrow(x2,y,x1,y,c,2,9);text(min(x1,x2),y-39,abs(x2-x1),36,s,sz,c,True,'center')
def dimv(y1,y2,x,s,c='navy',sz=23,w=190):
 arrow(x,y1,x,y2,c,2,9);arrow(x,y2,x,y1,c,2,9);text(x+14,(y1+y2)/2-18,w,40,s,sz,c,True)
def dotlabel(x,y,s,c='teal',sz=24,w=260):
 circle(x,y+15,6,c);text(x+20,y-4,w,45,s,sz,c,True)

# 1. System placement, load path and optical axis.
new('基本構成：正面のスマホ＋可動・固定の2つの目印','カメラのレンズ中心を試料中央の高さへ合わせ、試料の幅2 mmの面を正面から撮影する。')
with group('試験機と力の経路'):
 rect(250,210,240,556,'paper',r=10);rect(300,225,140,488,'machine')
 rect(235,738,285,40,'navy',r=5)
 rect(315,269,115,49,'white',line='gray',r=5);text(175,188,405,34,'可動クロスヘッド',23,'navy',True,'center')
 rect(335,347,75,65,'sensor',line='orange',r=4);line(372,318,372,347,'navy',7)
 text(112,350,200,40,'ロードセル',24,'orange',True,'right');line(314,369,334,369,'orange',2)
 line(372,412,372,466,'navy',5)
 # 55x15 faces, 22mm free opening and 35mm specimen are shown at about 4px/mm.
 rect(262,466,220,60,'gray',line='navy',r=3);rect(262,614,220,60,'gray',line='navy',r=3)
 for yy in [496,644]:
  for xx in [302,442]:circle(xx,yy,7,'white','navy',2)
 poly([(360,500),(360,528),(368,546),(368,594),(360,612),(360,640),(384,640),(384,612),(376,594),(376,546),(384,528),(384,500)],fill='orange',line=None,closed=True);rect(262,466,220,60,'gray',line='navy',r=3);rect(262,614,220,60,'gray',line='navy',r=3)
 for yy in [496,644]:
  for xx in [302,442]:circle(xx,yy,7,'white','navy',2)
 line(368,550,376,550,'white',3);line(368,590,376,590,'white',3)
 rect(342,674,60,64,'gray')
 text(84,475,160,40,'上側つかみ',22,'navy',True,'right');line(245,493,260,493,'navy',2)
 text(84,629,160,40,'下側つかみ',22,'navy',True,'right');line(245,645,260,645,'navy',2)
 text(94,560,228,40,'試料・標線10 mm',22,'orange',True,'right');arrow(327,577,365,570,'orange',2,8)
with group('同期目印の支持点'):
 # Independent supports; the moving support is upstream of the sensor.
 poly([(428,291),(535,291),(535,550),(386,550)],line='teal',lw=3)
 rect(383,546,7,8,'teal')
 poly([(245,739),(217,739),(217,590),(358,590)],line='muted',lw=3)
 rect(354,586,7,8,'navy')
 dashbox(354,538,36,64,'blue',2)
 text(565,276,490,80,'可動目印：ロードセル上流の\nクロスヘッド側から支持',25,'teal',True)
 text(565,367,470,80,'軽い支持アームを外側へ回し、\n目印だけを試料の横へ入れる',24,'muted')
 text(565,559,470,80,'固定目印：固定台側から支持\n試料・可動部とは独立させる',24,'navy',True)
with group('正面直角のカメラと照明：側面図'):
 rect(1080,220,450,541,'light',r=18)
 text(1100,239,410,43,'側面から見た撮影配置',28,'navy',True,'center')
 line(1110,553,1500,553,'gray',3)
 rect(1125,530,115,23,'navy',r=6);rect(1173,464,17,66,'navy');line(1180,464,1220,464,'navy',5)
 rect(1211,380,20,140,'navy',r=6);circle(1221,425,8,'blue')
 rect(1430,380,9,172,'orange');arrow(1239,425,1427,425,'blue',3,12)
 line(1434,405,1457,405,'navy',2);line(1457,405,1457,425,'navy',2)
 rect(1475,388,17,139,'cyan',line='teal',r=3)
 text(1100,560,420,73,'独立スタンド・前後微動\nレンズの高さ＝試料中央',24,'navy',True,'center')
 text(1100,637,420,50,'距離はピントと視野で決める',21,'muted',False,'center')
 text(1100,303,420,58,'背面は拡散板や明るい背景\n標線には斜めから柔らかい照明',21,'teal',False,'center')
text(70,782,1460,30,'スタンド台座は試験機の脇へ置き、アームを正面へ。操作パネル・非常停止ボタンへのアクセスを残す。',22,'navy',True,'center')
save('''写真の正面側から、試料の幅が見える面を撮影します。スマホ本体の中心ではなく、使用するレンズの中心を標線間中央の高さへ合わせます。カメラは独立した支柱・アームで保持し、台座は機械の脇に置く案です。前後位置は使用レンズの実際の最短撮影距離と必要な視野で決めます。写真だけから距離を何cmと確定していません。

ユーザー確認：取り付け治具本体＋固定治具（押さえ板）を上下に1組ずつ使い、スマートフォン1台で構成します。本図の機械本体・ロードセル・支柱・アームの長さと取り付け点は模式的な位置です。機械の全寸法を復元した組立CADではありません。

力の経路は、可動クロスヘッド→ロードセル→上側つかみ→試料→下側つかみ→固定台です。同期用の可動目印は、ロードセルより上流のクロスヘッド側から支持し、試料の横へ軽いアームで回す案です。下流へ質量や外力を追加する影響を避けることが狙いですが、具体的な固定方法・剛性・干渉は現物での確認が必要です。目印は試料表面とほぼ同じ奥行きへ配置し、目印そのものだけを小さい視野へ入れます。

固定目印は固定台側から独立に支持します。可動側と固定側を連結する構造にはせず、互い・試料・つかみ治具へ触れないことを全測定範囲で確認します。支持アームは短く軽く剛性を確保し、たわみや振動が追跡量に混ざらないよう予備試験で確認します。

背面照明は機械柱・治具との空間に余裕がある場合の案です。スペースがなければ白い背景と斜めからの拡散照明で、輪郭と白い標線が同時に見えるよう調整します。''','01_layout')

# 2. Actual dimensions and insertion plan.
new('つかみ方：端部だけを保持し、標線間を露出させる','STEPで確認：押さえ板55 × 15 × 4.42 mm、穴径6.3 mm、穴中心間35 mm。本体側も同じ穴ピッチ。')
with group('治具と試料の正面配置案'):
 rect(70,211,715,548,'light',r=16)
 # specimen first, then faces hide the inserted end portions.
 poly([(398,348),(398,404),(414,440),(414,536),(398,572),(398,628),(446,628),(446,572),(430,536),(430,440),(446,404),(446,348)],fill='orange',line=None,closed=True)
 rect(202,280,440,120,'gray',line='navy',r=4);rect(202,576,440,120,'gray',line='navy',r=4)
 for yy in [340,636]:
  for xx in [282,562]:circle(xx,yy,15,'white','navy',2)
 line(414,448,430,448,'white',4);line(414,528,430,528,'white',4)
 dimh(202,642,254,'55 mm',sz=23)
 dimv(400,576,685,'約22 mm',sz=22,w=150)
 arrow(353,448,353,528,'navy',2,9);arrow(353,528,353,448,'navy',2,9);text(237,470,105,40,'10 mm',21,'navy',True,'right')
 text(126,715,600,35,'公称長さ35 mmの試料：つかみ長は各6.5 mmの例',21,'navy',True,'center')
with group('確認する寸法と見通し'):
 for k,(h,b,c) in enumerate([
  ('端部の挿入長','まず各6〜7 mm程度を目安に調整','teal'),
  ('中央の露出長','約21〜23 mmを確保する案','navy'),
  ('撮影する範囲','標線間10 mm＋上下の余白','blue')]):
  yy=230+k*144;text(845,yy,650,49,h,32,c,True);text(845,yy+57,650,45,b,27,'ink')
 text(845,676,650,74,'15 mmのつかみ面へ全長を入れると、\n35 mm試料では露出が5 mmしか残らない。',24,'orange',True)
text(77,779,1450,31,'試料の実寸に合わせて開口を調整。平行部・標線を隠さず、片締め・すべり・荷重軸のずれを予備試験で確認。',21,'muted',False,'center')
save('''固定治具.stepは、55×15×4.42 mmの角丸板で、径6.3 mmの貫通穴が中心間35 mmで2つあります。取り付け治具.stepは2個のソリッドを含み、全体が約55×40×55 mmです。上部ブロックには中心間35 mmの径約5 mmの穴があり、押さえ板との組み合わせと整合します。ねじ山・ねじ規格・締付け力はSTEPから確認できません。

公称35 mmの7号形試料を、両端6.5 mmずつ把持すると中央の自由長は22 mmになります。これは初期の配置案で、現物の長さと端部形状に合わせて調整します。標線間距離10 mmと、つかみ口の間隔22 mmは異なる量です。試料を伸ばして開口へ合わせず、無負荷で保持できる位置へクロスヘッドを合わせます。

押さえ板の高さ15 mm全てへ端部を入れると、35−15−15=5 mmしか中央へ残らず、10 mm標線を観察できません。端のつかみ部分だけを挿入することが重要です。差し込み量をそろえる印や端部ストッパの使用は候補ですが、引張時の力の伝達を妨げないよう設計・確認が必要です。

把持面は平面であり、CAD形状だけから滑り防止や試料の損傷防止が成立したとは言えません。試料の端部と治具の相対位置が動かないかを、広めの予備撮影で確認します。締付けは左右対称にそろえ、押さえ板が傾かないことを確認します。スペーサや接触面の変更を行う場合は、把持機構としての再検証が必要です。''','02_grips')

# 3. FOV, optical resolution and markers.
new('スマホの視野：標線10 mmと小さい同期目印を同時に入れる','最初は縦16 × 横9 mm程度を仮の視野にし、実画像のピント・画素数・測定ばらつきから調整する。')
with group('拡大視野：公称比率の図'):
 # 16 mm high x 9 mm wide; 31px/mm.
 x0,y0,ww,hh=125,235,279,496;cx=x0+ww/2;cy=y0+hh/2
 rect(x0,y0,ww,hh,'white',line='blue',lw=3)
 rect(cx-31,cy-248,62,496,'teal')
 for yy in [cy-155,cy+155]:line(cx-31,yy,cx+31,yy,'white',8)
 # Side references do not touch the specimen.
 rect(cx+3.2*31-18.6,cy-3.3*31-18.6,37.2,37.2,'pale',line='navy',r=2);circle(cx+3.2*31,cy-3.3*31,9,'orange')
 rect(cx-3.2*31-18.6,cy+3.3*31-18.6,37.2,37.2,'pale',line='navy',r=2);circle(cx-3.2*31,cy+3.3*31,9,'navy')
 dimv(cy-155,cy+155,454,'標線間10 mm',sz=22,w=240)
 text(105,746,330,35,'視野横9 mm（例）',23,'blue',True,'center')
 text(86,202,390,30,'目印は試料と同じ奥行きへ',20,'muted',False,'center')
with group('追跡する対象'):
 dotlabel(700,226,'白い標線：縦ひずみ','teal',30,700)
 text(723,276,770,47,'2本の中心位置から L(t) を測る',28,'ink')
 dotlabel(700,350,'試料の左右輪郭：横ひずみ','teal',30,760)
 text(723,400,770,47,'同じ材料位置の幅 w(t) を測る',28,'ink')
 dotlabel(700,474,'可動目印：CSVとの時刻合わせ','orange',29,780)
 text(723,524,770,47,'クロスヘッド側の動きを画像で読む',27,'ink')
 dotlabel(700,598,'固定目印：画像の位置ずれ確認','navy',29,780)
 text(723,648,770,47,'カメラの微小な動きも確認する',27,'ink')
rect(70,774,1460,35,'cyan',r=8)
text(80,778,1440,30,'4K縦3840 px・視野16 mmの仮定：幅2 mmは480 px。縦ひずみ1%・ν=0.5なら幅の縮みは約2.4 px。',20,'teal',True,'center')
save('''視野16×9 mmは、スマートフォンを縦向きにし、16:9の4K動画3840×2160を利用できる場合を想定した初期案です。使用スマホの対応モード・最短撮影距離・使用レンズは未確認のため、現物で決めます。16 mmを3840 pxへ写せば240 px/mm、試料幅2 mmは480 pxです。縦ひずみ1%、ポアソン比0.5を仮定した幅の縮み10 µmは2.4 pxです。

この計算はポアソン比を十分な精度で測れる保証ではありません。0.1 pxの位置測定ばらつきを仮定しても、幅変化の測定は厳しい場合があります。静止時の幅のばらつき、既知寸法・既知変位、面外変形、倍率変化、動画処理の影響を確認します。視野が広すぎる場合は実光学系を拡大します。表示だけのデジタルズームで分解能が増えたと判断しません。

今回の基本案はスマホ1台です。標線10 mm全体と同期目印を確保した結果、横ひずみの目標精度を満たせない場合は、マクロ光学系やより高分解能の撮影を再検討する必要があります。別の拡大カメラ追加はその後の選択肢であり、現在の1台構成の成立を未検証のまま保証しません。

目印の横位置±3.2 mm、白いパッド1.2 mm角・中心印0.6 mm程度は配置検討用の値です。試料幅2 mmと離して置き、最初は試料表面とほぼ同じ奥行きで撮ります。可動目印は上へ移動するので、対象とする小ひずみ区間で視野から出ない位置にします。破断まで大きく伸ばす場合には、この小視野だけで全過程を追えるとは限りません。

ポアソン比は同じ動画の縦ひずみと横ひずみから求めるため、力CSVとの同期は必須ではありません。荷重と縦ひずみを組み合わせてヤング率を求めるときに、同期が必要です。''','03_fov')

# 4. Synchronization, zero and the mechanics of added holders.
new('同期用治具：共通の動きを撮るための軽い目印ホルダ','大きな同期装置より、クロスヘッドの動きを小さい視野へ運ぶ目印が有用。実機の固定部寸法は要確認。')
with group('支持点と測定の経路'):
 rect(70,213,595,455,'light',r=18)
 for yy,lab,c in [(245,'可動クロスヘッド','teal'),(370,'ロードセル','orange'),(495,'上側つかみ → 試料','navy')]:
  rect(140,yy,450,66,'cyan' if c=='teal' else 'peach2' if c=='orange' else 'pale',r=10);text(155,yy+15,420,44,lab,29,c,True,'center')
 arrow(365,316,365,361,'muted',4,11);arrow(365,441,365,486,'muted',4,11)
 poly([(590,277),(627,277),(627,591),(560,591)],line='teal',lw=3);circle(553,591,9,'orange')
 text(105,603,510,37,'目印の支持はロードセルより上流へ',25,'teal',True,'center')
with group('同期の手順'):
 rows=[('1','移動量ゼロと動画の静止位置を対応させる'),('2','動画の可動目印をmmへ換算する'),('3','同じ移動量になるよう時刻を合わせる'),('4','全区間の一致と残差を確認する')]
 for k,(n,lab) in enumerate(rows):
  yy=227+k*108;circle(750,yy+22,22,'teal');text(730,yy+2,40,42,n,27,'white',True,'center');text(800,yy+2,710,76,lab,27,'navy',True)
rect(70,697,1460,75,'cyan',r=14)
text(92,714,1416,50,'比較する量は「試験機の移動量」同士。試料の伸びを機械の移動へ無理に一致させない。',28,'teal',True,'center')
text(80,784,1450,29,'LEDを動画に写すだけではCSVに点灯時刻が残らない。共通トリガを使う場合は、実機側の入力・記録仕様を確認。',19,'muted',False,'center')
save('''同期治具は厳密には必須ではありません。クロスヘッドの同じ動きを動画へ直接写せるなら、追加部品なしでも使えます。ただし標線10 mmを拡大すると55 mm幅のつかみやクロスヘッドは視野へ入りにくいため、細い支持アームで小さい可動目印を視野へ運ぶ構成を推奨します。これは時刻信号を生成する装置ではなく、同じ変位をCSVと動画で観察するための目印ホルダです。

支持点はロードセル上流の可動クロスヘッド・その剛なブラケットを第一候補とします。写真だけでは取付穴、ねじ規格、必要なアーム長、干渉余裕は決められません。ロードセル本体やその下流へ無検証の重い部品を付けず、試料・下側固定部・配線との接触や、可動側と固定側をまたぐ力の経路を作らないよう確認します。小さい荷重測定では、目印の振動・接触・ケーブルの引張りも無視できるか検証します。

手順：静止中に試験機の移動量をゼロにし、その時点の可動目印位置を動画の基準位置p0として残します。目印面と同じ奥行きで校正した画素寸法sを使い、d_video(t)=s×[p(t)-p0]を求め、CSVの移動量d_csvと比較します。必要なら固定目印を差し引いてカメラの動きを補正します。

時刻差Δは、例えばΣ[d_video(t_csv+Δ)−d_csv]^2が小さくなるように求めます。ゼロ位置と縮尺は独立に定めます。一定速度区間だけで時刻差と任意の位置オフセットを両方自由に合わせると、それらを区別できなくなるため、両方を無制限に調整してはいけません。

MSAT-Liteの標準試験は移動量基準のサンプリングです。停止中にもCSVが連続して記録されると仮定しません。動き始め・停止の照合は、それらを記録できている範囲で行います。動画とCSVのどちらにイベントが記録されているかを確認してください。元動画のフレーム時刻を使用し、可変フレームレートを考慮します。CSVの時刻が実センサー時刻と一致するか、通信・処理遅延がどの程度かは、この配置図からは保証できません。

LEDが動画だけに写っても、その点灯時刻が荷重CSVに記録されなければ単独では同期基準になりません。機械が外部トリガに対応するかは提供資料で未確認です。高い時刻精度が必要になった場合は、その仕様をメーカーへ確認します。''','04_sync')

# 5. Initial assembly and validation decisions.
new('初回は、無負荷の動作確認 → 小ひずみ予備試験で判定する','写真とSTEPで確定できる寸法と、実物で決める項目を分ける。設定値は記録し、解析精度を実測する。')
with group('装置を組む順序'):
 todo=[('1','つかみの向き・開口を調整','両面がカメラへ向き、標線間10 mmが露出する。'),('2','スマホ・背景・照明を固定','レンズ中心を試料中央へ。ピントと倍率を固定する。'),('3','2つの目印を設置して無負荷移動','試料へ触れず、可動目印とCSVの変位が一致するか確認。'),('4','小ひずみ試験を実施','標線・幅・時刻対応・滑りを確認してから本試験へ。')]
 for k,(n,h,b) in enumerate(todo):
  yy=215+k*124;circle(100,yy+24,23,'teal');text(80,yy+3,40,42,n,28,'white',True,'center')
  text(145,yy,790,49,h,31,'navy',True);text(146,yy+54,800,43,b,23,'muted')
with group('実物で確認する項目'):
 rect(1000,211,530,488,'light',r=18)
 text(1025,230,480,50,'確認が必要な実物寸法・仕様',28,'teal',True)
 text(1025,313,480,160,'・クロスヘッド側の固定箇所\n・試料面から機械柱までの空間\n・使用レンズの最短撮影距離\n・動画での実効画素数',26,'navy')
 text(1025,517,480,145,'写真のロードセル表示は\n500 Nに見えるため要確認。\n小荷重域の精度は校正範囲で確認。',25,'orange',True)
rect(70,730,1460,67,'cyan',r=14)
text(85,746,1430,44,'本案は装置構成の設計資料。取付寸法・干渉・撮影精度・荷重精度は実機での検証が必要。',26,'teal',True,'center')
save('''初回は試料を取り付ける前に、軽い可動目印と固定目印を使った動作・同期の確認を行います。動作範囲を必要最小限に設定し、既存のリミット・停止機能を保ちます。その後、予備試料で把持の滑り・偏心・面外変形・画像計測の繰返し性を確認します。機械の操作パネルと非常停止は常にアクセスできる配置にします。

写真のロードセルラベルはCAP:500Nと読めるように見えますが、実物の型番・定格・校正資料で確認してください。断面積2 mm²、ヤング率1 MPa、縦ひずみ1%を仮定すると力は0.02 Nです。これは分解能検討の例で、今回のPMEの物性を決めているわけではありません。定格やCSVの表示桁数だけから小荷重域の精度は保証できません。目的とする力の範囲での仕様・ノイズ・校正を確認します。

MSAT-Liteの既確認事項：試験速度はメイン画面で設定し、本体詳細のトラバース速度・リターン速度と区別します。標準モードのサンプリング間隔は移動量µm基準で、間引き数0をまず使用します。例えば10 mm/min・5 µmが受け付けられる場合、理論上約0.03秒ごとの記録です。実際のCSVで確認します。これは200 mm/minのJIS標準速度から変更する小ひずみ物性測定の予備条件で、標準速度に準拠した試験と区別して報告します。

ヤング率は各試験片の断面積から求めた応力と、画像による縦ひずみで算出します。ポアソン比は同じ動画の幅方向・縦方向のひずみから算出します。本資料はカメラ・同期配置を決める案であり、装置の強度、取り付けボルト、可動部の全干渉、JISへの完全適合を証明するものではありません。''','05_validation')

ppt=OUT/'tensile_camera_sync_layout_editable.pptx';prs.save(ppt)
pdf=fitz.open()
for item in data:
 page=pdf.new_page(width=960,height=540);page.insert_image(page.rect,filename=item['preview'])
pdf.save(OUT/'tensile_camera_sync_layout.pdf',deflate=True);pdf.close()
notes=['# MCT-2150W 撮影・同期配置案','', 'ユーザー確認済みの前提：上下に同じつかみ治具を1組ずつ使用し、スマートフォン1台で構成する。','']
for i,item in enumerate(data,1):notes += [f'## {i}. '+item['title'],'',item['notes'],'']
(OUT/'layout_notes.md').write_text('\n'.join(notes))
(BASE/'slides.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))

def walk(ss):
 for s in ss:
  yield s
  if s.shape_type==MSO_SHAPE_TYPE.GROUP:yield from walk(s.shapes)
p=Presentation(ppt);ss=[x for s in p.slides for x in walk(s.shapes)]
assert len(p.slides)==5
assert all(s.notes_slide.notes_text_frame.text for s in p.slides)
assert not issues,issues
with ZipFile(ppt) as z:
 assert z.testzip() is None
 assert not any(x.startswith('ppt/media/') for x in z.namelist())
for s in ss:
 assert s.shape_type!=MSO_SHAPE_TYPE.PICTURE
 assert s.left>=0 and s.top>=0
 assert s.left+s.width<=p.slide_width+100
 assert s.top+s.height<=p.slide_height+100
report={'slides':5,'pictures':0,'nonempty_textboxes':sum(s.has_text_frame and bool(s.text.strip()) for s in ss),'layout_issues':issues,'pptx_bytes':ppt.stat().st_size}
(OUT/'layout_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
