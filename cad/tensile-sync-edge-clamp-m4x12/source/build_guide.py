from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parent.parent
fp=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
blue='#d9edf7';edge='#287d9b';orange='#e5ad41';gray='#dde2e7';navy='#17334a'
fig=plt.figure(figsize=(12,9),facecolor='white');fig.suptitle('実測14 mm用：M4×12で押さえるC字クランプ',fontproperties=fp,fontsize=18,y=.97,color=navy)
a=fig.add_axes([.055,.31,.55,.59]);a.set_aspect('equal');a.set_xlim(-14,34);a.set_ylim(-32,23);a.axis('off');a.set_title('側面断面：既存の水平部を上下から挟む',fontproperties=fp,fontsize=12,pad=15)
for x,y,w,h in [(-10,-23,10,34),(0,3,14,8),(0,-23,14,8)]:a.add_patch(Rectangle((x,y),w,h,facecolor=blue,edgecolor=edge,lw=1.8))
a.add_patch(Rectangle((0,-15),20,14,facecolor=gray,edgecolor='#758593',lw=1.5))
a.add_patch(Rectangle((5,-1),8,2,facecolor=orange,edgecolor='#ac7413',lw=1))
a.add_patch(Rectangle((7.35,3),3.3,8,facecolor='white',edgecolor=edge,lw=.7))
a.add_patch(Rectangle((7,.6),4,12,facecolor='#999',edgecolor='#444',lw=1))
a.add_patch(Rectangle((5.5,12.6),7,3,facecolor='#999',edgecolor='#444',lw=1));a.plot([7.5,10.5],[15.6,15.6],color='black',lw=2)
a.text(10,-8,'実機の水平部\n厚さ14 mm',fontproperties=fp,ha='center',va='center',fontsize=10,color=navy)
a.annotate('手持ちM4×12',xy=(9,15.6),xytext=(23,20),fontproperties=fp,fontsize=11,ha='center',color=navy,arrowprops=dict(arrowstyle='->',color=navy))
a.annotate('保護パッド\n厚さ2',xy=(10,0),xytext=(29,8),fontproperties=fp,fontsize=10,ha='center',color='#9a6614',arrowprops=dict(arrowstyle='->',color='#9a6614'))
a.annotate('',(22,-15),(22,3),arrowprops=dict(arrowstyle='<->',color=edge,lw=1.5));a.text(24,-6,'開口18',fontproperties=fp,rotation=90,ha='center',va='center',color=edge,fontsize=11)
a.annotate('',(0,-27),(14,-27),arrowprops=dict(arrowstyle='<->',color=edge,lw=1.5));a.text(7,-30,'差込み14（空き20）',fontproperties=fp,fontsize=10,ha='center',color=edge)
b=fig.add_axes([.66,.35,.30,.51]);b.set_aspect('equal');b.set_xlim(-26,26);b.set_ylim(-32,23);b.axis('off');b.set_title('正面（アームは省略）',fontproperties=fp,fontsize=12,pad=15)
b.add_patch(Rectangle((-22,-6),44,17,facecolor=blue,edgecolor=edge,lw=1.8));b.add_patch(Rectangle((-5,-23),10,17,facecolor=blue,edgecolor=edge,lw=1.8))
for x in [-9,9]:b.add_patch(Circle((x,0),1.65,facecolor='white',edgecolor=edge,lw=1))
b.add_patch(Rectangle((-2,11),4,1.6,facecolor='#999',edgecolor='#444'));b.add_patch(Rectangle((-3.5,12.6),7,3,facecolor='#999',edgecolor='#444'))
b.text(0,5,'2穴：アーム用M4',fontproperties=fp,fontsize=9,ha='center',color=navy)
b.annotate('',(-22,18),(22,18),arrowprops=dict(arrowstyle='<->',color=edge,lw=1.3));b.text(0,20,'44 mm',ha='center',va='center',fontsize=10,color=edge)
b.annotate('',(-5,-26),(5,-26),arrowprops=dict(arrowstyle='<->',color=edge,lw=1.3));b.text(0,-29,'挟む部分の幅10',fontproperties=fp,fontsize=9,ha='center',color=edge)
fig.text(.06,.25,'既存のロードセル固定ボルトは外さず、その脇の平坦な縁へ差し込みます。',fontproperties=fp,fontsize=12,color=navy)
fig.text(.06,.19,'保護パッドを置き、上のねじを少しずつ回して保持します。ねじ頭を面へ着座させるまで締め込みません。',fontproperties=fp,fontsize=10.5,color='#a34e29')
fig.text(.06,.13,'実測済み：厚さ14／空き奥行き20。上下両面に幅10×奥行14の平坦部があることは現物で確認。',fontproperties=fp,fontsize=10.5,color=navy)
fig.text(.06,.07,'ねじ頭は模式図です。下穴はプリント後にM4×0.7タップ加工。保持力・実機全体との適合は未検証です。',fontproperties=fp,fontsize=10.5,color=navy)
fig.savefig(ROOT/'views/mounting_detail.png',dpi=170);fig.savefig(ROOT/'mounting_detail.pdf');plt.close(fig)

