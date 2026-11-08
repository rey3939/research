"""S50 side-clamp synchronization holder. Every screw is M4x12.
Receiver holes are post-print M4x0.7 tap pilots, not printed threads.
"""
from pathlib import Path
import argparse,json,math,struct,collections
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from cadquery.occ_impl.exporters.svg import getSVG
import fitz
from PIL import Image,ImageChops,ImageOps

P={
 'measured_clamped_span':50.,'measured_vertical_height':14.,
 'prior_available_edge_depth':20.,'side_contact_depth_verified':False,
 'jaw_insertion':14.,'jaw_contact_height':10.,'fit_clearance_total':.2,'opening':52.2,
 'pad_thickness':2.,'jaw_wall':8.,'tap_pilot_d':3.242,'female_minor_basic_d':4-1.082532*.7,'thread_pitch':.7,'clearance_d':4.2,'pad_pocket_d':4.2,'tap_exit_d':4.2,
 'all_screw_lengths':12.,'screw_head_min_assumed_d':7.,'head_envelope_d':10.,'head_envelope_h':5.,
 'anchor_x_ILLUSTRATIVE':0.,'anchor_z_ILLUSTRATIVE':120.,
 'vertical_rail_length':190.,'vertical_rail_center_z':52.,
 'target_x':4.2,'target_z':3.3,'target_face_y':-1.,
 'cross_slide_tip_x_min':-30.,'cross_slide_tip_x_max':46.,
 'depth_slider_y_min':-3.,'depth_slider_y_max':45.,'density_g_cm3':1.24,
}

def box(x0,x1,y0,y1,z0,z1):return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()
def cy(x,z,r,y0,y1):return cq.Solid.makeCylinder(r,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
def cz(x,y,r,z0,z1):return cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0))
def cut(s,tools):
 for t in tools:s=s.cut(t).clean()
 return s
