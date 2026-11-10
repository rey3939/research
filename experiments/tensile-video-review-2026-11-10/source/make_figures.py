from pathlib import Path
import json,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--workdir',type=Path,required=True);args=ap.parse_args()
p=args.workdir;out=Path(__file__).resolve().parent.parent/'figures';out.mkdir(exist_ok=True)
c=pd.read_csv(p/'analysis/force_data_utf8.csv');d=pd.read_csv(p/'analysis/video_ncc_tracking.csv');sync=json.loads((p/'analysis/sync_summary.json').read_text());summary=json.loads((p/'analysis/review_summary.json').read_text());stat=json.loads((p/'analysis/width_sensitivity_summary.json').read_text());w=pd.read_csv(p/'analysis/width_sensitivity.csv');fr=json.loads((p/'analysis/frame_index.json').read_text())
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':145,'savefig.dpi':170})
fig,ax=plt.subplots(2,1,figsize=(9,5.2),sharex=True,constrained_layout=True)
ax[0].plot(c.time_s,c.force_N,color='#067e8a',lw=1.5);ax[0].axvspan(48.85,49.09,color='#d46841',alpha=.25);ax[0].set_ylabel('Force [N]');ax[0].set_title('CSV: 542 samples, median interval 0.12 s; peak 4.075 N');ax[0].grid(alpha=.2)
ax[1].plot(c.time_s,c.crosshead_mm,color='#2775aa',lw=1.5);ax[1].set_xlabel('CSV time [s]');ax[1].set_ylabel('Crosshead [mm]');ax[1].text(.03,.83,'Fitted speed: 9.971 mm/min',transform=ax[1].transAxes);ax[1].grid(alpha=.2);fig.savefig(out/'csv_overview.png');plt.close(fig)
# Correlation-based virtual material markers, rather than an unverified nominal gauge length.
keep=(d.time_s<sync['video_visible_gap_window_s'][0])&(d.upper_mark_score>.7)&(d.lower_mark_score>.7)
fig,ax=plt.subplots(2,1,figsize=(9,5.3),sharex=True,constrained_layout=True)
ax[0].plot(d.loc[keep,'time_s'],d.loc[keep,'axial_strain']*100,color='#067e8a');ax[0].axvspan(3,10,color='#8fb8c5',alpha=.2);ax[0].set_ylabel('Virtual-gauge strain [%]');ax[0].set_title('Exploratory image measurement; reference length about 600 px');ax[0].grid(alpha=.2)
for f,co in [(.4,'#b3bfca'),(.5,'#d16c3d'),(.6,'#8cb5c4')]:ax[1].plot(d.loc[keep,'time_s'],d.loc[keep,f'width_{f:.1f}_px'],color=co,label=f'edge threshold {f:.1f}',lw=1.2)
ax[1].axvspan(3,10,color='#8fb8c5',alpha=.2);ax[1].set_xlabel('Video presentation time [s]');ax[1].set_ylabel('Mid-gauge width [px]');ax[1].legend(loc='best',fontsize=8);ax[1].grid(alpha=.2);fig.savefig(out/'video_tracking_overview.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(8.3,4),constrained_layout=True)
for z in stat:
 if z['static_width_std_px']>1:continue
 name=z['width_definition'];base=w.loc[(w.time_s>=3)&(w.time_s<=10),name].median();et=w[name]/base-1;ok=(w.axial_strain>=.005)&(w.axial_strain<=.05)
 ax.plot(w.loc[ok,'axial_strain']*100,-et[ok]*100,lw=.8,alpha=.4)
ax.set_xlabel('Virtual-gauge axial strain [%]');ax.set_ylabel('Apparent transverse contraction [%]');ax.set_title('Width sensitivity: three stations and edge thresholds');ax.grid(alpha=.2);ax.text(.03,.91,'Slope range about 0.32-0.41; exploratory, not a certified Poisson ratio',transform=ax.transAxes,fontsize=9);fig.savefig(out/'poisson_sensitivity.png');plt.close(fig)
# Annotated measurement windows on an unchanged first decoded frame.
im=np.array(Image.open(fr[0]['file']));x0,x1,y0,y1=220,525,550,1800
fig,ax=plt.subplots(figsize=(4.4,8),constrained_layout=True);ax.imshow(im[y0:y1,x0:x1],cmap='gray',vmin=0,vmax=255)
for x,y,ww,hh in [(298,885,150,110),(292,1480,150,120)]:ax.add_patch(Rectangle((x-x0,y-y0),ww,hh,fill=False,ec='#00a9c5',lw=1.5))
ax.plot([373-x0,367-x0],[940-y0,1540-y0],color='#00a9c5',lw=.8);ax.text(4,20,'Marker-region tracking',color='#067d92',fontsize=10,bbox=dict(fc='white',ec='none',alpha=.9))
ax.add_patch(Rectangle((432-x0,1010-y0),35,370,fill=False,ec='#d34c36',lw=1.2));ax.axhspan(1195-y0,1290-y0,color='#f2a24b',alpha=.2);ax.set_axis_off();fig.savefig(out/'measurement_regions.png');plt.close(fig)
# Rupture sequence: last connected sample and first visible gap, retaining the source PTS.
fig,ax=plt.subplots(1,2,figsize=(5.7,7.2),constrained_layout=True)
for aa,t in zip(ax,sync['video_visible_gap_window_s']):
 i=int(abs(d.time_s-t).idxmin());im=np.array(Image.open(fr[i]['file']));aa.imshow(im[250:1780,235:510],cmap='gray',vmin=0,vmax=255);aa.set_title(f'Video {d.time_s.iloc[i]:.3f} s',fontsize=10);aa.set_axis_off()
fig.savefig(out/'rupture_comparison.png');plt.close(fig)
# Reference stress using the unmeasured mould area only.
fig,ax=plt.subplots(figsize=(8,4.2),constrained_layout=True)
for off,label in [(sync['rupture_offset_midpoint_s'],'rupture-based alignment'),(sync['onset_offset_s'],'onset-fit alignment')]:
 tc=d.time_s-off;force=np.interp(tc,c.time_s,c.force_N,left=np.nan,right=np.nan);ok=(d.axial_strain>=0)&(d.axial_strain<=.10)&(d.upper_mark_score>.85)&np.isfinite(force);ax.plot(d.loc[ok,'axial_strain']*100,force[ok]/2,label=label,lw=1.2)
ax.set_xlabel('Virtual-gauge axial strain [%]');ax.set_ylabel('Reference stress [MPa]');ax.set_title('Assumed area 2 mm²; actual specimen dimensions NOT measured');ax.legend(fontsize=9);ax.grid(alpha=.2);fig.savefig(out/'reference_stress_strain.png');plt.close(fig)
print('Saved',len(list(out.glob('*.png'))),'figures')