exec((Path(__file__).parent/'guide_helpers.py').read_text(),globals())

header('写真と実測寸法に合わせたC字クランプ','全ねじM4×12・ナット不要・既存のロードセル固定ボルトは外さない')
card(75,220,1450,150,'実測：水平部の厚さ14、挟める平坦部の奥行き20。\n設計：開口18、差込み14、ジョー幅10、保護パッド厚さ2。',31)
image(ROOT/'views/mounting_detail.png',75,400,1450,1140)
card(75,1620,1450,300,'最初に01クランプ本体・02保護パッド・09穴確認用試験片を印刷。\n上下に幅10×奥行14以上の平坦部があり、差し込める空間を確認します。\n上のM4×12で保護パッドを押し、金属にねじ先端を直接当てません。\n柱・ガイド・リミット部品は挟まず、可動ブラケットだけに固定します。',29)
done('guide_01.png')

header('印刷する部品と、手持ちのねじ','RかLのどちらか一式だけを印刷する。左右を混在させない')
rows=[('01','クランプ本体 T14','1'),('02','保護パッド','1'),('03','水平長穴バー','1'),('04','コーナー','1'),('05','縦レール190','1'),('06','リブ付き奥行き調整部','1'),('07','横スライド受け','1'),('08','目印用の横長穴バー','1')]
yy=240
for i,(n,name,count) in enumerate([('番号','部品','数')]+rows):
 d.rectangle((75,yy,1525,yy+83),fill=TEAL if i==0 else '#f0f4f7' if i%2 else 'white');cc='white' if i==0 else NAVY
 text(100,yy+23,180,n,28,c=cc,b=i==0);text(320,yy+23,950,name,28,c=cc,b=i==0);text(1370,yy+23,110,count,28,c=cc,b=i==0);yy+=83
text(80,1040,1430,'金属部品はM4×12を13本のみ',34,True,TEAL)
text(85,1105,1420,'A〜Fの接続に2本ずつ、クランプ上の押さえに1本。\n写真のすりわり付き小ねじのような平らな座面を想定。頭径7以上を確認。\nナット・インサート・座金・結束バンドは不要。皿ねじ用の座面はありません。',29)
text(80,1345,1430,'印刷とタップ加工',34,True,TEAL)
text(85,1410,1420,'PLA、ノズル0.4、積層0.2、外周5本以上、充填40〜60%を出発点に試作。\nクランプ・ねじ受けは局所的に高密度にする。STLは推奨方向に配置済み。\nCOMMON/09は下段が径4.3／4.5／4.7、上段が径3.2／3.3／3.4。\n既定は逃げ穴4.5、下穴3.3。タップ後にM4ねじで確認する。',29)
card(75,1750,1450,200,'05bの240レールは交換候補。既定では印刷不要です。\nRは右寄り、Lは左寄りに取り付ける左右反転版です。\n現物で空きがある側を選び、01〜08を同じ側のフォルダから出力します。',28)
done('guide_02.png')

