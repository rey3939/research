from pathlib import Path
from zipfile import ZipFile
import json,math
ROOT=Path(__file__).resolve().parent.parent
exec((ROOT/'source/deck_engine.py').read_text(),globals())
plots=json.loads((ROOT/'data/source_plot_vectors.json').read_text())
TC={'t1':'0080FF','t2':'FF8000','t3':'FFD200','t4':'800040'}

def heading(x,y,w,s,size=32,c='teal'):text(x,y,w,50,s,size,c,True)
def body(x,y,w,s,size=31,h=140,c='ink'):text(x,y,w,h,s,size,c,wrapped=True)
def card(x,y,w,h,title,kind='teal'):
 rect(x,y,w,h,'pale' if kind=='teal' else 'peach' if kind=='orange' else 'light',r=15)
 text(x+22,y+17,w-44,50,title,min(31,31*(w-44)/max(1,measure(title,31,True))),kind,True)

def legend(x,y,series,size=22,spacing=140):
 for i,s in enumerate(series):
  cc=TC.get(s,{'Bx':'0000FF','By':'FF0000','Bz':'008000'}.get(s,'teal'))
  circle(x+i*spacing,y+13,6,cc)
  text(x+16+i*spacing,y,spacing-15,32,s.replace('t','t = '),size,cc)

def _native_plot(key,x,y,w,h,xlabel=None,ylabel=None,ticksize=24,highlight=None,showlegend=True):
 d=plots[key];x0,y0,x1,y1=d['frame'];xmin,xmax=d['xrange']
 def X(v):return x+(v-x0)/(x1-x0)*w
 def Y(v):return y+(v-y0)/(y1-y0)*h
 if highlight:
  a,b=highlight;xa=x+(a-xmin)/(xmax-xmin)*w;xb=x+(b-xmin)/(xmax-xmin)*w
  rect(xa,y,xb-xa,h,'pale')
 for val,yp in d['yticks']:
  yy=Y(yp);line(x,yy,x+w,yy,'gray',1)
  text(x-94,yy-15,76,35,f'{val:g}',ticksize,'muted',False,'right')
 xs=[0,1,2,3,4] if key=='components' else [-10,0,10,20,30,40]
 for v in xs:
  xx=x+(v-xmin)/(xmax-xmin)*w;line(xx,y+h,xx,y+h+7,'muted',1.5)
  text(xx-40,y+h+13,80,35,str(v),ticksize,'muted',False,'center')
 line(x,y,x,y+h,'muted',2);line(x,y+h,x+w,y+h,'muted',2)
 for m in d['markers']:
  poly([(X(a),Y(b)) for a,b in m['points']],fill=m['fill'],stroke=None,closed=True)
 label=ylabel or {'components':'磁束密度変化 ΔB [mT]','sensitivity':'感度 |S| [mT/mm]','r2':'決定係数 R²','nonlinearity':'非線形誤差 [%FS]'}[key]
 text(x-15,y-52,w+40,39,label,ticksize+2,'ink',True)
 text(x-25,y+h+57,w+50,37,xlabel or ('先端変位 u [mm]' if key=='components' else 'センサ位置 z_s [mm]'),ticksize,'muted',False,'center')
 if showlegend:legend(x+10,y-102,d['series'],ticksize-2,spacing=min(140,(w-10)/len(d['series'])))

def native_plot(key,*args,**kwargs):
 with group('実測グラフ：'+key):
  return _native_plot(key,*args,**kwargs)


def scheme_graph(x,y,w,h,linear=True):
 axes(x,y,w,h,'曲げ量','出力')
 pts=[]
 for i in range(51):
  q=i/50;v=q if linear else q*q
  pts.append((x+15+(w-40)*q,y+h-15-(h-40)*v))
 poly(pts,stroke='teal' if linear else 'orange',lw=4)
 for q in [.2,.4,.6,.8]:
  v=q if linear else q*q;circle(x+15+(w-40)*q,y+h-15-(h-40)*v,5,'teal' if linear else 'orange')

def metric_number(x,y,w,num,label,c='teal',size=60):
 numh=max(90,size*1.28+3);text(x,y,w,numh,num,size,c,True,'center');text(x,y+numh+10,w,75,label,26,'muted',False,'center')

# ── 本編：17枚、合計600秒 ──
new('永久磁石エラストマーの曲げ変形による磁場変化','中間審査会',
 '永久磁石エラストマーを曲げたときの磁場変化について報告します。実測で見られた感度と線形性の違いを整理し、それを今後のモデルでどう説明するかをお話しします。',15,'元資料 p.1、8｜図は模式図')
text(70,190,1050,150,'実測で特徴を捉え、\nモデルで理由を考える',51,'ink',True)
pill(75,390,490,'実測：感度・線形性を定量評価')
pill(75,454,620,'今後：1次元追従モデルで定性的に検証','orange')
text(75,611,880,105,'博士前期課程2年　機械工学プログラム\n大橋 怜倭',32)
with group('表紙：変形するPMEと磁場センサ'):
 clamp(1310,251);curved_strip(1310,251,390,100,48,particles=True)
 rect(1045,490,105,63,'bluepale','blue',r=8);text(1050,503,95,37,'Hall',26,'blue',True,'center')
 arrow(1200,510,1155,520,'blue',3)
text(1010,697,470,45,'曲がりを磁場で読み取る',29,'teal',True,'center')

