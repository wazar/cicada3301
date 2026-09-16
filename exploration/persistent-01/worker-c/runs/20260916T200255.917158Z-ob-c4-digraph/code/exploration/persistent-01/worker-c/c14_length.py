"""Factorial diagnostic for failed period32 fitting: more text vs restarts."""
import json,time
import numpy as np
from p03 import O,ROOT,dump
from p06 import Score,fit

def main():
 out=O/'c14';out.mkdir(exist_ok=True);q=Score();base=json.loads((O/'p06/results.json').read_text());cases=[x for x in base if x['period']==32];rows=[];t=time.monotonic()
 for ix,case in enumerate(cases):
  c=np.array(case['cipher']);truth=case['truth'];key=case['truth_key']
  for fraction in [.5,.75]:
   split=int(len(c)*fraction)
   for starts,sweeps in [(4,5),(32,12)]:
    (value,k),restart_rows,evals=fit(c[:split],32,q,'exact',330614+ix,starts,sweeps);p=(c-k[np.arange(len(c))%32])%29;r=dict(id=case['id'],fraction=fraction,split=split,restarts=starts,sweeps=sweeps,key=k.tolist(),plain=p.tolist(),train_score=value,continuation_score=float(q.batch(p[split:],'exact')[0]),restart_rows=restart_rows,evaluations=evals)
    if truth is not None:r.update(key_errors=int(np.sum(k!=key)),train_errors=int(np.sum(p[:split]!=truth[:split])),continuation_errors=int(np.sum(p[split:]!=truth[split:])))
    rows.append(r);dump(out/'results.json',rows);print(json.dumps({k:v for k,v in r.items() if k not in ['plain','key','restart_rows']}),flush=True)
 print(json.dumps(dict(seconds=time.monotonic()-t,cases=len(rows),evaluations=sum(r['evaluations'] for r in rows))))
if __name__=='__main__':main()
