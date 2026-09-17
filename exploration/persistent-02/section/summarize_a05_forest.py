import pathlib,json,numpy as np,gzip
O=pathlib.Path(__file__).resolve().parent;rows=[];texts=[];controls=[];counts=dict(datasets=0,candidates=0,max_score_error=0.)
for p in sorted((O/'A04').glob('*.json')):
 d=json.loads(p.read_text());
 if not d['batch'].startswith('A05-'):continue
 z=np.load(O/'A04'/d['array']);full=z['full_score'];best=int(full.argmax());d['full_best_score']=float(full[best]);d['full_best_stage_ranks']=z['stage_ranks'][best].tolist();d['full_best_plain']=z['plain'][best].tolist()
 counts['datasets']+=1;counts['candidates']+=d['candidate_count'];counts['max_score_error']=max(counts['max_score_error'],d['max_direct_score_error'])
 if 'truth_members' in d:
  original=json.load(gzip.open(O.parents[2]/d['source'],'rt'));truth=np.asarray(original['truth']);err=np.count_nonzero(z['plain']!=truth,axis=1);ix=np.flatnonzero(err==0);d['full_best_errors']=int(err[best]);d['truth_full_rank']=None if not len(ix) else 1+int(np.count_nonzero(full>full[ix[0]]));d['truth_full_ties']=None if not len(ix) else int(np.count_nonzero(full==full[ix[0]]));controls.append({k:v for k,v in d.items() if k not in ['selected_cell','full_best_plain','best_transliteration']})
 rows.append(d)
summary=[]
TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
for batch in ['A05-periodic','A05-finite']:
 for variant in ['body','whole']:
  for policy in ['continuous','page-reset']:
   a=next(d for d in rows if d['batch']==batch and d['label']=='actual-'+variant and d['policy']==policy);ns=[next(d for d in rows if d['batch']==batch and d['label']==f'null-{variant}-{i:02}' and d['policy']==policy) for i in range(19)]
   res=dict(batch=batch,variant=variant,policy=policy,candidate_count=a['candidate_count'],distinct_plaintexts=a['distinct_plaintexts'],max_suffix_score=a['best_suffix_score'],suffix_selected_ranks=a['best_stage_ranks'],suffix_tail=(1+sum(n['best_suffix_score']>=a['best_suffix_score'] for n in ns))/20,max_full_score=a['full_best_score'],full_selected_ranks=a['full_best_stage_ranks'],full_tail=(1+sum(n['full_best_score']>=a['full_best_score'] for n in ns))/20)
   summary.append(res);texts.extend([f'{batch}/{variant}/{policy}: full-objective winner {a["full_best_stage_ranks"]}', ''.join(TOK[x] for x in a['full_best_plain']),'',f'{batch}/{variant}/{policy}: suffix-statistic winner {a["best_stage_ranks"]}',a['best_transliteration'],''])
(O/'A05-forest-summary.json').write_text(json.dumps(dict(counts=counts,actual=summary,controls=controls),indent=2)+'\n');(O/'A05-leading-complete-outputs.txt').write_text('\n'.join(texts)+'\n');print(json.dumps(dict(counts=counts,actual=summary),indent=2))
