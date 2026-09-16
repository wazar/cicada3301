import m28 as m,itertools,json,random,math
checks=0;norms=0;witness=None
for n in range(1,5):
 for key in itertools.product(range(3),repeat=n):
  for i in range(n):
   for prev in ([None] if i==0 else range(3)):
    for a,sign in [(1,-1),(7,1)]:
     f=0 if prev is None else a*prev%29
     full={}
     for p in range(29):
      prob={}
      def rec(j,mass):
       c=(p-sign*(key[j]+f))%29
       if prev is not None and c==prev:
        prob[c]=prob.get(c,0)+mass*(1-m.S)
        if j+1==len(key):prob[c]=prob.get(c,0)+mass*m.S
        else:rec(j+1,mass*m.S)
       else:prob[c]=prob.get(c,0)+mass
      rec(i,1.);assert abs(sum(prob.values())-1)<1e-12;norms+=1
      for c,v in prob.items():full[c,p]=v
     for c in range(29):
      actual={p:v for p,v,tr in m.options(c,prev,i,key,a,sign)}
      expect={p:v for (cc,p),v in full.items() if cc==c}
      assert actual.keys()==expect.keys() and all(abs(actual[p]-expect[p])<1e-12 for p in actual);checks+=1
# Compare AST exact historical encoder to instrumented port on finite boundaries.
fixtures=[]
for ix in range(100):
 rng=random.Random(3328+ix);key=[rng.randrange(3) for _ in range(5)];p=[rng.randrange(4) for _ in range(5)];a=1+ix%28;s=1 if ix%2 else -1;c,e=m.encoder(p,key,a,s,ix);old=m.ns['encipher_ctfeedback'](p,key,k=1,coeffs=[0,a],sign=s,supp=m.S,seed=ix);assert c==old;fixtures.append(dict(key=key,plain=p,cipher=c,events=e,a=a,sign=s,seed=ix))
# Exact top16 DP against independent enumeration on finite short sequences.
backup=m.K;tiny=[]
for ix in range(80):
 rng=random.Random(3628+ix);m.K=[rng.randrange(4) for _ in range(10)];plain=[rng.randrange(4) for _ in range(8)];cell=dict(a=1+ix%28,sign=1 if ix%2 else -1);c,_=m.encoder(plain,m.K,cell['a'],cell['sign'],ix);ends={2,7};paths=[]
 def rec(i,ctx,score,p):
  if i==len(c):paths.append((score,p));return
  for x,prob,_ in m.options(c[i],c[i-1] if i else None,i,m.K,cell['a'],cell['sign']):
   ss,w=m.lm.extend(ctx,x,i in ends);rec(i+1,ss,score+w+math.log(prob),p+[x])
 rec(0,(29,29),0,[]);paths.sort(reverse=True);d=m.decode(c,ends,cell,16);assert len(d['alternatives'])==min(16,len(paths));assert all(abs(x['joint_total']-y[0])<1e-10 and x['plain']==y[1] for x,y in zip(d['alternatives'],paths));tiny.append(dict(key=m.K,cipher=c,cell=cell,paths=len(paths)))
m.K=backup
out=dict(status='PASS',conditional_probability_tables=checks,normalized_forward_distributions=norms,exact_ast_finite_encoders=100,independent_tiny_dp=80,finite_fixtures=fixtures,tiny=tiny)
m.dump('kernel-check',out);print({k:v for k,v in out.items() if k not in ['finite_fixtures','tiny']})
