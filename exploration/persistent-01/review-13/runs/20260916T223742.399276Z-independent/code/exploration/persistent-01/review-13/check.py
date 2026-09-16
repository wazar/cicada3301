from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as F
import json,gzip,ast,math,random,itertools,hashlib,re
D=Path('exploration/persistent-01/worker-m/M28');O=Path('exploration/persistent-01/review-13')
inputs=[]
def read(p):
 b=p.read_bytes();inputs.append(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest()));return json.load(gzip.open(p,'rt') if p.suffix=='.gz' else open(p))
source=read(D/'source.json');manifest=read(D/'manifest.json')
for name,h in manifest.items():
 assert hashlib.sha256((D/name).read_bytes()).hexdigest()==h,(name,h)
abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';trans='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
raw=Path(source['source']).read_text();upper=raw.upper();assert len(raw)==len(upper);key=[];spans=[];pos=0
tokens=sorted(enumerate(trans),key=lambda x:-len(x[1]))
while pos<len(upper):
 matches=[(r,s) for r,s in tokens if upper.startswith(s,pos)]
 if matches:r,s=matches[0];key.append(r);spans.append([pos,pos+len(s)]);pos+=len(s)
 else:
  if upper[pos] in 'VKZQ':key.append(dict(V=1,K=5,Z=15,Q=5)[upper[pos]]);spans.append([pos,pos+1])
  pos+=1
