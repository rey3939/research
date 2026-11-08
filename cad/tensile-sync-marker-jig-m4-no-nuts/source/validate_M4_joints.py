"""Check screw access, receiver engagement and unintended intersections.
Thread flanks are not modeled. Receiver holes are M4 tap pilot holes.
"""
from pathlib import Path
import importlib.util,json,math,argparse
import cadquery as cq

OUT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('design',OUT/'source/build_sync_jig.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ap=argparse.ArgumentParser();ap.add_argument('--mount',type=Path,required=True);ap.add_argument('--cover',type=Path,required=True);args=ap.parse_args()
mount=cq.importers.importStep(str(args.mount)).val();cover=cq.importers.importStep(str(args.cover)).val()
refs={
 'lower_mount':mount.translate((-27.5,-12.5,-66)),
 'lower_cover':cover.rotate((0,0,0),(1,0,0),90).translate((-27.5,-1,-26)),
 'upper_mount':mount.rotate((0,0,0),(0,1,0),180).translate((27.5,-12.5,66)),
 'upper_cover':cover.rotate((0,0,0),(1,0,0),90).translate((-27.5,-1,11)),
}

def overlap(a,b):
 aa=a.BoundingBox();bb=b.BoundingBox()
 if any(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min'))<1e-7 for k in ['x','y','z']):return 0.
 return a.intersect(b).Volume()

all_shapes={};by_kind={};entries=[]
for kind in ['moving']:
 sh,c=m.module(kind);side=1 if kind=='moving' else -1
 az,ay,cz,sy=c['anchor_z'],c['anchor_y'],c['tip_carriage_center_z'],c['depth_slider_center_y_local']
 joints=[]
 for x in [-9,9]:joints.append(('A',x,ay-14,az,(0,1,0),12,'strap_mount',8))
 for x in [28,52]:joints.append(('B',x,ay-10,az,(0,-1,0),12,'corner',8))
 for z in [az-11,az+11]:joints.append(('C',40,ay-28,z,(0,1,0),12,'corner',8))
 for z in [cz-10,cz+10]:joints.append(('D',40,ay-24,z,(0,-1,0),12,'depth_carriage',8))
 for y in [-5,5]:joints.append(('E',52,ay+sy+y,cz-3,(0,0,1),16,'target_arm',10))
 items={**sh};all_shapes.update({kind+'_'+n:s for n,s in sh.items()})
 for i,(group,x,y,z,axis,length,receiver,engage) in enumerate(joints,1):
  pos=cq.Vector(side*x,y,z);direction=cq.Vector(*axis)
  shaft=cq.Solid.makeCylinder(2,length,pos,direction)
  # Diameter 10 x height 5 is a conservative head envelope for specified truss/flange screws.
  head=cq.Solid.makeCylinder(5,5,pos,direction.multiply(-1))
  screw=shaft.fuse(head).clean();assert screw.isValid() and len(screw.Solids())==1
  for n,s in sh.items():
   assert overlap(head,s)<1e-5,(kind,i,'head',n)
   if n!=receiver:assert overlap(shaft,s)<1e-5,(kind,i,'shaft',n)
  ring_area=math.pi*(2**2-1.65**2)
  actual=shaft.intersect(sh[receiver]).Volume()/ring_area
  assert abs(actual-engage)<1e-5,(kind,i,'engagement',actual,engage)
  for rn,r in refs.items():assert overlap(screw,r)<1e-5,(kind,i,rn)
  name=f'M4_{group}_{i:02d}_L{length}'
  items[name]=screw;all_shapes[kind+'_'+name]=screw
  entries.append({'module':kind,'group':group,'length_mm':length,'head_envelope_diameter_mm':10,'head_envelope_height_mm':5,'receiver':receiver,'receiver_engagement_mm':engage,'receiver_back_margin_mm':2,'unintended_intersections':0})
 by_kind[kind]=items
for travel in [0,2,5,10,20]:
 for mn,ms in by_kind['moving'].items():
  moved=ms.translate((0,0,travel))
  for fn,fs in refs.items():
   if fn.startswith('lower_'):assert overlap(moved,fs)<1e-5,(travel,mn,fn)

assembly=m.make_assembly(all_shapes,'M4_screw_reference_no_modeled_threads')
path=OUT/'STEP/assembly_with_M4_screws_REFERENCE.step';assembly.save(str(path))
path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
s=cq.importers.importStep(str(path)).val();assert s.isValid() and len(s.Solids())==16
report={'screw_count':len(entries),'length_12mm_count':sum(e['length_mm']==12 for e in entries),'length_16mm_count':sum(e['length_mm']==16 for e in entries),'fixed_reference':'existing lower grip with applied label','nuts':0,'metal_inserts':0,'washers':0,'tap_specification':'M4x0.7, post-print tapping required','receiver_pilot_diameter_mm':3.3,'slot_width_mm':4.5,'joints':entries,'travel_test_mm':[0,2,5,10,20],'reference_assembly_solids':16,'thread_geometry_modeled':False,'physical_strength_tested':False}
(OUT/'hardware_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='joints'},ensure_ascii=False,indent=2))
