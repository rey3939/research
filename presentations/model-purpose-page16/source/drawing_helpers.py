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

BASE=Path(__file__).resolve().parent.parent; OUT=BASE; ASSET=BASE/'assets'
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
