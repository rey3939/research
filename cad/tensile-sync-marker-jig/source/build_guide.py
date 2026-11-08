from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import fitz,json

ROOT=Path(__file__).resolve().parent.parent;W,H=1600,2100
REG='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
NAVY='#17334a';TEAL='#007f86';MUTED='#536b7c';ORANGE='#b45426';GRAY='#e8eef2'
pages=[];issues=[]
def ft(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
def text(x,y,w,s,n=30,b=False,c=NAVY,spacing=1.42):
 font=ft(n,b);lines=[]
 for para in s.split('\n'):
  line=''
  for ch in para:
   if line and font.getlength(line+ch)>w:lines.append(line);line=ch
   else:line+=ch
  lines.append(line)
 for i,line in enumerate(lines):d.text((x,y+i*n*spacing),line,font=font,fill=c,anchor='lt')
 end=y+len(lines)*n*spacing
 if end>2020:issues.append((s[:30],end))
 return end
def header(title,sub):
 global im,d
 im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,15),fill=TEAL)
 text(75,55,1450,title,52,True);text(78,145,1440,sub,28,c=MUTED)
 d.line((75,2020,1525,2020),fill='#bacbd6',width=2)
 d.text((80,2050),'引張試験・同期目印ホルダ／調整式試作モデル・単位mm',font=ft(23),fill=MUTED,anchor='lt')
 d.text((1480,2045),str(len(pages)+1),font=ft(30,True),fill=TEAL,anchor='lt')
def image(path,x,y,w,h):
 a=Image.open(path).convert('RGB');a.thumbnail((w,h));im.paste(a,(int(x+(w-a.width)/2),int(y+(h-a.height)/2)))
def card(x,y,w,h,s,n=29,c=NAVY,fill='#edf6f6'):
 d.rounded_rectangle((x,y,x+w,y+h),radius=15,fill=fill)
 text(x+24,y+22,w-48,s,n,c=c)
def done(name):
 p=ROOT/'views'/name;im.save(p);pages.append(p)

header('可動目印と固定目印を、別々の支持体で撮る','ロードセル上流の可動部と、下側固定部に取り付ける構成')
card(75,220,1450,160,'実機の白い可動部の寸法・バンド経路は未確認です。\n48×32の台座を取り付けられるか確認してから、全体を印刷してください。',31,ORANGE,'#fff0e5')
image(ROOT/'views/context_front.png',90,410,660,1160)
text(820,430,670,'可動側（右の縦レール）',34,True,TEAL)
text(820,495,670,'上の台座を、ロードセルより上流の白い可動部へバンド2本で固定。\n標線中央から上120を仮置き。\n縦レールは180を使用。',30)
text(820,790,670,'固定側（左の縦レール）',34,True,TEAL)
text(820,855,670,'下側の取り付け治具の、押さえ板より下にある縦壁へ固定。\n添付CADの面は幅55×高さ35.5。\n標線中央から下44を仮置き。',30)
text(820,1140,670,'撮影する目印',34,True,TEAL)
text(820,1205,670,'先端面は2.5×3。白い面に黒点を付け、試料表面とほぼ同じ奥行きへ合わせる。\n目印を含む横幅は約10.9。\n今の合焦距離で視野を確認。',30)
card(75,1650,1450,270,'図は、添付されたつかみ治具と公称35の試料を使った参考配置です。\n試験機本体・白い可動部・ロードセルはモデル化していません。\nねじ・ナット・結束バンドも省略しています。\n組立STEPは確認用。印刷には部品別STLを使用してください。',29)
done('guide_01.png')

header('部品とねじ類をそろえる','最初に穴確認用の小さな試験片と取付台座を試す')
rows=[('01','バンド用台座','2'),('02','水平長穴バー','2'),('03','コーナー','2'),('04','縦レール180（可動側）','1'),('05','縦レール90（固定側）','1'),('06 R/L','奥行き調整付き先端受け','各1'),('07 R/L','目印アーム','各1'),('08','穴・ナット収納部の確認用試験片','最初に1')]
yy=240
for i,(no,name,count) in enumerate([('番号','部品名','数量')]+rows):
 fill=TEAL if i==0 else '#f0f4f7' if i%2 else 'white';d.rectangle((75,yy,1525,yy+85),fill=fill)
 cc='white' if i==0 else NAVY
 text(100,yy+22,230,no,28,b=i==0,c=cc);text(350,yy+22,900,name,28,b=i==0,c=cc);text(1300,yy+22,180,count,28,b=i==0,c=cc)
 yy+=85
