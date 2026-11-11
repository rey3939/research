from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
exec((ROOT/'source/pdf_helpers.py').read_text(),globals())
facts=json.loads((ROOT/'data/review_facts.json').read_text())

def pic(p,name,y,h):
 p.insert_image(fitz.Rect(M,y,W-M,y+h),filename=str(ROOT/'figures'/name),keep_proportion=True)
def para(p,y,s,size=11.3):return text(p,M,y,W-2*M,s,size)+13
def heading(p,y,s):return text(p,M,y,W-2*M,s,13,True,color=TEAL)+10
def note(p,y,h,s,size=11.1):
 p.draw_rect(fitz.Rect(M,y,W-M,y+h),fill=LIGHT,color=None)
 end=text(p,M+12,y+9,W-2*M-24,s,size)
 if end>y+h-4:issues.append({'page':len(doc),'note_overflow':end-(y+h-4)})
def bullet(p,y,s,size=11.1):
 p.draw_circle((M+4,y+7),2,color=None,fill=TEAL)
 return text(p,M+17,y,W-2*M-17,s,size)+11
def check_end(y):assert y<802,('body_overflow',len(doc),y)

p=new('考察を「説明できる」へ進める','対象：研究目的.pptx 全12ページ。材料特性測定と予定のモデルを含む検証計画。')
note(p,102,82,'中心方針：形状を決める力学と、形状から生じる磁場を分けて検証する。独立に測った材料特性・磁化・形状を使い、まだ合わせていない距離や位置の結果を予測する。',12)
# Native vector diagram; these are the proposed verification stages, not new observations.
for i,(title,body) in enumerate([('先端変位','実測値を指定'),('試料の形状','写真・E・ν'),('3軸磁場','位置・方向・磁化'),('変位の推定','未知データで評価')]):
 x=M+i*133;p.draw_rect(fitz.Rect(x,213,x+123,288),fill=LIGHT,color=TEAL,width=.7)
 text(p,x+8,224,109,title,12,True);text(p,x+8,251,109,body,9.7)
 if i<3:p.draw_line((x+123,251),(x+131,251),color=TEAL,width=2)
y=313;y=heading(p,y,'特に見直したい3つの説明')
for s in ['厚み増加→剛性増加→たわみ角が変わる：同じ先端変位の単純梁では、形状の式からEIが消えます。実測形状で確認します。','固定部で低感度→外乱が小さい：曲げへの応答が小さいことと、外乱磁場が小さいことは別です。空操作・静止時の対照が必要です。','モデルとの不一致→粒子追加回転：形状誤差、断面省略、磁化や位置の誤差も原因になります。順に切り分けます。']:
 y=bullet(p,y,s)
y=heading(p,y+8,'今回確認できた実験の範囲')
y=para(p,y,'厚み1・2・3・4 mm、7位置、変位0～4 mmの9段階。3回は同じ試料の繰返しで、独立した3試料ではありません。センサ距離は試料表面を基準に一定です。',11.3)
y=para(p,y,'全厚みの感度と、自由端・固定部の結果を新たに確認しました。図の表示値は整理できますが、平均前の生データや実測寸法がないため、新しい誤差棒・信頼区間は計算していません。',11.1)
note(p,737,61,'目指すのは「本条件の結果を、この機構で定量的に説明できる」という結論です。高いR²や一つの曲線への適合だけで、原因の一意性は証明できません。',11.1)
check_end(y)

p=new('2　Eとνを測る意義を明確にする','7ページの剛性による説明と、12ページの力学モデルを検証する。')
text(p,M,103,W-2*M,'u＝FL³/(3EI)　　I＝bt³/12',13,True)
text(p,M,135,W-2*M,'w(z)/u＝z²(3L−z)/(2L³)',13,True)
note(p,174,70,'一様な線形Euler–Bernoulli梁で、同じ先端変位uを与える場合、w(z)とθ(z)はE・Iに依存しません。厚くすると必要な力は増えますが、剛性だけで形状が変わるとは言えません。',11.2)
pic(p,'prescribed_displacement.png',256,212)
y=487
for title,s in [('E：反力と剛性の検証','実測Eと寸法からEIを計算し、曲げ反力を予測する。可能なら反力も測る。形状差がある場合は、自重、糸の向き・張力、初期反り、固定・せん断などを確認する。'),('ν：断面変形とせん断の検証','横収縮・厚さ変化を検討する入力。等方線形材料ならG＝E/[2(1＋ν)]を使えるが、磁化・配向による異方性があれば方向ごとの確認が必要。'),('エネルギーと変位拘束','保存外力の全ポテンシャルは通常Π＝U−W_ext。外力がした仕事と外力のポテンシャルは符号が異なる。先端変位を指定する場合は、その拘束の下でUを最小化する。')]:
 y=heading(p,y,title);y=para(p,y,s,11.0)
