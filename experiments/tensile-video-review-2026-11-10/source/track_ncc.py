from pathlib import Path
import cv2,numpy as np,pandas as pd,json
from scipy.ndimage import gaussian_filter1d
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--workdir',type=Path,required=True);args=ap.parse_args()
p=args.workdir;frames=json.loads((p/'analysis/frame_index.json').read_text());im0=cv2.imread(frames[0]['file'],0)
regions={'upper_mark':(298,885,150,110),'lower_mark':(292,1480,150,120),'upper_grip':(140,480,470,85),'lower_grip':(130,1815,500,120)}
templates={};centers={}
for n,(x,y,w,h) in regions.items():templates[n]=im0[y:y+h,x:x+w];centers[n]=np.array([x+w/2,y+h/2],float)
Lref=float(np.linalg.norm(centers['lower_mark']-centers['upper_mark']));previous={n:xy.copy() for n,xy in centers.items()};lambda_y=1.;lambda_x=1.;out=[]
def subpix(r,pt):
 x,y=pt
 def s(a,b,c):
  q=a-2*b+c
  return float(np.clip(.5*(a-c)/q,-.8,.8)) if abs(q)>1e-9 else 0.
 dx=s(r[y,x-1],r[y,x],r[y,x+1]) if 0<x<r.shape[1]-1 else 0
 dy=s(r[y-1,x],r[y,x],r[y+1,x]) if 0<y<r.shape[0]-1 else 0
 return np.array([x+dx,y+dy])
def match(im,name,center,sx,sy,delta=45):
 templ=templates[name];h,w=templ.shape;tw=max(20,int(round(w*sx)));th=max(20,int(round(h*sy)))
 if tw>=im.shape[1] or th>=im.shape[0]:return np.array([np.nan,np.nan]),np.nan
 tt=cv2.resize(templ,(tw,th),interpolation=cv2.INTER_LINEAR)
 x0=max(0,int(center[0]-tw/2-delta));x1=min(im.shape[1],int(center[0]+tw/2+delta+2));y0=max(0,int(center[1]-th/2-delta));y1=min(im.shape[0],int(center[1]+th/2+delta+2))
 if x1-x0<tw+3 or y1-y0<th+3:return np.array([np.nan,np.nan]),np.nan
 search=im[y0:y1,x0:x1];res=cv2.matchTemplate(search,tt,cv2.TM_CCOEFF_NORMED);_,score,_,pt=cv2.minMaxLoc(res);xy=subpix(res,pt)+[x0+tw/2,y0+th/2];return xy,float(score)
def width(im,a,b,fraction=.5):
 center=(a+b)/2;cx,cy=np.round(center).astype(int);half=int(np.clip(np.linalg.norm(a-b)*.08,25,95))
 if cy-half<0 or cy+half>=im.shape[0] or cx-130<0 or cx+130>=im.shape[1]:return [np.nan]*4
 z=im[cy-half:cy+half+1,cx-130:cx+131];prof=gaussian_filter1d(np.median(z,axis=0).astype(float),1.1);fg=np.median(prof[115:146]);bl=np.median(prof[:20]);br=np.median(prof[-20:]);tl=bl+fraction*(fg-bl);tr=br+fraction*(fg-br);xs=np.arange(260)
 left=np.flatnonzero((prof[:-1]<tl)&(prof[1:]>=tl)&(xs>=20)&(xs<110));right=np.flatnonzero((prof[:-1]>=tr)&(prof[1:]<tr)&(xs>150)&(xs<245))
 if len(left)==0 or len(right)==0:return [np.nan]*4
 k=int(left[-1]);j=int(right[0]);xl=k+(tl-prof[k])/(prof[k+1]-prof[k]);xr=j+(tr-prof[j])/(prof[j+1]-prof[j]);cos=abs((b[1]-a[1])/np.linalg.norm(b-a));return [(xr-xl)*cos,cx-130+xl,cx-130+xr,cy]
