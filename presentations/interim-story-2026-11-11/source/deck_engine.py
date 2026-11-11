from pathlib import Path
from contextlib import contextmanager
import math,json,tempfile,shutil
import fitz
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter,Options
from pptx import Presentation
from pptx.util import Inches,Pt,Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE,MSO_SHAPE
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement

ROOT=Path(__file__).resolve().parent.parent
W,H=1600,900;K=.6;U=7620
C={'ink':'183044','muted':'647787','teal':'007F86','pale':'E9F5F4','blue':'2184C8','bluepale':'EAF1FA','orange':'C96932','peach':'FFF0E5','purple':'80345F','gray':'CCD7DD','light':'F4F7F9','white':'FFFFFF','dark':'213B50','red':'C9454B','green':'267D5E','gold':'B5870B'}
def color(s):
 s=C.get(s,s);return tuple(int(s[i:i+2],16)/255 for i in (0,2,4))
def rgb(s):return RGBColor.from_string(C.get(s,s))
def em(v):return Emu(round(v*U))

font_dir=Path(tempfile.mkdtemp(prefix='interim_story_fonts_'))
chars=set(ord(c) for p in (ROOT/'source').glob('*.py') for c in p.read_text())
F={}
for weight in ['Regular','Bold']:
 f=TTFont('/usr/share/fonts/opentype/noto/NotoSansCJK-'+weight+'.ttc',fontNumber=0)
 missing=[chr(c) for c in chars if not chr(c).isspace() and c not in f.getBestCmap()]
 assert not missing,('unsupported_font_characters',missing)
 opts=Options();opts.recalc_timestamp=False;opts.retain_gids=True
 sub=Subsetter(options=opts);sub.populate(unicodes=chars);sub.subset(f)
 path=font_dir/(weight+'.otf');f.save(path);F[weight]=fitz.Font(fontfile=str(path))

prs=Presentation();prs.slide_width=Inches(13.333333333);prs.slide_height=Inches(7.5)
prs.core_properties.title='永久磁石エラストマーの曲げ変形による磁場変化｜中間審査会 改訂版'
prs.core_properties.author='大橋 怜倭';prs.core_properties.subject='実測結果から仮説、1次元追従モデルによる定性的検証へ。本編17枚・約10分。'
pdf=fitz.open();slides=[];issues=[];all_text=[];cur=None;page=None;slide=None

def rect(x,y,w,h,fill='white',stroke=None,lw=1.5,r=0):
 s=cur.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE,em(x),em(y),em(w),em(h))
 if fill:s.fill.solid();s.fill.fore_color.rgb=rgb(fill)
 else:s.fill.background()
 if stroke:s.line.color.rgb=rgb(stroke);s.line.width=Pt(lw*K)
 else:s.line.fill.background()
 if r:
  try:s.adjustments[0]=min(.15,r/min(w,h))
  except Exception:pass
 rr=fitz.Rect(x*K,y*K,(x+w)*K,(y+h)*K)
 page.draw_rect(rr,color=color(stroke) if stroke else None,fill=color(fill) if fill else None,width=lw*K)
 return s

def poly(points,fill=None,stroke='ink',lw=2,closed=False):
 if len(points)<2:return
 b=cur.shapes.build_freeform(round(points[0][0]*10),round(points[0][1]*10),scale=U/10)
 b.add_line_segments([(round(x*10),round(y*10)) for x,y in points[1:]],close=closed)
 s=b.convert_to_shape()
 if fill:s.fill.solid();s.fill.fore_color.rgb=rgb(fill)
 else:s.fill.background()
 if stroke:s.line.color.rgb=rgb(stroke);s.line.width=Pt(lw*K)
 else:s.line.fill.background()
 sh=page.new_shape();sh.draw_polyline([(x*K,y*K) for x,y in points])
 sh.finish(color=color(stroke) if stroke else None,fill=color(fill) if fill else None,width=lw*K,closePath=closed);sh.commit()
 return s

def line(x1,y1,x2,y2,c='ink',lw=2,dash=False):
 if dash:
  length=math.hypot(x2-x1,y2-y1);n=max(1,math.ceil(length/12))
  for i in range(0,n,2):
   a=i/n;b=min((i+1)/n,1);poly([(x1+(x2-x1)*a,y1+(y2-y1)*a),(x1+(x2-x1)*b,y1+(y2-y1)*b)],stroke=c,lw=lw)
 else:return poly([(x1,y1),(x2,y2)],stroke=c,lw=lw)