check_end(y)

p=new('3　厚みの効果を磁気量と幾何に分ける','5ページ：今回の全4厚みの表示値を使用。誤差棒は未提供。')
pic(p,'four_thicknesses.png',103,229)
y=352
for title,s in [('観測事実と、まだ言えないこと','z_s＝15で感度は増加するが、S/tも増える。厚み4倍に対して感度4.93倍、S/tは約23.2％増。比例性や差の有意性は、実測寸法・繰返し・磁化差を確認して評価する。'),('磁化・磁気量を独立に校正する','均一磁化なら総磁気モーメントm＝MV。同じ30 vol.%でもMが同じとは限らない。試料ごとの無変形時3軸磁場を複数位置で測り、寸法・位置とともに校正する。'),('表面距離固定と中心距離固定を比べる','表面距離d一定では中心距離R＝d＋t/2。1 mmと4 mmの差は1.5 mm。既存4 mm条件へ合わせるなら1 mmの表面距離を1.5 mm増す。断面の広がりは有限サイズ計算で扱う。')]:
 y=heading(p,y,title);y=para(p,y,s,11.1)
note(p,727,71,'同じ試料3回は繰返し性の評価です。厚みの効果を一般化するには独立に作った試料が必要です。またz_s＝40では4 mmの感度は低く、厚み増加の効果は全位置で一様ではありません。',11.1)
check_end(y)

p=new('4　固定端・自由端の差を予測で検証する','4・6・7ページ：角度の比例だけでは磁場の線形性は説明できない。')
note(p,102,80,'θ(z)＝3u(2Lz−z²)/(2L³) は、どのzでもuに比例します。磁場は位置・方向に非線形に依存するため、B_y(u)＝B_y(0)＋a1u＋a2u²＋…の高次項まで評価します。',11.6)
y=206
for title,s in [('最も有用な対照：4 mmのz_s＝35と40','35 mmではS＝2.348、R²≃0.953。40 mmでは感度・線形性が大きく低下する。実測形状を保ってセンサを動かし、空間分布・相殺候補を調べる。現段階で相殺が原因と断定はしない。'),('まず3つの変位で自由端の磁場を走査','u＝0・2・4 mmで保持し、z_s＝30～45 mm付近を可能なら1～2 mm刻みで走査する。位置分解能と予備測定で間隔を調整。表面距離を変えたときの変化も先に予測して測る。'),('実測形状から3軸を同時に予測する','各変位の写真から全長の位置・向きを得て、無変形場で校正した磁化を固定して計算する。Byだけでなく、代表条件で小さかったBx・Bzの符号と大きさも確認する。'),('ノイズによる指標改善を分ける','厚い試料は信号幅が大きく、同じ絶対ノイズでもR²や%FSが改善しうる。静止時ノイズ・ドリフトを測り、平均前の3回も解析する。正規化曲線とノイズを加えた予測を比較する。')]:
 y=heading(p,y,title);y=para(p,y,s,11.1)
note(p,724,74,'B∝1/r³は方向係数を含む点磁気双極子の距離依存です。試料全体を1双極子とするのは遠方近似。試料近傍では、有限な幅・厚みと分布した位置・向きを含む計算で確かめます。',11.0)
check_end(y)