wref=width(im0,centers['upper_mark'],centers['lower_mark'])[0]
for i,fr in enumerate(frames):
 im=cv2.imread(fr['file'],0);row={'time_s':fr['time_s'],'frame_index':i*6};cur={}
 for name in ['upper_mark','lower_mark']:
  # Direct registration to the original texture avoids accumulated feature-loss drift.
  candidates=[]
  for ys in [lambda_y*.985,lambda_y,lambda_y*1.015]:
   xy,score=match(im,name,previous[name],lambda_x,ys)
   if np.isfinite(score):candidates.append((score,xy,ys))
  if not candidates:continue
  score,xy,ys=max(candidates,key=lambda v:v[0]);cur[name]=xy;previous[name]=xy
  row[name+'_score']=score;row[name+'_x_px']=float(xy[0]);row[name+'_y_px']=float(xy[1])
 for name in ['upper_grip','lower_grip']:
  xy,score=match(im,name,previous[name],1.,1.,delta=15 if i else 25)
  if np.isfinite(score) and score>.5:previous[name]=xy;cur[name]=xy
  row[name+'_score']=score;row[name+'_x_px']=float(xy[0]);row[name+'_y_px']=float(xy[1])
 if 'upper_mark' in cur and 'lower_mark' in cur:
  a,b=cur['upper_mark'],cur['lower_mark'];L=float(np.linalg.norm(b-a));row['gauge_length_px']=L
  for f in [.4,.5,.6]:
   w,xl,xr,yy=width(im,a,b,f);row[f'width_{f:.1f}_px']=w
   if f==.5:row['edge_left_px']=xl;row['edge_right_px']=xr;row['width_row_y_px']=yy
  if np.isfinite(row['width_0.5_px']) and min(row['upper_mark_score'],row['lower_mark_score'])>.65:
   lambda_y=float(np.clip(L/Lref,.9,1.9));lambda_x=float(np.clip(row['width_0.5_px']/wref,.6,1.1))
  # Check for a visible open gap using positions from the preceding and current marks.
  lo=int(min(a[1],b[1])+40);hi=int(max(a[1],b[1])-40);xs=int((a[0]+b[0])/2)
  if 0<=lo<hi<im.shape[0]:
   cnt=(im[lo:hi,max(0,xs-115):xs+116]>105).sum(1);run=best=0
   for flag in cnt<5:run=run+1 if flag else 0;best=max(run,best)
   row['empty_gap_run_rows']=best
 if np.isfinite(row.get('upper_grip_y_px',np.nan)) and np.isfinite(row.get('lower_grip_y_px',np.nan)):
  row['upper_grip_displacement_px']=(row['lower_grip_y_px']-row['upper_grip_y_px'])-(centers['lower_grip'][1]-centers['upper_grip'][1])
 out.append(row)
 if i%100==0:print(i,fr['time_s'],row.get('gauge_length_px'),row.get('upper_mark_score'),row.get('lower_mark_score'),flush=True)
d=pd.DataFrame(out);b=d[(d.time_s>=3)&(d.time_s<=10)];L0=float(b.gauge_length_px.median());w0=float(b['width_0.5_px'].median());d['axial_strain']=d.gauge_length_px/L0-1;d['transverse_strain']=d['width_0.5_px']/w0-1;d.to_csv(p/'analysis/video_ncc_tracking.csv',index=False)
s={'method':'direct normalized cross correlation to original marker-region textures, with axial and transverse scale search; no camera-scale correction','initial_gauge_length_px':L0,'initial_mid_gauge_width_px':w0,'static_interval_s':[3,10],'static_gauge_std_px':float(b.gauge_length_px.std()),'static_width_std_px':float(b['width_0.5_px'].std()),'static_gauge_range_px':float(b.gauge_length_px.max()-b.gauge_length_px.min()),'static_width_range_px':float(b['width_0.5_px'].max()-b['width_0.5_px'].min()),'reference_centers':{k:v.tolist() for k,v in centers.items()}}
(p/'analysis/ncc_summary.json').write_text(json.dumps(s,indent=2)+'\n');print(s)
