import gzip,json
from pathlib import Path
O=Path(__file__).resolve().parent

def read(policy,model,family,name):
 return json.load(gzip.open(O/('A07' if policy=='major' else 'A07-continuous')/model/family/(name+'.json.gz'),'rt'))
def tail(x,ns):return (1+sum(n>=x for n in ns))/(1+len(ns))
rows=[];controls=[];leaders=[];count=0;paths=0;maxerr=0
for model in ['p03','complementary']:
 for family in ['periodic','finite']:
  for variant in ['body','whole']:
   a={p:read(p,model,family,'actual-'+variant) for p in ['major','continuous']}
   ns={p:[read(p,model,family,f'null-{variant}-{j:02}') for j in range(19)] for p in a}
   assert a['major']['case']['cipher']==a['continuous']['case']['cipher']
   r=dict(model=model,family=family,variant=variant,policies={})
   for p,x in a.items():
    r['policies'][p]=dict(key=x['selected_cell']['id'],full=x['best_full_score'],suffix=x['best_suffix_score'],full_tail=tail(x['best_full_score'],[n['best_full_score'] for n in ns[p]]),suffix_tail=tail(x['best_suffix_score'],[n['best_suffix_score'] for n in ns[p]]),part_scores=x['full_winner']['part_scores'],candidate_count=x['candidate_count'])
    for w in ['full_winner','suffix_winner']:leaders.append(f'{model} {family} {variant} {p} {w}\n{x[w]["transliteration"]}\n')
   for stat in ['full','suffix']:
    key='best_'+stat+'_score';gain=a['major'][key]-a['continuous'][key];ng=[x[key]-y[key] for x,y in zip(ns['major'],ns['continuous'])];r[stat+'_paired_gain']=gain;r[stat+'_paired_gain_tail']=tail(gain,ng);r[stat+'_null_gains']=ng
   rows.append(r)
  for policy in ['major','continuous']:
   d=O/('A07' if policy=='major' else 'A07-continuous')/model/family
   for f in sorted(d.glob('*.json.gz')):
    x=json.load(gzip.open(f,'rt'));count+=1;paths+=x['candidate_count'];maxerr=max(maxerr,x['max_direct_score_error'])
    if 'control'in x:controls.append(dict(policy=policy,model=model,family=family,id=x['case']['id'],**{k:v for k,v in x['control'].items() if k not in ['oracle_alternatives','oracle_diagnostics']}))
result=dict(note='Ranks are descriptive shared-panel ranks, not independent p-values. Continuous controls are competing-model decodes of major-reset plants, not positive controls for continuous policy.',panels=count,retained_paths=paths,max_direct_score_error=maxerr,actual=rows,controls=controls)
(O/'A07-summary.json').write_text(json.dumps(result,indent=2)+'\n');(O/'A07-leading-complete-outputs.txt').write_text('\n'.join(leaders))
print(json.dumps({k:v for k,v in result.items() if k not in ['actual','controls']}))
for r in rows:print(json.dumps({k:v for k,v in r.items() if not k.endswith('_null_gains')}))
