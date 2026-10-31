"""Rebuild the specimen-marking fixture. Requires cadquery>=2.7 and numpy.
All dimensions are mm. The source contour was extracted from the supplied F3D.
Run: python build_jig.py --output ../
"""
from pathlib import Path
import argparse,json,math,time
import numpy as np
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

P={
 'plate_width_x':97.0,'plate_length_y':102.0,
 'base_seat_height':5.5,'pocket_floor_height':4.0,
 'sample_nominal_thickness':1.0,'sample_max_design_thickness':1.2,
 'lid_thickness':4.0,'guide_membrane_thickness':0.6,
 'pocket_clearance_per_side':0.4,'pocket_clearance_alternative':0.6,
 'mark_spacing':10.0,'guide_slot_width':1.0,'guide_slot_alternative':1.2,
 'guide_slot_length':4.0,'pen_access_well_length_x':24.0,'pen_access_well_width_y':8.2,
 'top_edge_chamfer':0.2,'pocket_lead_in_per_side':0.25,'pocket_lead_in_height':0.3,'bolt_clearance_diameter':6.6,
 'registration_pin_diameter':3.0,'registration_pin_height':2.5,
 'registration_hole_diameter':3.4,'registration_slot_length':4.6,
 'row_pitch':75.737/7,'column_centers_original':[6.0,45.94199993294477],
 'row_start_original':3.0,'original_plate_center':[26.77944830551339,40.92772430255406],
 'original_bolt_centers':[
  [-15.799746003208242,-4.616571597647692],[-16.19940788215981,86.27115123292132],
  [69.40633234170568,85.58779626741872],[68.93598573100899,-4.052137081516353]],
 'registration_pin_centers':[[-43.5,-20.0],[43.5,20.0]],
 'fit_coupon_clearances':[0.2,0.4,0.6],
 'pen_coupon_slot_widths':[0.8,0.9,1.0,1.1,1.2,1.4]
}

def exact_bounds(s):
 box=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,box,False,False);return list(box.Get())

def source_wire():
 records=json.loads((Path(__file__).parent/'source_profile_edges.json').read_text())
 edges=[]
 for e in records:
  a=np.array(e['start'])*10-np.array([6,3,0]);b=np.array(e['end'])*10-np.array([6,3,0])
  if e['curve']=='straight-curve':edge=cq.Edge.makeLine(cq.Vector(*a),cq.Vector(*b))
  else:
   d=e['curve_data'];c=np.array(d[1][1]);n=np.array(d[2][1]);A=np.array(d[3][1]);B=np.cross(n,A)*d[4][1]
   t=(d[6][1]+d[8][1])/2;mid=(c+A*math.cos(t)+B*math.sin(t))*10-np.array([6,3,0])
   edge=cq.Edge.makeThreePointArc(cq.Vector(*a),cq.Vector(*mid),cq.Vector(*b))
  edges.append(edge)
 wire=cq.Wire.assembleEdges(edges)
 assert wire.IsClosed() and wire.isValid()
 return wire

def shifted(w,x,y,z=0):return w.translate((x,y,z))
def profile(c):
 if c==0:return source_wire()
 w=cq.Workplane('XY').add(source_wire()).toPending().offset2D(c,kind='arc').val()
 assert w.BoundingBox().xlen>35 and w.BoundingBox().ylen>6
 return w

def extrude_wire(w,h):return cq.Solid.extrudeLinear(w,[],cq.Vector(0,0,h))
def rectsolid(x,y,w,h,z0,z1):
 return cq.Workplane('XY').box(w,h,z1-z0,centered=(True,True,False)).translate((x,y,z0)).val()
def cyl(x,y,r,z0,z1):return cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0))
def slot(x,y,length,width,angle,z0,z1):
 return cq.Workplane('XY').slot2D(length,width,angle).extrude(z1-z0).translate((x,y,z0)).val()
def cut_many(s,cutters):return s.cut(cq.Compound.makeCompound(cutters)).clean()
def chamfer_outer(s,w,h,z):
 edges=[e for e in s.Edges() if abs(e.Center().z-z)<1e-6 and (abs(abs(e.Center().x)-w/2)<1e-6 or abs(abs(e.Center().y)-h/2)<1e-6)]
 assert len(edges)==4,len(edges)
 out=cq.Workplane('XY').add(s).newObject(edges).chamfer(P['top_edge_chamfer']).val().clean()
 assert out.isValid() and len(out.Solids())==1
 return out
def entrance(clearance,x,y):
 h=P['base_seat_height'];a=shifted(profile(clearance),x,y,h-P['pocket_lead_in_height'])
 b=shifted(profile(clearance+P['pocket_lead_in_per_side']),x,y,h)
 out=cq.Solid.makeLoft([a,b],ruled=True)
 assert out.isValid()
 return out
