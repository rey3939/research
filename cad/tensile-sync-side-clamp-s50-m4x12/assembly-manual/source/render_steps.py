from pathlib import Path
import argparse,importlib.util,json,math
import numpy as np
from PIL import Image,ImageChops,ImageOps
ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser();ap.add_argument('--design-root',type=Path,default=ROOT.parent if (ROOT.parent/'source/build_side_clamp.py').exists() else Path('/workspace/research/cad/tensile-sync-side-clamp-s50-m4x12'));args=ap.parse_args()
spec=importlib.util.spec_from_file_location('design',args.design_root/'source/build_side_clamp.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
S,cfg=g.module('R');fast,records=g.screws('R',cfg)
P={n.split('_')[0]:s for n,s in S.items()};F={}
for name,(s,h,shaft,receiver) in fast.items():F.setdefault(name.split('_')[1],[]).append(s)
COLORS={'old':'#c5d0d7','new':'#3e9db5','screw':'#e39135','metal':'#a4adb6','pad':'#dbb96b'}
cache={};renders=[]
def mesh(s):
 k=id(s)
 if k not in cache:
  vv,tt=s.tessellate(.12,.24);v=np.array([list(x.toTuple()) for x in vv]);t=np.array(tt,dtype=int);cache[k]=(s,v[t])
 return cache[k][1]
def shift(s,v):return s.translate(tuple(v))
def render(name,objects,elev=24,azim=-66,arrows=None,rings=None,labels=None):
 # Orthographic CPU z-buffer: solid front faces correctly hide rear triangles.
 from PIL import ImageDraw,ImageFont,ImageColor
 triangles=[];colors=[]
 for solid,col in objects:
  t=mesh(solid);triangles.append(t);rgb=np.array(ImageColor.getrgb(COLORS.get(col,col)),dtype=float)
  nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-12)
  light=np.array([-.3,-.5,.8]);light/=np.linalg.norm(light);fac=.58+.42*np.abs(nn@light)
  colors.append(np.clip(rgb[None,:]*fac[:,None],0,255).astype(np.uint8))
 t=np.concatenate(triangles);fc=np.concatenate(colors)
 el,az=np.radians([elev,azim]);view=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
 right=np.array([-np.sin(az),np.cos(az),0]);up=np.cross(view,right);matrix=np.stack([right,up,view],axis=1)
 proj=t@matrix;allp=proj.reshape(-1,3)
 extra=[p for aa,bb in arrows or [] for p in [aa,bb]]+[p for p,label in labels or []]
 if extra:allp=np.concatenate([allp,np.array(extra)@matrix])
 lo=allp[:,:2].min(0);hi=allp[:,:2].max(0);center=(lo+hi)/2
 width,height=1300,980;margin=52;scale=min((width-2*margin)/max(hi[0]-lo[0],1),(height-2*margin)/max(hi[1]-lo[1],1))
 def project(points):
  r=np.asarray(points)@matrix;r=np.array(r,copy=True);r[...,0]=(r[...,0]-center[0])*scale+width/2;r[...,1]=-(r[...,1]-center[1])*scale+height/2;return r
 q=project(t);canvas=np.full((height,width,3),255,dtype=np.uint8);zbuf=np.full((height,width),-np.inf,dtype=np.float32)
 for v,col in zip(q,fc):
  x0=max(0,int(np.floor(v[:,0].min())));x1=min(width-1,int(np.ceil(v[:,0].max())));y0=max(0,int(np.floor(v[:,1].min())));y1=min(height-1,int(np.ceil(v[:,1].max())))
  if x1<x0 or y1<y0:continue
  a,b,c=v;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-9:continue
  xx=np.arange(x0,x1+1)[None,:]+.5;yy=np.arange(y0,y1+1)[:,None]+.5
  wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
  wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
  depth=wa*a[2]+wb*b[2]+wc*c[2];area=zbuf[y0:y1+1,x0:x1+1];take=(wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7)&(depth>area)
  area[take]=depth[take];canvas[y0:y1+1,x0:x1+1][take]=col
 im=Image.fromarray(canvas);d=ImageDraw.Draw(im)
 for a,b in arrows or []:
  aa=project(a)[:2];bb=project(b)[:2];d.line([tuple(aa),tuple(bb)],fill='#c5423d',width=6)
  th=np.arctan2(bb[1]-aa[1],bb[0]-aa[0]);rr=19
  p1=bb-rr*np.array([np.cos(th),np.sin(th)])+rr*.5*np.array([-np.sin(th),np.cos(th)])
  p2=bb-rr*np.array([np.cos(th),np.sin(th)])-rr*.5*np.array([-np.sin(th),np.cos(th)])
  d.polygon([tuple(bb),tuple(p1),tuple(p2)],fill='#c5423d')
 for centerpoint,axis in rings or []:
  x,y=project(centerpoint)[:2];r=18;d.ellipse((x-r,y-r,x+r,y+r),outline='#c5423d',width=5)
 label_font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',32)
 for point,label in labels or []:
  x,y=project(point)[:2];bb=d.textbbox((x,y),label,font=label_font);d.rectangle((bb[0]-7,bb[1]-5,bb[2]+7,bb[3]+5),fill='white',outline='#708899',width=2);d.text((x,y),label,font=label_font,fill='#17334a')
 bb=ImageChops.difference(im,Image.new('RGB',im.size,'white')).convert('L').point(lambda x:255 if x>15 else 0).getbbox()
 if bb:im=im.crop(bb)
 im=ImageOps.expand(im,border=24,fill='white');path=ROOT/'views'/(name+'.png');im.save(path);renders.append(name)