p=new('5　低感度と「最適」の主張を確かめる','8・9ページ：観測事実から直接言える範囲を整理する。')
y=103;y=heading(p,y,'固定部の低感度は、外乱が小さい証拠ではない')
y=para(p,y,'z_s＝−10で言えるのは、曲げ変位に対する磁場の傾きが小さいことです。減衰、成分の相殺、分解能以下などをモデルと絶対ノイズで調べます。「到達しない」とは言い切れません。')
y=para(p,y,'一定の外乱磁場は差分や傾きに現れにくいため、外乱の大きさは別に測ります。試料静止中の時系列、試料を外した装置操作、可能なら固定した基準センサの同時記録を比べます。')
y=para(p,y,'信号幅がほぼゼロの領域では、R²や%FSが不安定・無意味になり得ます。S、絶対変動、ノイズ、傾きの不確かさを使います。',11.0)
y=heading(p,y+6,'4 mm・15 mmは、有望な候補として評価する')
y=para(p,y,'15 mm：S＝0.478、R²＝0.998。35 mm：S＝2.348、R²≃0.953。感度と直線性のどちらを重視するか、許容誤差を決めないと最適条件は一意になりません。')
for s in ['微小変位の目安：σ_u≃σ_B/|S|。検出判定の基準と測定帯域・平均化条件を示す。R²だけから検出分解能を決めない。','校正に使わない変位・測定回で、変位推定のRMSE・最大誤差を確認する。上り下り、取付誤差、ドリフトも評価する。','同じE・b・Lの単純梁では、1→4 mmで剛性は64倍。柔軟構造物の姿勢を変えにくいという要求も、設計の評価に含める。']:
 y=bullet(p,y,s)
note(p,733,65,'現時点の表現案：「測定範囲内で、直線換算のしやすさを重視した設計候補は4 mm・15 mmである。」最適性は用途と未知データでの推定誤差を含めて判定します。',11.1)
check_end(y)

p=new('6　粒子追加回転と1次元近似を分ける','11・12ページ：不一致だけから追加回転を原因にしない。')
note(p,102,88,'同じ曲率なら表面の曲げひずみは |ε_b|max≃|κ|t/2。薄くすると曲げひずみが小さくなることは力学的に説明できます。そこから粒子単独の追加回転も小さくなるかは、未検証の仮説です。',11.5)
y=214
for title,s in [('A → B：形状予測の誤差を調べる','A＝力学で予測した形状＋1次元磁場源。B＝写真で測った形状＋同じ1次元磁場源。磁化・位置条件を共通にして、形状だけを置き換える。'),('B → C：有限断面を省く誤差を調べる','C＝実測形状＋有限な幅・厚みを持つ体積要素。B・Cとも粒子単独の追加回転は省略し、母材の回転には追従させる。厚みだけでなく、幅と観測距離の比も検討する。'),('Cで合わない場合に、追加の物理を検討する','磁化不均一、センサ位置・姿勢、断面・体積変化、ノイズ、数値分割の収束を点検する。その後で、独立な根拠で回転則を決めたDを検証する。残差をそのまま回転角に換算しない。')]:
 y=heading(p,y,title);y=para(p,y,s,11.1)
y=heading(p,y+4,'学術的な到達点は「省略モデルの適用範囲」')
y=para(p,y,'追加回転を省いたモデルが、どのt/L、κt、観測距離、位置で、何％または何mmの誤差に収まるかを示す。厚みだけでなく形状・観測条件を併記する。これは粒子が回転しない証明とは異なる。',11.2)
note(p,722,76,'PMFUEの0.536°/1%一様圧縮は、別材料・別変形の報告値です。今回のPMEの曲げに係数を転用しません。追加回転の寄与そのものを特定するには、独立な観察や識別実験が必要です。',11.0)
check_end(y)

p=new('7　追加実験を重複なく組み合わせる','同じ試料・同じ形状の測定を、複数の考察の検証に使う。')
y=103
for title,s in [('最初：既存の3回を平均前で再解析','全厚み・位置の符号付きΔB–u、S、残差を確認。特に4 mm・35/40 mm。実測寸法、待ち時間、測定順と結び付ける。3回は独立試料数と区別する。'),('次に：形状・初期磁場・背景を測る','1・4 mm、u＝0・2・4 mmの側面写真を撮り、同じ変位での形状を比較。無変形時3軸磁場の空間分布と、静止・空操作の対照から磁化・位置・外乱を校正する。'),('幾何の検証：4 mmの距離・位置変更','z_s＝15・35・40、表面距離2段階、uの9段階、同一試料3回なら162条件点、3軸は同時記録。既存条件の再利用で減らす。距離変更前にモデルの予測を出す。'),('材料特性：曲げで使うひずみ範囲に合わせる','同じ配合・硬化・磁化・製作方向で引張る。各試験片の実測断面積と局所ひずみからEを求める。νは横方向を明記。幅方向と厚さ方向で等しいかは異方性も考えて検討する。')]:
 y=heading(p,y,title);y=para(p,y,s,11.1)
