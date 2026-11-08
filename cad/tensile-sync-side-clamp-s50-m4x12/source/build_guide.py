from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parent.parent
fp=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
blue='#cce8f0';edge='#287d9b';orange='#e5ad41';gray='#dce2e7';navy='#17334a'
fig=plt.figure(figsize=(12,9),facecolor='white')
fig.suptitle('赤丸部分：50 mm離れた側面を挟む',fontproperties=fp,fontsize=20,color=navy,y=.97)
a=fig.add_axes([.06,.40,.59,.47]);a.set_aspect('equal');a.set_xlim(-44,55);a.set_ylim(-20,30);a.axis('off');a.set_title('上から見た断面模式図：押さえねじは横から',fontproperties=fp,fontsize=12,pad=20)
for x,y,w,h in [(-33,-10,68.2,10),(-33,0,8,14),(27.2,0,8,14)]:a.add_patch(Rectangle((x,y),w,h,facecolor=blue,edgecolor=edge,lw=1.8))
a.add_patch(Rectangle((-25,0),50,24,facecolor=gray,edgecolor='#758593',lw=1.2));a.plot([-25,25],[24,24],color='white',lw=4)
a.add_patch(Rectangle((25,5),2,8,facecolor=orange,edgecolor='#ac7413',lw=1))
a.add_patch(Rectangle((27.2,7.379),8,3.242,facecolor='white',edgecolor=edge,lw=.8))
a.add_patch(Rectangle((26.6,7),12,4,facecolor='#999',edgecolor='#444',lw=1));a.add_patch(Rectangle((38.6,5.5),3,7,facecolor='#999',edgecolor='#444',lw=1))
a.annotate('',(-25,20),(25,20),arrowprops=dict(arrowstyle='<->',lw=1.5,color=navy));a.text(0,22,'挟む面の間隔50 mm',fontproperties=fp,fontsize=12,ha='center',color=navy)
a.annotate('樹脂の保護パッド',xy=(26,5),xytext=(43,-15),ha='center',fontproperties=fp,fontsize=10,color='#9a6614',arrowprops=dict(arrowstyle='->',color='#9a6614'))
a.annotate('M4×12',xy=(40,9),xytext=(45,27),ha='center',fontproperties=fp,fontsize=11,color=navy,arrowprops=dict(arrowstyle='->',color=navy))
a.annotate('差し込む向き',xy=(-5,0),xytext=(-5,-18),ha='center',fontproperties=fp,fontsize=10,color=edge,arrowprops=dict(arrowstyle='->',color=edge,lw=2))
a.text(-29,9,'固定側',fontproperties=fp,fontsize=8,rotation=90,ha='center',va='center',color=edge)
b=fig.add_axes([.72,.40,.24,.47]);b.set_aspect('equal');b.set_xlim(-4,28);b.set_ylim(-13,14);b.axis('off');b.set_title('挟む側面の接触範囲',fontproperties=fp,fontsize=12,pad=20)
b.add_patch(Rectangle((0,-7),23,14,facecolor=gray,edgecolor='#758593',lw=1.2));b.add_patch(Rectangle((0,-5),14,10,facecolor=blue,edgecolor=edge,lw=1.5,alpha=.85))
b.annotate('',(25,-7),(25,7),arrowprops=dict(arrowstyle='<->',color=navy));b.text(27,0,'上下の高さ14',fontproperties=fp,rotation=90,ha='center',va='center',fontsize=10,color=navy)
b.annotate('',(0,-10),(14,-10),arrowprops=dict(arrowstyle='<->',color=edge));b.text(7,-12,'接触奥行き14',fontproperties=fp,ha='center',fontsize=10,color=edge)
b.text(7,0,'高さ10',fontproperties=fp,ha='center',va='center',fontsize=11,color=edge);b.text(0,11,'前方の縁 → 内側',fontproperties=fp,fontsize=10,color=navy)
fig.text(.06,.31,'50 mmは挟む方向、14 mmは上下の高さ。上下の面を挟む前回のクランプとは向きが異なります。',fontproperties=fp,fontsize=12,color=navy)
fig.text(.06,.24,'開口52.2＝実測50＋保護パッド2＋差込み用の余裕0.2。樹脂本体が50 mmをまたぎます。',fontproperties=fp,fontsize=11,color=navy)
fig.text(.06,.17,'まず01本体と02パッドだけで取付確認。両側面の高さ10×奥行14が平らか、現物で確認します。',fontproperties=fp,fontsize=11,color=navy)
fig.text(.06,.10,'既存の固定ボルトは外しません。ロードセル・柱に接触させません。図は局所形状の模式図です。',fontproperties=fp,fontsize=10.5,color=navy)
fig.savefig(ROOT/'mounting_direction.pdf');fig.savefig(ROOT/'views/mounting_direction.png',dpi=160);plt.close(fig)
exec((Path(__file__).parent/'guide_helpers.py').read_text(),globals())
header('穴寸法とはめあいの隙間：更新版','M4×0.7を使用。受け側は印刷後にタップ加工する')
rows=[('タップ加工する受け側','下穴 φ3.242'),('ねじを通す穴','φ4.20'),('ねじを通す長穴','幅4.20'),('保護パッドの浅いくぼみ','φ4.20'),('07の奥の加工逃げ穴','φ4.20'),('50 mm部分を挟む開口','52.20＝50＋パッド2＋隙間0.20')]
yy=250
for i,(n,val) in enumerate([('対象','今回のCAD寸法（mm）')]+rows):
 d.rectangle((75,yy,1525,yy+110),fill=TEAL if i==0 else '#f0f4f7' if i%2 else 'white');cc='white' if i==0 else NAVY
 text(100,yy+30,640,n,29,c=cc,b=i==0);text(770,yy+30,720,val,29,c=cc,b=i==0);yy+=110
