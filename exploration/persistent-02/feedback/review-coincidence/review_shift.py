import json,pathlib
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];A=R/'exploration/persistent-02/section/coincidence';d=json.loads((A/'inputs.json').read_text());reported=json.loads((A/'shift-blindness.json').read_text());rows=[]
for r in reported['cases']:
 s=d['controls'][r['index']];sign=s['plant']['sign'];other=next(x for x in d['grid']['finite'] if x['id']==r['shifted_cell']);assert all((b-a)%29==1 for a,b in zip(s['plant']['key'],other['key']));lit=set(s['truth_literal_positions']);resets=set(s['reset_before']);at=0;p=[];groups=[];current=[]
 for i,c in enumerate(s['cipher']):
  if i in resets:
   if current:groups.append(current)
   current=[];at=0
  if i in lit:v=0
  else:v=(c+sign*other['key'][at])%29;at+=1
  p.append(v);current.append(i)
 if current:groups.append(current)
 gain=0;formula=0
 for indices in groups:
  gain+=sum(p[i]==p[j] for i in indices for j in indices if i!=j)-sum(s['truth'][i]==s['truth'][j] for i in indices for j in indices if i!=j)
  L=sum(i in lit for i in indices);normal=[s['truth'][i] for i in indices if i not in lit];formula+=2*L*(sum(x==(-sign)%29 for x in normal)-sum(x==0 for x in normal))
 assert gain==formula==r['collision_gain'];assert sum(a!=b for a,b in zip(p,s['truth']))==r['errors'];rows.append(dict(index=r['index'],gain=gain,errors=r['errors']))
(O/'shift-review.json').write_text(json.dumps(dict(status='PASS',cases=rows),indent=2)+'\n');print('PASS',len(rows))
