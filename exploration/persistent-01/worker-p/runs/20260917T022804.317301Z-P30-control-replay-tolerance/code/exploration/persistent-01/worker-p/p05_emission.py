import pathlib,gzip,json,math,collections,fractions
D=pathlib.Path('exploration/persistent-01/worker-p/P05');assert not D.parents[1].joinpath('STOP').exists();F=fractions.Fraction
# closed form, no experiment encoder calls
checks=[]
for k in range(1,6):
 for prev in [-1,0]:
  probs=[F(0)]*k
  for initial in range(k):
   if initial==prev and k>1:
    probs[initial]+=F(1,k)*F(17,100)
    for alt in range(k):
     if alt!=prev:probs[alt]+=F(1,k)*F(83,100)*F(1,k-1)
   else:probs[initial]+=F(1,k)
  formula=[F(1,k) if prev==-1 or k==1 else F(17,100*k) if out==prev else F(1,k)+F(83,100*k*(k-1)) for out in range(k)];assert probs==formula and sum(probs)==1;checks.append(dict(k=k,previous=prev,probabilities=[str(p) for p in probs]))
def emission(mapping,cipher):
 counts=collections.Counter(mapping);out=[]
 for i,r in enumerate(cipher):
  k=counts[mapping[r]]
  if i==0 or mapping[cipher[i-1]]!=mapping[r] or k==1:p=1/k
  elif cipher[i-1]==r:p=.17/k
  else:p=1/k+.83/(k*(k-1))
  out.append(math.log(p))
 return out
records=[]
for p in sorted(D.glob('*.json.gz')):
 if not p.name.startswith(('control-','real-','null-')):continue
 with gzip.open(p,'rt') as f:r=json.load(f)
 choices=[]
 for a in r['alternatives']:
  terms=emission(a['map'],r['cipher']);choices.append(dict(restart=a['restart'],map=a['map'],emission_terms=terms,prefix_lm=a['prefix_total'],prefix_emission=sum(terms[:r['cut']]),prefix_joint=a['prefix_total']+sum(terms[:r['cut']])))
 row=dict(label=r['label'],original_selected=r['selected'],saved_candidates=choices,joint_selected=max(range(8),key=lambda i:choices[i]['prefix_joint']))
 if 'control'in r:
  truth=r['control'];assert [truth['truth'][v] for v in r['cipher']]==truth['plain'];terms=emission(truth['truth'],r['cipher']);joint=r['truth_score']['prefix_total']+sum(terms[:r['cut']]);row.update(truth_lm_rank=r['truth_rank'],truth_emission_terms=terms,truth_lm=r['truth_score']['prefix_total'],truth_emission=sum(terms[:r['cut']]),truth_joint=joint,truth_joint_rank=1+sum(a['prefix_joint']>joint+1e-9 for a in choices));best=r['alternatives'][row['joint_selected']]['decoded'];row['saved_joint_selected_suffix_accuracy']=sum(a==b for a,b in zip(best[r['cut']:],truth['plain'][r['cut']:]))/(len(best)-r['cut'])
 records.append(row)
with gzip.open(D/'emission-evidence.json.gz','wt') as f:json.dump(dict(probability_checks=checks,records=records),f)
controls=[r for r in records if 'truth_joint_rank'in r];out=dict(checked_packet_count=len(records),finite_probability_controls=checks,controls=[{k:v for k,v in r.items() if k not in ['saved_candidates','truth_emission_terms']} for r in controls],truth_joint_ranks=[r['truth_joint_rank'] for r in controls],truth_lm_ranks=[r['truth_lm_rank'] for r in controls]);(D/'emission-results.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['controls','finite_probability_controls']},indent=2))
