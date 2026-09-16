"""Bounded numeric and periodic searches; imports inert, writes only OWNER."""
import argparse,gzip,hashlib,itertools,json,math,pathlib,time
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]; OWNER=pathlib.Path(__file__).parent
TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def dump(p,x):
 q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,indent=2,default=lambda v:v.item())+'\n');q.replace(p)
def txt(x):return ''.join(TOK[int(i)] for i in x)
class Score:
 def __init__(self):
  d={s:int(n) for s,n in (l.split() for l in (ROOT/'liber-primus/data/english_quadgrams.txt').read_text().splitlines())};total=sum(d.values());self.d={s:math.log10(n/total) for s,n in d.items()};self.floor=math.log10(.01/total)
  cache=OWNER/'quad-contribution.npy'
  if cache.exists():self.tab=np.load(cache)
  else:
   self.tab=np.empty((29,)*4)
   for a,b,c,d in itertools.product(range(29),repeat=4):
    t=TOK[a]+TOK[b]+TOK[c]+TOK[d];self.tab[a,b,c,d]=sum(self.d.get(t[j-3:j+1],self.floor) for j in range(len(t)-len(TOK[d]),len(t)))
   np.save(cache,self.tab)
  self.lens=np.array(list(map(len,TOK)))
 def batch(self,x):
  if x.ndim==1:x=x[None,:]
  return self.tab[x[:,:-3],x[:,1:-2],x[:,2:-1],x[:,3:]].sum(1)/self.lens[x[:,3:]].sum(1)
 def exact(self,x):
  t=txt(x);return sum(self.d.get(t[i:i+4],self.floor) for i in range(len(t)-3))/max(1,len(t)-3)
def seqs(n):
 limit=max(100, int(n*(math.log(max(n,3))+math.log(math.log(max(n,3))))+100));s=np.ones(limit,dtype=bool);s[:2]=False
 for i in range(2,math.isqrt(limit)+1):
  if s[i]:s[i*i::i]=False
 primes=np.flatnonzero(s)[:n+1];assert len(primes)>n
 phi=np.arange(n+1)
 for i in range(2,n+1):
  if phi[i]==i:phi[i::i]-=phi[i::i]//i
 fib=[];a,b=0,1
 for i in range(n):fib.append(a);a,b=b,(a+b)%29
 out={'primes':primes[:n]%29,'prime_minus_one':(primes[:n]-1)%29,'integer_phi':phi[1:]%29,'integers':np.arange(1,n+1)%29,'fibonacci':np.array(fib),'prime_gaps':np.diff(primes)%29}
 assert list(out['primes'][:5])==[2,3,5,7,11] and list(out['integer_phi'][:5])==[1,1,2,2,4] and list(out['fibonacci'][:7])==[0,1,1,2,3,5,8] and list(out['prime_gaps'][:5])==[1,2,2,4,2]
 return out
def record(c,p,meta,score):
 return {**meta,'status':'UNREVIEWED','score':score.exact(p),'rune_indices':list(map(int,p)),'transliteration':txt(p),'cipher_sha256':hashlib.sha256(bytes(c)).hexdigest()}
