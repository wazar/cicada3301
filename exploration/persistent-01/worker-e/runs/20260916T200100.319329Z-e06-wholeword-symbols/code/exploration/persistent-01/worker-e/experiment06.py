import pathlib,json,re,numpy as np,time
R=pathlib.Path(__file__).parent;D=json.load(open('audit/parallel-01/inputs/dataset.json'));S=json.load(open(R/'experiment01-result.json'));A=D['alphabet'];P=np.array([x for x in range(2,110) if all(x%d for d in range(2,int(x**.5)+1))]);maps={'index':np.arange(29),'prime':P};rng=np.random.default_rng(2026091706)
ps=[];positions=[]
for p in D['pages']:
 if p['original_page'] not in S['pages']:continue
 words=[]
 for ln in p['lines']:
  for m in re.finditer('['+A+']+',ln['raw']):
   words.append([A.index(c) for c in m[0]]);positions.append({'page':p['original_page'],'word':len(words)-1,'line':ln['source_line'],'raw_start':m.start(),'raw_end':m.end()})
 lengths=np.array([len(w) for w in words]);ps.append((np.array([x for w in words for x in w]),lengths))
def decode(ps,m):return [np.add.reduceat(m[v],np.r_[0,np.cumsum(ls)[:-1]])%29 for v,ls in ps]
def stats(seq):
 x=np.concatenate(seq);f=np.bincount(x,minlength=29);ex=len(x)/29;chi=float(np.sum((f-ex)**2/ex));joint=np.zeros((29,29))
 for s in seq:joint+=np.bincount(s[:-1]*29+s[1:],minlength=841).reshape(29,29)
 joint/=joint.sum();a=joint.sum(1);b=joint.sum(0);prod=a[:,None]*b[None,:];ok=joint>0;mi=float(np.sum(joint[ok]*np.log(joint[ok]/prod[ok])))
 return [chi,mi]
def scan(ps):return np.array([v for m in maps.values() for v in stats(decode(ps,m))])
def shuffle(ps):return [(rng.permutation(v),ls) for v,ls in ps]
real=scan(ps);null=np.array([scan(shuffle(ps)) for _ in range(1000)]);tails=(1+(null>=real).sum(0))/1001
controls=[]
for name,m in maps.items():
 for typ in ['biased','markov']:
  if typ=='biased':target=rng.choice(29,2000,p=np.arange(29,0,-1)/435)
  else:
   target=np.empty(2000,dtype=np.int64);target[0]=0
   for i in range(1,2000):target[i]=(target[i-1]+1)%29 if rng.random()<.7 else rng.integers(29)
  words=[];attempts=0
  for t in target:
   while True:
    w=rng.integers(29,size=3);attempts+=1
    if sum(m[w])%29==t:words.append(w);break
  cp=[(np.array(words).ravel(),np.full(2000,3))];out=decode(cp,m)[0];assert np.array_equal(target,out)
  cs=stats([out]);ns=np.array([stats(decode(shuffle(cp),m)) for _ in range(100)]);k=0 if typ=='biased' else 1
  controls.append({'map':name,'type':typ,'attempts':attempts,'truth_stat':cs,'recovery':1.0,'detected':cs[k]>np.quantile(ns[:,k],.99),'null_max':ns.max(0).tolist()})
x={'stat_order':['index_chi','index_MI','prime_chi','prime_MI'],'real':real.tolist(),'null_mean':null.mean(0).tolist(),'null_99':np.quantile(null,.99,axis=0).tolist(),'empirical_tails':tails.tolist(),'bonferroni4':np.minimum(1,4*tails).tolist(),'controls':controls,'word_count':sum(len(ls) for v,ls in ps),'pages':S['pages']}
(R/'experiment06-result.json').write_text(json.dumps(x,indent=2)+'\n');(R/'experiment06-mapping.json').write_text(json.dumps(positions)+'\n');print(json.dumps(x,indent=2))
