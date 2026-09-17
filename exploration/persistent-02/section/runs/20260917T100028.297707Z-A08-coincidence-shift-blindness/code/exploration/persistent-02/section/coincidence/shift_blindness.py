from pathlib import Path
from collections import Counter
import json
O=Path(__file__).resolve().parent;x=json.loads((O/'inputs.json').read_text());rows=[]
for ix in [8,13,14,15]:
 s=x['controls'][ix];sgn=s['plant']['sign'];other=next(c for c in x['grid']['finite'] if c['id']==f'primes:{sgn}');pos=0;out=[];literals=set(s['truth_literal_positions']);resets=set(s['reset_before']);segments=[];start=0
 for i,c in enumerate(s['cipher']):
  if i in resets:
   if i>start:segments.append((start,i));start=i
   pos=0
  if i in literals:out.append(0)
  else:out.append((c+sgn*other['key'][pos])%29);pos+=1
 segments.append((start,len(out)));diff=pred=0
 for a,b in segments:
  normal=[s['truth'][i] for i in range(a,b) if i not in literals];L=sum(i in literals for i in range(a,b));formula=2*L*(normal.count((-sgn)%29)-normal.count(0));u=Counter(s['truth'][a:b]);v=Counter(out[a:b]);delta=sum(n*(n-1) for n in v.values())-sum(n*(n-1) for n in u.values());assert delta==formula;diff+=delta;pred+=formula
 assert all(out[i]==(0 if i in literals else (s['truth'][i]+sgn)%29) for i in range(len(out)))
 rows.append(dict(index=ix,true_cell=s['plant']['id'],shifted_cell=other['id'],same_literal_mask=True,normal_shift=sgn,errors=sum(a!=b for a,b in zip(out,s['truth'])),collision_gain=diff,formula_gain=pred))
(O/'shift-blindness.json').write_text(json.dumps(dict(passed=True,formula='2 L (normal_count[-sign mod29] - normal_count[0]) per segment',cases=rows),indent=2)+'\n');print(json.dumps(rows))
