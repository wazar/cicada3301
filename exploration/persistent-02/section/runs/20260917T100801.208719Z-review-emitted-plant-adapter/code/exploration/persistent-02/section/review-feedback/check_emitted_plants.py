from pathlib import Path
import json,hashlib,numpy as np
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/feedback';x=json.loads((D/'C11/plants.json').read_text());src=R/x['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==x['source_sha256'];old=json.loads(src.read_text())['cases']
def enc(p,seed,lit,include=True):
 hist=[];phase=0;c=[]
 for i,v in enumerate(p):
  if i in lit:assert v==0;c.append(0)
  else:c.append((v+(seed[phase] if phase<len(seed) else sum(hist[-len(seed):])))%29);phase+=1
  if include or i not in lit:hist.append(v)
 return c
def dec(c,seed,lit,include):
 hist=[];phase=0;p=[]
 for i,v in enumerate(c):
  if i in lit:z=0
  else:z=(v-(seed[phase] if phase<len(seed) else sum(hist[-len(seed):])))%29;phase+=1
  p.append(z)
  if include or i not in lit:hist.append(z)
 return p
for a,b in zip(x['cases'],old):
 assert all(a[k]==v for k,v in b.items() if k!='cipher') and a['old_cipher']==b['cipher'];assert enc(a['truth'],a['seed'],a['literal_positions'])==a['cipher'];assert sum(p!=q for p,q in zip(dec(a['cipher'],a['seed'],a['literal_positions'],False),a['truth']))==a['old_transition_on_new_errors'];assert sum(p!=q for p,q in zip(dec(a['old_cipher'],a['seed'],a['literal_positions'],True),a['truth']))==a['new_transition_on_old_errors']
s=x['cases'][0];z=json.loads((D/'C11/p03-plant00.json').read_text());L=np.load(R/'exploration/persistent-02/decoder/reset-feedback/model-p03.npz')['L'];err=0
for alt in z['result']['alternatives']:
 assert enc(alt['plain'],alt['seed'],alt['literal_positions'])==s['cipher'];score=0.;a=b=29
 for i,p in enumerate(alt['plain']):
  score+=L[a,b,p];a,b=b,p
  if i in s['ends']:score+=L[a,b,29];a,b=b,29
 assert abs(score-alt['total'])<1e-8;err=max(err,abs(score-alt['total']))
out=dict(passed=True,source_plants=len(old),paired_transition_checks=2*len(old),representative_paths=len(z['result']['alternatives']),max_error=err,representative_errors=z['selected_rune_errors']);(Path(__file__).parent/'emitted-plant-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
