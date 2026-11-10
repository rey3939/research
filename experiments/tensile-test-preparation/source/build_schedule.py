from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
exec((ROOT/'source/pdf_helpers.py').read_text(),globals())

def box(p,y,h,s,size=11.7):
 p.draw_rect(fitz.Rect(M,y,W-M,y+h),fill=LIGHT,color=None)
 end=text(p,M+12,y+9,W-2*M-24,s,size)
 if end>y+h-3:issues.append({'page':len(doc),'box':s[:25],'bottom':end,'limit':y+h})

def check(p,y,s,size=11.6):
 p.draw_rect(fitz.Rect(M+3,y+3,M+12,y+12),color=TEAL,width=.8)
 return text(p,M+23,y,W-2*M-23,s,size)+7

def stage(p,y,title,items):
 text(p,M,y,W-2*M,title,15.5,True,color=TEAL);y+=31
 for s in items:y=check(p,y,s)
 return y+15

p=new('引張試験　実験準備スケジュール','組立後から本試験までの作業順。チェック欄を使い、確認結果を記録する。')
box(p,99,54,'進め方：試料なしの動作・撮影・同期確認 → 予備試験1本 → 本試験\n目的：永久磁石エラストマーのヤング率・ポアソン比を評価する。',11.8)
y=177
y=stage(p,y,'1　治具の固定と無試料での動作確認',[
 'Pで本体を固定し、D・E・Fを含む接続のがたつき・滑り・傾きを確認。',
 '試料なしで小さい範囲を動かし、治具の振動と周辺への接触を確認。',
 'ロードセル本体・配線・柱・ガイドに接触していないことを確認。'])
y=stage(p,y,'2　可動点と固定点の準備',[
 '08の小さな先端に白地と黒点を付け、可動点にする。',
 '固定点は、既存の下側つかみ治具に付ける。',
 '可動点を試料表面とほぼ同じ奥行きへ合わせ、試料に触れない位置に置く。'])
y=stage(p,y,'3　カメラ・照明・縮尺を固定',[
 '今ピントが合っている距離・倍率でカメラを固定。撮影途中のピント・倍率・露出の変化を抑える。',
 '標線2本、試料の左右の縁、可動点、固定点が同じ画面に入る構図にする。',
 '試料と同じ奥行きで既知寸法のスケールを撮影。以後はカメラ位置と倍率を変えない。'])
y=stage(p,y,'4　動画とCSVの同期を予備運転で確認',[
 '先に録画し、開始前の静止状態と動き出す瞬間を残す。',
 '無試料で「静止→移動→停止」を記録。動画の移動量とCSVのクロスヘッド変位を照合する。',
 'CSVに時刻・荷重・変位が保存されることを確認。撮影設定と測定の記録間隔も控える。'])
assert y<805,('page1',y)

p=new('試験片の準備 → 予備試験 → 本試験','幅・厚み・標線間隔は試験片ごとに記録し、その試験片の値を解析に使う。')
y=103
y=stage(p,y,'5　試験片ごとの寸法と標線を記録',[
 '各試験片に番号を付け、幅b0と厚みt0を押しつぶさないように個別に測定。断面積A0＝b0×t0を記録する。',
 '白い標線2本を付け、乾燥させる。幅を測る中央部と、左右の縁が画像で見えることを確認する。',
 '標線間隔を「約10 mm」のまま計算に使わず、画像の実際の初期間隔L0を設定する。'])
y=stage(p,y,'6　試料を取り付け、初期状態を撮影',[
 'つかみ治具を取り付けた状態で、試料をつかむ前に荷重をゼロ化する。',
 '試料を真っすぐ取り付け、ねじれと、つかみ部の滑りがないことを確認する。',
 'たるみを取る小さな予荷重を予備試験で決めてそろえる。値と、その状態の標線間隔L0・幅w0を記録する。'])