new('柔らかい構造物の「曲がり」を知りたい','背景',
 'ソフトロボットなどでは、対象を柔らかいまま動かしながら、その曲がり具合を知りたい場面があります。対象の状態を知るには、変形についていけるセンサと、信号を曲げ量へ換算する仕組みが必要です。本研究は自己姿勢推定に向けた基礎評価です。',30,'元資料 p.3、8、21、39｜最終用途の模式図')
with group('柔らかいロボットと変形センサ'):
 tiny_robot(240,260,1.4);curved_strip(404,376,140,30,13,'orange')
 text(100,615,610,51,'対象の動きを妨げず、変形を測る',31,'ink',True,'center')
card(850,215,640,190,'① 大きな変形に追従できる')
body(880,282,570,'センサ自身にも柔らかさが必要',31,80)
card(850,440,640,190,'② 信号を曲げ量に換算できる')
body(880,507,570,'出力と入力の関係を把握する',31,80)
takeaway('最終目標：柔軟構造物の自己姿勢推定につながる曲げセンサ')

new('柔らかい磁石で、変形を磁場に変える','背景',
 '永久磁石エラストマー、PMEは、柔らかいエラストマーに磁性微粒子を混ぜ、着磁した材料です。広い弾性領域を活かせることが材料選択の利点です。変形で周囲の磁場が変わり、ホールセンサで読み取れます。図の回復過程は材料の利点を示す模式図で、本試料の弾性限界の測定結果ではありません。',40,'元資料 p.5、6、26、28｜模式図。本試料の弾性限界は未評価')
card(65,205,440,455,'材料：磁性粒子＋エラストマー')
rect(180,330,210,175,'white','teal',2)
for px,py in [(210,360),(270,370),(335,360),(230,430),(310,435),(350,475),(200,480)]:circle(px,py,9,'teal');arrow(px,py,px-26,py,'teal',2,7)
text(93,555,385,90,'SmFeN：30 vol.%\n母材：シリコーン',29,'ink',False,'center')
arrow(525,430,580,430)
card(600,205,450,455,'曲げると、粒子の配置が変わる')
clamp(895,320,95);curved_strip(895,320,220,0,0,'gray',dashed=True);curved_strip(895,320,220,75,48,particles=True)
arrow(835,551,887,551,'teal',2.5,8);text(900,531,120,36,'戻る',24,'teal',True)
text(622,575,405,50,'広い弾性領域を活用',31,'teal',True,'center')
arrow(1072,430,1127,430)
card(1150,205,385,455,'磁場を読み取る')
rect(1270,360,145,90,'white','blue',2,r=8);text(1278,379,129,55,'Hall',36,'blue',True,'center')
arrow(1200,404,1255,404,'blue',3)
text(1174,545,338,95,'曲げ量に応じた\n磁束密度変化',30,'ink',True,'center')
takeaway('変形 → 磁場変化 → 電気信号：接触させずに変化を読む')

new('線形なら、磁場から曲げ量へ換算しやすい','背景',
 '線形性が重要なのは、磁場から曲げ量を簡単に求められるからです。線形なら、同じ量だけ曲げるたびに信号の増分も一定になり、傾きと切片で換算できます。非線形でも換算できますが、入力によって傾きが変わるため、曲線に応じた校正が必要です。ここでの二つのグラフは概念図です。',40,'元資料 p.3、7、31をもとに整理｜グラフは概念図')
pill(220,204,370,'線形：増分が一定')
pill(1020,204,370,'非線形：増分が変わる','orange')
scheme_graph(170,330,440,230,True);scheme_graph(960,330,440,230,False)
text(120,654,610,48,'ΔBy = a u + b　→　u = (ΔBy − b)/a',28,'teal',True,'center')
text(870,654,600,48,'入力によって換算の傾きが変わる',29,'orange',True,'center')
takeaway('感度だけでなく、曲げ量への換算のしやすさを評価する')

new('実測で特徴を見つけ、モデルで理由を検討する','研究目的',
 '本研究では、まず曲げ変位と磁場の関係を実測し、厚みと測定位置によって感度・線形性がどう変わるかを定量的に評価します。次に、粒子が母材に追従する1次元モデルで、実測の特徴を定性的に説明できるか検証します。実験は完了し、モデルは今後の検証です。',30,'元資料 p.7、8、15～18｜直近の議論に基づき研究目的を整理')
text(95,180,1400,42,'先行例：接触力・一様圧縮　→　本研究：薄板の曲げ変形',27,'muted',False,'center')
card(80,235,650,365,'① 実測：どこで測ると使いやすいか')
metric_number(125,335,560,'厚み × 測定位置','感度・線形性を定量評価',size=47)
pill(260,620,280,'測定・評価済み')
arrow(755,425,825,425,'orange',4)
card(850,235,650,365,'② モデル：なぜ、その特徴が出るか','orange')
metric_number(885,335,570,'1次元追従モデル','実測の主要傾向を定性的に検証','orange',45)
pill(1050,620,250,'今後の予定','orange')
takeaway('実測された厚み・位置依存を説明し、曲げセンサの設計につなげる')

new('厚みと測定位置を変え、静的に曲げた','実測結果',
 '長さ40ミリ、幅10ミリの試料を一端で固定し、自由端を厚さ方向に0から4ミリまで静的に変位させました。厚みは1から4ミリ、センサ位置は固定端を原点とする7か所です。表面からのセンサ距離は一定に設定しました。各条件で同じ試料を3回測定し、平均を評価しています。図は座標関係を示す模式図です。',45,'元資料 p.10、26、30｜距離基準と同一試料3回はユーザー確認済み')