def fit(c,period,score,seed,restarts=4):
 rng=np.random.default_rng(seed);n=len(c);phase=np.arange(n)%period;best=None;rows=[];evals=0
 # First restart uses independent unigram-derived phase shifts, remaining random.
 freq=np.array([2.2,2.8,3,7.5,6,2.8,2,2.2,5.5,6.7,7,.15,.1,1.9,.15,6.3,9,1.5,12.7,2.4,4,.5,.1,4.2,8.2,.1,2,.1,.1]);logfreq=np.log(freq/freq.sum())
 key=np.array([np.argmax(logfreq[(c[phase==j,None]-np.arange(29))%29].sum(0)) for j in range(period)])
 for restart in range(restarts):
  k=key.copy() if restart==0 else rng.integers(0,29,period);p=(c-k[phase])%29
  for sweep in range(5):
   changed=False
   for j in rng.permutation(period):
    variants=np.tile(p,(29,1));sites=phase==j;variants[:,sites]=(c[sites][None,:]-np.arange(29)[:,None])%29;vals=score.batch(variants);evals+=29;v=int(np.argmax(vals))
    if vals[v]>score.batch(p)[0]+1e-12:changed=True;k[j]=v;p=variants[v]
   if not changed:break
  value=float(score.batch(p)[0]);rows.append({'restart':restart,'fit_score':value,'key':k.tolist()})
  if best is None or value>best[0]:best=(value,k.copy())
 return best,rows,evals
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['r03','r04']);ap.add_argument('--wide',action='store_true');ap.add_argument('--seconds',type=int,default=820);ap.add_argument('--pages',type=int,default=100);a=ap.parse_args();start=time.monotonic()
 cfg=json.loads((ROOT/'exploration/overnight-01/config.json').read_text());data=ROOT/'audit/parallel-01/inputs/dataset.json';assert hashlib.sha256(data.read_bytes()).hexdigest()==cfg['dataset_sha256'];assert hashlib.sha256((ROOT/'audit/parallel-01/inputs/page-map.json').read_bytes()).hexdigest()==cfg['map_sha256'];pages=[p for p in json.loads(data.read_text())['pages'] if p['original_page']<=55 and p['original_page'] not in cfg['reserved_original_pages']];score=Score();lane=OWNER/a.mode;lane.mkdir(exist_ok=True);statepath=lane/'checkpoint.json';state=json.loads(statepath.read_text()) if statepath.exists() else {'cursor':0,'trials':0,'evaluations':0,'top':[],'cells':[]};top=state['top']
 if a.mode=='r03':
  seq=seqs(15000);defs={'primes':'p[n], p[0]=2','prime_minus_one':'p[n]-1','integer_phi':'phi(n+1)','integers':'n+1','fibonacci':'F[n], F[0]=0,F[1]=1; recurrence mod29 exact','prime_gaps':'p[n+1]-p[n]'};dump(lane/'sequences.json',{k:{'definition':defs[k],'first16':v[:16].tolist(),'sha256':hashlib.sha256(v.tobytes()).hexdigest(),'source':'Explicit OVERNIGHT-01 R03 six-family authorization; no compositions'} for k,v in seq.items()})
  # Search truth among complete family/sign/offset matrix, not only decode known key.
  plain=np.array([ABC.index(x) for x in (ROOT/'audit/parallel-01/reference/sources/solved_p56_an_end.txt').read_text() if x in ABC]);truth=(plain+seq['prime_minus_one'][37:37+len(plain)])%29;controls=[]
  for label,c in [('planted',truth),('corrupted', (truth+np.random.default_rng(330103).integers(1,29,len(truth)))%29)]:
   found=[]
   for name,s in seq.items():
    for sign in [-1,1]:
     for off in range(128):
      p=(c+sign*s[off:off+len(c)])%29;found.append((score.exact(p),name,sign,off,int(np.sum(p!=plain))))
   found.sort(reverse=True);truthrow=next(i for i,r in enumerate(found) if r[1:4]==('prime_minus_one',-1,37));controls.append({'name':label,'truth_rank':truthrow+1,'top20':found[:20],'truth_errors':found[truthrow][4]})
  dump(lane/'controls.json',controls)
  cells=[(p,reset) for p in pages for reset in ['page','continuous_stream_start']]
  for idx in range(state['cursor'],len(cells)):
   page,reset=cells[idx];c=np.array(page['indices']);base=0 if reset=='page' else page['stream_start'];rows=[]
   for name,s in seq.items():
    for sign in [-1,1]:
     for off in range(128):
      p=(c+sign*s[base+off:base+off+len(c)])%29;v=score.exact(p);meta={'id':f'{page["original_page"]}:{reset}:{name}:{sign}:{off}','page':page['original_page'],'family':name,'sign':sign,'offset':off,'reset':reset,'key_start':base+off,'model':'rigid'};rows.append([meta['id'],v]);state['trials']+=1
      if len(top)<20 or v>top[-1]['score']:top.append(record(c,p,meta,score));top.sort(key=lambda r:r['score'],reverse=True);top[:]=top[:20]
   with gzip.open(lane/f'cell-{idx:03}.json.gz','wt') as f:json.dump(rows,f)
   state.update(cursor=idx+1,top=top);dump(statepath,state);print(json.dumps({'mode':a.mode,'cursor':idx+1,'total':len(cells),'trials':state['trials'],'best':top[0]['score']}),flush=True)
   if time.monotonic()-start>a.seconds or idx+1-state.get('batch_start',0)>=a.pages:break
 else:
  if a.wide:
   lane=OWNER/'r04-wide';lane.mkdir(exist_ok=True);statepath=lane/'checkpoint.json';state=json.loads(statepath.read_text()) if statepath.exists() else {'cursor':0,'trials':0,'evaluations':0,'top':[],'cells':[]};top=state['top'];dump(lane/'definition.json',{'periods':[33,64],'min_training_observations_per_phase':2,'skipped':[{'page':p['original_page'],'period':k,'train_length':3*len(p['indices'])//4} for p in pages for k in range(33,65) if k>(3*len(p['indices'])//4)//2],'authorization':'Coordinator explicit extension before execution; four restarts, five sweeps, matched shuffle, no holdout refit'})
  cells=[(p,k) for p in pages for k in (range(33,65) if a.wide else range(1,33)) if not a.wide or k<=(3*len(p['indices'])//4)//2]
  for idx in range(state['cursor'],min(len(cells),state['cursor']+a.pages)):
   page,period=cells[idx];c=np.array(page['indices']);split=3*len(c)//4;rows=[]
   for control in [False,True]:
    source=np.random.default_rng(330104+page['original_page']).permutation(c) if control else c;best,restarts,ev=fit(source[:split],period,score,330104+idx);value,key=best;p=(source-key[np.arange(len(c))%period])%29;hold=score.exact(p[split:]);meta={'id':f'{page["original_page"]}:period{period}:shuffle{control}','page':page['original_page'],'period':period,'key':key.tolist(),'seed':330104+idx,'model':'p=(c-key[i%period])mod29; equivalent plus-key covered by negation','split':split,'train_score':score.exact(p[:split]),'continuation_score':hold,'surrogate_train':value,'control':control,'restarts':restarts,'evaluations':ev};rows.append(record(source,p,meta,score));state['evaluations']+=ev;state['trials']+=1
    if not control:
     # Priority is continuation, compared with matched control; no refit allowed.
     if len(top)<20 or hold>top[-1]['continuation_score']:top.append(rows[-1]);top.sort(key=lambda r:r['continuation_score'],reverse=True);top[:]=top[:20]
   with gzip.open(lane/f'cell-{idx:04}.json.gz','wt') as f:json.dump(rows,f)
   state['cells'].append({'id':rows[0]['id'],'real_train':rows[0]['train_score'],'real_check':rows[0]['continuation_score'],'random_train':rows[1]['train_score'],'random_check':rows[1]['continuation_score'],'evaluations':sum(r['evaluations'] for r in rows)});state.update(cursor=idx+1,top=top);dump(statepath,state);print(json.dumps({'mode':a.mode,'cursor':idx+1,'total':len(cells),'evaluations':state['evaluations'],'best_continuation':top[0]['continuation_score']}),flush=True)
   if time.monotonic()-start>a.seconds:break
 dump(lane/'top20.json',top)
if __name__=='__main__':main()