header('ねじを入れる方向とタップ加工する場所','「表」はカメラ側、「裏」は機械側。全てM4×12を使用する')
rows=[('A','水平バーの表 → クランプ本体','2'),('B','水平バーの裏 → コーナー','2'),('C','縦レールの表 → コーナー','2'),('D','縦レールの裏 → 奥行き調整部','2'),('E','奥行きレールの下 → 横スライド受け','2'),('F','目印バーの表 → 横スライド受け','2'),('P','クランプ上面から下へ → 保護パッドを押す','1')]
yy=240
for i,(n,name,count) in enumerate([('接続','ねじを入れる側 → ねじ受け側','数')]+rows):
 d.rectangle((75,yy,1525,yy+87),fill=TEAL if i==0 else '#f0f4f7' if i%2 else 'white');cc='white' if i==0 else NAVY
 text(100,yy+24,160,n,28,c=cc,b=i==0);text(280,yy+24,1040,name,28,c=cc,b=i==0);text(1380,yy+24,100,count,28,c=cc,b=i==0);yy+=87
text(80,1010,1430,'タップ対象は合計13穴',34,True,TEAL)
text(85,1075,1420,'01の3穴、04の4穴、06の2穴、07の4穴。\n径3.3の面からM4×0.7タップを通す。07の奥の径5.2は逃げ穴で、\nそちらへタップを立てたり、そちらからねじを入れたりしない。\n係合長さは8。B・Dは裏から入れるため、実機取付け前に机上で仮組み。',29)
image(ROOT/'views/clamp_detail.png',75,1360,580,540)
card(720,1390,805,480,'Pは押さえねじです。\n頭を面へ着座させるまで締めません。\n参考CADでは、パッドに接触した状態で\n頭が上面から1.6浮いています。\n\n強く締め過ぎず、滑り・割れ・空回りを\n確認します。保持力・ねじの強度は\n実物で検証が必要です。',27)
done('guide_03.png')

header('実機に合わせて高さ・奥行き・横位置を調整','固定側は既存の下側つかみ治具へ白地と黒点を貼る')
image(ROOT/'views/installation_R.png',80,230,660,1100)
text(820,250,670,'参考配置の数値',33,True,TEAL)
text(820,315,670,'左右位置20・高さ120は説明用の\n仮置きで、実測値ではありません。\n実測した形状は厚さ14・奥行き20の\n局所部分だけです。\n機械本体・ロードセルの全形状は\n復元していません。',28)
text(820,650,670,'調整する順番',33,True,TEAL)
text(820,715,670,'1　縦長穴で高さ\n2　リブ付きレールで奥行き\n3　横長穴で目印の横位置\n目印面を試料とほぼ同じ奥行きへ。\n白い面と黒点を付けて追跡します。',28)
text(80,1370,1430,'試料を付ける前に動作確認',34,True,TEAL)
text(85,1435,1420,'クランプとねじの滑り、振動、往復後の再現性、周辺との接触を確認。\n機械移動量ゼロと動画の目印位置を対応させ、同じ奥行きで縮尺を校正。\n動画とCSVのクロスヘッド移動量を照合して時刻を合わせる。\n固定点だけではCSVとの時刻合わせはできません。',29)
card(75,1730,1450,220,'CAD検証：STEP再読み込み、閉じたSTL、ねじ頭・軸と8の係合長さ。\n仮配置で0／2／5／10／20移動時に、下側つかみ治具との干渉なし。\n実機取付け・全干渉・保持力・剛性・耐久性・同期精度は未検証です。',28)
done('guide_04.png')

assert not issues,issues
doc=fitz.open()
for p in pages:
 page=doc.new_page(width=595.28,height=781.3);page.insert_image(page.rect,filename=str(p))
doc.save(ROOT/'assembly_guide.pdf',deflate=True)
(ROOT/'guide_validation.json').write_text(json.dumps({'pages':len(pages),'layout_issues':issues},ensure_ascii=False,indent=2)+'\n')
print('Guide pages:',len(pages))
