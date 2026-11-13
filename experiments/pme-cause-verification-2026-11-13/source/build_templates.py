from pathlib import Path
import csv,json,zipfile

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'templates';OUT.mkdir(exist_ok=True)
D0=10.0;DALT=15.0
rows=[]
def condition(cid,t,z,d,phase,mode,pilot,existing):
 rows.append({'condition_id':cid,'phase':phase,'pilot':pilot,'t_nominal_mm':t,'z_s_mm':z,'z_actual_mm':'','d_nominal_mm':d,'distance_mode':mode,'source_condition_exists':existing,'t_actual_mm':'','d_actual_mm':'','sample_id':'','reuse_accepted':'','note':'Nominal planning value only. For center matching use measured thicknesses; d_alt is provisional.'})
for t in [1,2,3,4]:
 condition(f'A{t}S',t,15,D0,'A','surface' if t<4 else 'surface_and_center',t in [1,4],True)
 if t<4:condition(f'A{t}C',t,15,D0+(4-t)/2,'A','center',t==1,False)
condition('B0S',4,0,D0,'B','surface',True,True)
condition('B0D',4,0,DALT,'B','alternate_gap',True,False)
condition('B15D',4,15,DALT,'B','alternate_gap',True,False)
for z in [35,40]:
 condition(f'C{z}S',4,z,D0,'C_optional','surface',False,True)
 condition(f'C{z}D',4,z,DALT,'C_optional','alternate_gap',False,False)

def write(name,fields,records):
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(records)
write('conditions.csv',list(rows[0]),rows)
fields=['condition_id','phase','sample_id','cycle','step_type','u_target_mm','u_actual_mm','z_s_mm','z_actual_mm','d_nominal_mm','d_actual_mm','clock_time_JST','wait_s','average_window_s','sample_rate_Hz','sample_count','Bx_mean_mT','By_mean_mT','Bz_mean_mT','Bx_sd_mT','By_sd_mT','Bz_sd_mT','temperature_C','raw_file','photo_file','background_record_id','remarks']
measurements=[]
for c in rows:
 for cycle in range(1,4):
  for u in [i*.5 for i in range(9)]+[0.0]:
   idx=len(measurements)%10
   a={k:'' for k in fields};a.update(condition_id=c['condition_id'],phase=c['phase'],cycle=cycle,step_type='return_zero_check' if idx==9 else 'analysis_point',u_target_mm=u,z_s_mm=c['z_s_mm'],d_nominal_mm=c['d_nominal_mm'])
   measurements.append(a)
write('bending_measurements.csv',fields,measurements)
lookup={r['condition_id']:r for r in rows};order=[]
for stage,pair in [('pilot',['A1S','A1C']),('pilot',['A4S','B15D']),('pilot',['B0S','B0D']),('expansion',['A2S','A2C']),('expansion',['A3S','A3C']),('C_optional',['C35S','C35D']),('C_optional',['C40S','C40D'])]:
 pair=sorted(pair,key=lambda k:lookup[k]['d_nominal_mm'])
 for cycle in [1,2,3]:
  for cid in (pair if cycle%2 else pair[::-1]):
   c=lookup[cid];order.append({'sequence':len(order)+1,'stage':stage,'condition_id':cid,'cycle':cycle,'z_s_mm':c['z_s_mm'],'d_nominal_mm':c['d_nominal_mm'],'remarks':''})
write('run_order.csv',list(order[0]),order)

cf=['record_id','record_type','sample_id','t_nominal_mm','z_s_mm','z_actual_mm','d_nominal_mm','d_actual_mm','sensor_orientation_id','repeat','clock_time_JST','Bx_mean_mT','By_mean_mT','Bz_mean_mT','Bx_sd_mT','By_sd_mT','Bz_sd_mT','wait_s','average_window_s','raw_file','remarks']
cal=[];zs=[-10,-5,0,5,15,35,40]
for phase in ['background_before','sample','background_after']:
 for t in ([1,2,3,4] if phase=='sample' else ['']):
  for z in zs:
   for rep in [1,2,3]:
    a={k:'' for k in cf};a.update(record_id=f'{phase}_T{t}_Z{z}_R{rep}',record_type=phase,t_nominal_mm=t,z_s_mm=z,d_nominal_mm=D0,repeat=rep);cal.append(a)
