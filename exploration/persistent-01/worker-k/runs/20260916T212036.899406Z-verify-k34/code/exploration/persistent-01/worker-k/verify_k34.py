import pathlib,json,math,hashlib
O=pathlib.Path(__file__).resolve().parent
S={s['name']:s['indices'] for s in json.loads((O/'k02-results.json').read_text())['sources']}
checks=0;maps=0
for row in map(json.loads,(O/'k03-controls.jsonl').read_text().splitlines()):
 cs=[]
 for name,o in zip(row['names'],row['outputs']):
  src=S[name];keys=row['permutations'];used=o['accepted_source_positions'];rej=o['rejected_source_positions'];assert sorted(used+rej)==list(range(len(src)));ci=0
  for i,x in enumerate(src):
   y=keys[ci%len(keys)][x]
   if i in rej:assert ci>0 and y==o['cipher'][ci-1]
   else:assert used[ci]==i and y==o['cipher'][ci];ci+=1
  assert [src[i] for i in used]==o['accepted_plaintext'];cs.append(o['cipher']);maps+=1
 r=row['result'];v=[0.]*8;t=[0.]*8
 for m in range(8):
  for j,c in enumerate(cs):
   if row['method']=='independent':f=r['fitted'][j];q=f['models'][m]['probabilities'];a=f['train_stop'];b=f['validation_stop'];lam=f['repeat_weight']
   else:f=r['fitted'][m];q=f['probabilities'];ff=f['pages'][j];a=ff['train_stop'];b=ff['validation_stop'];lam=ff['repeat_weight']
   for i in range(a,len(c)):
    prob=q[i%(m+1)].copy();prob[c[i-1]]*=lam;lp=math.log(prob[c[i]]/sum(prob));
    if i<b:v[m]+=lp
    else:t[m]+=lp
 selected=max(range(8),key=lambda i:v[i]);assert selected+1==r['selected_period'];assert abs(t[selected]-t[0]-r['statistic'])<1e-8;assert r['p']==(1+sum(x['statistic']>=r['statistic'] for x in r['null']))/(len(r['null'])+1);checks+=1
D=json.loads((O/'k04-results.json').read_text());cases=[([x['indices'] for x in D['real']],[x['schedules'] for x in D['real']],D['result'])]
for x in D['controls']:
 model=['global','initial','terminal','forward_cap3','reverse_cap3','forward_parity'].index(x['true_model'])
 for p,s,c in zip(x['source_indices'],x['schedules'],x['ciphers']):assert [x['keys'][st][rr] for st,rr in zip(s[model],p)]==c;maps+=1
 cases.append((x['ciphers'],x['schedules'],x['result']))
for cs,ss,r in cases:
 v=[0.]*6;t=[0.]*6
 for m,f in enumerate(r['fitted']):
  q=f['probabilities']
  for c,s,ff in zip(cs,ss,f['pages']):
   a=ff['train_stop'];b=ff['validation_stop'];lam=ff['lambda']
   for i in range(a,len(c)):
    prob=q[s[m][i]].copy();prob[c[i-1]]*=lam;lp=math.log(prob[c[i]]/sum(prob))
    if i<b:v[m]+=lp
    else:t[m]+=lp
 selected=max(range(6),key=lambda i:v[i]);assert r['fitted'][selected]['schedule']==r['selected'];assert abs(t[selected]-t[0]-r['statistic'])<1e-8;assert r['p']==(1+sum(x['statistic']>=r['statistic'] for x in r['null']))/(len(r['null'])+1);checks+=1
out={'passed':True,'scalar_prediction_cases':checks,'source_permutation_maps':maps,'hashes':{s:hashlib.sha256((O/s).read_bytes()).hexdigest() for s in ['k03-controls.jsonl','k03-results.json','k04-results.json']}};(O/'verification-k34.json').write_text(json.dumps(out,indent=2));print(out)
