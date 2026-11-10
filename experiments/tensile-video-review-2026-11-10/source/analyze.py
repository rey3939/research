from pathlib import Path
import argparse,subprocess,sys,json,shutil
import pandas as pd
from scipy.stats import linregress
ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser();ap.add_argument('--video',type=Path,required=True);ap.add_argument('--csv',type=Path,required=True);ap.add_argument('--workdir',type=Path,required=True);args=ap.parse_args();w=args.workdir.resolve();w.mkdir(parents=True,exist_ok=True);(w/'analysis').mkdir(exist_ok=True)
c=pd.read_csv(args.csv,encoding='cp932');c.columns=['test','time_s','crosshead_mm','force_N'];c.to_csv(w/'analysis/force_data_utf8.csv',index=False);r=linregress(c.time_s.iloc[2:],c.crosshead_mm.iloc[2:]);i=int(c.force_N.diff().idxmin())
summary={'rows':len(c),'duration_s':[float(c.time_s.min()),float(c.time_s.max())],'median_interval_s':float(c.time_s.diff().median()),'speed_mm_min':float(r.slope*60),'time_displacement_r2':float(r.rvalue**2),'max_force_N':float(c.force_N.max()),'peak_time_s':float(c.loc[c.force_N.idxmax(),'time_s']),'peak_crosshead_mm':float(c.loc[c.force_N.idxmax(),'crosshead_mm']),'largest_load_drop_window_s':[float(c.loc[i-1,'time_s']),float(c.loc[i,'time_s'])],'reference_area_mm2':2,'specimen_actual_dimensions_measured':False,'reference_peak_engineering_stress_MPa':float(c.force_N.max()/2)}
(w/'analysis/csv_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for script in ['extract_frames.py','track_ncc.py','summarize_analysis.py','make_figures.py']:
 cmd=[sys.executable,str(ROOT/'source'/script),'--workdir',str(w)]
 if script=='extract_frames.py':cmd+=['--video',str(args.video.resolve())]
 subprocess.run(cmd,check=True)
(ROOT/'data').mkdir(exist_ok=True)
for n in ['csv_summary.json','sync_summary.json','review_summary.json','ncc_summary.json','width_sensitivity_summary.json','reference_modulus_sensitivity.json','force_data_utf8.csv','video_ncc_tracking.csv','width_sensitivity.csv']:shutil.copy2(w/'analysis'/n,ROOT/'data'/n)
subprocess.run([sys.executable,str(ROOT/'source/build_report.py')],check=True)