def engraving(s,labels,z_top,depth=.3,size=2.4):
 cutters=[]
 for x,y,label in labels:
  t=cq.Workplane('XY').text(label,size,depth+.05,font='DejaVu Sans',halign='center',valign='center',combine=False).val().translate((x,y,z_top-depth))
  cutters.append(t)
 return cut_many(s,cutters) if cutters else s

def centers():
 ox,oy=P['original_plate_center']
 return [(col*8+i+1,x-ox,P['row_start_original']+i*P['row_pitch']-oy)
         for col,x in enumerate(P['column_centers_original']) for i in range(8)]
def bolts():
 ox,oy=P['original_plate_center'];return [(x-ox,y-oy) for x,y in P['original_bolt_centers']]
def labels():return [( -43.5 if i<=8 else 43.5,y,('A' if i<=8 else 'B')+str((i-1)%8+1)) for i,x,y in centers()]

def base(clearance):
 h=P['base_seat_height'];floor=P['pocket_floor_height']
 s=rectsolid(0,0,P['plate_width_x'],P['plate_length_y'],0,h)
 w=profile(clearance)
 cuts=[extrude_wire(shifted(w,x,y,floor),h-floor+1) for i,x,y in centers()]
 cuts += [cyl(x,y,P['bolt_clearance_diameter']/2,-1,h+1) for x,y in bolts()]
 s=cut_many(s,cuts)
 # Ruled offset profiles create a verified lead-in without fragile tiny-edge chamfers.
 s=cut_many(s,[entrance(clearance,x,y) for i,x,y in centers()])
 s=chamfer_outer(s,P['plate_width_x'],P['plate_length_y'],h)
 s=engraving(s,labels(),h)
 for x,y in P['registration_pin_centers']:
  r=P['registration_pin_diameter']/2;total=P['registration_pin_height']
  pin=cyl(x,y,r,h-.1,h+total-.4)
  tip=cq.Solid.makeCone(r,r-.35,.4,cq.Vector(x,y,h+total-.4))
  s=s.fuse(pin,tip).clean()
 assert s.isValid() and len(s.Solids())==1
 return s

def lid(slot_width):
 h=P['lid_thickness'];mem=P['guide_membrane_thickness']
 s=rectsolid(0,0,P['plate_width_x'],P['plate_length_y'],0,h)
 cuts=[]
 for i,x,y in centers():
  cuts.append(rectsolid(x,y,P['pen_access_well_length_x'],P['pen_access_well_width_y'],mem,h+1))
  for sign in [-1,1]:
   cuts.append(slot(x+sign*P['mark_spacing']/2,y,P['guide_slot_length'],slot_width,90,-1,mem+.1))
 cuts += [cyl(x,y,P['bolt_clearance_diameter']/2,-1,h+1) for x,y in bolts()]
 (x1,y1),(x2,y2)=P['registration_pin_centers']
 cuts.append(cyl(x1,y1,P['registration_hole_diameter']/2,-1,h+1))
 angle=math.degrees(math.atan2(y2-y1,x2-x1))
 cuts.append(slot(x2,y2,P['registration_slot_length'],P['registration_hole_diameter'],angle,-1,h+1))
 s=cut_many(s,cuts)
 s=chamfer_outer(s,P['plate_width_x'],P['plate_length_y'],h)
 s=engraving(s,labels(),h)
 assert s.isValid() and len(s.Solids())==1
 return s

def fit_coupon():
 h=P['base_seat_height'];floor=P['pocket_floor_height'];s=rectsolid(0,0,64,34,0,h)
 cuts=[];labs=[]
 for c,y in zip(P['fit_coupon_clearances'],[-9,0,9]):
  cuts.append(extrude_wire(shifted(profile(c),-5,y,floor),h-floor+1));labs.append((23,y,f'C{c:.1f}'))
 s=cut_many(s,cuts)
 s=cut_many(s,[entrance(c,-5,y) for c,y in zip(P['fit_coupon_clearances'],[-9,0,9])])
 s=chamfer_outer(s,64,34,h)
 s=engraving(s,labs,h,size=2.5)
 assert s.isValid() and len(s.Solids())==1
 return s

def pen_coupon():
 h=P['lid_thickness'];mem=P['guide_membrane_thickness'];s=rectsolid(0,0,54,30,0,h)
 cuts=[];labs=[]
 for x,w in zip([-20,-12,-4,4,12,20],P['pen_coupon_slot_widths']):
  cuts.append(rectsolid(x,-2,6,8.2,mem,h+1))
  cuts.append(slot(x,-2,4,w,90,-1,mem+.1));labs.append((x,9,f'{w:.1f}'))
 s=cut_many(s,cuts);s=chamfer_outer(s,54,30,h)
 s=engraving(s,labs,h,size=2.4)
 assert s.isValid() and len(s.Solids())==1
 return s

def nominal_sample(i,x,y,t=1):return extrude_wire(shifted(source_wire(),x,y,P['pocket_floor_height']),t)

