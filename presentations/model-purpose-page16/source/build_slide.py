from pathlib import Path
from contextlib import contextmanager
from zipfile import ZipFile
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from PIL import Image,ImageDraw
import math,json,fitz,argparse
ROOT=Path(__file__).resolve().parent.parent
exec((ROOT/'source/drawing_helpers.py').read_text(),globals())
BASE=ROOT;OUT=ROOT
prs=Presentation();prs.slide_width=Inches(13.333333);prs.slide_height=Inches(7.5)
prs.core_properties.title='実施目的：薄板化で粒子の追加回転の影響が小さくなると考える理由'
prs.core_properties.author='大橋 怜倭'
C.update({'black':'121212','bar':'858585','paper':'F2F2F2','palered':'FCE9E0','softblue':'EAF3FA','cyan2':'D8EBEA','tension':'C75946','compression':'397FB0'})
slide=prs.slides.add_slide(prs.slide_layouts[6]);root=slide.shapes.add_group_shape();root.name='16ページ：薄板化の仮説と根拠（編集可能）';cur=root
im=Image.new('RGB',(2400,1350),'white');dr=ImageDraw.Draw(im)
issues=[];alltext=[];slides=[]
exec((ROOT/'source/native_groups.py').read_text(),globals())

def strain_strip(x,y,w,t):
 pts=bent_strip(x,y,w,t)
 normals=[]
 for i in range(len(pts)):
  p0=pts[max(i-1,0)];p1=pts[min(i+1,len(pts)-1)];dx=p1[0]-p0[0];dy=p1[1]-p0[1];r=math.hypot(dx,dy);normals.append((-dy/r,dx/r))
 poly([(p[0]-n[0]*t/2,p[1]-n[1]*t/2) for p,n in zip(pts,normals)],line='tension',lw=4)
 poly([(p[0]+n[0]*t/2,p[1]+n[1]*t/2) for p,n in zip(pts,normals)],line='compression',lw=4)
 xx=x+w/2
 arrow(xx,y-t/2+2,xx,y+t/2-2,'black',1.5,5)
 arrow(xx,y+t/2-2,xx,y-t/2+2,'black',1.5,5)
 text(xx+10,y-13,40,31,'t',21,'black')

with group('見出しとフッター'):
 text(50,20,1485,80,'実施目的',58,'black',True)
 rect(0,111,1600,13,'bar')
 rect(240,158,1120,61,'palered')
 text(255,169,1090,44,'単純モデルで磁場を推定できるPMEの厚み範囲を調べる',31,'black',False,'center')
 text(220,866,1160,29,'Function Design Laboratory, Nagoya Institute of Technology',21,'black',False,'center')
 text(1465,865,80,30,'16',23,'black',False,'right')

for x,w,color,title,sz in [(50,355,'softblue','先行研究：回転が関与',26),(430,730,'palered','仮説：薄板化で追加回転の影響が減る',28),(1185,365,'paper','検証：厚みごとに比較',25)]:
 with group(title):
  rect(x,260,w,420,color,r=18)
  text(x+15,275,w-30,44,title,sz,'blue' if x==50 else 'orange' if x==430 else 'navy',True,'center')

with group('先行研究：別材料PMFUEの圧縮'):
 text(70,326,315,36,'PMFUEの一様圧縮',24,'black',False,'center')
 text(65,365,325,27,'●：粒子　→：磁化の向き',17,'muted',False,'center')
 material(75,405,112,90,[0,0,0]);arrow(203,453,238,453,'blue',3,9)
 material(256,420,120,60,[-23,18,-12])
 arrow(283,397,283,414,'blue',3,7);arrow(343,397,343,414,'blue',3,7)
 text(65,520,325,39,'1%圧縮あたり0.536°',25,'blue',True,'center')
 text(67,574,321,72,'PMEでも粒子の追加回転が\n関与する可能性',23,'black',False,'center')

