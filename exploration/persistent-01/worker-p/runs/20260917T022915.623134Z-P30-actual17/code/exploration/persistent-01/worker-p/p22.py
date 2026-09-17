import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,random,re,hashlib,sys,time,datetime
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'exploration/persistent-01';OUT=BASE/'worker-p/P22'
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def guard():
 assert not (BASE/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def pages():return sorted(json.loads((BASE/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page'])
def fit(seqs):
 C=np.zeros((32,29),int);H=np.zeros((32,29),int);decoded=np.full((32,sum(map(len,seqs))),255,np.uint8);prefix=np.r_[0,np.cumsum(list(map(len,seqs)))]
 for ix,s in enumerate(seqs):
  a=np.asarray(s,int)
  for L in range(1,33):
   p=(a[L:]-a[:-L])%29;decoded[L-1,prefix[ix]+L:prefix[ix+1]]=p
   (C if ix<23 else H)[L-1]+=np.bincount(p,minlength=29)
 q=(C+1)/(C.sum(1)[:,None]+29);scores=(H*np.log(29*q)).sum(1)/H.sum(1)
 return dict(train_counts=C.tolist(),held_counts=H.tolist(),q=q.tolist(),scores=scores.tolist(),selected_lag=int(np.argmax(scores)+1),maximum=float(max(scores))),decoded
def weights(seqs):
 x=np.bincount(np.concatenate(seqs[:23]),minlength=29)+1;return x/x.sum()
def null(seqs,w,seed):
 rng=random.Random(seed);out=[]
 for s in seqs:
  v=[s[0]]
  for i in range(1,len(s)):
   if s[i]==s[i-1]:v.append(v[-1]);continue
   pool=[j for j in range(29) if j!=v[-1]];z=rng.random()*sum(w[j] for j in pool);total=0
   for j in pool:
    total+=w[j]
    if z<total:break
   v.append(j)
  out.append(v)
 return out
def archive(name,seqs,extra={}):
 guard();file=OUT/(name+'.json')
 if file.exists():return json.loads(file.read_text())
 t=time.monotonic();r,d=fit(seqs);r.update(name=name,seconds=time.monotonic()-t,**extra)
 np.savez_compressed(OUT/(name+'.npz'),cipher=np.concatenate(seqs).astype(np.uint8),lengths=np.array(list(map(len,seqs))),decoded=d)
 save(name+'.json',r);return r
def control(ix):
 pgs=pages();name=['0_welcome','jpg107-167','p56_an_end','p57_parable'][ix];L=[1,8,16,32][ix]
 f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=f.read_text();positions=[i for i,x in enumerate(raw) if x in ABC];plain=[ABC.index(raw[i]) for i in positions]
 rng=random.Random(522100+ix);seqs=[];maps=[]
 for page in pgs:
  n=len(page['indices']);start=rng.randrange(len(plain));p=[plain[(start+i)%len(plain)] for i in range(n)];seed=[rng.randrange(29) for _ in range(L)];c=[]
  for i,v in enumerate(p):c.append((v+(seed[i] if i<L else c[i-L]))%29)
  assert [(c[i]-c[i-L])%29 for i in range(L,n)]==p[L:]
  seqs.append(c);maps.append(dict(page=page['page'],source_start=start,source_indices=[(start+i)%len(plain) for i in range(n)],source_chars=[positions[(start+i)%len(plain)] for i in range(n)],seed=seed,plain=p))
 extra=dict(planted_lag=L,source=str(f.relative_to(ROOT)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_runes=plain,source_char_positions=positions,maps=maps,rng_seed=522100+ix)
 return seqs,extra
def runcontrol(ix,n=99):
 seqs,extra=control(ix);r=archive('control-'+str(ix),seqs,extra);w=weights(seqs);ns=[]
 for j in range(n):ns.append(archive(f'control-{ix}-null-{j:03}',null(seqs,w,522200+100*ix+j),dict(seed=522200+100*ix+j,weights=w.tolist())))
 L=extra['planted_lag'];summary=dict(control=ix,planted_lag=L,rank=1+sum(s>r['scores'][L-1] for s in r['scores']),selected_lag=r['selected_lag'],maximum=r['maximum'],true_gain=r['scores'][L-1],tail=(1+sum(z['maximum']>=r['maximum'] for z in ns))/(n+1),nulls=n,repeat_count=sum(sum(a==b for a,b in zip(s,s[1:])) for s in seqs))
 save('control-'+str(ix)+('-pilot' if n<99 else '-summary')+'.json',summary);print(json.dumps(summary),flush=True)
def pilot():
 for a in range(29):
  for b in range(29):assert (((a+b)%29)-b)%29==a
 runcontrol(0,3)
def controls():
 for i in range(4):runcontrol(i)
def actual():
 assert all((OUT/f'control-{i}-summary.json').exists() for i in range(4))
 pgs=pages();seqs=[p['indices'] for p in pgs];r=archive('actual',seqs,dict(pages=[p['page'] for p in pgs],source_maps=[dict(page=p['page'],source_char_positions=p['source_char_positions']) for p in pgs]))
 w=weights(seqs);ns=[]
 for j in range(199):ns.append(archive(f'actual-null-{j:03}',null(seqs,w,522300+j),dict(seed=522300+j,weights=w.tolist())))
 save('summary.json',dict(selected_lag=r['selected_lag'],maximum=r['maximum'],tail=(1+sum(z['maximum']>=r['maximum'] for z in ns))/200,scores=r['scores'],null_maxima=[z['maximum'] for z in ns],controls=[json.loads((OUT/f'control-{i}-summary.json').read_text()) for i in range(4)]))
 print((OUT/'summary.json').read_text())
if __name__=='__main__':
 guard();t=time.monotonic();{'pilot':pilot,'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