with group('実験配置：固定端と7測定位置'):
 x0,y0,L=605,290,350
 clamp(x0,y0,150);curved_strip(x0,y0,L,0,30,'gray');curved_strip(x0,y0,L,95,30,'teal')
 line(330,190,330,650,'blue',2,True)
 for z in [-10,-5,0,5,15,35,40]:
  yy=y0+L*z/40;circle(330,yy,6,'blue');text(350,yy-17,110,40,str(z),26,'muted')
 rect(218,404,88,50,'bluepale','blue',2,r=5);text(220,411,84,38,'Hall',25,'blue',True,'center')
 text(90,220,200,100,'センサを\n7位置へ移動',28,'blue',True,'center')
 text(485,190,300,52,'固定端 z_s = 0',29,'ink',True,'center')
 arrow(615,685,510,685,'orange',4,12);text(464,696,290,43,'先端変位 u',27,'orange',True,'center')
 text(630,430,220,90,'L = 40 mm\nW = 10 mm',27,'muted')
text(90,688,345,37,'灰：変形前／緑：曲げ後',22,'muted')
card(900,205,635,508,'厚み × 位置 × 曲げ量')
heading(925,282,575,'厚み t：1・2・3・4 mm',31)
heading(925,353,575,'変位 u：0～4 mm',31)
body(925,401,575,'0.5 mm刻みの9段階',29,55)
heading(925,478,575,'位置 z_s：7か所',31)
body(925,527,575,'−10, −5, 0, 5, 15, 35, 40 mm',27,50)
text(925,626,575,47,'同じ試料を3回測定 → 平均',29,'ink',True)
takeaway('試料の表面からセンサまでの初期間隔を一定に設定')

new('曲げ方向の磁場成分に着目し、3指標で評価','実測結果',
 '代表として厚み4ミリ、位置0ミリを示します。y成分の磁束密度が変位とともに大きく変わるため、この成分に着目します。評価するのは、1ミリ曲げたときの変化の大きさである感度、直線への近さを示す決定係数、直線からの最大のずれを示す非線形誤差です。感度は傾きの絶対値として表記します。',40,'実測グラフ：元資料 p.11｜元PDFのプロット位置を保持して再描画')
native_plot('components',157,350,650,310,ticksize=25)
pill(190,201,580,'代表条件：t = 4 mm、z_s = 0 mm')
for yy,title,desc in [(235,'感度 |S|','1 mm曲げたときの信号の変化量'),(405,'決定係数 R²','曲線がどの程度、直線に近いか'),(575,'非線形誤差','近似直線からの最大のずれ [%FS]')]:
 card(935,yy,590,130,title)
 text(957,yy+67,548,45,desc,27)

new('15 mm位置では、厚い試料ほど感度が高い','実測結果',
 'センサ位置15ミリにおける感度は、厚み1、2、3、4ミリの順に0.097、0.203、0.333、0.478でした。4ミリでは1ミリ比で約4.93倍です。これは観測された増加です。厚み4倍に感度4.93倍なので、厳密な比例と断定せず、磁性粉の総量や配置が関係するという仮説につなげます。',40,'数値：元資料 p.12｜表示値から編集可能な棒グラフを作成')
x,y,w,h=165,290,710,370
for v in [0,.1,.2,.3,.4,.5]:
 yy=y+h-v/.55*h;line(x,yy,x+w,yy,'gray',1);text(x-80,yy-17,65,37,f'{v:g}',25,'muted',False,'right')
line(x,y,x,y+h,'muted',2);line(x,y+h,x+w,y+h,'muted',2)
for i,v in enumerate([.097,.203,.333,.478]):
 xx=x+65+i*170;bh=v/.55*h;rect(xx,y+h-bh,95,bh,'teal');text(xx-20,y+h-bh-45,135,40,f'{v:.3f}',29,'ink',True,'center');text(xx,y+h+17,95,39,str(i+1),27,'muted',False,'center')
text(x,y-49,w,42,'感度 |S| [mT/mm]',28,'ink',True)
text(x,y+h+65,w,42,'厚み t [mm]',28,'muted',False,'center')
card(980,244,540,400,'厚み 1 → 4 mm')
metric_number(1000,345,500,'4.93 倍','感度の増加',size=94)
text(999,558,500,48,'比較位置：z_s = 15 mm',29,'muted',False,'center')
takeaway('観測事実：この位置では、厚みの増加とともに感度が増大')

new('固定端付近から15 mm位置で、線形性が高い','実測結果',
 '位置ごとに線形性を比べると、マイナス5から15ミリで、全ての厚みの決定係数が0.969以上、非線形誤差が9.75パーセントFS以下でした。厚み2から4ミリでは、決定係数0.993以上、非線形誤差6.46パーセントFS以下です。今回の静的変位範囲では、直線で換算しやすい領域が見つかりました。',40,'元資料 p.13の本文値とグラフ｜u = 0～4 mm、静的測定の範囲')