with group('仮説の理由：同じ曲率と表面ひずみ'):
 text(450,322,690,35,'同じ曲げ形状（曲率 κ）で比較',24,'black',True,'center')
 text(470,356,650,27,'赤：引張　青：圧縮　破線：中立軸',18,'muted',False,'center')
 with group('厚い試料：大きい表面ひずみ'):
  strain_strip(480,420,225,72)
  text(450,502,320,34,'厚い：表面ひずみ 大',23,'black',True,'center')
 with group('薄い試料：小さい表面ひずみ'):
  strain_strip(870,420,225,24)
  text(840,502,300,34,'薄い：表面ひずみ 小',23,'black',True,'center')
 arrow(760,450,823,450,'orange',4,12)
 text(450,549,690,38,'薄い → 曲げによるひずみが小さい',27,'black',True,'center')
 text(450,591,690,38,'→ 粒子の追加回転の影響も小さいと予想',26,'orange',True,'center')
 text(450,641,690,30,'表面ひずみの大きさ　|ε|max ≈ |κ|t / 2',21,'muted',False,'center')

with group('追加回転を省いたモデルを実測と比較'):
 text(1200,326,335,35,'追加回転を省いたモデル',23,'navy',True,'center')
 text(1200,367,335,30,'母材の曲がりには追従',21,'muted',False,'center')
 x0,y0,ww,hh=1242,439,235,120
 arrow(x0,y0+hh,x0+ww,y0+hh,'muted',2,9);arrow(x0,y0+hh,x0,y0,'muted',2,9)
 def point(u):return (x0+14+(ww-34)*u,y0+hh-12-(hh-25)*u)
 poly([point(k/40) for k in range(41)],line='blue',lw=3)
 for u,d in [(.08,3),(.29,-6),(.51,5),(.75,-4),(.96,4)]:
  xx,yy=point(u);circle(xx,yy+d,4,'orange')
 text(1207,410,220,27,'磁場変化',18,'muted')
 text(1390,565,120,26,'変位',18,'muted')
 line(1220,597,1250,597,'blue',3);text(1257,582,90,28,'モデル',18,'blue')
 circle(1382,597,4,'orange');text(1394,582,110,28,'実測',18,'orange')
 text(1205,627,325,29,'両者の差を評価（模式図）',20,'navy',True,'center')

with group('検証で確かめること'):
 text(50,705,1500,40,'誤差の範囲で一致 → 追加回転の寄与を省いて推定できる条件を特定',27,'navy',True,'center')

with group('学術的知見と設計基盤'):
 rect(50,759,735,74,'softblue',r=14);text(70,776,195,37,'学術的知見',25,'blue',True)
 text(280,780,485,33,'追加回転を省ける条件・適用範囲',23,'black',False,'center')
 rect(815,759,735,74,'cyan',r=14);text(835,776,195,37,'設計基盤',25,'teal',True)
 text(1043,780,487,33,'単純な磁場予測によるセンサ設計',23,'black',False,'center')

with group('出典'):
 text(55,839,1490,24,'出典：大江岳歩，永久磁石発泡ウレタンエラストマーの圧縮による磁場変化，修士論文，2025。図は模式図。',16,'muted')

