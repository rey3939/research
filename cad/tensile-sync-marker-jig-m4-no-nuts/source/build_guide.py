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
 d.text((80,2050),'同期目印ホルダ／M4・ナット不要版／単位mm',font=ft(23),fill=MUTED,anchor='lt')
 d.text((1480,2045),str(len(pages)+1),font=ft(30,True),fill=TEAL,anchor='lt')
def image(path,x,y,w,h):
 a=Image.open(path).convert('RGB');a.thumbnail((w,h));im.paste(a,(int(x+(w-a.width)/2),int(y+(h-a.height)/2)))
def card(x,y,w,h,s,n=29,c=NAVY,fill='#edf6f6'):
 d.rounded_rectangle((x,y,x+w,y+h),radius=15,fill=fill)
 text(x+24,y+22,w-48,s,n,c=c)
def done(name):
 p=ROOT/'views'/name;im.save(p);pages.append(p)

header('同期用治具：M4ねじのみ・ナット不要版','ねじ受けを厚肉化し、下穴へM4×0.7タップ加工して締結する')
card(75,220,1450,160,'プリント後のM4×0.7タップ加工が必要です。\nSTEP/STLは径3.3の下穴モデル。ねじ山を直接造形する方式ではありません。',30,ORANGE,'#fff0e5')
image(ROOT/'views/context_front.png',90,410,660,1160)
text(820,440,670,'変更したところ',34,True,TEAL)
text(820,505,670,'長穴幅：4.5\n受け側下穴：3.3 → M4タップ\n受けの厚さ：10／12\n台座：44×32×10\nナット・インサート・座金：不要',30)
text(820,845,670,'M4ねじは2種類',34,True,TEAL)
text(820,910,670,'M4×12：8本\nM4×16：2本\n座金なしで長穴を押さえるため、\n頭径9〜10程度のトラス頭・\nフランジ付きねじを推奨。',30)
text(820,1230,670,'固定側は既存治具を利用',34,True,TEAL)
text(820,1295,670,'可動ホルダだけを製作。\n台座はロードセル上流へ\nバンド2本で固定する。\n固定点は下側つかみ治具へ貼る。',30)
card(75,1650,1450,270,'実機の白い可動部の寸法・バンド経路は未確認です。\n44×32の台座を取り付けられることを先に確認してください。\n台座裏のバンド逃げ溝を追加。通し方は mounting_detail.pdf を参照。\n印刷は部品別STLを使用し、旧M3版と部品を混在させないでください。',29)
done('guide_01.png')

header('ねじを入れる方向と、タップ加工する場所','「表」はカメラ側、「裏」は機械側。各接続は2本で固定する')
rows=[('A','水平バーの表 → 台座','M4×12','8'),('B','水平バーの裏 → コーナー','M4×12','8'),('C','縦レールの表 → コーナー','M4×12','8'),('D','縦レールの裏 → 先端受け','M4×12','8'),('E','奥行きレールの下 → アームの足','M4×16','10')]
yy=240
for i,(g,label,bolt,engage) in enumerate([('接続','ねじを通す側 → タップ側','ねじ','係合長')]+rows):
 fill=TEAL if i==0 else '#f0f4f7' if i%2 else 'white';d.rectangle((75,yy,1525,yy+95),fill=fill);cc='white' if i==0 else NAVY
 text(95,yy+28,130,g,28,b=i==0,c=cc);text(245,yy+28,900,label,28,b=i==0,c=cc);text(1160,yy+28,190,bolt,28,b=i==0,c=cc);text(1370,yy+28,135,engage,28,b=i==0,c=cc);yy+=95
text(80,900,1430,'先に確認用試験片を印刷する',34,True,TEAL)
text(85,965,1420,'08の試験片：下段の丸穴は左から径4.3／4.5／4.7（通り穴の確認）。\n上段は径3.2／3.3／3.4（タップ加工後の締結確認）。既定は4.5と3.3。',29)
text(80,1120,1430,'タップ加工する穴',34,True,TEAL)
text(85,1185,1420,'01の2穴、03の4穴、06の2穴、07の2穴。合計10穴。\n部品を保持し、必要なら下穴を径3.3に仕上げ、M4×0.7タップを穴軸へ\nまっすぐ通す。切粉を除去してから、M4ねじが入るか確認する。\n長穴・逃げ穴にはタップを立てない。普通のM4ねじを無理にねじ込まない。',29)
card(75,1490,1450,380,'組立前にタップ加工を完了してください。\nBとDのねじはバー・レールの裏から入れるため、装置の外で組み立てます。\nねじ先端は受け側裏面の2手前に収まる設計ですが、実物でも確認します。\n\nねじ山の強度・耐久性は未検証です。軽く締めて滑り・緩みを確認し、\n樹脂をつぶすほど締めないでください。摩耗や空回りが出た部品は交換します。',29)
done('guide_02.png')

header('印刷・組立後に、位置と動作を確認する','目印の前面を試料と同じ奥行きへ合わせる')
image(ROOT/'views/tip_detail.png',80,235,650,500)
text(820,245,670,'可動側のみ：樹脂6部品',33,True,TEAL)
text(820,310,670,'01台座・02水平バー・03コーナー、\n04レール180、06先端受けR、\n07アームRを各1個。\n08は先に印刷する確認用試験片。\n固定側のホルダは製作しない。',28)
text(820,590,670,'印刷条件の出発点',33,True,TEAL)
text(820,650,670,'PLA、ノズル0.4、積層0.2、\n外周5本以上、充填40〜60%。\nねじ受け付近は局所的に高密度へ。',28)
text(80,850,1430,'目印と取付けの確認',34,True,TEAL)
text(85,915,1420,'先端の2.5×3の面へ白いラベルと黒点を付ける。右上が可動、下側つかみ治具の点が固定。\n標線2本・可動点・固定点が同じ視野へ入るようにし、合焦距離を固定。\nアーム・ねじ・バンド端が、試料・ロードセル・反対側の部材に触れない\nことを確認する。実機のリミットと非常停止へのアクセスを保つ。',29)
text(80,1205,1430,'試料を付ける前に、小さな移動範囲で確認',34,True,TEAL)
text(85,1270,1420,'固定点は画面の揺れを確認する基準。奥行き差があると単純な差引補正は不可。\n機械移動量ゼロと動画の目印基準位置を対応させ、同じ奥行きで縮尺を校正。\n動画とCSVの同じ移動量を照合する。一定速度だけで時刻差と位置オフセットを\n両方自由に合わせない。停止中にもCSVが連続記録されるとは仮定しない。',29)
card(75,1570,1450,350,'CADで確認：部品の有効性、STEP再読み込み、閉じたSTLメッシュ。\n頭径10×高さ5のM4ねじ10本で、受け位置・係合長・不要な干渉を確認。\n可動側を0／2／5／10／20動かした各位置で、下側つかみ治具との干渉なし。\n\n実機取付け・全干渉・樹脂ねじの強度・振動・同期精度は未検証です。\n参考図は縮尺不同。M4ねじの参考CADも、ねじ山は省略しています。',28)
done('guide_03.png')

assert not issues,issues
doc=fitz.open()
for p in pages:
 page=doc.new_page(width=595.28,height=781.3);page.insert_image(page.rect,filename=str(p))
doc.save(ROOT/'assembly_guide.pdf',deflate=True)
(ROOT/'guide_validation.json').write_text(json.dumps({'pages':len(pages),'layout_issues':issues,'guide_image_size':[W,H]},ensure_ascii=False,indent=2))
print('Guide pages:',len(pages))
