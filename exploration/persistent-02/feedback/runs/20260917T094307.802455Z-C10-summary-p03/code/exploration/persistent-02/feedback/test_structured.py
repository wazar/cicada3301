import pathlib,json,random,time,hashlib,sys
import extend as ex
import structured as st
import numpy as np
O=ex.O/'C02';O.mkdir(exist_ok=True)
def main():
 ex.guard();rng=random.Random(2026091702);records=[]
 for k in [2,3,4]:
  for rep in range(3):
   c=[rng.randrange(29) for _ in range(37)];ends={4,11,17,25,36};q=ex.q.decode(c,[0]*k);W=ex.q.table(q,ends,k)
   result=st.solve(W,max_nodes=100000,max_seconds=30)
   exhaustive=ex.q.scores(W,k);expected=float(exhaustive.max());assert abs(result['maximum']-expected)<1e-9 and result['certified_within_1e_10']
   for alt in result['alternatives']:
    plain=ex.q.decode(c,[(-x)%29 for x in alt['offset'][:k]])
    assert abs(ex.q.lm.score(plain,ends)*(len(c)+len(ends))-alt['score'])<1e-9
   records.append(dict(k=k,rep=rep,cipher=c,ends=sorted(ends),result=result,exhaustive_maximum=expected,seeds=len(exhaustive)))
   print('random',k,rep,result['seconds'],result['gap'],flush=True)
 for ix in range(4):
  data=ex.q.packet(ix);p=data['truth'];ends=set(data['ends'])
  for k in [2,3,4,5,6,7,8]:
   ex.guard();seed=[rng.randrange(29) for _ in range(k)];c=ex.q.enc(p,seed);W=ex.q.table(ex.q.decode(c,[0]*k),ends,k);result=st.solve(W,max_nodes=100000,max_seconds=30);best=result['alternatives'][0];out=ex.q.decode(c,[(-x)%29 for x in best['offset'][:k]])
   for alt in result['alternatives']:
    pp=ex.q.decode(c,[(-x)%29 for x in alt['offset'][:k]]);assert abs(ex.q.lm.score(pp,ends)*(len(c)+len(ends))-alt['score'])<1e-9
   if k<=4:
    expected=float(ex.q.scores(W,k).max());assert abs(result['maximum']-expected)<1e-9 and result['certified_within_1e_10']
   truthscore=ex.q.lm.score(p,ends)*(len(c)+len(ends));errors=sum(a!=b for a,b in zip(p,out));records.append(dict(control=ix,k=k,seed=seed,cipher=c,ends=sorted(ends),truth=p,truth_score=truthscore,errors=errors,result=result,source=data['source']))
   print('control',ix,k,'errors',errors,'seconds',result['seconds'],'gap',result['gap'],flush=True)
   (O/'tests.json').write_text(json.dumps(records,separators=(',',':'))+'\n')
 (O/'tests.json').write_text(json.dumps(records,separators=(',',':'))+'\n')
if __name__=='__main__':main()