notes='''【この1枚で伝えること】
同じ曲げ形状では、薄いほど曲げによる表面の引張・圧縮ひずみが小さい。そこで、局所ひずみに伴う粒子単独の追加回転も小さくなり、磁場への寄与を省けるのではないか、という仮説を示す。

【中央部分の説明原稿：約25秒】
同じ曲がり具合で比較すると、厚い試料では外側が大きく引き伸ばされ、内側が大きく圧縮されます。試料を薄くすると、この引張・圧縮ひずみが小さくなります。そこで、ひずみに伴う粒子の追加回転も小さくなり、その磁場への影響を省けるのではないかと考えました。これを厚みごとのモデルと実測の比較で検証します。

【力学的根拠と条件】
単純な梁の曲げでは、中立軸から厚さ方向距離ζの位置の軸ひずみは ε≈−κζ で、曲げによる表面ひずみの大きさは |ε|max≈|κ|t/2。κは曲率、tは厚さ。式は断面保持を仮定した曲げひずみの近似を示す。軸方向の平均伸び等の全ひずみが必ずゼロになることを主張するものではない。
比較の前提は同じ曲げ形状・曲率である。同じ力では薄いほど大きく曲がる場合があるため、同じ荷重だけではこの結論を使えない。
ひずみの厚さ方向勾配の大きさ |∂ε/∂ζ|=|κ| 自体は、同じκでは厚さに依存しない。小さくなるのは表面ひずみと断面全体のひずみ差 |κ|t である。「薄いとひずみ勾配が小さくなる」とは書かない。

【何が確立した根拠で、何が仮説か】
曲げひずみがtに比例することは、上の梁の仮定から導かれる。一方、追加粒子回転やその磁場寄与が同じように減ることは未検証の仮説。粒子形状、磁気相互作用、母材との拘束等も関係するため、厚さだけで寄与が必ずゼロになるとは断定しない。スライドの矢印の最後を「予想」とした理由である。

【省略する回転：ユーザー確認済み】
磁化の向きは母材の曲がりに追従し、粒子単独の追加回転だけを省く、というモデルである。母材の姿勢回転自体は厚さを薄くしても消えない。薄板化の根拠を使って、磁化方向を空間座標で固定できると結論づけない。
添付PDF17ページの「内部粒子は母材に完全追従」に整合する。35ページは「回転：母材の回転に追従（粒子単独の追加回転は省略）」と書き換えると解釈を揃えられる。今回の差し替え済みPDFで変更したのは16ページだけで、35ページは元のままである。

【結果の解釈】
モデルと実測の一致は、評価した条件と精度の範囲で追加回転の寄与を省いて磁場を予測できることを支持する。粒子が全く回転しない証明にはならない。不一致も、それだけで追加回転が原因とは断定できない。17ページの「差が増大した厚み＝粒子の回転の影響を無視できない」は「差が増大した厚みでは、追加回転等の効果の必要性を検討する」と表現するとよい。

【先行研究と模式図】
0.536°/1%圧縮は添付資料24ページに記載された別材料PMFUEの報告値。原修士論文本文で追加確認していない。PMEの曲げへ数値を転用しない。先行研究の粒子図、曲げ試料、比較グラフは模式図であり、測定した回転角や既に一致したデータを示さない。中央の2試料は同じ中心線曲率で、厚さだけを変えて描いた。

【編集】
PowerPointは全て図形・線・矢印・テキストボックスで、画像を埋め込んでいない。指定フォントは游ゴシック。PDFは同じ配置を別レンダラーで描いた確認版で、Microsoft PowerPointでの描画確認は行っていない。'''
slide.notes_slide.notes_text_frame.text=notes
root.shapes._recalculate_extents()
for node in slide._element.iter(qn('a:rPr')):
 for ch in node:
  if ch.tag in [qn('a:latin'),qn('a:ea')]:ch.set('typeface','Yu Gothic')
pptx=OUT/'model_purpose_page16_editable.pptx';prs.save(pptx)
preview=BASE/'model_purpose_page16_preview.png';im.save(preview)
doc=fitz.open();pg=doc.new_page(width=960,height=540);pg.insert_image(pg.rect,filename=str(preview));doc.save(OUT/'model_purpose_page16_preview.pdf',deflate=True);doc.close()
(OUT/'model_purpose_page16_notes.md').write_text('# 16ページ：薄板化の仮説と理由\n\n'+notes+'\n')

def walk(ss):
 for s in ss:
  yield s
  if s.shape_type==MSO_SHAPE_TYPE.GROUP:yield from walk(s.shapes)
p=Presentation(pptx);ss=list(walk(p.slides[0].shapes))
with ZipFile(pptx) as z:
 assert z.testzip() is None
 assert not any(n.startswith('ppt/media/') for n in z.namelist())
assert len(p.slides)==1 and not any(s.shape_type==MSO_SHAPE_TYPE.PICTURE for s in ss)
assert not issues,issues
report={'slides':1,'native_objects':len(ss),'textboxes':sum(s.has_text_frame and bool(s.text.strip()) for s in ss),'pictures':0,'layout_issues':issues,'bytes':pptx.stat().st_size,'comparison':'equal curvature; different thickness','hypothesis':'strain-related additional particle rotation relative to matrix'}
(BASE/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source-pdf',type=Path);args=ap.parse_args()
 if args.source_pdf:
  original=fitz.open(args.source_pdf);new=fitz.open();new.insert_pdf(original,from_page=0,to_page=14)
  replacement=fitz.open(OUT/'model_purpose_page16_preview.pdf');new.insert_pdf(replacement);new.insert_pdf(original,from_page=16)
  assert len(new)==len(original);new.save(OUT/'interim_review_page16_replaced.pdf',garbage=4,deflate=True)
  print('Replaced PDF page16; pages',len(new))