def screws(group,col='screw',offset=(0,0,0)):
 return [(shift(s,offset),col) for s in F[group]]
def screw_arrows(group,offset):
 arr=[]
 for name,(s,h,shaft,receiver) in fast.items():
  if name.split('_')[1]!=group:continue
  h=np.array(h.Center().toTuple());sh=np.array(shaft.Center().toTuple());axis=(sh-h)/np.linalg.norm(sh-h);start=sh+axis*7+np.array(offset);arr.append((start,start+axis*13))
 return arr
# Separate parts and tap entrances, in their local coordinates.
local={'01':g.clamp_body(),'02':g.pad(),'03':g.hbar(),'04':g.corner(),'05':g.rail(190),'06':g.depth_carriage(),'07':g.cross_carriage(),'08':g.flag()}
for n,s in local.items():render('part_'+n,[(s,'new' if n!='02' else 'pad')])
render('tap_01',[(local['01'],'old')],rings=[((-9,-10,0),(0,-1,0)),((9,-10,0),(0,-1,0)),((35.2,9,0),(1,0,0))])
render('tap_04',[(local['04'],'old')],rings=[((x,-24,z),(0,-1,0)) for x,z in [(46,0),(70,0),(58,-11),(58,11)]])
render('tap_06',[(local['06'],'old')],rings=[((58,-38,z),(0,-1,0)) for z in [-10,10]])
render('tap_07',[(local['07'],'old')],elev=-26,rings=[((72,y,3),(0,0,-1)) for y in [-5,5]]+[((x,-11,22),(0,-1,0)) for x in [64,80]])
patch=g.box(-25,25,0,20,113,127)
render('clamp_fit',[(P['01'],'new'),(P['02'],'pad'),(patch,'metal')]+screws('P'),elev=26,azim=-65)
# Progressively assembled scenes: blue is newly attached, orange is the current screw group.
render('A_exploded',[(P['01'],'old'),(shift(P['03'],(0,-18,0)),'new')]+screws('A',offset=(0,-38,0)),arrows=screw_arrows('A',(0,-38,0)))
upper=[(P['01'],'old'),(P['03'],'old')]+screws('A','old')
render('A_done',[(P['01'],'old'),(P['03'],'new')]+screws('A'))
render('B_exploded',upper+[(shift(P['04'],(0,-24,0)),'new')]+screws('B',offset=(0,22,0)),azim=110,arrows=screw_arrows('B',(0,22,0)))
render('B_done',upper+[(P['04'],'new')]+screws('B'),azim=110)
upper+= [(P['04'],'old')]+screws('B','old')
rail_top=P['05'].intersect(g.box(40,75,-35,-15,90,150))
render('C_exploded',upper+[(shift(rail_top,(0,-20,0)),'new')]+screws('C',offset=(0,-42,0)),arrows=screw_arrows('C',(0,-42,0)))
render('C_done',upper+[(rail_top,'new')]+screws('C'))
render('E_exploded',[(P['06'],'old'),(shift(P['07'],(0,0,25)),'new')]+screws('E',offset=(0,0,-25)),elev=-30,arrows=screw_arrows('E',(0,0,-25)))
render('E_done',[(P['06'],'old'),(P['07'],'new')]+screws('E'),elev=-30)
lower=[(P['06'],'old'),(P['07'],'old')]+screws('E','old')
render('F_exploded',lower+[(shift(P['08'],(0,-23,0)),'new')]+screws('F',offset=(0,-45,0)),arrows=screw_arrows('F',(0,-45,0)))
render('F_done',lower+[(P['08'],'new')]+screws('F'))
lower += [(P['08'],'old')]+screws('F','old')
rail_bottom=P['05'].intersect(g.box(40,75,-35,-15,-45,20))
render('D_exploded',[(rail_bottom,'old')]+[(shift(s,(0,-27,0)),'new' if col=='old' else col) for s,col in lower]+screws('D',offset=(0,25,0)),azim=110,arrows=screw_arrows('D',(0,25,0)))
render('D_done',[(rail_bottom,'old')]+[(s,'new') for s,col in lower]+screws('D'),azim=110)
allparts=[(s,'pad' if n=='02' else 'new') for n,s in P.items()]
allbolts=[(s,'screw') for group in F.values() for s in group]
render('complete',allparts+allbolts,elev=12,azim=-82)
render('mounted_reference',allparts+allbolts+[(patch,'metal')],elev=16,azim=-73)
render('adjust_lower',[(P['05'].intersect(g.box(40,75,-35,-15,-45,30)),'old')]+lower+screws('D'),elev=24,azim=-68,labels=[((58,-24,-30),'D'),((82,14,-20),'E'),((83,-1,5),'F')])
(ROOT/'render_validation.json').write_text(json.dumps({'images':renders,'side':'R','screw_groups':{k:len(v) for k,v in F.items()},'tap_pilot_mm':g.P['tap_pilot_d'],'clearance_mm':g.P['clearance_d'],'clamped_span_mm':50,'exploded_arrows':'screw insertion direction derived from head and shaft CAD centers','partial_rail_views':['C','D']},ensure_ascii=False,indent=2)+'\n')
print('Rendered',len(renders),'images')
