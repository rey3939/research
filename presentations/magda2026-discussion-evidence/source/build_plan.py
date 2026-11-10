from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
exec((ROOT/'source/pdf_helpers.py').read_text(),globals())
calc=json.loads((ROOT/'data/preliminary_calculations.json').read_text())
def image(p,n,x,y,w,h):p.insert_image(fitz.Rect(x,y,x+w,y+h),filename=str(ROOT/'figures'/n),keep_proportion=True)
def box(p,y,h,t,size=11.3):
 p.draw_rect(fitz.Rect(M,y,W-M,y+h),fill=LIGHT,color=None);end=text(p,M+12,y+9,W-2*M-24,t,size)
 if end>y+h-3:issues.append({'page':len(doc),'box':t[:20],'bottom':end,'limit':y+h})
def bullet(p,y,t,size=11.3):
 p.draw_circle((M+4,y+7),2,color=None,fill=TEAL);return text(p,M+17,y,W-2*M-17,t,size)+9

p=new('考察強化プラン：MAGDA2026','対象：追加添付の「実験結果・評価指標.pptx」4ページと、ユーザー確認済みの距離条件。')
box(p,100,72,'狙い：観測事実と原因の説明を分け、独立した測定・モデルの予測・対照実験をそろえる。「文献にもある」だけで、自分の実験の原因を確定することはできません。',12)
text(p,M,191,W-2*M,'1　厚みと感度：「増加」と「比例」を分ける',15,True,color=TEAL)
image(p,'thickness_normalization.png',M,226,W-2*M,226)
y=474
for t in ['提示値は1 mmで0.097、4 mmで0.478 mT/mm。厚み4倍に対して感度4.93倍は観測事実です。','S/tは0.097と0.1195で約23.2％異なります。誤差棒がない段階では、厳密な比例とも、比例から有意に外れたとも断定できません。','今回の抜粋は2厚み。以前の中間審査資料にある2・3 mmのデータも利用し、実測厚みと繰返しのばらつきを使ってS/tを評価します。','表面からセンサ距離を一定にした比較では、磁性粉の総量に加え、磁場源の中心位置・広がりも同時に変化しています。']:
 y=bullet(p,y,t)
box(p,733,63,'今の結論例：「本条件では、厚み1→4 mmで感度が4.93倍となった。」原因の主張は、磁化量と幾何条件をそろえた検証結果を加えてから述べます。',11.3)

p=new('2　角度が比例しても、磁場の比例は別の検証','小たわみ片持ち梁の式は、固定端付近だけに成り立つ関係ではありません。')
text(p,M,102,W-2*M,'θ(z)＝3u(2Lz−z²)/(2L³)　　κ(z)＝3u(L−z)/L³',12.4,True)
box(p,138,75,'この式では、どのzでもθは先端変位uに比例します。したがって、この式だけでは「固定端側は線形、自由端側は非線形」という差を説明できません。磁場の位置・向きへの依存までつなげる必要があります。',11.5)
image(p,'beam_kinematics.png',M,227,W-2*M,228)
text(p,M,472,W-2*M,'以前の条件L＝40 mm、u＝4 mmを使った力学の数値例',12.2,True,color=TEAL)
for i,(z,w,theta) in enumerate([(15,.738,5.24),(35,3.254,8.46)]):
 y=509+i*34;p.draw_rect(fitz.Rect(M,y,W-M,y+32),fill=LIGHT,color=None);text(p,M+10,y+8,500,f'z＝{z} mm：局所変位 約{w:.3f} mm、たわみ角 約{theta:.2f}°',11.5)
text(p,M,594,W-2*M,'磁場は B_y(u)＝B_y(0)＋a1 u＋a2 u²＋… と評価する',12.4,True,color=TEAL)
text(p,M,628,W-2*M,'梁上の位置・角度がuに比例しても、磁場の位置依存や角度依存は一般に非線形です。新しい測定条件へ予測を出し、高次項が測定不確かさに比べて小さいかを確認します。',11.6)
box(p,712,85,'B∝r⁻³は、向きも含む磁気双極子の式の一部で、試料全体を1双極子にする場合は遠方近似です。有限サイズ試料の近傍では、分布した磁場源の位置・向き・体積を含む計算で検証します。',11.3)

p=new('3　距離条件を対照実験でそろえる','ユーザー確認：現状は、試料表面からHallセンサまでの初期距離が一定。')
image(p,'surface_vs_center_distance.png',M,101,W-2*M,249)
box(p,369,73,'表面距離dが一定なら、厚み中心までの距離はR＝d＋t/2。1 mmと4 mmでは中心距離が1.5 mm異なります。図は初期平行面の模式図で、dの実測値は未提供です。',11.5)
y=465
for t in ['対照条件：既存の4 mm条件の中心距離へ合わせる場合、1 mm試料の表面距離を1.5 mm増やす。実際には実測厚みの差の半分で調整します。','各試料の無変形時の3軸磁場分布を測り、実測寸法と位置を固定した有限サイズモデルから磁化の大きさ・向きを校正する。','曲げ変位ごとに側面写真を撮り、実測中心線の位置と向きを磁場計算へ直接入れる。これにより形状予測と磁場予測を分けて評価できます。','磁化量を校正後に固定し、新しい距離・位置の磁場、感度、線形性を予測する。曲げデータごとに自由に当てはめ直さない検証にします。']:
 y=bullet(p,y,t)
