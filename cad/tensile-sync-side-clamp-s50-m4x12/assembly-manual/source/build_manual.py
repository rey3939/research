from pathlib import Path
import json,fitz,math
ROOT=Path(__file__).resolve().parent.parent
W,H=595.28,841.89;M=36
NAVY=(.09,.20,.29);TEAL=(.0,.47,.52);MUTED=(.32,.40,.46);RED=(.70,.22,.18);ORANGE=(.76,.39,.10);LIGHT=(.93,.96,.97)
# Pre-subset the installed CJK fonts so the PDF remains small and searchable.
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter,Options
import tempfile,shutil
font_dir=Path(tempfile.mkdtemp(prefix='s50_manual_fonts_'))
chars=set(map(ord,Path(__file__).read_text()))
for weight in ['Regular','Bold']:
 original=TTFont('/usr/share/fonts/opentype/noto/NotoSansCJK-'+weight+'.ttc',fontNumber=0)
 opts=Options();opts.recalc_timestamp=False;opts.retain_gids=True;sub=Subsetter(options=opts);sub.populate(unicodes=chars);sub.subset(original);original.save(font_dir/(weight+'.otf'))
FONT=fitz.Font(fontfile=str(font_dir/'Regular.otf'));BOLD=fitz.Font(fontfile=str(font_dir/'Bold.otf'))

doc=fitz.open();issues=[];pages=[]
def text(p,x,y,w,s,size=12,bold=False,color=NAVY,leading=1.5):
 f=BOLD if bold else FONT;name='FB' if bold else 'FR';lines=[]
 for para in s.split('\n'):
  line=''
  for c in para:
   if line and f.text_length(line+c,fontsize=size)>w:lines.append(line);line=c
   else:line+=c
  lines.append(line)
 for i,line in enumerate(lines):
  yy=y+size+i*size*leading
  if yy>805 and y<814:issues.append({'page':len(doc),'text':line,'bottom':yy})
  p.insert_text((x,yy),line,fontname=name,fontsize=size,color=color)
 return y+len(lines)*size*leading

def new(title,sub):
 p=doc.new_page(width=W,height=H);p.insert_font(fontname='FR',fontbuffer=FONT.buffer);p.insert_font(fontname='FB',fontbuffer=BOLD.buffer)
 p.draw_rect(fitz.Rect(0,0,W,7),fill=TEAL,color=None)
 text(p,M,23,W-2*M,title,22,True);text(p,M,59,W-2*M,sub,10.5,color=MUTED)
 p.draw_line((M,83),(W-M,83),color=(.77,.83,.86),width=.7)
 p.draw_line((M,814),(W-M,814),color=(.77,.83,.86),width=.7)
 text(p,M,821,440,'S50・R用｜下穴φ3.242／通り穴4.2｜全ねじM4×12',8.6,color=MUTED)
 p.insert_text((W-55,830),str(len(doc)),fontname='FB',fontsize=10,color=TEAL)
 pages.append(title);return p

def image(p,name,x,y,w,h):p.insert_image(fitz.Rect(x,y,x+w,y+h),filename=str(ROOT/'views'/(name+'.png')),keep_proportion=True)
def box(p,x,y,w,h,s,size=11.5,color=NAVY,fill=LIGHT):
 p.draw_rect(fitz.Rect(x,y,x+w,y+h),fill=fill,color=None)
 end=text(p,x+12,y+9,w-24,s,size,color=color)
 if end>y+h-3:issues.append({'page':len(doc),'box_text':s[:25],'bottom':end,'limit':y+h})

def numbered(p,x,y,w,items,size=12):
 for i,s in enumerate(items,1):
  text(p,x,y,23,str(i)+'.',size,True,color=TEAL);end=text(p,x+24,y,w-24,s,size);y=end+12
 return y

