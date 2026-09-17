import pathlib,json,gzip,hashlib,statistics
O=pathlib.Path(__file__).resolve().parent
load=lambda p:json.load(gzip.open(p,'rt'))
def score(d,policy):
 x=next(x for x in d['continuations'] if x['prefix_path_rank']==1 and x['policy']==policy);tot=0;n=0
 for p in x['parts'][1:]:
  a,b=p['span'];nn=b-a+sum(a<=e<b for e in d['ends']);tot+=p['score']*nn;n+=nn
 return tot/n
results=[];out=[]
for v in ['body','whole']:
 d=load(O/'A01'/f'actual-{v}.json.gz');ns=[load(O/'A01'/f'null-{v}-{i:02}.json.gz') for i in range(19)];row=dict(variant=v,selected_cell=d['selected_cell']['id'],policies={})
 for policy in ['continuous','page-reset']:
  val=score(d,policy);nv=[score(x,policy) for x in ns];row['policies'][policy]=dict(continuation_score=val,null_scores=nv,descriptive_upper_tail=(1+sum(x>=val for x in nv))/20)
  best=next(x for x in d['continuations'] if x['prefix_path_rank']==1 and x['policy']==policy)
  out.extend([f'### {v} / {policy} / fixed prefix winner',best['transliteration'],''])
 row['continuous_minus_reset']=score(d,'continuous')-score(d,'page-reset');row['null_clock_differences']=[score(x,'continuous')-score(x,'page-reset') for x in ns];results.append(row)
(O/'A01-summary.json').write_text(json.dumps(results,indent=2)+'\n');(O/'A01-leading-complete-outputs.txt').write_text('\n'.join(out)+'\n');print(json.dumps(results,indent=2))
