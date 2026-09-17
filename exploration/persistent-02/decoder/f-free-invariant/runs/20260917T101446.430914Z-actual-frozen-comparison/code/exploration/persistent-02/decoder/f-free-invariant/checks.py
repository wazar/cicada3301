import pathlib,sys,json,random,collections
from invariant import statistic,family
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];sys.path.insert(0,str(R/'exploration/persistent-02/feedback'))
from literal_feedback import encode as old
from emitted_feedback import encode as new

def main():
 rng=random.Random(2026092799);checks=edges=pairs=0;startsafterliteral=0
 for constructor in (old,new):
  for k in (2,3):
   for trial in range(400):
    n=rng.randrange(5,100);p=[rng.randrange(29) if rng.random()>.25 else 0 for _ in range(n)];seed=[rng.randrange(29) for _ in range(k)];lit=[i for i,v in enumerate(p) if v==0 and rng.random()<.8];c=constructor(p,seed,lit);s=statistic(c,k);nn=dd=0
    for run in s['runs']:
     a,b=run['start'],run['stop'];startsafterliteral+=a>0 and a-1 in lit
     for j in range(b-a):assert run['q'][j]==(p[a+j]-p[a+j%(k+1)])%29
     for i in range(a+k+1,b):assert (c[i]-c[i-1])%29==(p[i]-p[i-k-1])%29;edges+=1
     for phase in range(k+1):
      vals=p[a+phase:b:k+1];dd+=len(vals)*(len(vals)-1);nn+=sum(x==y for i,x in enumerate(vals) for j,y in enumerate(vals) if i!=j);pairs+=len(vals)*(len(vals)-1)
    assert (nn,dd)==(s['numerator'],s['denominator']);checks+=1
 fixture=family([[{'collision':.1},{'collision':.3}] for _ in range(20)]);assert fixture['rank_count_ge']==20 and fixture['family']==[0.]*20
 out=dict(constant_panel_fixture='PASS',status='PASS',cases=checks,identity_edges=edges,direct_ordered_pairs=pairs,runs_starting_after_literal=startsafterliteral,scope='randomfullrecurrences, no resetting seed/history at F-free run starts');(O/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