box(p,733,63,'中心距離固定の対照と、有限サイズの磁場計算を組み合わせます。観測された差が磁気モーメントと幾何条件から再現されれば、その範囲の説明根拠になります。',11.1)

p=new('4　追加実験を最小構成で始める','既存データの再解析を先に行い、必要な条件だけを追加する。')
y=103
for title,body in [
 ('優先0：既存データの再解析','各厚み・位置で、Sと誤差棒、S/t、正規化した変位－磁場曲線を比較。1回の測定内の繰返しと、別々に作製した試料の個体差は分ける。感度を正の大きさで表す場合は|S|と定義する。'),
 ('優先1：写真＋距離だけを変える対照実験','まずS/N比の良い厚み4 mmを使用。z＝15、35 mmの2位置、表面距離2段階、u＝0～4 mmの9段階、各3回の上り測定なら108条件点。3軸は同時記録する。既存条件のデータは再利用する。'),
 ('優先2：静止時のノイズ・ドリフト測定','試料を固定した状態と背景磁場の時系列を、例えば30～60秒記録。厚い試料は信号幅が大きいため、同じ絶対ノイズでもR²や%FS誤差が良く見える可能性を定量的に確認する。'),
 ('優先3：厚み比較の距離・磁気量を校正','表面距離固定と中心距離固定を比較し、無変形場から校正した磁化と実測形状で厚み差を予測する。個体差も含めて主張する段階では独立試料を追加する。')]:
 text(p,M,y,W-2*M,title,13,True,color=TEAL);y+=28;y=text(p,M,y,W-2*M,body,11.3)+21
text(p,M,y,W-2*M,'「こうです」と言うための判定',14,True,color=TEAL);y+=31
for t in ['無変形状態で校正したモデルが、未フィットの距離・位置・変位条件を含めて3軸磁場と線形性の位置依存を再現する。','残差をセンサ・位置・磁化・形状の不確かさと比較し、系統的なずれを評価する。R²が高いことだけを原因の証明に使わない。']:
 y=bullet(p,y,t,11.1)
assert y<802,('p4',y)

p=new('5　文献の役割と、検証後の結論の書き方','出版社・論文検索サービスへの通信制限により、原著本文の確認はまだ完了していません。')
y=103
refs=[
 ('有限サイズ磁場の実装・方法論','Ortner & Bandeira, “Magpylib: A free Python package for magnetic field computation,” SoftwareX 11, 100466 (2020)。公式READMEで書誌を確認。公式文書と直方体磁石の計算実装を閲覧。原著本文は未読。'),
 ('直方体の漏れ磁場計算：原著候補','Engel-Herbert & Hesjedal, “Calculation of the magnetic stray field of a uniaxial magnetic domain,” J. Appl. Phys. 97, 074504 (2005)。公式実装が挙げる参考文献。出版社の書誌・本文確認待ち。'),
 ('硬磁性エラストマーのモデル：調査候補','Zhao et al., “Mechanics of hard-magnetic soft materials,” Journal of the Mechanics and Physics of Solids (2019)。磁化と有限変形をどう結びつけるかを確認する候補。今回、書誌照合・本文確認は未実施。')]
for title,body in refs:
 text(p,M,y,W-2*M,title,12.5,True,color=TEAL);y+=25;y=text(p,M,y,W-2*M,body,10.8)+17
text(p,M,y,W-2*M,'検証後の結論例（現時点の実証結果ではない）',13.3,True,color=TEAL);y+=29
y=text(p,M,y,W-2*M,'「本実験条件では、実測形状と無変形時に校正した磁化を用いたモデルが、センサ距離を変更した場合の磁場と非線形性の変化を再現した。したがって、観測した位置依存性は幾何学的な磁場変化で説明できる。」',11.2)+19
text(p,M,y,W-2*M,'アクセス設定の状況',12.5,True,color=TEAL);y+=25
y=text(p,M,y,W-2*M,'検索・原著確認のため、Crossref、OpenAlex、PMC、Nature、ScienceDirect、AIPの6サイトを許可する設定案を保存済みです。現在は未反映で、環境設定での保存・公開待ちです。',10.7)+17
text(p,M,y,W-2*M,'原著を確認後、適用条件・材料・形状・観測距離を照合して採用文献を絞ります。論文の一般的な法則は、自分の条件で検証して初めて今回の考察の根拠になります。',10.7)
assert not issues,issues
assert len(doc)==5
doc.set_metadata({'title':'MAGDA2026 結果の考察を強める検証計画','subject':'表面距離固定条件での厚み・感度・線形性の検証、原著確認は環境設定待ち'})
f=ROOT/'magda_discussion_evidence_plan.pdf';doc.save(f,garbage=4,deflate=True);doc.close();d=fitz.open(f)
for i,t in enumerate(pages):
 assert t in d[i].get_text()
 d[i].get_pixmap(matrix=fitz.Matrix(1,1)).save(ROOT/'figures'/f'plan_page_{i+1:02d}.png')
(ROOT/'validation.json').write_text(json.dumps({'pages':len(d),'titles':pages,'layout_issues':issues,'japanese_text_verified':True,'pdf_bytes':f.stat().st_size,'source_slides':4,'surface_gap_fixed_confirmed_by_user':True,'primary_article_full_text_review_complete':False,'network_access_draft_saved_not_applied':True},ensure_ascii=False,indent=2)+'\n');shutil.rmtree(font_dir,ignore_errors=True);print('Created plan pages',len(d),'bytes',f.stat().st_size)
