"""Adjustable image-synchronization target holders. Dimensions in mm.

Requires cadquery 2.7. Run: python build_sync_jig.py --output ../
The moving mount surface/strap access MUST be verified on the physical machine.
"""
from pathlib import Path
import argparse,json,math
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

P={
 'bolt_d':3.4,'nut_af':5.9,'nut_depth':3.0,
 'mount_w':48.0,'mount_h':32.0,'mount_plate_t':7.0,'mount_rear_clearance':3.0,
 'strap_slot_x':17.0,'strap_slot_z':10.0,'strap_slot_w':4.0,'strap_slot_h':6.0,
 'side_x':40.0,'depth_outboard_x':52.0,
 'moving_anchor_z':120.0,'moving_anchor_y':0.0,
 'fixed_anchor_z':-44.0,'fixed_anchor_y':12.5,
 'moving_rail_length':180.0,'moving_rail_center_z':60.0,
 'fixed_rail_length':90.0,'fixed_rail_center_z':-23.0,
 'moving_target_x':4.2,'moving_target_z':3.3,
 'fixed_target_x':-4.2,'fixed_target_z':-3.3,
 'target_front_y':-1.0,'target_pad_w':2.5,'target_pad_h':3.0,
 'depth_slot_y_min':-22.0,'depth_slot_y_max':30.0,
 'depth_screw_pitch':10.0,'target_face_offset_from_slider_center':-1.5,
 'nominal_density_g_cm3':1.24,
}

def box(x0,x1,y0,y1,z0,z1):
 return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()
def cyl_y(x,z,r,y0,y1):return cq.Solid.makeCylinder(r,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
def cyl_z(x,y,r,z0,z1):return cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0))
def slot_x(x0,x1,z,d,y0,y1):
 return box(x0,x1,y0,y1,z-d/2,z+d/2).fuse(cyl_y(x0,z,d/2,y0,y1),cyl_y(x1,z,d/2,y0,y1)).clean()
def slot_z(z0,z1,x,d,y0,y1):
 return box(x-d/2,x+d/2,y0,y1,z0,z1).fuse(cyl_y(x,z0,d/2,y0,y1),cyl_y(x,z1,d/2,y0,y1)).clean()
def slot_y(y0,y1,x,d,z0,z1):
 return box(x-d/2,x+d/2,y0,y1,z0,z1).fuse(cyl_z(x,y0,d/2,z0,z1),cyl_z(x,y1,d/2,z0,z1)).clean()