text(80,1055,1430,'ねじ類（既定の2組分）',34,True,TEAL)
text(85,1120,1420,'M3×12：4本　／　M3×16：16本　／　M3六角ナット：20個\nM3平座金：40枚程度　／　結束バンド：4本\n台座のナットは二面幅5.5・厚さ2.4を想定。台座側の座金は約0.5厚。\nバンド幅は3.5〜4.8程度。長さは実物の周長に合わせる。',29)
text(80,1380,1430,'印刷の出発点',34,True,TEAL)
text(85,1445,1420,'PLA、ノズル0.4、積層0.2、外周4本以上、充填30〜50%を候補にする。\nSTLは推奨方向で配置済み。先端受けはブリムを推奨。スライサーで接地・\n細い首・穴のブリッジを確認し、必要なサポートを判断する。\n240の長いレールと120の短いレールは交換候補。既定では印刷不要。',29)
card(75,1750,1450,200,'08の試験片：丸穴は左から径3.2／3.4／3.6。\n六角収納部は左から二面幅5.7／5.9／6.1。既定モデルは径3.4・二面幅5.9。\n入り具合を確認し、合わない場合は寸法補正後に本体を印刷してください。',28)
done('guide_02.png')

header('組み立てて、目印の位置を調整する','力の経路を追加せず、支持体の滑り・振動も確認する')
image(ROOT/'views/tip_detail.png',80,240,670,510)
text(820,245,670,'1　台座 → 水平バー → コーナー',31,True,TEAL)
text(820,300,670,'台座裏からナットを入れ、水平バーをM3×12で仮止め。\nコーナーと縦レールはM3×16。',28)
text(820,485,670,'2　縦レール → 先端受け → アーム',31,True,TEAL)
text(820,540,670,'先端受けは縦長穴へ2本で固定。\n目印アームは奥行き長穴へ2本で固定。\nRが可動側、Lが固定側。',28)
text(80,845,1430,'3　バンドで別々の部位へ固定し、位置を合わせる',34,True,TEAL)
text(85,910,1420,'上の台座はロードセル上流へ、下の台座は下側固定治具へ。配線や固定側まで\n一緒に縛らない。試料・ロードセル・反対側の治具へアームを接触させない。\n目印の前面を試料表面と同じ奥行きへ近づけ、締付け後の滑りを確認する。\n樹脂をつぶすほど締めず、ねじ先端が機械に当たらないことも確認する。',29)
text(80,1200,1430,'4　試料を付ける前に、小さい移動範囲で確認する',34,True,TEAL)
text(85,1265,1420,'静止時の目印位置、移動時の振動、往復後の位置の再現性を確認。\n録画中に、機械移動量ゼロと可動目印の基準位置を対応させる。\n目印面と同じ奥行きで画素寸法を校正し、動画の移動量とCSVの移動量を照合。\n時刻差と位置オフセットを同時に自由に合わせない。',29)
card(75,1555,1450,350,'CADで確認：部品12種類のSTEP再読み込みと閉じたSTLメッシュ。\n既定組立の樹脂部品間、および添付つかみ治具との初期配置で体積干渉なし。\n可動側を0／2／5／10／20動かした各位置で固定側との体積干渉なし。\n\n実機の取付け・全干渉・剛性・振動・同期精度は未検証です。\nこの治具は、JISが規定した同期装置ではありません。',28)
done('guide_03.png')

assert not issues,issues
doc=fitz.open()
for p in pages:
 page=doc.new_page(width=595.28,height=781.3);page.insert_image(page.rect,filename=str(p))
doc.save(ROOT/'assembly_guide.pdf',deflate=True)
(ROOT/'guide_validation.json').write_text(json.dumps({'pages':len(pages),'layout_issues':issues,'guide_image_size':[W,H]},ensure_ascii=False,indent=2))
print('Guide pages:',len(pages))