def arrow(x1,y1,x2,y2,c='teal',lw=4,head=13):
 line(x1,y1,x2,y2,c,lw);a=math.atan2(y2-y1,x2-x1)
 p=[(x2,y2),(x2-head*math.cos(a)+head*.5*math.sin(a),y2-head*math.sin(a)-head*.5*math.cos(a)),(x2-head*math.cos(a)-head*.5*math.sin(a),y2-head*math.sin(a)+head*.5*math.cos(a))]
 poly(p,fill=c,stroke=None,closed=True)

def circle(x,y,r,fill='teal',stroke=None,lw=2):
 s=cur.shapes.add_shape(MSO_SHAPE.OVAL,em(x-r),em(y-r),em(r*2),em(r*2))
 if fill:s.fill.solid();s.fill.fore_color.rgb=rgb(fill)
 else:s.fill.background()
 if stroke:s.line.color.rgb=rgb(stroke);s.line.width=Pt(lw*K)
 else:s.line.fill.background()
 page.draw_oval(fitz.Rect((x-r)*K,(y-r)*K,(x+r)*K,(y+r)*K),color=color(stroke) if stroke else None,fill=color(fill) if fill else None,width=lw*K)
 return s

def measure(s,size,bold=False):return F['Bold' if bold else 'Regular'].text_length(s,fontsize=size)
def wrap(s,width,size,bold=False):
 out=[]
 for para in s.split('\n'):
  v=''
  for c in para:
   if v and measure(v+c,size,bold)>width:out.append(v);v=c
   else:v+=c
  out.append(v)
 return out

def text(x,y,w,h,s,size=34,c='ink',bold=False,align='left',wrapped=False):
 ls=wrap(s,w,size,bold) if wrapped else s.split('\n');lh=size*1.28
 if len(ls)*lh>h+2:issues.append({'slide':len(slides),'kind':'text_height','text':s[:50],'need':len(ls)*lh,'height':h})
 if x<0 or y<0 or x+w>W+.1 or y+h>H+.1:issues.append({'slide':len(slides),'kind':'text_bounds','text':s[:40]})
 for a in ls:
  if measure(a,size,bold)>w+2:issues.append({'slide':len(slides),'kind':'text_width','text':a,'width':w,'need':measure(a,size,bold)})
 box=cur.shapes.add_textbox(em(x),em(y),em(w),em(h));tf=box.text_frame;tf.clear();tf.word_wrap=False
 tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.vertical_anchor=MSO_ANCHOR.TOP
 fkey='Bold' if bold else 'Regular';fn='FB' if bold else 'FR'
 for i,a in enumerate(ls):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=a;p.alignment={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}[align]
  p.space_before=Pt(0);p.space_after=Pt(0);p.line_spacing=Pt(lh*K)
  for run in p.runs:
   run.font.name='Yu Gothic';run.font.size=Pt(size*K);run.font.bold=bold;run.font.color.rgb=rgb(c)
   ea=OxmlElement('a:ea');ea.set('typeface','Yu Gothic');run._r.get_or_add_rPr().append(ea)
  width=measure(a,size,bold);dx=0 if align=='left' else (w-width)/2 if align=='center' else w-width
  page.insert_text(((x+dx)*K,(y+i*lh+size)*K),a,fontname=fn,fontsize=size*K,color=color(c))
 all_text.append(s);return box

@contextmanager
def group(name):
 global cur
 old=cur;g=old.shapes.add_group_shape();g.name=name;cur=g
 yield g
 if len(g.shapes):g.shapes._recalculate_extents()
 cur=old

def pill(x,y,w,s,kind='teal',size=23):
 rect(x,y,w,42,'pale' if kind=='teal' else 'peach' if kind=='orange' else 'light',r=12)
 text(x+10,y+5,w-20,32,s,size,kind,True,'center')