def hex_y(x,z,af,y0,y1):
 r=af/math.sqrt(3)
 pts=[cq.Vector(x+r*math.cos(math.pi/6+k*math.pi/3),y0,z+r*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
 w=cq.Wire.makePolygon(pts+[pts[0]])
 return cq.Solid.extrudeLinear(w,[],cq.Vector(0,y1-y0,0))
def cut(s,items):
 for item in items:s=s.cut(item).clean()
 return s
def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);return list(b.Get())

def strap_mount():
 s=box(-24,24,-10,-3,-16,16)
 # Two rear ribs provide clearance for captive nuts and screw ends.
 s=s.fuse(box(-24,-20,-3,0,-16,16),box(20,24,-3,0,-16,16)).clean()
 cuts=[]
 for x in [-17,17]:
  for z in [-10,10]:cuts.append(box(x-2,x+2,-11,1,z-3,z+3))
 for x in [-9,9]:
  cuts += [cyl_y(x,0,1.7,-11,1),hex_y(x,0,P['nut_af'],-6,-2.99)]
 return cut(s,cuts)
def horizontal_bar():
 return cut(box(-16,60,-14,-10,-6,6),[slot_x(-10,52,0,3.4,-15,-9)])
def corner():
 s=box(25,55,-18,-14,-17,17)
 return cut(s,[cyl_y(x,z,1.7,-19,-13) for x,z in [(30,0),(50,0),(40,-11),(40,11)]])
def rail(length):
 return cut(box(35,45,-22,-18,-length/2,length/2),[slot_z(-length/2+12,length/2-12,40,3.4,-23,-17)])
def depth_carriage():
 s=box(25,56,-26,-22,-16,16).fuse(box(48,56,-26,36,-3,3)).clean()
 return cut(s,[cyl_y(40,z,1.7,-27,-21) for z in [-10,10]]+[slot_y(-22,30,52,3.4,-4,4)])
def target_arm():
 # Flat-bottom print: thin neck is supported by the bed, not suspended.
 s=box(46,60,-9,9,3,6)
 s=s.fuse(box(13,48,-1,1,3,6),box(5.3,13,-1,1,3,4.2),box(2.95,5.45,-1.5,1.5,3,6)).clean()
 return cut(s,[cyl_z(52,y,1.7,2,7) for y in [-5,5]])
def coupon():
 s=box(0,66,0,24,0,6);cuts=[]
 for x,d,af in [(11,3.2,5.7),(33,3.4,5.9),(55,3.6,6.1)]:
  cuts.append(cyl_z(x,7,d/2,-1,7))
  # Open hexagonal test recess on top, with round screw hole below it.
  r=af/math.sqrt(3);pts=[(x+r*math.cos(math.pi/6+k*math.pi/3),17+r*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
  w=cq.Workplane('XY').polyline(pts).close().extrude(3.01).translate((0,0,3)).val()
  cuts += [w,cyl_z(x,17,d/2,-1,7)]
 return cut(s,cuts)

def translated(s,x=0,y=0,z=0):return s.translate((x,y,z))
def mirror_x(s):return s.mirror('YZ')
def module(kind):
 moving=kind=='moving';side=1 if moving else -1
 az=P['moving_anchor_z'] if moving else P['fixed_anchor_z']
 ay=P['moving_anchor_y'] if moving else P['fixed_anchor_y']
 length=P['moving_rail_length'] if moving else P['fixed_rail_length']
 rz=P['moving_rail_center_z'] if moving else P['fixed_rail_center_z']
 tz=P['moving_target_z'] if moving else P['fixed_target_z']
 cz=tz-4.5
 # Pad front face in the target-arm part is center_y - 1.5.
 slider_y=P['target_front_y']-ay+1.5
 lo=P['depth_slot_y_min']+P['depth_screw_pitch']/2
 hi=P['depth_slot_y_max']-P['depth_screw_pitch']/2
 assert lo<=slider_y<=hi,('depth outside range',kind,slider_y,lo,hi)
 # Both pairs of vertical attachment bolts must lie inside the straight slot.
 for z in [az-11,az+11,cz-10,cz+10]:
  assert abs(z-rz)<=length/2-12,('vertical slot',kind,z,rz,length)
 shapes={'strap_mount':translated(strap_mount(),y=ay,z=az),
  'horizontal_bar':translated(horizontal_bar(),y=ay,z=az),
  'corner':translated(corner(),y=ay,z=az),
  'vertical_rail':translated(rail(length),y=ay,z=rz),
  'depth_carriage':translated(depth_carriage(),y=ay,z=cz),
  'target_arm':translated(target_arm(),y=ay+slider_y,z=cz)}
 if side<0:shapes={n:mirror_x(s) for n,s in shapes.items()}
 return shapes,{'anchor_y':ay,'anchor_z':az,'rail_length':length,'rail_center_z':rz,'tip_carriage_center_z':cz,'depth_slider_center_y_local':slider_y,'target_center':[side*4.2,P['target_front_y'],tz]}

def make_assembly(shapes,name):
 a=cq.Assembly(name=name)
 palette=['D9E2E8','9BB9D1','F0B66F','337F9B','7AB8AD','F1D84B']
 for i,(n,s) in enumerate(shapes.items()):
  c=palette[i%len(palette)];a.add(s,name=n,color=cq.Color(*(int(c[k:k+2],16)/255 for k in [0,2,4])))
 return a

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent);args=ap.parse_args()
 out=args.output;steps=out/'STEP';stls=out/'STL';steps.mkdir(parents=True,exist_ok=True);stls.mkdir(exist_ok=True)
 parts={'01_strap_mount':strap_mount(),'02_horizontal_bar':horizontal_bar(),'03_corner_carriage':corner(),
  '04_vertical_rail_180':rail(180),'04b_vertical_rail_240_optional':rail(240),
  '05_vertical_rail_90':rail(90),'05b_vertical_rail_120_optional':rail(120),
  '06_depth_carriage_R':depth_carriage(),'06_depth_carriage_L':mirror_x(depth_carriage()),
  '07_target_arm_R':target_arm(),'07_target_arm_L':mirror_x(target_arm()),'08_fastener_fit_coupon':coupon()}
 report={'parameters':P,'parts':{},'assemblies':{},'collision_checks':[]}
 for n,s in parts.items():
  assert s.isValid() and len(s.Solids())==1,n
  cq.exporters.export(s,str(steps/(n+'.step')))
  s2=cq.importers.importStep(str(steps/(n+'.step'))).val()
  assert s2.isValid() and len(s2.Solids())==1,n
  assert abs(s2.Volume()-s.Volume())<max(1e-5,s.Volume()*1e-7),n
  pr=s if 'target_arm' in n or 'coupon' in n else s.rotate((0,0,0),(1,0,0),90)
  b=bounds(pr);pr=pr.translate((-b[0],-b[1],-b[2]))
  cq.exporters.export(pr,str(stls/(n+'.stl')),tolerance=.04,angularTolerance=.12)
  b=bounds(s);report['parts'][n]={'valid':True,'solids':1,'volume_mm3':s.Volume(),'bounds_mm':b,'bbox_mm':[b[i+3]-b[i] for i in range(3)]}
 allshapes={}
 for kind in ['moving','fixed']:
  sh,cfg=module(kind);allshapes.update({kind+'_'+n:s for n,s in sh.items()})
  vol=sum(s.Volume() for s in sh.values())
  report['assemblies'][kind]={'configuration':cfg,'printed_parts':len(sh),'printed_volume_cm3':vol/1000,'printed_mass_g_at_density':vol/1000*P['nominal_density_g_cm3']}
  a=make_assembly(sh,kind+'_marker_holder');a.save(str(steps/('assembly_'+kind+'.step')))
 make_assembly(allshapes,'two_independent_marker_holders').save(str(steps/'assembly_both.step'))
 names=list(allshapes)
 for i,a in enumerate(names):
  for b in names[i+1:]:
   v=allshapes[a].intersect(allshapes[b]).Volume()
   if v>1e-5:report['collision_checks'].append({'a':a,'b':b,'intersection_mm3':v})
 assert not report['collision_checks'],report['collision_checks']
 (out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 (out/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
 print(json.dumps({'parts':len(parts),'collision_checks':report['collision_checks'],'assemblies':report['assemblies']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