def sx(a,b,z,d,y0,y1):return box(a,b,y0,y1,z-d/2,z+d/2).fuse(cy(a,z,d/2,y0,y1),cy(b,z,d/2,y0,y1)).clean()
def sz(a,b,x,d,y0,y1):return box(x-d/2,x+d/2,y0,y1,a,b).fuse(cy(x,a,d/2,y0,y1),cy(x,b,d/2,y0,y1)).clean()
def sy(a,b,x,d,z0,z1):return box(x-d/2,x+d/2,a,b,z0,z1).fuse(cz(x,a,d/2,z0,z1),cz(x,b,d/2,z0,z1)).clean()
def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);return list(b.Get())
def trans(s,x=0,y=0,z=0):return s.translate((x,y,z))
def mirror(s):return s.mirror('YZ')
def overlap(a,b):
 aa=a.BoundingBox();bb=b.BoundingBox()
 if any(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min'))<1e-7 for k in 'xyz'):return 0.
 return a.intersect(b).Volume()

def cx(y,z,r,x0,x1):return cq.Solid.makeCylinder(r,x1-x0,cq.Vector(x0,y,z),cq.Vector(1,0,0))
def clamp_body():
 # X is the 50 mm face-to-face direction; Z is the 14 mm vertical height.
 # Opening 52.2 = 50 mm metal + 2 mm pad + 0.2 mm total insertion clearance.
 right=-25+P['opening'];outer=right+P['jaw_wall']
 s=box(-33,outer,-10,0,-5,5).fuse(box(-33,-25,-.5,14,-5,5),box(right,outer,-.5,14,-5,5)).clean()
 return cut(s,[cy(x,0,(P['tap_pilot_d']/2),-11,1) for x in [-9,9]]+[cx(9,0,(P['tap_pilot_d']/2),right-1,outer+1)])
def pad():return cut(box(25,27,5,13,-4,4),[cx(9,0,P['pad_pocket_d']/2,26.6,27.1)])
def hbar():return cut(box(-16,78,-14,-10,-6,6),[sx(-10,70,0,P['clearance_d'],-15,-9)])
def corner():return trans(cut(box(22,58,-24,-14,-17,17),[cy(x,z,(P['tap_pilot_d']/2),-25,-13) for x,z in [(28,0),(52,0),(40,-11),(40,11)]]),x=18)
def rail(length):return trans(cut(box(35,45,-28,-24,-length/2,length/2),[sz(-length/2+12,length/2-12,40,P['clearance_d'],-29,-23)]),x=18)
def depth_carriage():
 s=box(25,62,-38,-28,-16,16).fuse(box(46,62,-38,56,-1,3),box(46,48,-38,56,-7,-1),box(60,62,-38,56,-7,-1)).clean()
 return trans(cut(s,[cy(40,z,(P['tap_pilot_d']/2),-39,-27) for z in [-10,10]]+[sy(-30,50,54,P['clearance_d'],-2,4)]),x=18)
def cross_carriage():
 s=box(40,68,-11,11,3,28)
 # The thread-bearing section is 10 mm. Larger rear bores provide tap exit.
 tools=[cz(54,y,(P['tap_pilot_d']/2),2,29) for y in [-5,5]]+[cz(54,y,P['tap_exit_d']/2,13,29) for y in [-5,5]]
 tools += [cy(x,22,(P['tap_pilot_d']/2),-12,12) for x in [46,62]]+[cy(x,22,P['tap_exit_d']/2,-1,12) for x in [46,62]]
 return trans(cut(s,tools),x=18)
def flag():
 s=box(8,122,-15,-11,17,27).fuse(box(1.1,8,-15,-11,20.5,21.7),box(-1.25,1.25,-15,-11,20.5,23.5)).clean()
 return cut(s,[sx(18,110,22,P['clearance_d'],-16,-10)])
def coupon():
 s=box(0,66,0,28,0,10)
 return cut(s,[cz(x,7,d/2,-1,11) for x,d in [(11,4.0),(33,4.2),(55,4.4)]]+[cz(x,21,d/2,-1,11) for x,d in [(11,3.2),(33,3.242),(55,3.3)]])

def module(side='R'):
 ax=P['anchor_x_ILLUSTRATIVE'];az=P['anchor_z_ILLUSTRATIVE'];dz=P['target_z']-22;dy=P['target_face_y']+15;tx=P['target_x']-ax
 assert P['cross_slide_tip_x_min']<=tx<=P['cross_slide_tip_x_max']
 assert P['depth_slider_y_min']<=dy<=P['depth_slider_y_max']
 L=P['vertical_rail_length'];rz=P['vertical_rail_center_z']
 for z in [az-11,az+11,dz-10,dz+10]:assert abs(z-rz)<=L/2-12
 sh={'01_side_clamp_S50':trans(clamp_body(),ax,0,az),'02_protective_pad':trans(pad(),ax,0,az),
  '03_horizontal_bar':trans(hbar(),ax,0,az),'04_corner':trans(corner(),ax,0,az),
  '05_vertical_rail_190':trans(rail(L),ax,0,rz),'06_ribbed_depth_carriage':trans(depth_carriage(),ax,0,dz),
  '07_cross_slide_carriage':trans(cross_carriage(),ax,dy,dz),'08_sliding_target_flag':trans(flag(),ax+tx,dy,dz)}
 if side=='L':sh={n:mirror(s) for n,s in sh.items()}
 return sh,{'side':side,'anchor_x_illustrative':ax if side=='R' else -ax,'anchor_z_illustrative':az,'tip_carriage_z':dz,'depth_slider_y':dy,'cross_slide_translation_x':tx,'target_center':[P['target_x'] if side=='R' else -P['target_x'],P['target_face_y'],P['target_z']]}

def assembly(sh,name):
 a=cq.Assembly(name=name);colors=[(.75,.82,.88),(.93,.9,.65),(.4,.7,.75),(.7,.73,.78),(.3,.55,.65),(.2,.65,.62),(.5,.65,.8),(.95,.72,.25)]
 for i,(n,s) in enumerate(sh.items()):a.add(s,name=n,color=cq.Color(*colors[i%len(colors)]))
 return a

def screws(side,cfg):
 ax=P['anchor_x_ILLUSTRATIVE'];az=P['anchor_z_ILLUSTRATIVE'];dz=cfg['tip_carriage_z'];dy=cfg['depth_slider_y'];sign=1 if side=='R' else -1
 jobs=[]
 for x in [-9,9]:jobs.append(('A',x,-14,az,(0,1,0),'01_side_clamp_S50',2))
 for x in [46,70]:jobs.append(('B',x,-10,az,(0,-1,0),'04_corner',2))
 for z in [az-11,az+11]:jobs.append(('C',58,-28,z,(0,1,0),'04_corner',2))
 for z in [dz-10,dz+10]:jobs.append(('D',58,-24,z,(0,-1,0),'06_ribbed_depth_carriage',2))
 for y in [-5,5]:jobs.append(('E',72,dy+y,dz-1,(0,0,1),'07_cross_slide_carriage',2))
 for x in [64,80]:jobs.append(('F',x,dy-15,dz+22,(0,1,0),'07_cross_slide_carriage',2))
 jobs.append(('P',38.6,9,az,(-1,0,0),'01_side_clamp_S50',None))
 shapes={};records=[]
 for i,(g,x,y,z,axis,receiver,margin) in enumerate(jobs,1):
  pos=cq.Vector(sign*(ax+x),y,z);direction=cq.Vector(axis[0]*sign,axis[1],axis[2])
  shaft=cq.Solid.makeCylinder(2,12,pos,direction);head=cq.Solid.makeCylinder(5,5,pos,direction.multiply(-1))
  s=shaft.fuse(head).clean();assert s.isValid() and len(s.Solids())==1
  shapes[f'M4x12_{g}_{i:02d}']=(s,head,shaft,receiver)
  records.append({'group':g,'length_mm':12,'receiver':receiver,'thread_engagement_mm':8,'tip_to_back_margin_mm':margin,'head_gap_mm':3.4 if g=='P' else 0,'role':'pressure screw' if g=='P' else 'joint clamp'})
 return shapes,records

def save_step(s,path):
 if isinstance(s,cq.Assembly):s.save(str(path))
 else:cq.exporters.export(s,str(path))
 path.write_text('\n'.join(t.rstrip() for t in path.read_text().splitlines())+'\n')
def check_stl(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n
 edge=collections.Counter();volume=0
 for i in range(n):
  vs=struct.unpack_from('<12fH',raw,84+50*i);v=[tuple(round(x,5) for x in vs[3+j*3:6+j*3]) for j in range(3)]
  for j in range(3):edge[tuple(sorted((v[j],v[(j+1)%3])))] +=1
  a,b,c=v;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 assert all(k==2 for k in edge.values()),(path.name,'nonmanifold')
 assert volume>0
 return {'triangles':n,'nonmanifold_edges':0,'signed_volume_mm3':volume}
def export_part(s,path,flat_z=False):
 assert s.isValid() and len(s.Solids())==1
 save_step(s,path.with_suffix('.step'))
 r=cq.importers.importStep(str(path.with_suffix('.step'))).val();assert r.isValid() and len(r.Solids())==1
 assert abs(r.Volume()-s.Volume())<max(1e-5,s.Volume()*1e-7)
 pr=s if flat_z else s.rotate((0,0,0),(1,0,0),90)
 if path.name=='02_protective_pad':pr=s.rotate((0,0,0),(0,1,0),90)
 b=bounds(pr);pr=trans(pr,-b[0],-b[1],-b[2])
 target=path.parent.parent.parent/'STL'/path.parent.name/(path.name+'.stl');target.parent.mkdir(exist_ok=True,parents=True)
 cq.exporters.export(pr,str(target),tolerance=.04,angularTolerance=.12)
 return {'volume_mm3':s.Volume(),'bounds_mm':bounds(s),'stl':check_stl(target)}

def picture(s,path,direction=(1,-2,1)):
 svg=getSVG(s,{'width':950,'height':1150,'marginLeft':30,'marginTop':25,'projectionDir':direction,'showAxes':False,'showHidden':False,'strokeWidth':.22,'strokeColor':(25,66,81)})
 path.with_suffix('.svg').write_text(svg)
 doc=fitz.open(stream=svg.encode(),filetype='svg');doc[0].get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False).save(path)
 im=Image.open(path).convert('RGB').rotate(-90,expand=True);bb=ImageChops.difference(im,Image.new('RGB',im.size,'white')).convert('L').point(lambda x:255 if x>12 else 0).getbbox()
 if bb:im=im.crop(bb)
 ImageOps.expand(im,border=25,fill='white').save(path)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent);ap.add_argument('--mount',type=Path,required=True);ap.add_argument('--cover',type=Path,required=True);args=ap.parse_args()
 out=args.output;steps=out/'STEP';views=out/'views';steps.mkdir(exist_ok=True,parents=True);views.mkdir(exist_ok=True)
 parts={'01_side_clamp_S50':clamp_body(),'02_protective_pad':pad(),'03_horizontal_bar':hbar(),'04_corner':corner(),'05_vertical_rail_190':rail(190),'06_ribbed_depth_carriage':depth_carriage(),'07_cross_slide_carriage':cross_carriage(),'08_sliding_target_flag':flag(),'05b_vertical_rail_240_OPTIONAL':rail(240)}
 report={'parameters':P,'parts':{},'installations':{},'checks':[]}
 for side in ['R','L']:
  (steps/side).mkdir(exist_ok=True)
  for name,s in parts.items():
   shape=s if side=='R' else mirror(s)
   report['parts'][side+'/'+name]=export_part(shape,steps/side/name,flat_z=name in ['01_side_clamp_S50','07_cross_slide_carriage'])
 (steps/'COMMON').mkdir(exist_ok=True)
 report['parts']['COMMON/09_tap_test_coupon']=export_part(coupon(),steps/'COMMON/09_tap_test_coupon',flat_z=True)
 mount=cq.importers.importStep(str(args.mount)).val();cover=cq.importers.importStep(str(args.cover)).val()
 fixture={'lower_mount':trans(mount,-27.5,-12.5,-66),'upper_mount':trans(mount.rotate((0,0,0),(0,1,0),180),27.5,-12.5,66),
  'lower_cover':trans(cover.rotate((0,0,0),(1,0,0),90),-27.5,-1,-26),'upper_cover':trans(cover.rotate((0,0,0),(1,0,0),90),-27.5,-1,11)}
 pts=[(-3,-17.5),(-3,-10.5),(-1,-6),(-1,6),(-3,10.5),(-3,17.5),(3,17.5),(3,10.5),(1,6),(1,-6),(3,-10.5),(3,-17.5)]
 wire=cq.Wire.makePolygon([cq.Vector(x,-1,z) for x,z in pts]+[cq.Vector(pts[0][0],-1,pts[0][1])])
 fixture['nominal_sample']=cq.Solid.extrudeLinear(wire,[],cq.Vector(0,1,0))
 fixture['fixed_label']=box(-2,2,-5.5,-5.42,-20.5,-16.5);fixture['fixed_dot']=cy(0,-18.5,.5,-5.55,-5.5)
 for side in ['R','L']:
  sh,cfg=module(side);fast,records=screws(side,cfg);names=list(sh)
  for i,n in enumerate(names):
   for b in names[i+1:]:assert overlap(sh[n],sh[b])<1e-5,(side,n,b)
  ax=P['anchor_x_ILLUSTRATIVE'];az=P['anchor_z_ILLUSTRATIVE'];patch=trans(box(-25,25,0,20,-7,7),ax,0,az)
  if side=='L':patch=mirror(patch)
  ring=math.pi*(2**2-(P['tap_pilot_d']/2)**2)
  for (name,(s,head,shaft,receiver)),rec in zip(fast.items(),records):
   for n,p in sh.items():
    assert overlap(head,p)<1e-5,(side,name,'head',n)
    if n!=receiver:assert overlap(shaft,p)<1e-5,(side,name,'shaft',n)
   assert abs(shaft.intersect(sh[receiver]).Volume()/ring-8)<1e-5,(side,name,'engagement')
   assert overlap(s,patch)<1e-5,(side,name,'metal patch')
  for n,s in sh.items():
   assert overlap(s,patch)<1e-5,(side,n,'patch')
   for fn,fs in fixture.items():assert overlap(s,fs)<1e-5,(side,n,fn)
  metal={n:v[0] for n,v in fast.items()};total={**sh,**metal}
  for travel in [0,2,5,10,20]:
   for n,s in total.items():
    for fn in ['lower_mount','lower_cover','fixed_label','fixed_dot']:
     assert overlap(trans(s,z=travel),fixture[fn])<1e-5,(side,travel,n,fn)
  save_step(assembly(sh,side+'_printed_holder'),steps/f'assembly_{side}.step')
  save_step(assembly(total,side+'_with_M4x12_REFERENCE'),steps/f'assembly_{side}_with_M4x12_REFERENCE.step')
  clamped={k:sh[k] for k in ['01_side_clamp_S50','02_protective_pad']};clamped['pressure_screw']=metal['M4x12_P_13'];clamped['local_S50_H14_patch_REFERENCE']=patch
  save_step(assembly(clamped,side+'_clamped_S50_LOCAL_REFERENCE'),steps/f'clamp_{side}_S50_REFERENCE.step')
  context={**total,'local_S50_patch_REFERENCE':patch,**fixture}
  save_step(assembly(context,side+'_installation_ASSUMED_REFERENCE'),steps/f'installation_{side}_ASSUMED_REFERENCE.step')
  for fn,count in [(f'assembly_{side}',8),(f'assembly_{side}_with_M4x12_REFERENCE',21),(f'clamp_{side}_S50_REFERENCE',4),(f'installation_{side}_ASSUMED_REFERENCE',31)]:
   s=cq.importers.importStep(str(steps/(fn+'.step'))).val();assert s.isValid() and len(s.Solids())==count,(fn,len(s.Solids()))
  vol=sum(s.Volume() for s in sh.values())
  report['installations'][side]={'configuration':cfg,'printed_parts':8,'M4x12_screws':13,'nuts':0,'washers':0,'straps':0,'tap_holes':13,'screw_details':records,'plastic_solid_mass_g':vol/1000*P['density_g_cm3'],'measured_fit_inputs_mm':{'clamped_span':50,'vertical_height':14},'side_contact_patch_assumed_mm':[10,14],'tested_travel_mm':[0,2,5,10,20],'collisions':[]}
  if side=='R':
   picture(cq.Compound.makeCompound(list(sh.values())),views/'assembly_R.png')
   picture(cq.Compound.makeCompound(list(context.values())),views/'installation_R.png',(0,-1,0))
   picture(cq.Compound.makeCompound(list(clamped.values())),views/'clamp_detail.png')
   picture(cq.Compound.makeCompound([sh['06_ribbed_depth_carriage'],sh['07_cross_slide_carriage'],sh['08_sliding_target_flag']]),views/'cross_slide_detail.png')
 report['limitations']=['Red-circled front projection, 50 mm between side faces; not the 14 mm top-to-bottom direction','Side contact 10 mm vertical x 14 mm insertion depth is a design assumption pending physical fit','Prior reported 20 mm free depth does not establish side-face flatness','Illustrative attachment height 120 mm is not measured; machine, bolt and load cell full shapes not modeled','Physical fit, holding force, printed thread strength and synchronization accuracy not validated','Pilot 3.242 follows the user-specified M4x0.7 female-thread basic minor diameter; threads are cut after printing','Flat screw head diameter assumed >=7 mm; envelope diameter10 x height5 checked']
 (out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(out/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'part_files':len(report['parts']),'screws_per_holder':13,'printed_parts_per_holder':8,'all_screws':'M4x12','R_mass_g':report['installations']['R']['plastic_solid_mass_g'],'checks':'valid BRep / roundtrip STEP / closed STL / head and shaft clearances / 8 mm engagement / measured local patch / lower grips travel'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
