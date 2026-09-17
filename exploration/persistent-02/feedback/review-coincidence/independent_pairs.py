"""Frozen reviewer arithmetic fixture, independent of decryption implementation."""
import itertools,json,random,pathlib
rng=random.Random(2026092303);rows=[]
for case in range(100):
 n=case%17;N=2+case%4;p=[rng.randrange(N) for _ in range(n)];split=case%(n+1);reset={i for i in range(n) if rng.random()<.2};segment=[];s=-1
 for i in range(n):
  if i==0 or i in reset:s+=1
  segment.append(s)
 full=sum(p[i]==p[j] and segment[i]==segment[j] for i in range(n) for j in range(n) if i!=j)
 prefix=sum(p[i]==p[j] and segment[i]==segment[j] for i in range(split) for j in range(split) if i!=j)
 future=sum(p[i]==p[j] and segment[i]==segment[j] for i in range(n) for j in range(n) if i!=j and (i>=split or j>=split))
 assert full-prefix==future
 rows.append(dict(case=case,plain=p,split=split,resets=sorted(reset),full=full,prefix=prefix,continuation_increment=future))
O=pathlib.Path(__file__).resolve().parent;(O/'pair-fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');print('PASS',len(rows))
