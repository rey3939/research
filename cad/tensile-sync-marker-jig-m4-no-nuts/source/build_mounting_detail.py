"""Engineering schematic of strap routing; machine rectangle is illustrative."""
from pathlib import Path
import importlib.util,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from matplotlib.font_manager import FontProperties

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('design',ROOT/'source/build_sync_jig.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=m.strap_mount();report=[]
assembly=m.cq.importers.importStep(str(ROOT/'STEP/assembly_with_M4_screws_REFERENCE.step')).val()
for z in [-10,10]:
 # Clearance envelope for a 4.8-wide x 1.5-thick band through the local mount.
 pieces=[m.box(-17,17,-11.5,-10,z-2.4,z+2.4)]
 for side in [-1,1]:
  x=17*side
  pieces += [m.box(x-.75,x+.75,-10.75,-.25,z-2.4,z+2.4)]
  x0,x1=(-22,-17) if side<0 else (17,22)
  pieces += [m.box(x0,x1,-1.75,-.25,z-2.4,z+2.4)]
 for p in pieces:
  assert base.intersect(p).Volume()<1e-5
  assert assembly.intersect(p.translate((0,m.P['moving_anchor_y'],m.P['moving_anchor_z']))).Volume()<1e-5
 report.append({'band_center_z_mm':z,'envelope_width_mm':4.8,'envelope_thickness_mm':1.5,'intersections_with_mount':0,'intersections_with_holder_and_M4_screws':0})
(ROOT/'mounting_validation.json').write_text(json.dumps({'band_clearance_checks':report,'rear_channel_depth_mm':2,'rear_channel_width_mm':6.4,'actual_machine_wrap_access_verified':False},ensure_ascii=False,indent=2)+'\n')

fp=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
fig=plt.figure(figsize=(12.5,8.8),facecolor='white')
fig.suptitle('実機と台座の接続：結束バンド2本で固定',fontproperties=fp,fontsize=19,y=.97,color='#17334a')
blue='#d9edf7';edge='#287d9b';orange='#e28330';gray='#e1e5e9'
a=fig.add_axes([.045,.27,.405,.61]);a.set_aspect('equal');a.set_xlim(-36,36);a.set_ylim(-27,27);a.axis('off')
a.set_title('① 正面から見る（水平バーは省略）',fontproperties=fp,fontsize=13,pad=15)
a.add_patch(Rectangle((-29,-21),58,42,facecolor='#f2f4f6',edgecolor='#aaa',ls='--'))
a.add_patch(Rectangle((-22,-16),44,32,facecolor=blue,edgecolor=edge,lw=2))
for z in [-10,10]:
 a.add_patch(Rectangle((-17,z-2.4),34,4.8,facecolor=orange,alpha=.8,edgecolor='none'))
 for x in [-17,17]:a.add_patch(Rectangle((x-2,z-3),4,6,facecolor='none',edgecolor=edge,lw=1.6))
for x in [-9,9]:a.add_patch(Circle((x,0),1.65,facecolor='white',edgecolor='#ba541e',lw=1.7))
a.text(0,0,'中央の丸穴2つ\nM4でバーを固定',fontproperties=fp,fontsize=10,ha='center',va='center',color='#17334a')
a.text(0,18.8,'角穴4つ：バンドを通す',fontproperties=fp,fontsize=11,ha='center',va='center',color='#17334a')
a.annotate('',(-22,-23),(22,-23),arrowprops=dict(arrowstyle='<->',color=edge,lw=1.4));a.text(0,-25,'44 mm',ha='center',va='center',color=edge,fontsize=11)
a.annotate('',(26,-16),(26,16),arrowprops=dict(arrowstyle='<->',color=edge,lw=1.4));a.text(29,0,'32 mm',rotation=90,ha='center',va='center',color=edge,fontsize=11)

b=fig.add_axes([.51,.27,.46,.61]);b.set_aspect('equal');b.set_xlim(-46,46);b.set_ylim(-30,34);b.axis('off')
b.set_title('② 上から見た断面（上側バンドの高さ）',fontproperties=fp,fontsize=13,pad=15)
b.add_patch(Rectangle((-35,0),70,25,facecolor=gray,edgecolor='#76838e',lw=1.8))
b.add_patch(Rectangle((-22,-10),44,10,facecolor=blue,edgecolor=edge,lw=1.8))
for side in [-1,1]:
 x=17*side
 b.add_patch(Rectangle((x-2,-10),4,10,facecolor='white',edgecolor='none'))
 x0,x1=(-22,-15) if side<0 else (15,22)
 b.add_patch(Rectangle((x0,-2),x1-x0,2,facecolor='white',edgecolor='none'))
xx=[-17,17,17,36,36,-36,-36,-17,-17]
yy=[-10.75,-10.75,-1,-1,26,26,-1,-1,-10.75]
b.plot(xx,yy,color=orange,lw=4,solid_capstyle='round',solid_joinstyle='round')
b.text(0,12,'白い可動部\n（模式形状）',fontproperties=fp,fontsize=12,ha='center',va='center',color='#263b49')
b.text(0,-5.3,'台座（厚さ10）',fontproperties=fp,fontsize=10,ha='center',va='center',color='#17334a')
b.annotate('裏の逃げ溝\n深さ2 mm',xy=(20,-1),xytext=(28,-18),fontproperties=fp,fontsize=10,color=edge,ha='center',arrowprops=dict(arrowstyle='->',color=edge,lw=1.2))
b.annotate('溝以外の裏面を\n実機へ当てる',xy=(-5,0),xytext=(-39,-19),fontproperties=fp,fontsize=9,color='#17334a',ha='left',arrowprops=dict(arrowstyle='->',color='#17334a',lw=1))
b.annotate('',xy=(0,-13),xytext=(0,-24),arrowprops=dict(arrowstyle='->',color='#17334a',lw=1.8));b.text(0,-28,'カメラ側',fontproperties=fp,fontsize=10,ha='center',color='#17334a')
fig.text(.06,.205,'青：3Dプリント台座　　橙：結束バンド　　灰：実機の可動部',fontproperties=fp,fontsize=12,color='#17334a')
fig.text(.06,.145,'上段・下段で1本ずつ、計2本を実機と台座へ周回させます。ロック部はアームや配線を避けて配置。',fontproperties=fp,fontsize=11,color='#17334a')
fig.text(.06,.095,'実機の形は模式図です。幅・奥行き・裏側へバンドを通せる空間は未確認です。',fontproperties=fp,fontsize=11,color='#a44f27')
fig.text(.06,.048,'M4ねじは台座とアームをつなぎます。現在の設計では、実機への固定には結束バンドを使います。',fontproperties=fp,fontsize=11,color='#17334a')
fig.savefig(ROOT/'views/mounting_detail.png',dpi=170)
fig.savefig(ROOT/'mounting_detail.pdf')
print('Strap clearance envelopes and mounting diagram checked')