write('initial_field_calibration.csv',cf,cal)
extra=[];configs=sorted({(c['z_s_mm'],c['d_nominal_mm']) for c in rows if c['d_nominal_mm']!=D0})
for phase in ['background_extra_before','background_extra_after']:
 for z,d in configs:
  for rep in [1,2,3]:
   a={k:'' for k in cf};a.update(record_id=f'{phase}_Z{z}_D{d}_R{rep}',record_type=phase,z_s_mm=z,d_nominal_mm=d,repeat=rep);extra.append(a)
write('background_extensions.csv',cf,extra)
pf=['condition_id','u_target_mm','model_version','parameter_file','mesh_N','penalty_parameter','actual_model_tip_mm','pred_Bx_mT','pred_By_mT','pred_Bz_mT','prediction_saved_JST','remarks']
pred=[]
for c in rows:
 for u in [i*.5 for i in range(9)]:
  a={k:'' for k in pf};a.update(condition_id=c['condition_id'],u_target_mm=u);pred.append(a)
write('model_predictions.csv',pf,pred)
sf=['sample_id','t_nominal_mm','t_1_mm','t_2_mm','t_3_mm','t_mean_mm','width_mm','free_length_mm','batch_id','cure_condition','magnetization_record','sensor_orientation_record','remarks']
spec=[]
for t in [1,2,3,4]:
 a={k:'' for k in sf};a['t_nominal_mm']=t;spec.append(a)
write('specimens.csv',sf,spec)
guide={'condition_id':'条件ID。条件表と照合する','phase':'A=厚み、B=固定端側の線形性、C_optional=任意の自由端検証','pilot':'先行試行に使う条件','source_condition_exists':'元資料に同じ名目条件がある。生データを再利用できる保証ではない','reuse_accepted':'既存生データ・設定・履歴の確認結果を記入','sample_id':'試料を識別するID','cycle':'同じ試料で0～4 mmを曲げ直した曲線の番号','step_type':'analysis_point=9解析点、return_zero_check=除荷後の0 mm確認','u_target_mm':'先端変位の目標値。計画として記入済み','u_actual_mm':'写真や目盛で確認した実際の先端変位','z_s_mm':'固定端を原点とする計画のセンサ位置','z_actual_mm':'実際に設定した長手方向位置','d_nominal_mm':'表面から感磁中心への名目距離。未測定の計画値','d_actual_mm':'実際の表面距離','sensor_orientation_id':'軸と取付角度を記録した図や写真のID','clock_time_JST':'取得時刻。日本標準時で記録','wait_s':'位置を変えてから待った時間','average_window_s':'平均・標準偏差を計算した時間窓','sample_rate_Hz':'時系列の記録頻度','sample_count':'時間窓のサンプル数。独立試料数ではない','temperature_C':'温度','raw_file':'元の全時系列ファイルへの参照','photo_file':'条件・時刻と結び付いた写真名','background_record_id':'背景測定の記録ID','record_type':'試料の初期場または背景測定の種別','repeat':'同じ静的条件の読み取り番号。曲げ直し回数と区別','t_nominal_mm':'名目厚み。実測値ではない','t_actual_mm':'実測厚み','t_1_mm':'厚み測定位置1','t_2_mm':'厚み測定位置2','t_3_mm':'厚み測定位置3','t_mean_mm':'各試料の厚み平均','width_mm':'実測幅','free_length_mm':'実測自由長','distance_mode':'surface=表面一定、center=中心一定、alternate_gap=変更距離','model_version':'計算コードの版','parameter_file':'モデル入力を保存したファイル','mesh_N':'モデルの要素数','penalty_parameter':'先端拘束の係数','actual_model_tip_mm':'モデルで実際に実現した先端変位','prediction_saved_JST':'測定前に予測を保存した時刻','remarks':'欠測、ずれ、回復、除外等の理由'}
for ax in ['x','y','z']:
 guide[f'B{ax}_mean_mT']=f'{ax}成分の絶対磁場の時間窓平均。差分前の値'
 guide[f'B{ax}_sd_mT']=f'{ax}成分の窓内標準偏差。平均の不確かさと同一視しない'
 guide[f'pred_B{ax}_mT']=f'モデルによる{ax}成分の絶対磁場予測。0 mmを引いた差分は別に計算'