native_plot('r2',160,330,700,332,highlight=(-5,15),ticksize=25)
pill(260,179,480,'着色：−5 ≤ z_s ≤ 15 mm')
card(975,225,550,210,'全厚み t = 1～4 mm')
text(1002,302,495,100,'R² ≥ 0.969\n非線形誤差 ≤ 9.75 %FS',31,'teal',True,'center')
card(975,465,550,210,'t = 2・3・4 mm')
text(1002,542,495,100,'R² ≥ 0.993\n非線形誤差 ≤ 6.46 %FS',31,'teal',True,'center')
takeaway('固定端付近～15 mm位置は、直線換算しやすい領域')

new('自由端付近では、高感度と非線形性が現れる','実測結果',
 '自由端40ミリでは、厚み1から3ミリで感度は高い一方、決定係数は0.722から0.804でした。4ミリ試料は35ミリで高感度になり、40ミリでは感度が下がります。このように、厚みの効果は測定位置で変わります。なお、固定部マイナス10ミリの感度は小さいですが、それだけで外乱磁場が小さいと判断はしません。',40,'元資料 p.12、32、33｜測定値の特徴を整理。原因の説明は次の仮説へ')
native_plot('sensitivity',155,330,700,332,highlight=(33,40),ticksize=25)
card(975,200,550,190,'z_s = 40 mm：t = 1～3 mm')
body(1000,273,500,'感度：1.143～2.641 mT/mm\nR²：0.722～0.804',29,95)
card(975,417,550,190,'t = 4 mm：z_s = 35 mm')
body(1000,488,500,'感度：2.348 mT/mm\nR²：0.953',30,95)
text(980,646,540,73,'固定部 z_s = −10 mm は低感度\n|S| ≤ 0.020 mT/mm',26,'muted')
takeaway('感度と線形性は、厚み・測定位置の組合せで変わる')

new('直線換算を重視するなら、4 mm・15 mmが候補','実測結果',
 '実測の範囲では、厚み4ミリ、位置15ミリを、感度と直線換算のしやすさを両立する有望な候補とします。感度は0.478、決定係数は0.998です。最適性や微小変位の検出性能を確定するには、ノイズや推定誤差、対象に与える剛性の影響も必要です。ここでは今回の測定範囲での設計候補として示します。',25,'元資料 p.14｜「最適」を本測定範囲での有望な候補に修正')
card(75,215,610,455,'現時点の設計候補')
text(105,319,550,175,'厚み 4 mm\n位置 15 mm',64,'teal',True,'center')
text(105,548,550,78,'長さ40 mm・幅10 mm\n静的変位0～4 mmの範囲',29,'muted',False,'center')
metric_number(825,260,650,'0.478 mT/mm','感度 |S|',size=66)
metric_number(825,485,650,'0.998','決定係数 R²',size=77)
takeaway('次の問い：なぜ、厚み・位置で応答が変わるのか？','orange')

new('仮説：磁気源の位置・向きの変化で説明できるか','考察・仮説',
 '実測から厚みと位置による特徴が見つかりましたが、実測だけでは原因を特定できません。そこで、磁性粉の総量と、曲げに伴う磁気源の位置・磁化方向の変化を考えます。粒子が母材に追従するという単純な仮定でも、実測の主要な特徴が現れるかを、予定のモデルで検証します。これはまだ仮説です。',40,'元資料 p.7、12、13、16、17を再構成｜図は仮説を示す模式図')
