from pathlib import Path
import importlib.util,json,struct,collections,math
import cadquery as cq
from cadquery.occ_impl.exporters.svg import getSVG
import fitz
from PIL import Image,ImageChops,ImageOps

import argparse
ap=argparse.ArgumentParser();ap.add_argument('--mount',type=Path,required=True);ap.add_argument('--cover',type=Path,required=True);args=ap.parse_args()
OUT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('design',OUT/'source/build_sync_jig.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
mount=cq.importers.importStep(str(args.mount)).val()
cover=cq.importers.importStep(str(args.cover)).val()
refs={
 'lower_mount_reference':mount.translate((-27.5,-12.5,-66)),
 'lower_cover_reference':cover.rotate((0,0,0),(1,0,0),90).translate((-27.5,-1,-26)),
 'upper_mount_reference':mount.rotate((0,0,0),(0,1,0),180).translate((27.5,-12.5,66)),
 'upper_cover_reference':cover.rotate((0,0,0),(1,0,0),90).translate((-27.5,-1,11)),
}
pts=[(-3,-17.5),(-3,-10.5),(-1,-6),(-1,6),(-3,10.5),(-3,17.5),(3,17.5),(3,10.5),(1,6),(1,-6),(3,-10.5),(3,-17.5)]
wire=cq.Wire.makePolygon([cq.Vector(x,-1,z) for x,z in pts]+[cq.Vector(pts[0][0],-1,pts[0][1])])
sample=cq.Solid.extrudeLinear(wire,[],cq.Vector(0,1,0));refs['nominal_specimen_reference']=sample
moving,_=m.module('moving')
refs['fixed_white_label_reference']=m.box(-2,2,-5.50,-5.42,-20.5,-16.5)
refs['fixed_black_dot_reference']=m.cyl_y(0,-18.5,.5,-5.55,-5.50)
checks=[]
for n,s in {'moving_'+k:v for k,v in moving.items()}.items():
 for rn,r in refs.items():
  overlap=s.intersect(r).Volume()
  assert overlap<1e-5,(n,rn,overlap)
  checks.append({'holder':n,'reference':rn,'overlap_mm3':overlap})
for travel in [0,2,5,10,20]:
 for mn,ms in moving.items():
  moved=ms.translate((0,0,travel))
  for fn,fs in refs.items():
   if fn.startswith('upper_') or fn=='nominal_specimen_reference':continue
   overlap=moved.intersect(fs).Volume()
   assert overlap<1e-5,(travel,mn,fn,overlap)

a=cq.Assembly(name='nominal_installation_reference_only')
for n,s in refs.items():
 color=cq.Color(.05,.05,.05) if 'black_dot' in n else cq.Color(1,1,1) if 'white_label' in n else cq.Color(.9,.45,.15) if 'specimen' in n else cq.Color(.66,.69,.72)
 a.add(s,name=n,color=color)
for kind,sh,col in [('moving',moving,cq.Color(.0,.55,.55))]:
 for n,s in sh.items():a.add(s,name=kind+'_'+n,color=col)
a.save(str(OUT/'STEP/assembly_with_supplied_grips_REFERENCE.step'))
f=OUT/'STEP/assembly_with_supplied_grips_REFERENCE.step';f.write_text('\n'.join(line.rstrip() for line in f.read_text().splitlines())+'\n')

stl_report={}
for f in (OUT/'STL').glob('*.stl'):
 data=f.read_bytes();count=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*count
 edges=collections.Counter();signed=0
 for i in range(count):
  vals=struct.unpack_from('<12fH',data,84+50*i);v=[tuple(round(t,5) for t in vals[3+3*j:6+3*j]) for j in range(3)]
  for j in range(3):edges[tuple(sorted((v[j],v[(j+1)%3])))] +=1
  x,y,z=v;signed+=(x[0]*(y[1]*z[2]-y[2]*z[1])+x[1]*(y[2]*z[0]-y[0]*z[2])+x[2]*(y[0]*z[1]-y[1]*z[0]))/6
 bad=sum(n!=2 for n in edges.values());assert bad==0,(f.name,bad)
 assert signed>0,(f.name,signed)
 stl_report[f.name]={'triangles':count,'nonmanifold_edges':bad,'signed_volume_mm3':signed}
counts={}
for name,expected in [('assembly_moving',6),('assembly_with_supplied_grips_REFERENCE',15)]:
 s=cq.importers.importStep(str(OUT/'STEP'/f'{name}.step')).val();assert s.isValid();assert len(s.Solids())==expected,(name,len(s.Solids()))
 counts[name]=len(s.Solids())

# Native CAD hidden-line projections, rendered as SVG by MuPDF.
views=OUT/'views';views.mkdir(exist_ok=True)
for name,sh,direction in [
 ('moving_isometric',cq.Compound.makeCompound(list(moving.values())),(1,-2,1.1)),
 ('tip_detail',cq.Compound.makeCompound([moving['depth_carriage'],moving['target_arm']]),(1,-2,1.1)),
 ('context_front',cq.Compound.makeCompound(list(moving.values())+list(refs.values())),(0,-1,0))]:
 svg=getSVG(sh,{'width':900,'height':1100 if 'front' in name or 'isometric' in name else 650,'marginLeft':40,'marginTop':35,'projectionDir':direction,'showAxes':False,'showHidden':False,'strokeWidth':.22,'strokeColor':(30,65,80)})
 (views/f'{name}.svg').write_text(svg)
 doc=fitz.open(stream=svg.encode(),filetype='svg');doc[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).save(views/f'{name}.png')
 im=Image.open(views/f'{name}.png').convert('RGB').rotate(-90,expand=True)
 bb=ImageChops.difference(im,Image.new('RGB',im.size,'white')).convert('L').point(lambda x:255 if x>12 else 0).getbbox()
 if bb:im=im.crop(bb)
 ImageOps.expand(im,border=30,fill='white').save(views/f'{name}.png')

report={'supplied_fixture_initial_intersection_checks':len(checks),'supplied_fixture_initial_intersections':[],'moving_vs_existing_lower_grip_tested_travel_mm':[0,2,5,10,20],'assembly_roundtrip_solid_counts':counts,'stl':stl_report,'sample_clearance_at_initial_pose_mm':min(s.distance(sample) for s in list(moving.values())),'limits':['Moving machine mount and other machine hardware not dimensionally verified','Nominal 22 mm grip opening and 35 mm specimen assumed for context','Grip-context STEP omits hardware; separate M4 reference STEP includes screw envelopes','Physical fit, stiffness and motion have not been tested']}
(OUT/'context_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='stl'},ensure_ascii=False,indent=2))
