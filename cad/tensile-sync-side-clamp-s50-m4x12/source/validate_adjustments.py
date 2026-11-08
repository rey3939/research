"""Self-clearance tests at optical X/depth adjustment endpoints.
These tests do not certify clearance to the unmeasured machine geometry.
"""
from pathlib import Path
import importlib.util,json,math
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('design',ROOT/'source/build_side_clamp.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
records=[]
for x in [-30,4.2,46]:
 for y in [-3,14,45]:
  m.P['target_x']=m.P['anchor_x_ILLUSTRATIVE']+x;m.P['target_face_y']=y-15
  sh,cfg=m.module('R');fast,joints=m.screws('R',cfg);names=list(sh)
  for i,n in enumerate(names):
   for b in names[i+1:]:assert m.overlap(sh[n],sh[b])<1e-5,(x,y,n,b)
  for name,(s,h,shaft,receiver) in fast.items():
   for n,p in sh.items():
    assert m.overlap(h,p)<1e-5,(x,y,name,'head',n)
    if n!=receiver:assert m.overlap(shaft,p)<1e-5,(x,y,name,'shaft',n)
   assert abs(shaft.intersect(sh[receiver]).Volume()/(math.pi*(2**2-1.65**2))-8)<1e-5
  records.append({'cross_slide_x_mm':x,'depth_slider_y_mm':y,'self_intersections':0,'all_M4_engagement_mm':8})
(ROOT/'adjustment_validation.json').write_text(json.dumps({'configurations':records,'machine_clearance_included':False,'sample_contact_included':False},ensure_ascii=False,indent=2)+'\n')
print('Adjustment endpoint combinations passed:',len(records))