note(p,642,84,'ひずみ範囲の理論例：L＝40 mm、u＝4 mmなら、固定端のκ＝0.0075 1/mm。表面の曲げひずみは1 mmで0.375%、4 mmで1.5%。実測値ではありません。2 mm幅の微小横収縮では、νの画像測定の不確かさを確認します。',11.0)
y=para(p,744,'E・νの算出区間、速度、保持時間、温度、上り下りを記録。粘弾性があれば静的曲げの待ち時間と整合させます。',10.9)
check_end(y)

p=new('8　スライドの主張を検証と対応させる','現在の観測事実と、検証後に述べる原因の説明を分ける。')
y=103
for title,s in [('5ページ：厚みと感度','「z_s＝15では厚みとともに感度が増加。磁気量と幾何条件の寄与を検証する。」厳密な比例や全位置での単調増加は断定しない。'),('6・7ページ：位置と線形性','「固定端側では直線近似誤差が小さい。実測形状と有限サイズ磁場計算で位置依存を説明する。」角度の比例や剛性だけを原因にしない。'),('8・9ページ：固定部と設計','「固定部の曲げ感度は小さい。外乱は対照実験で評価する。設計候補は変位推定誤差と剛性を含めて選定する。」'),('11・12ページ：モデルの適用範囲','「形状・断面・磁化等の影響を切り分け、追加粒子回転を省いたモデルの予測精度と適用範囲を示す。」不一致を追加回転だけに帰属させない。')]:
 y=heading(p,y,title);y=para(p,y,s,11.0)
note(p,545,102,'検証後の主張例（現時点の実証結果ではない）：\n「独立に測定した磁化と変形形状を使ったモデルが、距離を変えた未使用条件でも磁場と非線形性の位置依存を再現した。本条件の結果は、母材に追従する磁化の位置・方向変化で説明できる。」',11.2)
y=para(p,666,'6ページの本文は「−5～15、t＝2・3・4」、ノートは「0～15、t＝4」。元データで確認して説明をそろえます。正の感度は|S|と定義し、R²を総合精度とは呼ばないようにします。',10.7)
y=para(p,y,'根拠：添付12ページ、ユーザー確認済み条件、明記した力学例。原著論文の新しい本文確認は通信制限により未実施です。未確認文献やPMFUEの係数を今回の原因の実証には用いていません。詳しい手順と判定条件は付属READMEを参照してください。',10.5)
check_end(y)

assert not issues,issues
assert len(doc)==8
doc.set_metadata({'title':'研究目的・結果・モデルをつなぐ考察と検証計画','author':'Research discussion support','subject':'研究目的.pptx全12ページ、独立材料測定と磁場モデルの識別、2026-11-11'})
path=ROOT/'discussion_roadmap.pdf';doc.save(path,garbage=4,deflate=True);doc.close()
d=fitz.open(path)
for i,title in enumerate(pages):
 assert title in d[i].get_text()
 for b in d[i].get_text('blocks'):
  assert b[0]>=0 and b[1]>=0 and b[2]<=W+1 and b[3]<=H+1,(i,b[:4])
 d[i].get_pixmap(matrix=fitz.Matrix(1,1)).save(ROOT/'figures'/f'page_{i+1:02d}.png')
calc=facts['theory_example_not_measured'];s=facts['displayed_sensitivity_at_z15']['sensitivity_magnitude_mT_per_mm']
assert math.isclose(s[-1]/s[0],calc['sensitivity_ratio_z15_t4_over_t1'])
assert calc['stiffness_ratio_t4_over_t1']==4**3
assert math.isclose(3*4/40**2,calc['root_curvature_per_mm'])
assert math.isclose(calc['root_curvature_per_mm']*4/2,calc['surface_bending_strain_t4'])
assert facts['proposed_geometry_test']['condition_points_if_all_new']==3*2*9*3
assert 'a1' in d[3].get_text() and 'a2' in d[3].get_text() and '1/r³' in d[3].get_text()
assert '1/mm' in d[6].get_text()
v={'pages':len(d),'titles':pages,'layout_issues':issues,'text_bounds_within_page':True,'japanese_text_verified':True,'pdf_bytes':path.stat().st_size,'source_slides':12,'same_specimen_three_repeats_confirmed':True,'surface_distance_reference_confirmed':True,'illustrative_theory_not_measurement':True,'new_primary_article_full_text_reviewed':False,'new_experiments_performed':False,'formula_arithmetic_verified':True,'source_character_font_coverage_verified':True}
(ROOT/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
shutil.rmtree(font_dir,ignore_errors=True)
print(json.dumps(v,ensure_ascii=False))