def new(title,section,notes,seconds=0,source='',backup=False):
 global slide,cur,page
 slide=prs.slides.add_slide(prs.slide_layouts[6]);cur=slide
 page=pdf.new_page(width=W*K,height=H*K)
 page.insert_font(fontname='FR',fontbuffer=F['Regular'].buffer);page.insert_font(fontname='FB',fontbuffer=F['Bold'].buffer)
 n=len(slides)+1;label=f'A{n-17:02d}' if backup else f'{n:02d}'
 slides.append({'number':n,'label':label,'title':title,'section':section,'seconds':seconds,'source':source,'notes':notes,'backup':backup})
 rect(0,0,1600,9,'orange' if section in ['考察・仮説','モデル｜今後','今後の予定'] else 'teal')
 text(62,24,1480,32,section,22,'orange' if section in ['考察・仮説','モデル｜今後','今後の予定'] else 'teal',True)
 text(62,69,1470,74,title,47,'ink',True)
 line(62,153,1538,153,'gray',1)
 if source:text(64,838,1460,24,source,16,'muted')
 text(64,871,1320,24,'名古屋工業大学　機能設計研究室｜大橋 怜倭',16,'muted')
 text(1435,866,100,31,label,22,'muted',False,'right')
 slide.notes_slide.notes_text_frame.text=f'【話す内容】\n{notes}\n\n【目安】{seconds}秒\n【出典】{source}\n【図について】概念図は模式図。実測グラフの点は元PDFのプロット位置を保持。モデルの解析結果は未取得。'
 return slide

def takeaway(s,kind='teal',y=751,size=31):
 rect(62,y,1476,72,'pale' if kind=='teal' else 'peach',r=12)
 text(83,y+15,1434,48,s,size,kind,True,'center')

def curved_strip(x,y,L,bend=0,thick=30,c='teal',particles=False,segments=False,dashed=False):
 pts=[];normals=[]
 count=9 if segments else 45
 for i in range(count):
  q=i/(count-1);f=q*q*(3-q)/2;df=3*q-1.5*q*q
  px=x-bend*f;py=y+L*q;dx=-bend*df;dy=L;rr=math.hypot(dx,dy)
  pts.append((px,py));normals.append((-dy/rr,dx/rr))
 if thick:
  left=[(p[0]+n[0]*thick/2,p[1]+n[1]*thick/2) for p,n in zip(pts,normals)]
  right=[(p[0]-n[0]*thick/2,p[1]-n[1]*thick/2) for p,n in zip(pts,normals)]
  poly(left+right[::-1],fill='pale',stroke=c,lw=2,closed=True)
 for i in range(len(pts)-1):line(*pts[i],*pts[i+1],c,2.5,dashed)
 if segments:
  for p in pts:circle(*p,4,'white',c,1.5)
 if particles:
  for j in [2,4,6] if segments else [9,18,27,36]:
   p=pts[j];n=normals[j];circle(*p,6,c);arrow(p[0],p[1],p[0]+n[0]*39,p[1]+n[1]*39,c,2.8,9)
 return pts,normals

def clamp(x,y,w=125):
 rect(x-w/2,y-28,w,29,'gray')
 for a in range(6):line(x-w/2+a*w/6,y-28,x-w/2+a*w/6-13,y-44,'muted',2)

def axes(x,y,w,h,xlabel='先端変位 u [mm]',ylabel='磁束密度変化 ΔBy',xmax=4):
 arrow(x,y+h,x+w,y+h,'muted',2.5,9);arrow(x,y+h,x,y,'muted',2.5,9)
 text(x-5,y-38,w+10,31,ylabel,23,'muted')
 text(x,y+h+18,w,35,xlabel,23,'muted',False,'center')

def tiny_robot(x,y,scale=1):
 rect(x,y,190*scale,75*scale,'pale','teal',r=15)
 for k in range(3):
  xp=x+35*scale+k*55*scale
  pts=[(xp,y+70*scale),(xp-10*scale,y+120*scale),(xp+2*scale,y+165*scale),(xp+40*scale,y+184*scale)]
  poly(pts,stroke='teal',lw=15*scale)
 circle(x+95*scale,y+210*scale,33*scale,'peach','orange',2)

_original_curved_strip=curved_strip
def curved_strip(*args,**kwargs):
 with group('PMEの模式図：中心線・外形・磁気モーメント'):
  return _original_curved_strip(*args,**kwargs)