text(80,1080,1430,'0.2 mmは合計の隙間です',35,True,TEAL)
text(85,1150,1420,'φ4.20の穴とφ4.00の軸は、直径差0.20、片側の隙間0.10。\nクランプの隙間0.20も合計値で、片側0.20ずつではありません。\n以上はCAD寸法です。印刷後の実寸法は09の試験片で確認します。',30)
text(80,1370,1430,'下穴φ3.242：めねじ内径の基本寸法に合わせる',34,True,TEAL)
text(85,1440,1420,'M4並目・ピッチ0.7のめねじ内径基本寸法は約3.242 mm。\n今回のCAD下穴はφ3.242 mmです。\n受け側13穴は、印刷後にM4×0.7のタップ加工をします。\nねじ山はCAD・STLに直接造形しません。',29)
card(75,1740,1450,190,'09試験片：下段は左からφ4.0／4.2／4.4、上段はφ3.2／3.242／3.3。\n製品部品の既定値は、下穴φ3.242・通り穴および長穴幅4.2です。\n全13本ともM4×12。ナット・インサートは使いません。',28)
done('hole_dimensions.png')

header('赤丸部分を50 mmの方向に挟む','上下14 mm用から、側面50 mm用へ取付方向を変更')
image(ROOT/'views/mounting_direction.png',65,230,1470,1170)
card(75,1450,1450,440,'最初は01本体・02パッド・COMMON/09穴確認用試験片だけを印刷。\n赤丸の前方の縁から差し込み、50 mm離れた両側面を押さえます。\n両面の高さ10×奥行14が平らか、既存部品と干渉しないかを確認。\n前に伺った空き奥行き20は、側面の平坦さを保証する寸法ではありません。\n横からM4×12を回し、パッドで保持します。ねじ先を金属へ直接当てません。\n押さえねじの頭を面に着座させるまで締め込まないでください。',29)
done('guide_01.png')
header('部品とM4×12の入れ方','RまたはLの一式を選ぶ。ナット・インサート・座金は不要')
rows=[('01','側面クランプS50','1'),('02','保護パッド','1'),('03 / 04','水平バー / コーナー','各1'),('05 / 06','縦レール190 / 奥行き調整部','各1'),('07 / 08','横スライド受け / 目印バー','各1')]
yy=240
for i,(n,name,q) in enumerate([('番号','印刷する部品','数')]+rows):
 d.rectangle((75,yy,1525,yy+82),fill=TEAL if i==0 else '#f0f4f7' if i%2 else 'white');cc='white' if i==0 else NAVY
 text(100,yy+23,230,n,28,c=cc,b=i==0);text(400,yy+23,930,name,28,c=cc,b=i==0);text(1360,yy+23,140,q,28,c=cc,b=i==0);yy+=82