def arrow(p,a,b,color=RED):
 p.draw_line(a,b,color=color,width=1.6)
 dx=b[0]-a[0];dy=b[1]-a[1];th=math.atan2(dy,dx);q=[b,(b[0]-6*math.cos(th)+3*math.sin(th),b[1]-6*math.sin(th)-3*math.cos(th)),(b[0]-6*math.cos(th)-3*math.sin(th),b[1]-6*math.sin(th)+3*math.cos(th))]
 sh=p.new_shape();sh.draw_polyline(q+[q[0]]);sh.finish(fill=color,color=color);sh.commit()

parts=[('01','クランプ本体','U字形。ねじで金属の\n50 mmの両側面を挟む。'),('02','保護パッド','小さな薄板。片面に\nねじ先用のくぼみ。'),('03','水平長穴バー','長さ94 mm、幅12 mm。\n横向きの長穴バー。'),('04','コーナー','十字に並ぶ4穴。\n厚さ10 mmのブロック。'),('05','縦レール190','長さ190 mm、幅10 mm。\n最も長い長穴部品。'),('06','奥行き調整部','ブロックとリブ付き\nレールが一体。'),('07','横スライド受け','横2穴・底2穴。\n小径側がタップ入口。'),('08','目印バー','長穴バーの片端に\n細い目印先端がある。')]
p=new('組立手順書：部品をそろえる','R＝試験機を正面から見て、縦アームが右へ出る構成。各部品1個。')
for i,(n,name,desc) in enumerate(parts):
 x=M+(i%2)*268;y=102+(i//2)*151
 p.draw_rect(fitz.Rect(x,y,x+255,y+141),color=(.78,.84,.87),fill=(.985,.99,.995),width=.6)
 text(p,x+9,y+7,237,n+'  '+name,12.5,True)
 image(p,'part_'+n,x+5,y+36,112,96);text(p,x+124,y+40,122,desc,10.4,leading=1.5)
box(p,M,720,W-2*M,76,'用意するもの：M4×12ねじ13本、マイナスドライバー、M4×0.7タップとハンドル（加工済みなら不要）、バリ取り道具。ナット・座金は使いません。09試験片と05bレール240は組立に不要です。',10.7)

p=new('1　受け側13穴にタップを立てる','下穴φ3.242の穴へM4×0.7を加工。加工済みなら、穴位置の確認だけで進む。')
text(p,M,99,W-2*M,'赤丸＝加工する小径穴。形の見え方は見る方向によって変わります。',11.3,color=RED)
for i,(n,title,desc) in enumerate([('01','01：正面2穴＋側面1穴','計3穴。側面の1穴は押さえねじP用。'),('04','04：十字に並ぶ4穴','計4穴。水平方向2穴と、上下方向2穴。'),('06','06：ブロック側の上下2穴','計2穴。レールの長穴は通すだけ。'),('07','07：横2穴＋底2穴','計4穴。図は下から見て、小径入口を示す。')]):
 x=M+(i%2)*268;y=133+(i//2)*231
 p.draw_rect(fitz.Rect(x,y,x+255,y+218),color=(.78,.84,.87),width=.6)
 text(p,x+9,y+7,237,title,11.7,True);image(p,'tap_'+n,x+8,y+31,239,137);text(p,x+10,y+174,235,desc,10.1)
numbered(p,M,616,W-2*M,['バリ・サポート材を取り除き、部品を保持してタップを穴の軸に合わせる。','加工後は切粉を除去し、M4ねじが手で数山入ることを確かめる。'],11.6)
box(p,M,737,W-2*M,58,'03・05・08の長穴、06のレール長穴、02のくぼみにはタップ不要。07の反対側にあるφ4.2の大径穴は加工逃げです。小径側から加工します。',10.7)

p=new('2　01と02だけで取付けを確かめる','この確認はアームを付ける前に行う。01・02だけ印刷した場合は、このページまで。')
image(p,'clamp_fit',M,100,330,246);image(p,'part_02',394,109,155,99)
text(p,378,224,171,'02の向き\nくぼみ：ねじ先側\n平らな面：金属側',12.3,True)
# Schematic top view, deliberately not a reconstructed full machine.
x0,y0,sc=150,401,3.2
xy=lambda x,y:(x0+(x+33)*sc,y0+y*sc)
def rr(x,y,w,h,fill):
 a=xy(x,y);p.draw_rect(fitz.Rect(a[0],a[1],a[0]+w*sc,a[1]+h*sc),fill=fill,color=(.3,.44,.5),width=.5)
rr(-33,-10,68.2,10,(.75,.88,.92));rr(-33,0,8,14,(.75,.88,.92));rr(27.2,0,8,14,(.75,.88,.92));rr(-25,0,50,20,(.84,.86,.88));rr(25,5,2,8,(.88,.74,.4));rr(26.6,7,12,4,(.53,.56,.59));rr(38.6,5.5,3,7,(.53,.56,.59))
text(p,126,348,350,'上から見た模式図：50 mmの両側面を挟む',11.3,True)
text(p,xy(-14,13)[0],xy(-14,13)[1],160,'面間隔50 mm',11,True)
arrow(p,(125,375),(125,435),TEAL);text(p,40,429,100,'前方の縁から\n差し込む',9.5,color=TEAL)
numbered(p,M,486,W-2*M,['Pねじを側面のタップ穴へ入れ、先端が内側へ突き出さない位置まで戻しておく。','赤丸で確認した前方部分へ01を差し込む。挟む方向は50 mm、上下の高さは14 mm。','02をねじ先と金属の間へ入れ、くぼみをねじ先へ向ける。','01を手で支え、Pを少しずつ回してパッドを当て、ずれない範囲で保持する。','取付けを確認したらPを緩め、01・02を外して机上の組立へ進む。'],11.7)
box(p,M,748,W-2*M,48,'Pは押さえねじです。頭を本体へ着座させるまで締め込みません。既存のロードセル固定ボルトは外しません。',10.8,color=RED,fill=(.99,.94,.91))

steps=[
 {'group':'A','title':'3　03を01へ取り付ける','sub':'M4×12を2本。ねじはカメラ側（表）から。','view':'表側から見た図','prefix':'A','items':['01の正面にある横並び2穴へ、03の長穴を重ねる。','03は右へ長く伸ばし、01が03の左端寄りになる位置に置く。','03側からM4×12を2本通し、01のタップ穴へ入れる。','2本とも手で数山掛けてから、交互に軽く締める。03の長穴はタップ加工しない。'],'check':'確認：ねじ頭 → 03（厚さ4 mm）→ 01の順。03が本体に平らに当たる。'},
 {'group':'B','title':'4　04を03の先端へ取り付ける','sub':'M4×12を2本。ねじは機械側（裏）から。','view':'裏側から見た図：正面から見た左右とは反転します','prefix':'B','items':['03の反対側の端に04を置く。04の横並び2穴を、03の長穴へ合わせる。','04は03のカメラ側に位置する。ねじは03の裏側から入れる。','M4×12を2本通し、04の横並び2穴へ手で数山入れる。','2本を交互に軽く締める。04の残る上下2穴は、次の05固定用に空けておく。'],'check':'確認：ねじ頭 → 03 → 04の順。Bは裏から入れるので、実機取付け前に組む。'},
 {'group':'C','title':'5　05を04へ取り付ける','sub':'M4×12を2本。05の縦レールは下へ長く伸ばす。','view':'表側から見た図。05は上端部分だけを表示','prefix':'C','items':['05の上端寄りの長穴を、04の上下2穴へ重ねる。','05が下向きに長く伸びる姿勢にする。','05の表側からM4×12を2本通し、04の上下2穴へ入れる。','縦レールを真っすぐにし、2本を交互に軽く締める。これで上部ユニットが完成。'],'check':'確認：ねじ頭 → 05（厚さ4 mm）→ 04の順。A・B・Cで計6本。'},
 {'group':'E','title':'6　07を06へ取り付ける','sub':'M4×12を2本。ねじはリブ付きレールの下から上へ。','view':'下側から見た図。赤矢印はねじの進む向き','prefix':'E','items':['06はレールのリブ・溝が下側を向く姿勢にする。','07の底にある小径2穴を下へ向け、06の長穴の上に置く。','06の溝側からM4×12を2本、上向きに通して07の底2穴へ入れる。','奥行き調整のため、2本はがたつかない程度の仮締めにする。07の横並び小径2穴はカメラ側へ向ける。'],'check':'確認：ねじ頭 → 06の中央板（厚さ4 mm）→ 07の底のタップ穴。リブは下側。'},
 {'group':'F','title':'7　08を07へ取り付ける','sub':'M4×12を2本。08の細い目印先端を試料側へ向ける。','view':'表側から見た図。R用では目印先端は左へ出ます','prefix':'F','items':['08の長穴を、07の横並び小径2穴へ重ねる。','R用では、08の細い目印先端が左、長穴が右になる姿勢にする。','08の表側からM4×12を2本通し、07の横並び2穴へ入れる。','横位置は後で合わせるので、2本を軽く仮締めする。これで下部ユニットが完成。'],'check':'確認：ねじ頭 → 08（厚さ4 mm）→ 07の横のタップ穴。E・Fで計4本。'},
 {'group':'D','title':'8　下部ユニットを05へ取り付ける','sub':'M4×12を2本。ねじは05の裏側から06へ。','view':'裏側から見た図。05は下端部分だけを表示','prefix':'D','items':['下部ユニットの06ブロックを05へ当て、上下2穴を05の長穴へ合わせる。','05の裏側からM4×12を2本通し、06の上下2穴へ入れる。','下部ユニットを手で支え、いったん05の下部に置いて仮締めする。','机上で全体を確認する。目印の高さは実機へ付けてからDで調整する。'],'check':'確認：ねじ頭 → 05 → 06のブロック。A〜Fで計12本。残るPの1本は実機固定用。'}]
for st in steps:
 p=new(st['title'],st['group']+'ねじ：'+st['sub'])
 box(p,M,98,W-2*M,33,st['view'],10.8,color=RED if st['group'] in ['B','D','E'] else TEAL)
 text(p,M,143,255,'分解状態',12.5,True);text(p,310,143,249,'組立後',12.5,True)
 image(p,st['prefix']+'_exploded',M,168,255,241);image(p,st['prefix']+'_done',310,168,249,241)
 box(p,M,428,W-2*M,40,'灰色：ここまでの組立　青：今回つける部品・ユニット　橙：今回使うねじ',10.2)
 end=numbered(p,M,492,W-2*M,st['items'],12)
 box(p,M,744,W-2*M,52,st['check'],10.8,color=TEAL)

p=new('9　全体を実機へ取り付ける','机上でA〜Fの12本を組んでから、Pの1本でブラケットへ固定する。')
image(p,'mounted_reference',M,108,258,432)
text(p,319,109,240,'取付ける場所',15,True,color=TEAL)
text(p,319,142,240,'前に赤丸で確認した、前方へ張り出した部分です。50 mm離れた両側面を、01と02で挟みます。\n\n黄色の立ち上がり部分は使いません。上面・下面の14 mm方向を挟む方式でもありません。',12)
box(p,319,341,240,172,'図の金属部は、50 mm幅・高さ14 mmの局所形状です。実機全体の復元ではありません。アームの高さ・奥行きは参考配置で、実機と撮影範囲に合わせます。',11.4)
numbered(p,M,558,W-2*M,['機械を停止し、組み立てた治具を手で支えて、01を前方の縁へ差し込む。','02の平面を金属側、くぼみをねじ側に向けて挟み、Pを少しずつ締めて保持する。','手を離す前に、ずれ・傾きがないか確認する。Pの頭を面へ着座させるまで締め込まない。','ロードセル本体、配線、柱、ガイドなどに接触していないか確認する。'],11.8)

p=new('10　目印の高さ・奥行き・横位置を合わせる','調整するユニットを手で支え、ねじを少し緩める → 動かす → 2本を交互に固定。')
image(p,'adjust_lower',M,102,W-2*M,315)
text(p,M,431,W-2*M,'位置調整に使うねじ',15,True,color=TEAL)
for i,(label,where,move) in enumerate([('D  2本','05の裏側','下部ユニットを上下へ：目印の高さ'),('E  2本','06のレール下側','07をレールに沿って移動：目印の奥行き'),('F  2本','08の表側','08を長穴に沿って左右へ：目印の横位置')]):
 y=466+i*53;p.draw_rect(fitz.Rect(M,y,W-M,y+47),fill=LIGHT,color=None)
 text(p,M+9,y+10,80,label,11.5,True);text(p,123,y+10,126,where,10.7);text(p,264,y+10,286,move,10.5)
text(p,M,641,W-2*M,'目印面の小さな先端（約2.5×3 mm）へ白地と黒点を付け、試料表面とほぼ同じ奥行きへ置きます。試料や標線に触れない位置に合わせてください。',12)
box(p,M,723,W-2*M,73,'下側の固定点は、既存の下側つかみ治具へ白地と黒点を付けて作ります。今の合焦距離で、標線2本・可動点・固定点が同じ画面に入るようにします。',11.5)

p=new('11　組立の最終確認・困ったとき','ねじの総数は13本。A〜F各2本、Pだけ1本。')
rows=[('A','03表 → 01','2'),('B','03裏 → 04','2'),('C','05表 → 04','2'),('D','05裏 → 06','2'),('E','06下 → 07底','2'),('F','08表 → 07横','2'),('P','01側面 → パッドを押す','1')]
text(p,M,101,W-2*M,'ねじの入れ方・早見表',15,True,color=TEAL)
for i,(g,into,n) in enumerate([('接続','入れる側 → 受け側','本数')]+rows):
 y=132+i*28;fill=TEAL if i==0 else LIGHT if i%2 else (1,1,1);cc=(1,1,1) if i==0 else NAVY
 p.draw_rect(fitz.Rect(M,y,W-M,y+28),fill=fill,color=None);text(p,M+10,y+5,70,g,10.5,i==0,cc);text(p,133,y+5,335,into,10.5,i==0,cc);text(p,501,y+5,45,n,10.5,i==0,cc)
text(p,M,379,W-2*M,'実験を始める前に',15,True,color=TEAL)
numbered(p,M,413,W-2*M,['A〜Fは頭が部品へ当たり、がたつきがない。Pはパッドを押し、頭を着座させる締め方にしていない。','試料を付けずに小さい範囲で動かし、滑り・振動・周辺との接触がないか確かめる。','往復して可動点が元の位置へ戻るか確認し、試料・標線と目印が接触しないことを確かめる。'],11.5)
text(p,M,596,W-2*M,'困ったとき',15,True,color=TEAL)
text(p,M,629,W-2*M,'01が入らない：50 mm方向か、02の向き・バリ・接触面の段差を確認。\n07が付かない：小径穴が底と手前、大径の逃げ穴が上・奥かを確認。\nB・Dへねじを入れられない：Pを緩めて治具を外し、机上で組む。\n目印が動く：D・E・Fのどこが動くか確かめ、その2本を固定する。',10.7,leading=1.65)
box(p,M,740,W-2*M,57,'この手順書はCADに基づくものです。実物の保持力・樹脂ねじの締付トルクは未実測です。標準ねじ山は印刷後のタップ加工で作ります。',10.7,color=MUTED)

assert len(doc)==12,len(doc)
assert not issues,issues
# Font subsetting retains selectable Japanese text without embedding entire CJK collections.
doc.set_metadata({'title':'S50・R用 同期目印ホルダ 組立手順書','subject':'M4×12・タップ下穴3.242 mm・図付き12ページ'});out=ROOT/'assembly_manual_R_S50.pdf';doc.save(out,garbage=4,deflate=True);doc.close()
preview=fitz.open(out)
for i in range(len(preview)):preview[i].get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False).save(ROOT/'views'/f'manual_page_{i+1:02d}.png')
(ROOT/'manual_validation.json').write_text(json.dumps({'pages':len(preview),'titles':pages,'layout_issues':issues,'side':'R','joints':{s['group']:2 for s in steps}|{'P':1},'tap_holes':{'01':3,'04':4,'06':2,'07':4},'tap_pilot_mm':3.242,'through_slot_width_mm':4.2,'sequence':['tap','fit01+02','A','B','C','E','F','D','mountP','adjustDEF'],'pdf_bytes':out.stat().st_size,'actual_machine_assembly_verified':False},ensure_ascii=False,indent=2)+'\n')
# A text version with the same order is accessible without opening the PDF.
md=['# S50・R用 同期目印ホルダ 組立手順書','[図付きPDFを開く](assembly_manual_R_S50.pdf)','対象：50 mmの両側面を挟むS50版。下穴φ3.242、通り穴・長穴4.2。樹脂8部品とM4×12ねじ13本。','Rは試験機を正面から見て縦アームが右へ出る構成。表＝カメラ側、裏＝機械側。作業順は **タップ → クランプ単体確認 → A → B → C → E → F → D → 実機へPで固定 → D/E/Fで調整**。','## 部品','\n'.join(f'- {n} {name}：1個。{desc}' for n,name,desc in parts),'## 受け側の加工','01は正面2穴と側面1穴、04は十字の4穴、06はブロック側上下2穴、07は横2穴と底2穴をM4×0.7でタップ加工します。07は小径側から加工し、大径の加工逃げ側へはタップを立てません。バリ・切粉を除去してください。','## クランプ単体の取付け確認','Pを緩め、先端が内側へ突き出さない位置にします。赤丸で確認した前方部分の50 mm離れた両側面へ01を差し込みます。02はくぼみをねじ側、平らな面を金属側へ向けます。Pを少しずつ回して保持し、頭を本体へ着座させるまで締めません。確認後は実機から外して机上で組み立てます。01と02だけ印刷した場合は、ここまでで構いません。']
for st in steps:
 md += ['## '+st['title']+'（'+st['group']+'）',st['sub'],st['view'],'\n'.join(f'{i}. {s}' for i,s in enumerate(st['items'],1)),st['check'],f"![{st['group']}の分解図](views/{st['prefix']}_exploded.png)",f"![{st['group']}の組立後](views/{st['prefix']}_done.png)"]
md += ['## 実機への取付け','A〜Fの12本を机上で組んでから、Pで赤丸の50 mmの両側面へ固定します。02のくぼみをねじ先へ向けます。既存のロードセル固定ボルトは外しません。Pの頭を面へ着座させるまで締め込まず、ずれない範囲で保持します。機械全体・ロードセル・配線・柱・ガイドとの接触を確認します。','## 位置調整','下部ユニットを手で支え、D（05裏の2本）で高さ、E（06下の2本）で奥行き、F（08表の2本）で横位置を合わせます。目印先端の白地と黒点を、試料表面とほぼ同じ奥行きへ置きます。固定点は既存の下側つかみ治具へ付けます。標線2本・可動点・固定点を、今の合焦距離で撮影できる位置に合わせます。','## 最終確認','A〜F各2本とP1本の計13本を確認。試料を付けず小さい範囲で往復させ、滑り・振動・接触と、目印が元の位置へ戻るかを確認します。CAD上の手順であり、実物の保持力・締付トルクは未実測です。','## 元のCADと再生成','[対応するCAD一式](../README.md)。本手順書の追加に伴うCAD形状の変更はありません。','`python source/render_steps.py --design-root ..` で図を生成し、`python source/build_manual.py` でPDFを生成します。CadQuery、NumPy、Pillow、PyMuPDF、fontToolsとNoto Sans CJKフォントを使用します。']
(ROOT/'README.md').write_text('\n\n'.join(md)+'\n')
print('Created',out,'pages',len(preview),'bytes',out.stat().st_size)

shutil.rmtree(font_dir,ignore_errors=True)
