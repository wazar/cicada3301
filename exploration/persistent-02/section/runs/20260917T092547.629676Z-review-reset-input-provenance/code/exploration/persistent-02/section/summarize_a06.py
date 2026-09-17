import pathlib,json,numpy as np
O=pathlib.Path(__file__).resolve().parent;rows=[];total=0
for model in ['p03','complementary']:
 old=json.loads((O/('A04-summary.json' if model=='p03' else 'A05-forest-summary.json')).read_text())['actual']
 for family in ['periodic','finite']:
  original=('A01' if family=='periodic' else 'A02') if model=='p03' else 'A05-'+family
  for variant in ['body','whole']:
   for policy in ['continuous','page-reset']:
    actual=next(x for x in old if x['batch']==original and x['variant']==variant and x['policy']==policy);ns=[]
    for j in range(19):
     p=O/'A04'/f'A06-{model}-{family}-null-{variant}-{j:02}-{policy}.json';d=json.loads(p.read_text());z=np.load(O/'A04'/d['array']);ns.append(dict(replicate=j,max_full_score=float(z['full_score'].max()),max_suffix_score=float(z['suffix_score'].max()),candidates=d['candidate_count']));total+=d['candidate_count']
    row=dict(model=model,family=family,variant=variant,policy=policy,actual_full_score=actual['max_full_score'],actual_suffix_score=actual['max_suffix_score'],old_full_tail=actual['full_tail'],old_suffix_tail=actual['suffix_tail'],fixed_F_full_tail=(1+sum(n['max_full_score']>=actual['max_full_score'] for n in ns))/20,fixed_F_suffix_tail=(1+sum(n['max_suffix_score']>=actual['max_suffix_score'] for n in ns))/20,nulls=ns);rows.append(row)
(O/'A06-summary.json').write_text(json.dumps(dict(rows=rows,null_complete_paths=total,interpretation='Adaptive shared-comparator sensitivity: fixedFsites/equalitymask, no fixedfirst nor histogram. Actualsearches reused unchanged.'),indent=2)+'\n');print(json.dumps(dict(paths=total,rows=[{k:v for k,v in r.items() if k!='nulls'} for r in rows]),indent=2))