y=stage(p,y,'7　予備試験を1本行い、解析可能か確認',[
 'これまでの設定10 mm/minで動画とCSVを同時取得。速度・記録間隔・撮影設定を保存する。',
 '標線間隔と幅を連続して追えるか確認。ヤング率には標線間の縦ひずみ、ポアソン比には同じ平行部の横ひずみを使う。',
 '同期・滑り・画像の追跡精度を確認し、評価するひずみ範囲を決めてから本試験へ進む。'])
text(p,M,y,W-2*M,'幅の測定精度を確認する',14,True,color=TEAL);y+=30
box(p,y,91,'以前の撮影のように試料幅が約120 pxなら、縦ひずみ1％・ポアソン比0.5とした幅変化は約0.6 pxです。静止状態も数秒撮り、幅の測定値の揺れと、試験中の横収縮を比較してください。',11.4)
y+=106
box(p,y,63,'最初に揃える3点：①予備試験1本の元動画　②同時取得したCSV　③その試験片の寸法記録。編集・圧縮前の元動画を保存する。',11.4)
assert y+63<805,('page2',y+63)

p=new('実験記録シート：試験片ごとに記入','必要な枚数を複写して使用。空欄は実測値・実際の設定値を記入する。')
# Blank cells are for handwriting, with room to record filenames.
rows=[
 ('試験日／担当者',''),('試験片ID／材料・作製条件',''),
 ('幅 b0［mm］／厚み t0［mm］',''),('初期断面積 A0［mm²］',''),
 ('予荷重［N］／荷重ゼロ化の時点',''),('画像の初期標線間隔 L0［mm・px］',''),
 ('画像の初期幅 w0［mm・px］',''),('引張速度［mm/min］','設定の目安：10（これまでの条件）'),
 ('CSVの記録間隔［s］',''),('動画の解像度／fps',''),
 ('縮尺［mm/px］／校正画像名',''),('同期に使う移動開始の位置・時刻',''),
 ('元動画ファイル名',''),('CSVファイル名','')]
y=104
for i,(label,value) in enumerate(rows):
 h=32;p.draw_rect(fitz.Rect(M,y,W-M,y+h),color=(.73,.80,.84),width=.6)
 p.draw_rect(fitz.Rect(M,y,M+225,y+h),fill=LIGHT,color=None)
 text(p,M+9,y+7,208,label,10.3)
 if value:text(p,M+234,y+8,276,value,9.7,color=MUTED)
 y+=h
text(p,M,y+19,W-2*M,'開始前・終了後の確認',14,True,color=TEAL);y+=49
for s in ['標線・左右の縁・可動点・固定点が追える。','静止時の幅の揺れ、同期、つかみ部の滑りを確認した。','元動画・CSV・寸法記録を同じ試験片IDで対応付けて保存した。']:
 y=check(p,y,s,11.4)
text(p,M,y+4,W-2*M,'気付いたこと・変更点：',11.5,True)
p.draw_line((M,y+55),(W-M,y+55),color=(.73,.80,.84),width=.6)
p.draw_line((M,y+82),(W-M,y+82),color=(.73,.80,.84),width=.6)
assert y+82<805,('page3',y+82)
assert len(doc)==3 and not issues,issues
doc.set_metadata({'title':'引張試験 実験準備スケジュール','subject':'組立後の準備・同期確認・予備試験・記録シート'})
out=ROOT/'tensile_test_preparation_schedule.pdf';doc.save(out,garbage=4,deflate=True);doc.close()
d=fitz.open(out)
for i in range(len(d)):
 assert pages[i] in d[i].get_text(),i+1
 d[i].get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(ROOT/'views'/f'page_{i+1:02d}.png')
(ROOT/'validation.json').write_text(json.dumps({'pages':len(d),'titles':pages,'layout_issues':issues,'japanese_text_verified':True,'pdf_bytes':out.stat().st_size,'date':'2026-11-10','schedule_type':'procedure order; no invented clock times'},ensure_ascii=False,indent=2)+'\n')
shutil.rmtree(font_dir,ignore_errors=True)
print('Created',out,'pages',len(d),'bytes',out.stat().st_size)
