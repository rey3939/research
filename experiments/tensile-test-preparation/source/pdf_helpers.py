from pathlib import Path
import json,fitz,math
ROOT=Path(__file__).resolve().parent.parent
W,H=595.28,841.89;M=36
NAVY=(.09,.20,.29);TEAL=(.0,.47,.52);MUTED=(.32,.40,.46);RED=(.70,.22,.18);ORANGE=(.76,.39,.10);LIGHT=(.93,.96,.97)
# Pre-subset the installed CJK fonts so the PDF remains small and searchable.
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter,Options
import tempfile,shutil
font_dir=Path(tempfile.mkdtemp(prefix='s50_manual_fonts_'))
chars=set(map(ord,Path(__file__).read_text()+(ROOT/'source/pdf_helpers.py').read_text()))
for weight in ['Regular','Bold']:
 original=TTFont('/usr/share/fonts/opentype/noto/NotoSansCJK-'+weight+'.ttc',fontNumber=0)
 opts=Options();opts.recalc_timestamp=False;opts.retain_gids=True;sub=Subsetter(options=opts);sub.populate(unicodes=chars);sub.subset(original);original.save(font_dir/(weight+'.otf'))
FONT=fitz.Font(fontfile=str(font_dir/'Regular.otf'));BOLD=fitz.Font(fontfile=str(font_dir/'Bold.otf'))

doc=fitz.open();issues=[];pages=[]
def text(p,x,y,w,s,size=12,bold=False,color=NAVY,leading=1.5):
 f=BOLD if bold else FONT;name='FB' if bold else 'FR';lines=[]
 for para in s.split('\n'):
  line=''
  for c in para:
   if line and f.text_length(line+c,fontsize=size)>w:lines.append(line);line=c
   else:line+=c
  lines.append(line)
 for i,line in enumerate(lines):
  yy=y+size+i*size*leading
  if yy>805 and y<814:issues.append({'page':len(doc),'text':line,'bottom':yy})
  p.insert_text((x,yy),line,fontname=name,fontsize=size,color=color)
 return y+len(lines)*size*leading

def new(title,sub):
 p=doc.new_page(width=W,height=H);p.insert_font(fontname='FR',fontbuffer=FONT.buffer);p.insert_font(fontname='FB',fontbuffer=BOLD.buffer)
 p.draw_rect(fitz.Rect(0,0,W,7),fill=TEAL,color=None)
 text(p,M,23,W-2*M,title,22,True);text(p,M,59,W-2*M,sub,10.5,color=MUTED)
 p.draw_line((M,83),(W-M,83),color=(.77,.83,.86),width=.7)
 p.draw_line((M,814),(W-M,814),color=(.77,.83,.86),width=.7)
 text(p,M,821,440,'引張試験｜準備・測定・解析への引継ぎ｜2026-11-10',8.6,color=MUTED)
 p.insert_text((W-55,830),str(len(doc)),fontname='FB',fontsize=10,color=TEAL)
 pages.append(title);return p