text(80,780,1430,'M4×12を合計13本。設計上のねじ係合長さは8 mm。',33,True,TEAL)
text(85,850,1420,'A：水平バーの表 → 01本体（2本）\nB：水平バーの裏 → 04コーナー（2本）\nC：縦レールの表 → 04コーナー（2本）\nD：縦レールの裏 → 06奥行き調整部（2本）\nE：奥行きレールの下 → 07横スライド受け（2本）\nF：目印バーの表 → 07横スライド受け（2本）\nP：01本体の側面から横向き → 保護パッドを押す（1本）',29)
text(80,1220,1430,'プリント後にM4×0.7のタップ加工が必要',33,True,TEAL)
text(85,1285,1420,'01の3穴、04の4穴、06の2穴、07の4穴、合計13穴。径3.242側から加工。\n07の奥の径4.2は逃げ穴です。そちらからねじを入れません。\n普通のM4ねじを下穴へ無理にねじ込む方式ではありません。\n写真の平らな座面のねじを想定。頭径7以上を確認（頭径自体は未測定）。',28)
card(75,1550,1450,380,'印刷の出発点：PLA、ノズル0.4、積層0.2、外周5本以上、充填40〜60%。\nクランプ・ねじ受け部は局所的に高密度。強度を保証する条件ではありません。\nSTLは推奨方向に配置済み。本体はU字を平らに置きます。\nCOMMON/09で下穴・通り穴を確認。必要なサポートはスライサーで確認。\nB・Dは機械側から入れるため、実機取付け前に机上で仮組みします。\n05bの240 mmレールは交換候補で、最初から印刷する必要はありません。',28)
done('guide_02.png')
header('取付けと目印の位置合わせ','RとLは左右反転。空きがある側を選び、部品を混在させない')
image(ROOT/'views/installation_R.png',75,230,680,1100)
text(815,260,680,'参考配置について',33,True,TEAL)
text(815,330,680,'高さ120 mmは説明用の仮置きで、\n実測値ではありません。\n赤丸の局所形状を50×14で表現。\n機械本体・ロードセル・既存ボルトの\n全形状はモデル化していません。\n実機全体との干渉は現物で確認。',28)
text(815,710,680,'調整する順番',33,True,TEAL)
text(815,780,680,'1　縦長穴で高さ\n2　レールで奥行き\n3　横長穴で目印の横位置\n先端へ白地と黒点を付けます。\n試料とほぼ同じ奥行きに合わせ、\n今の合焦距離で撮影します。',28)
text(80,1360,1430,'固定基準と時刻同期',34,True,TEAL)
text(85,1430,1420,'固定点は既存の下側つかみ治具へ白地と黒点を付けて作ります。\n試料を付けず、小さい範囲で動かして滑り・振動・周辺との接触を確認。\n機械移動量ゼロと目印の基準位置を対応させ、同じ奥行きで縮尺を校正。\n動画とCSVのクロスヘッド移動量を照合します。固定点だけでは同期不可。',29)
card(75,1730,1450,220,'CAD確認：部品の有効形状・閉じたSTL・ねじ頭と軸の干渉・8 mm係合。\n仮のつかみ治具配置で、0／2／5／10／20 mm移動時の干渉を確認。\n実機適合・保持力・剛性・耐久性・同期精度は未検証の試作設計です。',28)
done('guide_03.png')
assert not issues,issues
doc=fitz.open()
for p in pages:
 pg=doc.new_page(width=595.28,height=781.3);pg.insert_image(pg.rect,filename=str(p))
doc.save(ROOT/'assembly_guide.pdf',deflate=True)
(ROOT/'guide_validation.json').write_text(json.dumps({'pages':len(pages),'layout_issues':issues},ensure_ascii=False,indent=2)+'\n')
print('guide pages',len(pages))
