"""Descriptive reranking of already frozen prefix alternatives; no new search."""
import pathlib,json,gzip
O=pathlib.Path(__file__).resolve().parent

def suffixscore(d,x):
 total=0;tokens=0
 for p in x['parts'][1:]:
  a,b=p['span'];n=b-a+sum(a<=e<b for e in d['ends']);total+=p['score']*n;tokens+=n
 return total/tokens
rows=[];texts=[]
for batch in ['A01','A02']:
 for variant in ['body','whole']:
  ds=[json.load(gzip.open(O/batch/(f'actual-{variant}.json.gz' if i<0 else f'null-{variant}-{i:02}.json.gz'),'rt')) for i in range(-1,19)]
  for policy in ['continuous','page-reset']:
   winners=[max((x for x in d['continuations'] if x['policy']==policy),key=lambda x:suffixscore(d,x)) for d in ds];scores=[suffixscore(d,x) for d,x in zip(ds,winners)];w=winners[0];row=dict(batch=batch,variant=variant,policy=policy,prefix_rank=w['prefix_path_rank'],continuation_score=scores[0],null_scores=scores[1:],descriptive_upper_tail=(1+sum(x>=scores[0] for x in scores[1:]))/20,selected_full_output=w)
   rows.append(row);texts.extend([f'{batch} {variant} {policy}: frozen prefix rank{w["prefix_path_rank"]}, suffix{scores[0]:.8f}',w['transliteration'],''])
(O/'A03-alternative-selection.json').write_text(json.dumps(rows,indent=2)+'\n');(O/'A03-leading-complete-outputs.txt').write_text('\n'.join(texts));print(json.dumps([{k:v for k,v in x.items() if k not in ['selected_full_output','null_scores']} for x in rows],indent=2))
