import json,gzip,math
from compare import O,LM
from complementary import LM as OtherLM
summary={};sourcecases={c['id']:c for c in json.loads((O/'continuation-inputs.json').read_text())['cases']}
for group in ['references','fresh','section']:
 rows=[]
 for p in sorted((O/('posterior-'+group)).glob('*.json.gz')):
  x=json.loads(gzip.decompress(p.read_bytes()));model=p.name.split('-',1)[0];r=dict(model=model,id=x['id'],log_partition=x['full']['log_partition'],legal_paths=x['full']['number_of_legal_decision_paths'],top16_mass=x['exact_top16_mass']['mass'],retained_mass=x['exact_retained_mass']['mass'],beam_pool_mass={w:b['pool_mass']['mass'] for w,b in x['beams'].items()},beam_returned16_mass={w:b['returned16_mass']['mass'] for w,b in x['beams'].items()},max_live_states=x['full']['max_live_states'],seconds=x['seconds'],joins=[])
  for prefix in x['prefix_only']:
   cut=prefix['cut'];before=prefix['posterior']['joins'][-1]['key_positions'];after=next(j['key_positions'] for j in x['full']['joins'] if j['cut_after_rune_count']==cut);a={j['position']:j['probability'] for j in before};b={j['position']:j['probability'] for j in after};r['joins'].append(dict(cut=cut,prefix_mode=max(a,key=a.get),full_mode=max(b,key=b.get),prefix_mode_mass=max(a.values()),full_mode_mass=max(b.values()),total_variation=.5*sum(abs(a.get(k,0)-b.get(k,0)) for k in a.keys()|b.keys())))
  if group=='fresh':
   c=sourcecases[x['id']];lm=LM() if model=='p03' else OtherLM();ctx=(29,29);score=0.;ee=set(c['ends_primary'])
   for i,v in enumerate(c['truth']):ctx,w=lm.extend(ctx,v,i in ee);score+=w
   r['truth_path_weight']=math.exp(score-x['full']['log_partition']);n=c['prefix_length'];r['selected_branch_marginals']=[]
   for pos in ([n-1] if c['id']=='fresh-mill-1' else [498,499,500,501,502,584,585,586] if c['id']=='fresh-shelley-2' else []):
    bef=next((b for b in x['prefix_only'][0]['posterior']['branch_marginals'] if b['position']==pos),None);aft=next((b for b in x['full']['branch_marginals'] if b['position']==pos),None)
    if bef:r['selected_branch_marginals'].append(dict(position=pos,planted_literal=pos in c['truth_literal_positions'],prefix_literal_probability=bef['literal']['probability'],full_literal_probability=aft['literal']['probability']))
  rows.append(r)
 summary[group]=rows
(O/'posterior-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for group,rows in summary.items():
 for model in ['p03','complementary']:
  r=[x for x in rows if x['model']==model]
  if not r:continue
  print(json.dumps(dict(group=group,model=model,cases=len(r),top16_mass_range=[min(x['top16_mass'] for x in r),max(x['top16_mass'] for x in r)],beam64_mass_range=[min(x['beam_pool_mass']['64'] for x in r),max(x['beam_pool_mass']['64'] for x in r)],mean_beam64_mass=sum(x['beam_pool_mass']['64'] for x in r)/len(r))))