write('column_guide.csv',['column_name','meaning_Japanese'],[{'column_name':k,'meaning_Japanese':v} for k,v in guide.items()])

main=[r for r in rows if r['phase']!='C_optional'];pilot=[r for r in main if r['pilot']]
meta={'planning_date_JST':'2026-11-13','nominal_surface_gap_mm':D0,'provisional_alternate_gap_mm':DALT,'reference_center_gap_nominal_mm':12.0,'center_gap_formula':'d_i = d0 + (t_ref_measured - t_i_measured)/2','conditions':rows,'pilot_unique_conditions':len(pilot),'main_unique_conditions':len(main),'optional_C_unique_conditions':4,'analysis_levels_per_cycle':9,'cycles_per_condition':3,'pilot_analysis_points':len(pilot)*27,'main_analysis_points':len(main)*27,'main_return_zero_checks':len(main)*3,'full_with_C_analysis_points':len(rows)*27,'all_template_bending_rows_including_return_checks':len(measurements),'calibration_sample_holds':84,'calibration_background_holds':42,'model_prediction_rows':len(pred),'new_measurements_performed':False,'existing_source_condition_is_not_automatic_reuse_approval':True,'magnetic_parameter':'effective total dipole moment estimated within the single model, not an independent true moment measurement'}
meta.update(main_extra_background_holds=30,extra_background_holds_with_C=len(extra),all_background_holds_with_C=42+len(extra))
(ROOT/'data/plan.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
(OUT/'README.txt').write_text('PME要因検証：未測定の記録用テンプレート\n\nconditions.csv：条件表。名目距離のみ記入済み。実測厚みから中心距離を補正する。変更距離15 mmは予備計算後に確定。\nbending_measurements.csv：各曲線9解析点＋除荷後0 mm確認1点。主実験10条件と任意C4条件。行順は実行順ではない。\nrun_order.csv：距離条件を交互に測る実行順の例。先行・展開・任意Cを区別する。\ninitial_field_calibration.csv：初期場84点＋校正用の背景42点。背景は試料を外し、装置配置を保って測る。\nbackground_extensions.csv：中心合わせ・変更距離での背景確認。主題A/Bは30点、Cまで含めると42点。\nmodel_predictions.csv：実験前に絶対磁場の予測を保存。差分は各条件の0 mmから算出。合わせ直しは別版として区別する。\nspecimens.csv：試料寸法と製作情報。\ncolumn_guide.csv：列名の日本語説明。\n\n記入前にテンプレートを測定日フォルダへコピーする。実測を記入したファイルを生成スクリプトで上書きしない。文字コードUTF-8 BOM。空欄は未測定。数値の0は空欄と区別する。CSVの距離・厚みは計画値で、測定値ではない。生の時系列を別ファイルで必ず保存する。詳細はPDF参照。\n',encoding='utf-8')
with zipfile.ZipFile(ROOT/'measurement_templates.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(OUT.iterdir()):z.write(p,'templates/'+p.name)
assert len(main)==10 and len(pilot)==6 and len(rows)==14 and len(measurements)==420 and len(cal)==126 and len(extra)==42 and len(order)==42
assert {(a['condition_id'],a['cycle']) for a in order}=={(r['condition_id'],c) for r in rows for c in [1,2,3]}
print(json.dumps({k:meta[k] for k in ['pilot_unique_conditions','main_unique_conditions','pilot_analysis_points','main_analysis_points','full_with_C_analysis_points','all_template_bending_rows_including_return_checks']},ensure_ascii=False))