assert key==source['values'] and spans==source['uppercase_spans'];assert hashlib.sha256(bytes(key)).hexdigest()==source['values_sha256']
assert hashlib.sha256(Path(source['source']).read_bytes()).hexdigest()==source['sha256']
def extract(path,names,namespace):
 tree=ast.parse(path.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
oldpath=Path(source['old_encoder_source']);oldns=dict(random=random,N=29);extract(oldpath,['encipher_ctfeedback'],oldns)
assert hashlib.sha256(oldpath.read_bytes()).hexdigest()==source['old_sha256']
# Independently reconstruct all P03 probabilities, including word-boundary token29.
cc=[Counter() for _ in range(3)];tot=[Counter() for _ in range(3)]
def parse(raw):
 words=re.findall('['+abc+']+',raw);p=[];ends=set()
 for word in words:p.extend(abc.index(c) for c in word);ends.add(len(p)-1)
 return p,ends
for name in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229']:
 path=Path('audit/parallel-01/reference/sources')/('solved_'+name+'.txt');p,ends=parse(path.read_text());ctx=(29,29)
 for i,r in enumerate(p):
  for token in ([r,29] if i in ends else [r]):
   for n in range(3):k=ctx[-n:] if n else ();cc[n][k+(token,)]+=1;tot[n][k]+=1
   ctx=ctx[1],token
class IndependentLM:
 def extend(self,ctx,r,end):
  score=0
  for token in ([r,29] if end else [r]):
   v=(cc[0][(token,)]+.5)/(tot[0][()]+15)
   for n,a in [(1,8),(2,5)]:q=ctx[-n:];v=(cc[n][q+(token,)]+a*v)/(tot[n][q]+a)
   score+=math.log(v);ctx=ctx[1],token
  return ctx,score
 def score(self,p,ends):
  ctx=(29,29);s=0
  for i,v in enumerate(p):ctx,w=self.extend(ctx,v,i in ends);s+=w
  return s/(len(p)+len(ends))
lm=IndependentLM();ns=dict(math=math,collections=__import__('collections'),K=key,lm=lm,S=.83);extract(D/'m28.py',['options','decode'],ns)
def forward(p,prev,i,k,a,sign):
 mass=F(1);out=defaultdict(F);f=0 if prev is None else a*prev%29
 for j in range(i,len(k)):
  v=(p-sign*(k[j]+f))%29
  if prev is None or v!=prev:out[v]+=mass;break
  if j==len(k)-1:out[v]+=mass;break
  out[v]+=mass*F(17,100);mass*=F(83,100)
 return dict(out)
tables=0;norms=0
for n in range(1,5):
 for k in itertools.product(range(2),repeat=n):
  for i in range(n):
   for prev in ([None] if i==0 else [0,1,28]):
    for a,sign in [(1,-1),(7,1),(28,-1)]:
     expected=defaultdict(dict)
     for p in range(29):
      ff=forward(p,prev,i,k,a,sign);assert sum(ff.values())==1;norms+=1
      for c,mass in ff.items():expected[c][p]=mass
     for c in range(29):
      observed={p:prob for p,prob,tr in ns['options'](c,prev,i,k,a,sign)}
      assert observed.keys()==expected[c].keys()
      for p,v in observed.items():assert abs(v-float(expected[c][p]))<1e-12
      tables+=1
# Deliberately branch-rich tiny inputs; exhaustive path scores versus extracted DP.
tiny=[];rng=random.Random(131313)
for trial in range(64):
 k=[rng.randrange(4) for _ in range(13)];a=1+rng.randrange(28);sign=rng.choice([-1,1]);c=[rng.randrange(29)]
 for i in range(1,10):
  j=i+1
  while j<len(k) and k[j]==k[i]:j+=1
  c.append((c[-1]+sign*(k[i]-k[j]))%29 if j<len(k) and rng.random()<.8 else rng.randrange(29))
 ends={2,5,9};opts=[]
 for i,v in enumerate(c):opts.append([(p,float(forward(p,c[i-1] if i else None,i,k,a,sign).get(v,0))) for p in range(29)]);opts[-1]=[(p,prob) for p,prob in opts[-1] if prob]
 exhaustive=[]
 for choices in itertools.product(*opts):
  p=bytes(x for x,prob in choices);score=lm.score(p,ends)*(len(c)+len(ends))+sum(math.log(prob) for x,prob in choices);exhaustive.append((score,p))
 exhaustive.sort(reverse=True);ns['K']=k
 for retain in [1,16]:
  d=ns['decode'](c,ends,dict(a=a,sign=sign),retain)['alternatives'];assert len(d)==min(retain,len(exhaustive))
  for x,y in zip(d,exhaustive):assert x['plain']==list(y[1]) and abs(x['joint_total']-y[0])<1e-10
 tiny.append(dict(key=k,cipher=c,a=a,sign=sign,paths=len(exhaustive)))
ns['K']=key
controls=[];packets={};mainnames=[]
for ix,name in enumerate(['0_welcome','jpg107-167','p56_an_end','p57_parable']):
 f=read(D/f'control-{name}-fixture.json');p,ends=parse(Path(f['source']).read_text());assert p==f['plain'] and sorted(ends)==f['ends'];cell=f['cell'];a=cell['a'];sign=cell['sign'];c=f['cipher'];seed=330828+ix
 assert oldns['encipher_ctfeedback'](p,key,k=1,coeffs=[0,a],sign=sign,supp=.83,seed=seed)==c
 rng2=random.Random(seed);events=[];out=[]
 for i,x in enumerate(p):
  j=i;dec=[];prev=out[-1] if out else None;feedback=0 if prev is None else a*prev%29
  while True:
   v=(x-sign*(key[j]+feedback))%29
   if prev is None or v!=prev:break
   u=rng2.random();dec.append([j,u])
   if u>=.83:break
   j+=1
   if j==len(key):break
  out.append(v);events.append(dict(start=i,accepted=min(j,len(key)-1),forced_eof=j==len(key),decisions=dec))
 assert out==c and events==f['events'];reset=all(forward(x,c[i-1] if i else None,i,key,a,sign).get(v,0)>0 for i,(x,v) in enumerate(zip(p,c)));assert reset
 pointers={0};dead=None
 for i,(x,v) in enumerate(zip(p,c)):
  nxt=set();feedback=a*c[i-1]%29 if i else 0
  for start in pointers:
   for j in range(start,len(key)):
    z=(x-sign*(key[j]+feedback))%29
    if z==v:nxt.add(j+1)
    if i==0 or z!=c[i-1]:break
  pointers=nxt
  if not pointers and dead is None:dead=i
 assert dead==f['cumulative']['first_dead'];mainnames.append('control-'+name)
 controls.append(dict(name=name,n=len(p),reset_reachable=reset,cumulative_dead=dead,forced_events=sum(x['forced_eof'] for x in events)))
mainnames+=['real-0','real-17'];savedpaths=0;cells=0
for path in sorted((D/'evidence').glob('*.json.gz')):
 r=read(path);packets[r['name']]=r;assert len(r['rows'])==56;cells+=56;savedpaths+=56+len(r['top16']['alternatives'])
 assert r['score']==max(x['score'] for x in r['rows']);assert len({(x['cell']['a'],x['cell']['sign']) for x in r['rows']})==56
checkedpaths=0;actualoutputs=[]
for name in mainnames:
 r=packets[name];c=r['cipher'];ends=set(r['ends']);paths=[(x['cell'],x['decode']['alternatives'][0]) for x in r['rows']]+[(r['rows'][0]['cell'],p) for p in r['top16']['alternatives']]
 for cell,path in paths:
  p=path['plain'];prob=0.
  for i,(x,v) in enumerate(zip(p,c)):
   value=forward(x,c[i-1] if i else None,i,key,cell['a'],cell['sign']).get(v,0);assert value>0;prob+=math.log(float(value))
  score=lm.score(p,ends)*(len(p)+len(ends))+prob;assert abs(score-path['joint_total'])<1e-8;checkedpaths+=1
 if name.startswith('control'):
  ix=mainnames.index(name);f=read(D/(name+'-fixture.json'));top=r['top16']['alternatives'];controls[ix].update(errors=sum(a!=b for a,b in zip(top[0]['plain'],f['plain'])),truth_top16=next((i+1 for i,p in enumerate(top) if p['plain']==f['plain']),None),true_cell_rank=next(i+1 for i,z in enumerate(r['rows']) if z['cell']==f['cell']))
 else:
  plain=r['top16']['alternatives'][0]['plain'];actualoutputs.append(dict(name=name,cell=r['rows'][0]['cell'],text=''.join(trans[v]+(' ' if i in ends else '') for i,v in enumerate(plain))))
# Recreate complete shared RNG sequence; exact masks alone would miss seed/order bugs.
rng=random.Random(338028);nulls=0;tails={}
for name in mainnames:
 base=packets[name];c=base['cipher'];nn=19 if name.startswith('control') else 99;values=[]
 for rep in range(nn):
  z=[rng.randrange(29)]
  for x,y in zip(c,c[1:]):
   if x==y:z.append(z[-1])
   else:q=rng.randrange(28);z.append(q+(q>=z[-1]))
  packet=packets[f'{name}-null{rep}'];assert z==packet['cipher'];assert packet['ends']==base['ends'];values.append(packet['score']);nulls+=1
 tails[name]=(1+sum(v>=base['score'] for v in values))/(nn+1)
result=dict(status='PASS',manifest_files=len(manifest),key_length=len(key),exact_probability_tables=tables,normalized_forward_distributions=norms,tiny_cases=len(tiny),tiny_total_paths=sum(x['paths'] for x in tiny),controls=controls,searches=len(packets),cell_fits=cells,saved_paths=savedpaths,main_paths_scored=checkedpaths,nulls_seed_replayed=nulls,tails=tails,real_outputs=actualoutputs)
(O/'results.json').write_text(json.dumps(result,indent=2));(O/'tiny.json').write_text(json.dumps(tiny,indent=2));(O/'inputs.json').write_text(json.dumps(inputs,indent=2));print(json.dumps(result,indent=2))
