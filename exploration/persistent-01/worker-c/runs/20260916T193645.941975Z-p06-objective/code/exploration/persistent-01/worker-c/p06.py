"""Matched periodic fit: inherited quad surrogate vs exact quad objective."""
import pathlib,json,math,time,importlib.util,sys
import numpy as np
from p03 import ROOT,O,ABC,parse,dump,LM
TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
class Score:
 def __init__(self):
  d={s:int(n) for s,n in (l.split() for l in (ROOT/'liber-primus/data/english_quadgrams.txt').read_text().splitlines())};total=sum(d.values());self.d={s:math.log10(n/total) for s,n in d.items()};self.floor=math.log10(.01/total);self.tab=np.load(ROOT/'exploration/overnight-01/worker-b/quad-contribution.npy');self.lens=np.array(list(map(len,TOK)));self.prefix=np.zeros((29,29,29))
  for a in range(29):
   for b in range(29):
    for c in range(29):
     text=TOK[a]+TOK[b]+TOK[c];self.prefix[a,b,c]=sum(self.d.get(text[i:i+4],self.floor) for i in range(len(text)-3))
 def batch(self,x,mode):
  if x.ndim==1:x=x[None,:]
  total=self.tab[x[:,:-3],x[:,1:-2],x[:,2:-1],x[:,3:]].sum(1)
  if mode=='surrogate':return total/self.lens[x[:,3:]].sum(1)
  return (total+self.prefix[x[:,0],x[:,1],x[:,2]])/(self.lens[x].sum(1)-3)
 def direct(self,p):
  t=''.join(TOK[x] for x in p);return sum(self.d.get(t[i:i+4],self.floor) for i in range(len(t)-3))/(len(t)-3)
def fit(c,period,q,mode,seed):
 rng=np.random.default_rng(seed);phase=np.arange(len(c))%period;best=None;starts=[];evaluations=0
 freq=np.array([2.2,2.8,3,7.5,6,2.8,2,2.2,5.5,6.7,7,.15,.1,1.9,.15,6.3,9,1.5,12.7,2.4,4,.5,.1,4.2,8.2,.1,2,.1,.1]);logfreq=np.log(freq/freq.sum());initial=np.array([np.argmax(logfreq[(c[phase==j,None]-np.arange(29))%29].sum(0)) for j in range(period)])
 for restart in range(4):
  k=initial.copy() if restart==0 else rng.integers(0,29,period);p=(c-k[phase])%29;orders=[rng.permutation(period) for _ in range(5)]
  # Consume identical RNG draws/order regardless of convergence/objective.
  for order in orders:
   change=False
   for j in order:
    variants=np.tile(p,(29,1));sites=phase==j;variants[:,sites]=(c[sites][None,:]-np.arange(29)[:,None])%29;vals=q.batch(variants,mode);evaluations+=30;v=int(np.argmax(vals))
    if vals[v]>q.batch(p,mode)[0]+1e-12:k[j]=v;p=variants[v];change=True
   if not change:break
  val=float(q.batch(p,mode)[0]);starts.append(dict(restart=restart,score=val,key=k.tolist()))
  if best is None or val>best[0]:best=(val,k.copy())
 return best,starts,evaluations
def main():
 out=O/'p06';out.mkdir(exist_ok=True);q=Score();rng=np.random.default_rng(330106);randoms=rng.integers(0,29,(100,120));error=float(np.max(np.abs(q.batch(randoms,'exact')-np.array([q.direct(p) for p in randoms]))));assert error<1e-12;dump(out/'arithmetic.json',dict(random_cases=100,max_error=error,source='direct Latin-token quadgram evaluation versus corrected vector objective'))
 cases=[]
 for name in ['0_welcome','jpg107-167']:
  truth,_=parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text());truth=np.array(truth)
  for period in [1,3,8,16,32]:
   key=rng.integers(0,29,period);cipher=(truth+key[np.arange(len(truth))%period])%29;cases.append((f'control-{name}-{period}',cipher,period,truth,key))
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());pages=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages']
 for p in pages:
  if p['original_page'] not in [0,17,55]:continue
  assert p['original_page'] not in cfg['reserved_original_pages']
  for period in [1,3,8,16,32]:
   if len(p['indices'])//2<2*period:continue
   c=np.array(p['indices']);cases.append((f'real-{p["original_page"]}-{period}',c,period,None,None));cases.append((f'null-{p["original_page"]}-{period}',rng.permutation(c),period,None,None))
 results=[];t=time.monotonic()
 for ix,(name,c,period,truth,key) in enumerate(cases):
  split=len(c)//2;row=dict(id=name,period=period,split=split,cipher=c.tolist(),truth=None if truth is None else truth.tolist(),truth_key=None if key is None else key.tolist(),models=[])
  for mode in ['surrogate','exact']:
   (v,k),starts,evals=fit(c[:split],period,q,mode,330106+ix);plain=(c-k[np.arange(len(c))%period])%29;r=dict(model=mode,key=k.tolist(),train_objective=v,train_exact=float(q.batch(plain[:split],'exact')[0]),continuation_exact=float(q.batch(plain[split:],'exact')[0]),plain=plain.tolist(),starts=starts,evaluations=evals)
   if truth is not None:r.update(key_errors=int(np.sum(k!=key)),train_errors=int(np.sum(plain[:split]!=truth[:split])),continuation_errors=int(np.sum(plain[split:]!=truth[split:])))
   row['models'].append(r)
  results.append(row);dump(out/'results.json',results);print(json.dumps(dict(id=name,models=[{k:v for k,v in x.items() if k not in ['plain','starts','key']} for x in row['models']],elapsed=time.monotonic()-t)),flush=True)
 dump(out/'summary.json',dict(cases=len(cases),same_keys=sum(r['models'][0]['key']==r['models'][1]['key'] for r in results),seconds=time.monotonic()-t))
if __name__=='__main__':main()
