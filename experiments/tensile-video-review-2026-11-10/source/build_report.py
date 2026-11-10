from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
exec((ROOT/'source/pdf_helpers.py').read_text(),globals())
s=json.loads((ROOT/'data/review_summary.json').read_text());c=json.loads((ROOT/'data/csv_summary.json').read_text());sync=json.loads((ROOT/'data/sync_summary.json').read_text())
def image(p,n,x,y,w,h):p.insert_image(fitz.Rect(x,y,x+w,y+h),filename=str(ROOT/'figures'/n),keep_proportion=True)
def box(p,y,h,t,size=11.4):
 p.draw_rect(fitz.Rect(M,y,W-M,y+h),fill=LIGHT,color=None);end=text(p,M+12,y+9,W-2*M-24,t,size)
 if end>y+h-3:issues.append({'page':len(doc),'box':t[:20],'bottom':end,'limit':y+h})
def bullet(p,y,t,size=11.5):
 p.draw_circle((M+4,y+7),2,fill=TEAL,color=None);return text(p,M+17,y,W-2*M-17,t,size)+9

p=new('動画・CSVの確認結果（予備評価）','対象：2026-11-10の引張試験1本。動画とCSVを独立に確認して照合。')
box(p,100,62,'縦方向の伸びは画像から追跡できる見込みがあります。物性値の確定には、試験片の寸法実測・同期精度・幅の画像計測精度をそろえる必要があります。',12)
rows=[('動画','約69.38秒、3840×2160、約60 fps（表示は縦向き）'),('CSV','542行、約65.34秒、保存間隔の中央値0.12秒'),('引張速度','時刻と移動量から約9.97 mm/min'),('最大荷重','CSV上で約4.075 N（48.01秒）'),('急減','CSV 48.85～48.97秒で大きく低下'),('破断','動画65.37～65.47秒の間に目視できる開口が発生'),('寸法','未実測。型の幅2 mm・厚み1 mmは仮定値')]
y=186
for a,b in rows:
 p.draw_rect(fitz.Rect(M,y,W-M,y+35),fill=LIGHT if int((y-186)/35)%2==0 else (1,1,1),color=None);text(p,M+8,y+9,88,a,11.2,True);text(p,M+105,y+9,410,b,10.8);y+=35
text(p,M,458,W-2*M,'現状の判断',15,True,color=TEAL)
y=492
for t in ['標線周辺の2領域を元画像へ直接照合する方法で、破断前の縦方向の伸びを追跡できました。厳密な標線中心の標準化・精度校正は未実施です。','同期用治具がなくても、破断と荷重急減から概略の時刻差を見積もれます。共通トリガーによる精密な同期ではありません。','ヤング率は断面積が必要です。今回は実寸法がないため、型寸法を仮定した参考計算と区別します。','ポアソン比は、輪郭の凹凸・バリ状の部分、画像の揺れ、幅を測る位置と方法の影響を確認する必要があります。']:
 y=bullet(p,y,t)
box(p,744,53,'この資料は撮影・記録条件の予備確認です。以下の数値を、そのまま材料の確定した物性値やJIS準拠の結果として扱うものではありません。',10.6)

p=new('画像で見えたことと、追跡の定義','左：初期フレームの計測領域。右：接続状態から破断開口が生じた前後。')
image(p,'measurement_regions.png',M,106,235,451);image(p,'rupture_comparison.png',302,106,257,451)
text(p,M,574,240,'青：標線周辺の追跡領域\n橙：中央付近の幅の評価帯\n赤：輪郭の凹凸・細い部分',10.7)
text(p,302,574,257,'上側の白い標線付近で破断。\n塗料が原因とは断定できません。\n表面の傷や塗膜も確認する箇所です。',10.7)
box(p,657,130,'画像追跡は、白線周辺の元画像を拡大・縮小して照合した仮想標点の計測です。初期の2領域間距離は約600 px、中央幅は約124 pxでした。これは「標線間隔が実測10 mm」という意味ではありません。\n\n試料表面の模様は追跡に使えますが、白い塗膜は割れ方や太さが不均一で、輪郭には細い突出部も見られます。毎回同じ基準で読むことが必要です。',11.2)