card(70,210,460,450,'厚みで変わるもの','orange')
for i,(xx,tt) in enumerate([(180,20),(350,65)]):
 rect(xx,350,tt,175,'pale','teal',2)
 for j in range(3 if i==0 else 9):circle(xx+tt*(.25+.5*(j%2)),375+(j//2)*24,4.5,'teal')
text(90,563,420,90,'磁性粉の総量・\n磁場源の広がり',31,'ink',True,'center')
card(570,210,460,450,'曲げで変わるもの','orange')
clamp(900,321,100);curved_strip(900,321,210,80,28,particles=True)
text(592,563,416,90,'粒子の位置・\n磁化の向き',31,'ink',True,'center')
arrow(1050,430,1110,430,'orange',4)
card(1130,210,400,450,'モデルで検証する','orange')
text(1154,355,352,180,'母材に追従する\n磁気源の変化で\n実測の特徴が出る？',32,'orange',True,'center')
takeaway('実測結果 → 仮説 → 予定の1次元追従モデルによる検証','orange')

new('1次元追従モデルで、形状から磁場を計算する','モデル｜今後',
 'モデルは三段階です。まず、先端変位の拘束と曲げエネルギーから試料の形状を求めます。次に、各セグメントの磁気モーメントを母材の位置と回転に追従させ、磁場を足し合わせます。最後に、実測に見られた厚み・位置依存の傾向が再現されるか比較します。図は計算方法の模式図で、解析結果ではありません。',50,'元資料 p.17、34、35｜図は方法の模式図。モデル解析は今後実施')
for xx,tt in [(65,'1　変形形状を求める'),(565,'2　磁場を計算する'),(1065,'3　実測の特徴と比べる')]:card(xx,210,470,480,tt,'orange')
clamp(370,351,100);curved_strip(370,351,220,65,18,'teal',segments=True)
text(90,600,420,71,'曲げエネルギー＋\n先端変位の拘束条件',28,'ink',False,'center')
clamp(886,351,100);curved_strip(886,351,220,65,18,'teal',particles=True,segments=True)
rect(640,450,80,50,'bluepale','blue',2);text(642,457,76,34,'Hall',24,'blue',True,'center')
text(590,600,420,71,'位置・回転は母材に追従\n変形中の磁気モーメントは一定',25,'ink',False,'center')
for yy,ss in [(340,'厚みと感度の順序'),(435,'線形な応答の領域'),(530,'自由端付近の特徴')]:
 circle(1110,yy+18,18,'peach','orange',2);text(1098,yy-1,24,37,'?',25,'orange',True,'center');text(1147,yy,348,52,ss,29,'ink',True)
takeaway('省くもの：粒子単独の追加回転　／　母材の回転には追従する','orange',size=29)

new('薄いほど、追加回転を省いて説明しやすい？','モデル｜今後',
 '同じ曲率で比較すると、薄い試料ほど表面の曲げひずみは小さくなります。そこから、局所ひずみに伴う粒子単独の追加回転の影響も小さくなるのではないか、と仮説を立てます。ひずみが小さくなることと、追加回転が小さくなることは区別し、後者は未検証です。薄くしても、母材の曲がりに追従する回転は残ります。',40,'元資料 p.16、24｜同じ曲率での曲げひずみの説明。追加回転の減少は仮説')
pill(112,195,620,'前提：同じ曲げ形状・曲率 κ','orange')
text(125,250,940,35,'赤：引張側　／　青：圧縮側　　図は同じ曲率の模式図',23,'muted')
for xx,tt,title in [(435,78,'厚い：曲げひずみ 大'),(985,24,'薄い：曲げひずみ 小')]:
 pts,ns=curved_strip(xx,305,240,90,tt,'muted')
 poly([(p[0]+n[0]*tt/2,p[1]+n[1]*tt/2) for p,n in zip(pts,ns)],stroke='blue',lw=4)
 poly([(p[0]-n[0]*tt/2,p[1]-n[1]*tt/2) for p,n in zip(pts,ns)],stroke='red',lw=4)
 text(xx-220,587,440,50,title,32,'ink',True,'center')
arrow(580,435,720,435,'orange',4,16)
text(1110,335,380,115,'表面の曲げひずみ\n|ε|max ≈ |κ|t / 2',29,'muted',False,'center')
text(1090,510,420,117,'追加回転の影響も\n小さくなると予想',32,'orange',True,'center')
takeaway('追加回転を省いたモデルで、定性的に再現できる条件を調べる','orange',size=29)

new('定性的な一致を、3つの特徴で判断する','モデル｜今後',
 '今回のモデルでは、磁場の数値を真値とはせず、実測の主要傾向が再現されるかを確認します。比較するのは、厚みによる感度の順序、直線に近い領域、自由端の特徴です。主要傾向が再現されれば、母材追従モデルの説明力を支持できます。一致しても粒子追加回転がない証明にはならず、不一致も追加回転だけには帰属させません。',35,'元資料 p.15～18と直近の議論に基づく検証計画｜比較結果は未取得')
heading(135,207,650,'実測で確認した特徴',34,'teal');heading(930,207,560,'モデルで確かめること',34,'orange')
rows=[('15 mmで、厚いほど高感度','感度の大小関係が現れるか'),('固定端付近は直線に近い','線形な応答の領域が現れるか'),('自由端は位置で挙動が変わる','高感度・非線形の位置依存が現れるか')]
for i,(left,right) in enumerate(rows):
 yy=290+i*130;rect(80,yy,650,97,'pale',r=10);text(103,yy+23,605,54,left,30,'ink',True,'center')
 arrow(760,yy+50,828,yy+50,'orange',3)
 rect(860,yy,665,97,'peach',r=10);text(881,yy+23,623,54,right,29,'ink',True,'center')
text(92,700,1400,38,'分割数を変えても傾向が安定すること、条件ごとに恣意的に合わせ直さないことを確認',25,'muted',False,'center')
takeaway('一致はモデルの説明力を支持する。粒子追加回転の有無を断定しない','orange',size=29)

new('材料特性を測定し、予定のモデルで比較を進める','今後の予定',
 '今後は、まず作製した材料のヤング率とポアソン比を引張試験で測定します。ヤング率は曲げ剛性の入力、ポアソン比は横収縮の把握に使います。次に予定の1次元追従モデルを解析し、同じ厚み・位置・変位条件で実測の傾向と比べます。最後に一致した特徴と再現できない条件を整理し、設計指針とモデルの再現範囲をまとめます。',30,'元資料 p.18、27～29｜材料測定とモデル比較はいずれも今後の予定')
for x,title in [(70,'1　材料特性を測る'),(570,'2　モデルで計算する'),(1070,'3　実測と比較する')]:card(x,250,460,405,title,'orange')
text(97,355,406,160,'引張試験\nE：曲げ剛性の入力\nν：横収縮の把握',32,'ink',False,'center')
text(597,355,406,160,'1次元追従モデル\n実験と同じ条件で\n磁場を算出',32,'ink',False,'center')
text(1097,355,406,160,'一致する特徴\n再現しない条件\n定性的な再現範囲',32,'ink',False,'center')
arrow(535,455,562,455,'orange',3,10);arrow(1035,455,1062,455,'orange',3,10)
takeaway('実測の特徴を説明し、厚み・センサ配置の設計指針へつなげる','orange')

new('実測の特徴を、単純なモデルで説明する研究へ','まとめ',
 'まとめます。実測では、感度と線形性の厚み・測定位置依存を定量的に示しました。直線換算を重視する候補は厚み4ミリ、位置15ミリです。今後は、母材追従を仮定した1次元モデルで主要傾向を定性的に検証し、説明できる範囲を設計指針に結び付けます。以上です。',20,'実測結果：元資料 p.12～14、32｜モデルの検証結果は今後報告')
card(75,220,1450,190,'実測で分かったこと')
body(108,290,1380,'厚み・位置によって、感度と線形性が変わる。\n直線換算を重視する候補：t = 4 mm、z_s = 15 mm',35,105)
card(75,445,1450,190,'今後、モデルで確かめること','orange')
body(108,515,1380,'粒子単独の追加回転を省いた母材追従モデルで、\n実測の主要傾向を定性的に再現できるか。',35,105)
takeaway('入出力の定量評価 ＋ モデルによる機構の検討 → 曲げセンサの設計指針')

# ── 補足：質問時に表示する8枚 ──
new('試料・曲げ・測定の条件','補足｜実験条件',
 '詳細条件です。粒子径は元資料28・30ページの36マイクロメートルを採用し、26ページのミリメートル表記は修正しました。表面距離の基準と、同一試料で3回という点はユーザー確認済みです。',0,'元資料 p.10、26、28、30｜粒子径の単位はp.28、30に整合',True)
card(70,215,710,465,'試料')
for i,(a,b) in enumerate([('寸法','L = 40 mm、W = 10 mm'),('厚み','t = 1・2・3・4 mm'),('母材','SILPOT 184、主剤：硬化剤 = 10：1'),('磁性粒子','SmFeN、SFN2M-250A、36 μm'),('配合・着磁','30 vol.%、厚み方向')]):
 yy=295+i*70;text(95,yy,160,45,a,26,'teal',True);text(265,yy,480,48,b,25)
card(820,215,710,465,'測定')
for i,(a,b) in enumerate([('支持・入力','一端固定、自由端を厚み方向に変位'),('変位','0～4 mm、0.5 mm刻み'),('位置 z_s','−10, −5, 0, 5, 15, 35, 40 mm'),('センサ','x_s = 0、元資料 y_s = 10 mm'),('繰返し','各条件で同一試料を3回測定')]):
 yy=295+i*70;text(845,yy,165,45,a,25,'teal',True);text(1010,yy,490,52,b,24)
takeaway('距離の基準は試料表面。図中の変位は u、実測の y 成分は ΔBy と表記',size=28)

new('感度・決定係数・非線形誤差の定義','補足｜評価指標',
 '感度は符号付き回帰係数aの大きさとします。決定係数は直線への適合度であり、総合的な測定精度ではありません。非線形誤差は磁場変化の最大値と最小値の差で正規化します。信号幅がほぼゼロの位置では、R²や%FSの解釈に注意します。',0,'元資料 p.11、31｜感度の大きさと符号付き傾きを区別',True)
for yy,title,formula,desc in [(200,'感度 |S| [mT/mm]','ΔBy = a u + b　　|S| = |a|','1 mm変位させたときの磁場変化の大きさ'),(390,'決定係数 R²','R² = 1 − Σ(ΔBy_i − ΔBy_fit,i)² / Σ(ΔBy_i − ΔBy_mean)²','直線への適合度。推定誤差そのものではない'),(580,'非線形誤差 NL [%FS]','NL = 100 × max|ΔBy − ΔBy_fit| / (ΔBy_max − ΔBy_min)','最大残差を、測定した磁場変化の全幅で正規化')]:
 rect(75,yy,1450,165,'light',r=10);heading(103,yy+13,1370,title,29);text(103,yy+66,1370,47,formula,28,'ink',True);text(103,yy+115,1370,42,desc,25,'muted')

new('感度・線形性の測定位置依存を一覧で見る','補足｜実測グラフ',
 '三つの指標の全体分布です。点の位置は元PDFから保持しています。固定部では信号幅が小さく、R²や非線形誤差だけで性能を比較しません。各厚みは同一試料の3回平均であり、独立した複数試料の厚み効果を実証したものではありません。',0,'元資料 p.12、13｜点の位置を保持して再描画。生データの再解析ではない',True)
native_plot('sensitivity',125,350,350,300,ticksize=20)
native_plot('r2',650,350,350,300,ticksize=20)
native_plot('nonlinearity',1170,350,350,300,ticksize=20)
text(80,192,1440,45,'注目点：固定端側の線形性、自由端の位置依存、固定部の小さな感度',30,'ink',True,'center')
takeaway('各グラフの特徴を、同じ1次元追従モデルで定性的に再現できるか比較する','orange',size=27)

new('形状計算：曲げエネルギーと先端変位の拘束','補足｜モデルの式',
 '元資料の離散梁モデルを示します。曲げエネルギーと先端変位を与えるペナルティ項の和を最小化して形状を求めます。有限のペナルティでは先端変位の残差が生じるため、目標変位とのずれを確認します。厚みでEIが変わると同じペナルティ係数でも拘束誤差が変わり得るため、厚み間で実際の先端変位がそろっているか確認します。式の座標yは実験の変位方向に統一しています。',0,'元資料 p.34｜外部磁場で駆動する別の旧モデルフローは今回の計画に含めない',True)
card(75,215,1450,180,'先端変位の拘束')
text(110,285,1360,60,'E_constraint = (k_p / 2) × (y_tip − u_target)²',35,'ink',True,'center')
card(75,425,1450,180,'離散梁の曲げエネルギー')
text(110,495,1360,60,'E_bend = EI / (2Lseg) × {θ_1² + Σ(θ_i − θ_(i−1))²}',32,'ink',True,'center')
text(95,650,1410,66,'E_total = E_bend + E_constraint　を小さくする角度列 θ を求める',34,'orange',True,'center')
takeaway('分割数・収束条件・ペナルティによる先端変位のずれを確認する','orange',size=29)

new('磁場計算：磁気モーメントは母材に追従する','補足｜モデルの仮定',
 '各セグメントに磁気モーメントを置き、位置と向きは母材に追従させ、変形中の大きさは一定とします。同じ磁化を仮定する厚み間の比較では、総磁気モーメントは体積に対応させます。省略するのは粒子単独の追加回転です。元資料35ページの回転無しという表現は、ユーザー確認済みの定義に合わせて修正しました。点双極子の式を各要素に適用し、観測点で合成します。',0,'元資料 p.17、35｜回転の定義をユーザー確認済みの母材追従に統一',True)
card(70,220,650,440,'磁気モーメント m の仮定')
for i,s in enumerate(['大きさ：変形中は一定','位置：母材に追従','向き：母材の回転に追従','粒子単独の追加回転：省略']):text(103,309+i*77,585,57,s,31,'ink',i==3)
card(770,220,760,440,'各要素の磁場を足し合わせる')
text(800,320,700,120,'B = μ0 / (4πr³)\n     × {3(m・r)r / r² − m}',34,'ink',True,'center')
body(810,520,680,'r：要素から観測点へのベクトル\n各要素の磁場を観測点で合成する',28,95)
takeaway('1次元の磁場源の近似を含むため、一致する特徴と再現しない条件を整理する','orange',size=27)

new('薄板化の仮説：小さくなるのは曲げひずみ','補足｜仮説の根拠',
 '同じ曲率では表面の曲げひずみが厚みに比例します。厚さ方向のひずみ差は小さくなりますが、ひずみ勾配の大きさ自体は曲率で決まります。別材料PMFUEの0.536度という係数は、今回のPMEの曲げへ転用しません。追加回転が減るかは未検証です。',0,'元資料 p.16、22～24｜PMFUEの値は元資料から転記。原修論の新規照合は未実施',True)
card(70,215,700,455,'曲げひずみから言えること')
text(105,310,630,75,'|ε_b|max ≈ |κ|t / 2',45,'teal',True,'center')
body(105,430,630,'同じ曲率なら、薄いほど表面ひずみと断面内のひずみ差が小さい。\n母材の姿勢回転は残る。',31,155)
card(815,215,710,455,'先行研究からの動機','orange')
text(847,300,645,150,'PMFUEの一様圧縮\n1%圧縮あたり0.536°\n粒子がランダムに回転',32,'ink',True,'center')
body(855,492,630,'材料も変形も異なるため、PMEの曲げへ係数をそのまま移植しない。',28,125)
takeaway('力学的な根拠と、追加回転に関する未検証の仮説を区別する','orange',size=29)

new('定性的比較で言えること・確認すること','補足｜検証の位置づけ',
 '数値解析は仮定と入力条件に基づく予測です。分割数などを変えて主要傾向が変わらないことを確認し、入力値の決め方を明示します。定性的な再現はモデルの説明力を支持しますが、定量精度や粒子追加回転の不存在を証明しません。不一致も単一の原因へ帰属させません。',0,'直近の議論に基づく整理｜追加の物理モデルやCT観察を実施計画に加えていない',True)
card(75,215,700,460,'最低限確認すること')
for i,s in enumerate(['分割数・計算刻みを変えても傾向が安定','物性・磁化・センサ位置の決め方を明示','曲線ごとに恣意的な合わせ直しをしない','一致・不一致の特徴をどちらも示す']):body(105,300+i*81,640,s,28,75)
card(820,215,700,460,'結果の述べ方','orange')
body(853,315,634,'「母材追従を仮定したモデルで、実測の主要傾向を定性的に再現した」',34,155)
body(853,515,634,'一致しない場合も、追加回転だけを原因としない。',29,100)
takeaway('研究の到達点：実測の特徴を定性的に説明できるモデルの範囲を示す','orange',size=28)

new('出典と資料の位置づけ','補足｜参考文献',
 '引用は提供資料に記載された文献です。今回、原著本文を新しく照合したものではありません。新しい実験結果や解析結果は作成していません。元資料に含まれた過去の多段階モデル、CT、動的実験の計画は、今回の実施予定と混ざらないよう構成から整理しました。',0,'引用情報は提供PDFから転記。出典と構成対応の詳細は付属README・発表ノートを参照',True)
refs=[
 ('PMEの材料・製造','山口博司 他，磁気粘弾性体およびその製造方法，特開2016-152337，2016.'),
 ('PMEによるセンシング','S. Shembekar et al., PME Infused Soft Robot Skin for Tactile Sensing, IROS 2021, pp.6039–6046.'),
 ('入出力関係を使う先行研究','Qichen Wang et al., H-PME: Development of a Robot Skin Using Halbach Array Permanent Magnet Elastomer, Advanced Intelligent Systems 7(2), 2025.'),
 ('粒子挙動・磁場計算','大江岳歩，永久磁石発泡ウレタンエラストマーの圧縮による磁場変化，修士論文，2025.'),
 ('離散梁による形状計算','Benson Alejandro Kotei Zuriaga, Simulation of Permanent Magnet Elastomers Utilizing Discrete Elastic Rods, Master’s Thesis, 2026.')]
for i,(title,ref) in enumerate(refs):
 yy=205+i*112;heading(85,yy,1430,title,27);body(85,yy+45,1430,ref,23,66)
text(85,782,1420,42,'実測の出典：提供PDF p.10～14、30～33。解析結果は今後取得。',26,'muted',False,'center')

assert len(slides)==25
assert sum(s['seconds'] for s in slides if not s['backup'])==600
if issues:
 (ROOT/'layout_issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2))
 raise AssertionError(issues)
pptx=ROOT/'interim_review_rebuilt_editable.pptx';prs.save(pptx)
pdf.set_metadata({'title':'永久磁石エラストマーの曲げ変形による磁場変化｜中間審査会 改訂版','author':'大橋 怜倭','subject':'本編17枚・約10分＋補足8枚。実測から予定の1次元追従モデルによる定性的検証へ。'})
pdf.save(ROOT/'interim_review_rebuilt.pdf',garbage=4,deflate=True);pdf.close()
doc=fitz.open(ROOT/'interim_review_rebuilt.pdf')
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1,1)).save(ROOT/'previews'/f'slide_{i+1:02d}.png')
for name,lo,hi in [('main_01_09',1,9),('main_10_17',10,17),('backup_18_25',18,25)]:
 sheet=fitz.open();sp=sheet.new_page(width=1440,height=864)
 for j,n in enumerate(range(lo,hi+1)):
  xx=(j%3)*480+4;yy=(j//3)*288+4
  sp.show_pdf_page(fitz.Rect(xx,yy,xx+472,yy+266),doc,n-1)
 sp.get_pixmap().save(ROOT/'previews'/(name+'.png'));sheet.close()

notes=['# 発表ノート：本編17枚・10分＋補足8枚','実験は定量評価、モデルは今後の定性的検証。図形・プロットはPowerPoint上で編集可能。\n']
elapsed=0
for s in slides:
 if not s['backup']:
  start=elapsed;elapsed+=s['seconds'];timing=f'{start//60:02d}:{start%60:02d}～{elapsed//60:02d}:{elapsed%60:02d}（{s["seconds"]}秒）'
 else:timing='質疑用'
 notes.append(f'## {s["label"]}　{s["title"]}\n\n{timing}\n\n{s["notes"]}\n\n出典：{s["source"]}\n')
(ROOT/'speaker_notes.md').write_text('\n'.join(notes).rstrip()+'\n')
(ROOT/'data/slide_manifest.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2)+'\n')

def walk(shapes):
 for s in shapes:
  yield s
  if s.shape_type==MSO_SHAPE_TYPE.GROUP:yield from walk(s.shapes)
check=Presentation(pptx);objects=[s for sl in check.slides for s in walk(sl.shapes)]
for sl in check.slides:
 ids=[n.get('id') for n in sl._element.xpath('.//p:cNvPr')]
 assert len(ids)==len(set(ids)),('duplicate_shape_ids',ids)
for s in objects:
 assert s.left>=-em(.2) and s.top>=-em(.2) and s.left+s.width<=em(W+.2) and s.top+s.height<=em(H+.2),('shape_outside_slide',s.name,s.left,s.top,s.width,s.height)
with ZipFile(pptx) as z:
 assert z.testzip() is None
 media=[n for n in z.namelist() if n.startswith('ppt/media/')]
 assert not media,media
assert not any(s.shape_type==MSO_SHAPE_TYPE.PICTURE for s in objects)
assert len(doc)==len(check.slides)==25
for p in doc:
 for b in p.get_text('blocks'):
  assert b[0]>=-.2 and b[1]>=-.2 and b[2]<=W*K+.2 and b[3]<=H*K+.2,('pdf_text_outside_page',p.number,b[:4])
joined='\n'.join(s.text for s in objects if s.has_text_frame)
for expected in ['0.097','0.203','0.333','0.478','0.998','2.348','0.953','粒子単独の追加回転','定性的']:
 assert expected in joined,expected
assert '0.536' in joined
assert not any(s['seconds'] for s in slides if s['backup'])
validation={'slides':25,'main_slides':17,'backup_slides':8,'main_duration_seconds':600,'native_objects':len(objects),'textboxes':sum(bool(s.text.strip()) for s in objects if s.has_text_frame),'pictures':0,'embedded_media':0,'layout_issues':issues,'pptx_zip_valid':True,'pptx_reopened':True,'native_shape_bounds_verified':True,'shape_ids_unique':True,'pdf_text_bounds_verified':True,'pdf_searchable':True,'pdf_pages':len(doc),'pptx_bytes':pptx.stat().st_size,'pdf_bytes':(ROOT/'interim_review_rebuilt.pdf').stat().st_size,'source_pdf_pages':48,'source_plot_markers':{k:len(v['markers']) for k,v in plots.items()},'new_measurements_added':False,'model_results_available':False,'model_rotation':'follows_matrix_rotation; additional_particle_rotation_omitted','pdf_render_method':'vector PDF from the same layout definition; not Microsoft PowerPoint rendering','font_in_pptx':'Yu Gothic','font_in_pdf':'subset Noto Sans CJK'}
(ROOT/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(validation,ensure_ascii=False))
shutil.rmtree(font_dir,ignore_errors=True)