def build(output,reuse_existing=False):
 output.mkdir(parents=True,exist_ok=True);(output/'STEP').mkdir(exist_ok=True);(output/'STL').mkdir(exist_ok=True)
 prior=json.loads((output/'parameters.json').read_text()) if (output/'parameters.json').exists() else None
 can_reuse=reuse_existing and prior==P
 (output/'parameters.json').write_text(json.dumps(P,indent=2))
 parts={};report={}
 for name,fn in [
  ('base_C02',lambda:base(P['fit_coupon_clearances'][0])),('base_C04',lambda:base(P['pocket_clearance_per_side'])),('base_C06',lambda:base(P['pocket_clearance_alternative'])),
  ('lid_S10',lambda:lid(P['guide_slot_width'])),('lid_S12',lambda:lid(P['guide_slot_alternative'])),
  ('fit_coupon',fit_coupon),('pen_slot_coupon',pen_coupon)]:
  tick=time.monotonic()
  if can_reuse and (output/'STEP'/f'{name}.step').exists() and (output/'STL'/f'{name}.stl').exists():
   s=cq.importers.importStep(str(output/'STEP'/f'{name}.step')).val()
  else:
   s=fn()
   cq.exporters.export(s,str(output/'STEP'/f'{name}.step'))
   cq.exporters.export(s,str(output/'STL'/f'{name}.stl'),tolerance=.04,angularTolerance=.1)
  parts[name]=s
  bounds=exact_bounds(s)
  report[name]={'valid':s.isValid(),'solids':len(s.Solids()),'volume_mm3':s.Volume(),'bounds_mm_xyz_min_max':bounds}
  print(name,'completed',round(time.monotonic()-tick,1),'seconds',flush=True)
 # Only actual fixture parts are in the assembly (no specimen or ghost bodies).
 asm=cq.Assembly(name='JIS7_marking_jig_C04_S10')
 asm.add(parts['base_C04'],name='BASE_C04',color=cq.Color(.13,.55,.56))
 asm.add(parts['lid_S10'],name='LID_S10',loc=cq.Location(cq.Vector(0,0,P['base_seat_height'])),color=cq.Color(.72,.77,.84))
 asm.save(str(output/'STEP'/'assembly_C04_S10.step'))
 # STEP round-trip must retain native solids and mm scale.
 for name,s in parts.items():
  reread=cq.importers.importStep(str(output/'STEP'/f'{name}.step')).val()
  assert reread.isValid() and len(reread.Solids())==1,name
  assert abs(reread.Volume()-s.Volume())/s.Volume()<1e-8,name
  bb=exact_bounds(reread);orig=exact_bounds(s)
  assert max(abs(a-b) for a,b in zip(bb,orig))<1e-6,name
  report[name]['step_round_trip']=True
 lid_assembled=parts['lid_S10'].translate((0,0,P['base_seat_height']))
 overlap=parts['base_C04'].intersect(lid_assembled).Volume()
 assert overlap<1e-6,overlap
 # The complete nominal specimen lies clear of both support and lid except floor contact.
 sample=cq.Compound.makeCompound([nominal_sample(i,x,y,P['sample_max_design_thickness']) for i,x,y in centers()])
 b_inter=sample.intersect(parts['base_C04']).Volume();l_inter=sample.intersect(lid_assembled).Volume()
 assert b_inter<1e-6 and l_inter<1e-6,(b_inter,l_inter)
 reread=cq.importers.importStep(str(output/'STEP'/'assembly_C04_S10.step')).val()
 assert reread.isValid() and len(reread.Solids())==2
 report['assembly']={'base_lid_overlap_mm3':overlap,'nominal_sample_overlap_base_mm3':b_inter,'nominal_sample_overlap_lid_mm3':l_inter,'nominal_max_sample_top_gap_mm':P['base_seat_height']-P['pocket_floor_height']-P['sample_max_design_thickness'],'step_round_trip_solids':len(reread.Solids()),'guide_pairs':len(centers()),'guide_center_spacing_mm':P['mark_spacing']}
 # Probe slot widths and the material between the slots geometrically at the mask plane.
 z=P['guide_membrane_thickness']/2
 for i,x,y in centers():
  for sign in [-1,1]:
   xc=x+sign*P['mark_spacing']/2
   assert not parts['lid_S10'].isInside(cq.Vector(xc,y,z)),(i,'slot not open')
   assert parts['lid_S10'].isInside(cq.Vector(xc+P['guide_slot_width']/2+.1,y,z)),(i,'slot boundary incorrect')
  assert parts['lid_S10'].isInside(cq.Vector(x,y,z)),(i,'middle web missing')
 report['guide_checks']={'all_32_slots_open':True,'all_slot_sidewalls_present':True,'all_16_middle_webs_present':True}
 (output/'verification.json').write_text(json.dumps(report,indent=2))
 print('ALL GEOMETRY AND STEP ROUND-TRIP CHECKS PASSED',flush=True)
 return parts

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--reuse-existing',action='store_true');args=parser.parse_args();build(args.output,args.reuse_existing)
