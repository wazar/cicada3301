"""Post-stop accounting only. Does not import or call any decoder."""
import pathlib,json,hashlib
O=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
main=O/'outputs/20260916T180521.719679Z';pilot=O/'outputs/20260916T180424.220919Z'
f=read(main/'case-066.json');spec=read(O/'preregistration.json');allcases=sorted(list(pilot.glob('case-*.json'))+list(main.glob('case-*.json')))
cells=[]
for index,cell in enumerate(spec['positive_cells']):
 rows=[read(p) for p in allcases if read(p)['cell_index']==index]
 cells.append(dict(cell,cell_index=index,executed=len(rows),passed=sum(r['passed'] for r in rows),failed=sum(not r['passed'] for r in rows),skipped=20-len(rows),status='FAILED' if any(not r['passed'] for r in rows) else 'PASSED' if len(rows)==20 else 'SKIPPED_AFTER_FAILURE'))
required=[v for v in f['choices'] if v['recipe']=='DIVINITY' and v['sign']==1 and v['mode']=='beam']
failures=[]
for row in required:
 pg=row['page'];truth=f['plaintext'][pg];used=[t['accepted_key_index'] for t in f['encryption_state_trace'][pg]]
 failures.append({'page':pg,'score':row['score'],'truth_score':f['truth_scores'][pg],'exact':row['exact'],'rune_matches':row['rune_matches'],'wrong_runes':[{'index':i,'truth':p,'decoded':q,'truth_key_index':used[i],'decoded_key_index':row['key_use'][i]} for i,(p,q) in enumerate(zip(truth,row['plain_idx'])) if p!=q],'max_actual_consecutive_rejections':max(len(t['attempts'])-1 for t in f['encryption_state_trace'][pg]),'instrumentation_equals_production':row['instrumentation_equals_production']})
commands=[read(p) for p in sorted((O/'runs').glob('*/command.json'))]
a={'outcome':'BLOCKED_BY_POSITIVE_CONTROL','planned_positive_pairs':320,'executed_positive_pairs':len(allcases),'passed':66,'failed':1,'skipped':253,'cells':cells,'failure':failures,'phase_counts':{'calibration_pairs':0,'heldout_pairs':0,'shuffle_pairs':0,'real_page_choices':0},'all_logged_execution_seconds':sum(x['duration_seconds'] for x in commands),'dedup':read(main/'candidate-dedup.json'),'failure_top_hypotheses':f['top_hypotheses']}
with (O/'ACCOUNTING.json').open('x') as out:json.dump(a,out,indent=2);out.write('\n')
print(json.dumps(a,indent=2))
