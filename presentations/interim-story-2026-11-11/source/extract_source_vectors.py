"""Copy source PDF plot-marker geometry; do not infer numerical observations."""
from pathlib import Path
import argparse,json
import fitz

ROOT=Path(__file__).resolve().parent.parent
COLORS={'t1':(0,.502,1),'t2':(1,.502,0),'t3':(1,.824,0),'t4':(.502,0,.251),'Bx':(0,0,1),'By':(1,0,0),'Bz':(0,.502,0)}

def outline(d):
 out=[]
 for it in d['items']:
  if it[0]=='l':
   a,b=it[1:]
   if not out:out.append([a.x,a.y])
   out.append([b.x,b.y])
  elif it[0]=='c':
   a,b,c,e=it[1:]
   if not out:out.append([a.x,a.y])
   for i in range(1,13):
    t=i/12;v=1-t
    out.append([v**3*a.x+3*v*v*t*b.x+3*v*t*t*c.x+t**3*e.x,v**3*a.y+3*v*v*t*b.y+3*v*t*t*c.y+t**3*e.y])
  elif it[0]=='re':
   r=it[1];out.extend([[r.x0,r.y0],[r.x1,r.y0],[r.x1,r.y1],[r.x0,r.y1]])
  else:raise ValueError(it[0])
 return out

def extract(path):
 doc=fitz.open(path);assert len(doc)==48
 # Read the frame/tick provenance already stored with this source version.
 charts=json.loads((ROOT/'data/source_plot_vectors.json').read_text())
 for key,c in charts.items():
  x0,y0,x1,y1=c['frame'];c['markers']=[]
  for series in c['series']:
   candidates=[]
   for d in doc[c['page']-1].get_drawings():
    f=d['fill'];r=d['rect']
    if f and sum((a-b)**2 for a,b in zip(f,COLORS[series]))<.001 and 1<r.width<12 and 1<r.height<12 and y0-6<r.y0 and r.y1<y1+6:
     candidates.append(d)
   for xv in c['xvalues']:
    tx=x0+(x1-x0)*(xv-c['xrange'][0])/(c['xrange'][1]-c['xrange'][0])
    d=min(candidates,key=lambda d:abs((d['rect'].x0+d['rect'].x1)/2-tx))
    assert abs((d['rect'].x0+d['rect'].x1)/2-tx)<1.05,(key,series,xv)
    c['markers'].append({'series':series,'x_label':xv,'points':outline(d),'fill':'%02X%02X%02X'%tuple(round(t*255) for t in d['fill'])})
  assert len(c['markers'])==len(c['xvalues'])*len(c['series'])
 (ROOT/'data/source_plot_vectors.json').write_text(json.dumps(charts,ensure_ascii=False,indent=2)+'\n')
 print('Copied',sum(len(c['markers']) for c in charts.values()),'source plot symbols')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pdf',type=Path,required=True);a=p.parse_args();extract(a.pdf)
