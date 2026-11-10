from pathlib import Path
import cv2,numpy as np,pandas as pd,json
from scipy.stats import linregress
from scipy.ndimage import gaussian_filter1d
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--workdir',type=Path,required=True);args=ap.parse_args()
p=args.workdir;d=pd.read_csv(p/'analysis/video_ncc_tracking.csv');c=pd.read_csv(p/'analysis/force_data_utf8.csv');fr=json.loads((p/'analysis/frame_index.json').read_text());b=d[(d.time_s>=3)&(d.time_s<=10)]
# An onset fit uses stationary footage and visible grip motion; it does not align two arbitrary straight lines.
ok=(d.time_s<=58)&(d.upper_grip_score>.85)&(d.lower_grip_score>.65);t=d.loc[ok,'time_s'].to_numpy();v=d.loc[ok,'upper_grip_displacement_px'].to_numpy();fits=[]
for t0 in np.arange(15,19.001,.005):
 x=np.maximum(t-t0,0);coef=np.linalg.lstsq(np.c_[np.ones(len(x)),x],v,rcond=None)[0];res=v-(coef[0]+coef[1]*x);fits.append((np.mean(res**2),t0,*coef))
best=min(fits);csvfit=linregress(c.time_s.iloc[2:],c.crosshead_mm.iloc[2:]);csv_onset=-csvfit.intercept/csvfit.slope
rupture=int(np.flatnonzero(d.empty_gap_run_rows.to_numpy()>=10)[0]);vbreak=[float(d.time_s.iloc[rupture-1]),float(d.time_s.iloc[rupture])];df=c.force_N.diff();ix=int(df.idxmin());cbreak=[float(c.time_s.iloc[ix-1]),float(c.time_s.iloc[ix])]
offset_break=(sum(vbreak)-sum(cbreak))/2;offset_start=best[1]-csv_onset
sync={'video_visible_gap_window_s':vbreak,'csv_largest_drop_window_s':cbreak,'rupture_offset_midpoint_s':offset_break,'rupture_offset_envelope_s':[vbreak[0]-cbreak[1],vbreak[1]-cbreak[0]],'video_grip_motion_onset_fit_s':best[1],'csv_displacement_onset_fit_s':csv_onset,'onset_offset_s':offset_start,'onset_vs_rupture_offset_difference_s':offset_start-offset_break,'video_grip_motion_speed_px_s':best[3],'onset_fit_rms_px':float(np.sqrt(best[0])),'status':'approximate cross-check only; no common-clock trigger or upstream marker'}
(p/'analysis/sync_summary.json').write_text(json.dumps(sync,indent=2)+'\n');print('sync',sync)
# Width sensitivity across three material bands and three edge-threshold definitions.
def edge_width(im,a,b,frac_station,frac_edge):
 cent=a+(b-a)*frac_station;cx,cy=np.round(cent).astype(int);half=int(np.clip(np.linalg.norm(a-b)*.065,20,80))
 if cy-half<0 or cy+half>=im.shape[0] or cx-130<0 or cx+130>=im.shape[1]:return np.nan
 z=im[cy-half:cy+half+1,cx-130:cx+131];prof=gaussian_filter1d(np.median(z,axis=0).astype(float),1.1);fg=np.median(prof[115:146]);bl=np.median(prof[:20]);br=np.median(prof[-20:]);tl=bl+frac_edge*(fg-bl);tr=br+frac_edge*(fg-br);xs=np.arange(260)
 l=np.flatnonzero((prof[:-1]<tl)&(prof[1:]>=tl)&(xs>=20)&(xs<110));r=np.flatnonzero((prof[:-1]>=tr)&(prof[1:]<tr)&(xs>150)&(xs<245))
 if not len(l) or not len(r):return np.nan
 k=int(l[-1]);j=int(r[0]);left=k+(tl-prof[k])/(prof[k+1]-prof[k]);right=j+(tr-prof[j])/(prof[j+1]-prof[j]);return float((right-left)*abs((b[1]-a[1])/np.linalg.norm(b-a)))
widthrows=[]
for i,row in d.iterrows():
 if row.time_s>34:break
 im=cv2.imread(fr[i]['file'],0);a=np.array([row.upper_mark_x_px,row.upper_mark_y_px]);bb=np.array([row.lower_mark_x_px,row.lower_mark_y_px]);q={'time_s':row.time_s,'axial_strain':row.axial_strain}
 for st in [.25,.5,.75]:
  for level in [.4,.5,.6]:q[f'w_s{st:.2f}_e{level:.1f}']=edge_width(im,a,bb,st,level)
 widthrows.append(q)
w=pd.DataFrame(widthrows);w.to_csv(p/'analysis/width_sensitivity.csv',index=False);stats=[]
for name in w.columns[2:]:
 bas=w.loc[(w.time_s>=3)&(w.time_s<=10),name];initial=float(bas.median());et=w[name]/initial-1;keep=(w.axial_strain>=.005)&(w.axial_strain<=.05)&np.isfinite(et);fit=linregress(w.loc[keep,'axial_strain'],et[keep]);stats.append({'width_definition':name,'initial_width_px':initial,'static_width_std_px':float(bas.std()),'strain_range':[.005,.05],'points':int(keep.sum()),'apparent_poisson_slope':float(-fit.slope),'r2':float(fit.rvalue**2),'accepted_for_width_sensitivity_plot':float(bas.std())<=1})
(p/'analysis/width_sensitivity_summary.json').write_text(json.dumps(stats,indent=2)+'\n');print('apparent nu by width definition',[(x['width_definition'],round(x['apparent_poisson_slope'],3),round(x['static_width_std_px'],3)) for x in stats])
# Explicitly labelled nominal-area Young slopes, used only as a sensitivity calculation.
E=[]
for offset in [offset_break,offset_start]:
 tc=d.time_s.to_numpy()-offset;force=np.interp(tc,c.time_s,c.force_N,left=np.nan,right=np.nan)
 for lo,hi in [(.005,.02),(.01,.03),(.02,.05),(.05,.10)]:
  keep=(d.axial_strain>=lo)&(d.axial_strain<=hi)&(d.upper_mark_score>.85)&(d.lower_mark_score>.85)&np.isfinite(force)
  if keep.sum()<3:continue
  r=linregress(d.loc[keep,'axial_strain'],force[keep]/2);E.append({'offset_s':offset,'nominal_area_mm2':2,'strain_range':[lo,hi],'points':int(keep.sum()),'reference_slope_MPa':float(r.slope),'r2':float(r.rvalue**2)})
(p/'analysis/reference_modulus_sensitivity.json').write_text(json.dumps(E,indent=2)+'\n');print('reference E',E)
# Sample values for the report use the valid pre-rupture interval only.
valid=d[(d.time_s<vbreak[0])&(d.upper_mark_score>.7)&(d.lower_mark_score>.7)];r=valid.iloc[-1];summary=json.loads((p/'analysis/ncc_summary.json').read_text());summary.update({'last_pre_gap_time_s':float(r.time_s),'last_pre_gap_virtual_gauge_strain':float(r.axial_strain),'max_reliable_evaluation_strain_for_report':.1,'width_at_last_pre_gap_px':float(r['width_0.5_px']),'specimen_actual_dimensions_measured':False,'nominal_width_mm':2,'nominal_thickness_mm':1,'poisson_fit_sensitivity_minmax':[min(x['apparent_poisson_slope'] for x in stats if x['accepted_for_width_sensitivity_plot']),max(x['apparent_poisson_slope'] for x in stats if x['accepted_for_width_sensitivity_plot'])]});(p/'analysis/review_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
