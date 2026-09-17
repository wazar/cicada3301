import itertools,json,pathlib
from bound import forced,scalar_encode
O=pathlib.Path(__file__).resolve().parent

def main():
 cases=edges=positive=0;by=[]
 for N,maxlen in ((2,8),(3,6)):
  count=0
  for n in range(maxlen+1):
   for p in itertools.product(range(N),repeat=n):
    zeros=[i for i,x in enumerate(p) if x==0]
    for k in (2,3):
     b=forced(p,k)
     for seed in itertools.product(range(N),repeat=k):
      for bits in itertools.product((0,1),repeat=len(zeros)):
       mask={i for i,v in zip(zeros,bits) if v}
       for mode in (False,True):
        c=scalar_encode(p,seed,mask,mode,N);assert all(c[i]==c[i-1] for i in b['forced_doublet_positions']);assert sum(x==y for x,y in zip(c,c[1:]))>=b['lower_bound']
        for i in b['eligible_positions']:assert (c[i]-c[i-1])%N==(p[i]-p[i-k-1])%N
        cases+=1;count+=1;edges+=b['eligible'];positive+=b['lower_bound']>0
  by.append(dict(alphabet=N,max_length=maxlen,seed_mask_constructor_cases=count))
 out=dict(status='PASS',cases=cases,eligible_edges=edges,positive_bound_cases=positive,coverage=by,constructors=['literal-excluded-history','literal-included-history'],mask_scope='every subset of plaintextF positions',seed_scope='allN^k for k2,3');(O/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
