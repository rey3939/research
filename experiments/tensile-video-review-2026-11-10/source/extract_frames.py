from pathlib import Path
import subprocess,re,json
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--workdir',type=Path,required=True);ap.add_argument('--video',type=Path,required=True);args=ap.parse_args()
p=args.workdir;out=p/'sampled';out.mkdir(exist_ok=True)
v=args.video;log=p/'analysis/extract_showinfo.log'
cmd=['ffmpeg','-hide_banner','-y','-i',str(v),'-map','0:v:0','-an','-vf',"select='not(mod(n,6))',crop=750:1950:650:600,format=gray,showinfo",'-fps_mode','passthrough',str(out/'frame_%04d.png')]
print('Extracting every sixth source frame at original PTS; lossless grayscale ROI',flush=True)
with log.open('w') as f:r=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=f)
if r.returncode:raise RuntimeError(log.read_text()[-4000:])
s=log.read_text();pts=[float(x) for x in re.findall(r'\bn:\s*\d+.*?\bpts_time:([\d.\-]+)',s)];files=sorted(out.glob('frame_*.png'));assert len(files)==len(pts),(len(files),len(pts));assert all(b>a for a,b in zip(pts,pts[1:]));rows=[{'file':str(f),'time_s':t,'source_frame_index':i*6} for i,(f,t) in enumerate(zip(files,pts))];(p/'analysis/frame_index.json').write_text(json.dumps(rows,indent=2)+'\n');print('Extracted',len(rows),'frames; times',pts[0],pts[-1])
