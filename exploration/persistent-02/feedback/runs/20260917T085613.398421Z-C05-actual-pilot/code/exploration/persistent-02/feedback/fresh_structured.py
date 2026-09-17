"""Independent sum-feedback plants on frozen non-P03-source excerpts."""
import extend as ex,structured as st
import json,random,hashlib,numpy as np
O=ex.O/'C02';O.mkdir(exist_ok=True)
source=ex.R/'exploration/persistent-02/decoder/fresh-controls.json'
def main():
 data=json.loads(source.read_text());rng=random.Random(2026091703);rows=[]
 for case in data['cases']:
  p=case['truth'];ends=set(case['ends'])
  for k in [5,6,7,8]:
   ex.guard();seed=[rng.randrange(29) for _ in range(k)];c=ex.q.enc(p,seed);W=ex.q.table(ex.q.decode(c,[0]*k),ends,k);result=st.solve(W,max_nodes=100000,max_seconds=30);best=result['alternatives'][0];out=ex.q.decode(c,[(-x)%29 for x in best['offset'][:k]]);truth=ex.q.lm.score(p,ends)*(len(p)+len(ends))
   alts=[]
   for alt in result['alternatives']:
    pp=ex.q.decode(c,[(-x)%29 for x in alt['offset'][:k]]);assert abs(ex.q.lm.score(pp,ends)*(len(p)+len(ends))-alt['score'])<1e-9;alts.append(dict(**alt,plain=pp))
   row=dict(id=case['id'],k=k,seed=seed,cipher=c,ends=sorted(ends),truth=p,truth_score=truth,errors=sum(x!=y for x,y in zip(p,out)),result=result,alternatives=alts,source=case['source'],source_rune_span=case['source_rune_span']);rows.append(row)
   print(case['id'],k,'errors',row['errors'],'gap',result['gap'],'seconds',result['seconds'],flush=True)
   (O/'fresh-tests.json').write_text(json.dumps(dict(source=str(source.relative_to(ex.R)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),rng_seed=2026091703,scope='source-disjoint from P03 training; reused B excerpts but independently planted sum-feedback seed/recurrence; Blake authorial headings retained per qualification',rows=rows),separators=(',',':'))+'\n')
if __name__=='__main__':main()