p=new('荷重・伸び・時刻の照合','フレーム番号÷60ではなく、動画に記録された表示時刻（PTS）を使って確認。')
image(p,'csv_overview.png',M,101,W-2*M,270)
image(p,'video_tracking_overview.png',M,389,W-2*M,271)
box(p,677,113,'破断前後を照合すると、動画時刻－CSV時刻は概ね16.5秒です。可視グリップの運動開始を近似モデルで推定すると約16.9秒となり、推定方法で約0.4秒の差がありました。運動モデル・荷重応答・追跡誤差も含むため、精密な同期の確認には使い切れません。\n次回は上流の可動点と下側の固定点を入れ、開始前の静止状態から記録します。',11.1)

p=new('幅の精度と参考計算・次回の準備','材料の確定値ではなく、今回のデータがどこまで使えそうかを見る試算。')
text(p,M,101,W-2*M,'幅の精度',15,True,color=TEAL)
box(p,132,76,f'3～10秒の静止区間で、中央幅の揺れの標準偏差は約{s["static_width_std_px"]:.2f} px。幅約124 pxの試料が1％伸び、ポアソン比0.5なら幅変化は約0.62 pxです。1枚同士の比較だけで、小ひずみのポアソン比を決めるには厳しい大きさです。',11.2)
image(p,'poisson_sensitivity.png',M,221,W-2*M,214)
text(p,M,452,W-2*M,'参考計算の読み方',14.5,True,color=TEAL)
y=483
for t in ['断面積を型寸法の2 mm²と仮定し、仮想標点のひずみ0.5～5％の複数範囲で直線を当てた傾きは、概ね7.7～8.2 MPaでした。実測断面積に基づくヤング率の確定値ではありません。','同じ初期ひずみ域で幅の位置・輪郭しきい値を変えた見かけのポアソン比は約0.32～0.41。これは不確かさの保証区間ではありません。静止時の揺れが大きい1条件は除外しています。','大ひずみ側で幅が跳ぶ箇所は、輪郭抽出の不安定さを含みます。今回の参考値は初期域だけのものです。']:
 y=bullet(p,y,t,10.9)
text(p,M,y+4,W-2*M,'次回はこの順にそろえる',14,True,color=TEAL);y+=36
for t in ['試験前に、試験片ごとの幅・厚みを実測して記録する。','標線を細く均一にし、縁のバリ・段差・傷を確認する。','同期用の可動点と固定点、同じ奥行きの縮尺を撮影する。','静止動画と荷重データも残し、初期ひずみ域の点数と低荷重域の測定精度を確認する。']:
 y=bullet(p,y,t,10.8)
assert y<803,('page4',y)
assert len(doc)==4 and not issues,issues
doc.set_metadata({'title':'2026-11-10 引張試験の動画・CSV予備評価','subject':'未実測の型寸法を用いた参考計算と、次回の改善点'})
out=ROOT/'tensile_test_review_2026-11-10.pdf';doc.save(out,garbage=4,deflate=True);doc.close();d=fitz.open(out)
for i,t in enumerate(pages):
 assert t in d[i].get_text()
 d[i].get_pixmap(matrix=fitz.Matrix(1,1)).save(ROOT/'figures'/f'report_page_{i+1:02d}.png')
(ROOT/'report_validation.json').write_text(json.dumps({'pages':len(d),'titles':pages,'layout_issues':issues,'pdf_bytes':out.stat().st_size,'japanese_text_verified':True,'specimen_dimensions_measured':False,'reference_area_mm2':2,'reported_moduli_are_exploratory':True},ensure_ascii=False,indent=2)+'\n');shutil.rmtree(font_dir,ignore_errors=True);print('Created',out,'pages',len(d),'bytes',out.stat().st_size)
