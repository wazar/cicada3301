import json,pathlib,math,numpy as np,hashlib
O=pathlib.Path(__file__).resolve().parent
checks=0
for name in ['k01','k02']:
 d=json.loads((O/(name+'-results.json')).read_text());cases=[([x['indices'] for x in d['real']],d['result'])]
 if name=='k01':cases.extend(([x['cipher']],x['result']) for x in map(json.loads,(O/'k01-controls.jsonl').read_text().splitlines()))
 else:cases.extend((x['ciphers'],x['result']) for x in d['controls'])
 for cs,r in cases:
  v=[0.]*8;t=[0.]*8
  for p in range(1,9):
   for j,c in enumerate(cs):
    if name=='k01':f=r['fitted'][j];q=f['models'][p-1]['probabilities'];a=f['train_stop'];b=f['validation_stop'];lam=f['repeat_weight']
    else:f=r['fitted'][p-1];q=f['probabilities'];ff=f['pages'][j];a=ff['train_stop'];b=ff['validation_stop'];lam=ff['repeat_weight']
    for i in range(a,len(c)):
     row=q[i%p];pr=[w*(lam if x==c[i-1] else 1) for x,w in enumerate(row)];lp=math.log(pr[c[i]]/sum(pr));
     if i<b:v[p-1]+=lp
     else:t[p-1]+=lp
  selected=max(range(8),key=lambda z:v[z]);assert selected+1==r['selected_period'];assert np.allclose(np.array(v)-v[0],r['validation_gain'],atol=1e-9);assert abs(t[selected]-t[0]-r['statistic'])<1e-9
  assert r['p']==(1+sum(x['statistic']>=r['statistic'] for x in r['null']))/(len(r['null'])+1);checks+=1
out={'scalar_replayed_cases':checks,'passed':True,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [O/'k01-results.json',O/'k01-controls.jsonl',O/'k02-results.json']}};(O/'verification.json').write_text(json.dumps(out,indent=2));print(out)
