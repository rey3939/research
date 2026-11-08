from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import fitz,json

ROOT=Path(__file__).resolve().parent.parent;W,H=1600,2100
REG='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
NAVY='#17334a';TEAL='#007f86';MUTED='#536b7c';ORANGE='#b45426';GRAY='#e8eef2'
pages=[];issues=[]
def ft(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
def text(x,y,w,s,n=30,b=False,c=NAVY,spacing=1.42):
 font=ft(n,b);lines=[]
 for para in s.split('\n'):
  line=''
  for ch in para:
   if line and font.getlength(line+ch)>w:lines.append(line);line=ch
   else:line+=ch
  lines.append(line)
 for i,line in enumerate(lines):d.text((x,y+i*n*spacing),line,font=font,fill=c,anchor='lt')
 end=y+len(lines)*n*spacing
 if end>2020:issues.append((s[:30],end))
 return end
def header(title,sub):
 global im,d
 im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,15),fill=TEAL)
 text(75,55,1450,title,52,True);text(78,145,1440,sub,28,c=MUTED)
 d.line((75,2020,1525,2020),fill='#bacbd6',width=2)
 d.text((80,2050),'同期目印ホルダ／S50側面クランプ・全ねじM4×12／単位mm',font=ft(23),fill=MUTED,anchor='lt')
 d.text((1480,2045),str(len(pages)+1),font=ft(30,True),fill=TEAL,anchor='lt')
def image(path,x,y,w,h):
 a=Image.open(path).convert('RGB');a.thumbnail((w,h));im.paste(a,(int(x+(w-a.width)/2),int(y+(h-a.height)/2)))
def card(x,y,w,h,s,n=29,c=NAVY,fill='#edf6f6'):
 d.rounded_rectangle((x,y,x+w,y+h),radius=15,fill=fill)
 text(x+24,y+22,w-48,s,n,c=c)
def done(name):
 p=ROOT/'views'/name;im.save(p);pages.append(p)
