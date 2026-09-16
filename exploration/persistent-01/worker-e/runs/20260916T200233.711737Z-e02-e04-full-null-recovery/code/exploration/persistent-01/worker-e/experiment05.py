import json,pathlib,random
R=pathlib.Path(__file__).parent;S=json.load(open(R/'experiment01-result.json'));a,b=[s['values'] for s in S['sources']]
P=[];n=2
while len(P)<max(a+b):
 if all(n%p for p in P if p*p<=n):P.append(n)
 n+=1
def phi(n):
 x=n;p=2
 while p*p<=n:
  if n%p==0:
   x-=x//p
   while n%p==0:n//=p
  p+=1
 if n>1:x-=x//n
 return x
maps={'identity':lambda n:n,'totient':phi,'nth_prime':lambda n:P[n-1]}
def fit(v,w):
 i=next((j for j in range(1,len(v)) if (v[j]-v[0])%29),None)
 if i is None:return {'pass':False,'reason':'no independent fitting pair'}
 scale=(w[i]-w[0])*pow((v[i]-v[0])%29,-1,29)%29;shift=(w[0]-scale*v[0])%29
 pred=[(scale*x+shift)%29 for x in v];matches=[j for j in range(len(v)) if pred[j]==w[j]%29]
 return {'pass':len(matches)==len(v) and scale!=0,'scale':scale,'shift':shift,'fitting_cells':[0,i],'matches':matches,'predicted':pred,'scale_nonzero':scale!=0}
def scan(a,b):return [{'direction':di,'map':name,**fit([f(x) for x in v],w)} for di,v,w in [('AtoB',a,b),('BtoA',b,a)] for name,f in maps.items()]
v=[phi(x) for x in a];w=[(7*x+3)%29 for x in v];z=fit(v,w);assert z['pass'] and z['scale']==7 and z['shift']==3
bad=w[:];j=next(i for i in range(25) if i not in z['fitting_cells']);bad[j]=(bad[j]+1)%29;assert not fit(v,bad)['pass']
real=scan(a,b);rng=random.Random(2026091705);uniq=list(dict.fromkeys(b));nullpasses=0;nullmax=[];null_all=[]
for rep in range(1000):
 p=uniq[:];rng.shuffle(p);mapping=dict(zip(uniq,p));ss=scan(a,[mapping[x] for x in b]);null_all.append([len(x.get('matches',[])) for x in ss]);nullpasses+=any(x['pass'] for x in ss);nullmax.append(max(len(x.get('matches',[])) for x in ss))
out={'recipes':real,'complete_passes':sum(x['pass'] for x in real),'control_pass':True,'null_reps':1000,'null_any_complete':nullpasses,'null_max_match':max(nullmax),'unique_cell_classes':13}
(R/'experiment05-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

import gzip
def gz(name,obj):
 with gzip.open(R/name,'wt') as f:json.dump(obj,f)
gz('experiment05-evidence.json.gz',{'null_all_match_counts':null_all,'null_max_match_counts':nullmax,'control_input':v,'control_target':w,'control_corrupted':bad,'rng_seed':2026091705,'ordering':'1000targetclass shuffles after deterministic controls'})
