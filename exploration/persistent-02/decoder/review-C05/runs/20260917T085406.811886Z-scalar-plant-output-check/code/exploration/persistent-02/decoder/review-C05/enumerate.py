"""Independent C05 complete seeds × ciphertext-F masks; no optimized implementation imports."""
import pathlib,sys,itertools,json,hashlib,time,random
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'));from p03_frozen import LM

def scalar(cipher,seed,literals,ends,weights):
 history=[];plain=[];ctx=[29,29];score=0.;used=0
 for i,c in enumerate(cipher):
  if i in literals:r=0
  else:
   k=seed[used] if used<len(seed) else sum(history[-len(seed):])%29
   r=(c-k)%29;history.append(r);used+=1
  score+=weights[ctx[0],ctx[1],r];ctx=[ctx[1],r]
  if i in ends:score+=weights[ctx[0],ctx[1],29];ctx=[ctx[1],29]
  plain.append(r)
 return score,plain,used

def main():
 assert not (O/'expected-manifest.json').exists();cases=[]
 for n in range(5):
  for cipher in itertools.product([0,7],repeat=n):
   for mode in ['integer','zero']:
    cases.append(dict(id=f'k2-{len(cases):03d}',k=2,cipher=list(cipher),ends=[i for i in range(n) if i%2==0],score=mode))
 for ix,c in enumerate([[0],[0,0],[0,1,0],[0,0,7,0],[7,0,4,0,3],[0,7,0,0,5,0],[0,7,3,0,5,1,0]]):
  cases.append(dict(id=f'k3-{ix:02d}',k=3,cipher=c,ends=[i for i in range(len(c)) if i%3==1],score='p03' if ix%2 else 'integer'))
 # Full local P03 arithmetic case with boundary after every rune, normal0 and leading/consecutive0.
 cases.extend([dict(id='k2-p03-'+str(i),k=2,cipher=c,ends=list(range(len(c))),score='p03') for i,c in enumerate([[0,0,4,0,7],[3,0,8,0,0,2],[0,4,0,5,0,0,2]])])
 (O/'cases.json').write_text(json.dumps(dict(seed=260917209,cases=cases,scope='Frozen before viewing C05 implementation. Full29^k seeds times every ciphertext-F decision mask. Unused seed suffixes remain explicit aliases.'),indent=2)+'\n')
 lm=LM();models={}
 for mode in ['integer','zero','p03']:
  models[mode]=np.array([0. if mode=='zero' else float(-((a*31+b*7+c*13)%17)) if mode=='integer' else lm.step((a,b),c)[1] for a,b,c in itertools.product(range(30),repeat=3)]).reshape(30,30,30)
 manifest=[];rng=random.Random(260917209);start=time.monotonic();total=0
 for case in cases:
  k=case['k'];cipher=case['cipher'];ends=set(case['ends']);n=len(cipher);seeds=np.array(list(itertools.product(range(29),repeat=k)),dtype=np.uint8);sites=[i for i,c in enumerate(cipher) if c==0];weights=models[case['score']];allscore=[];allplain=[];allused=[];maskarr=[]
  for mask in range(1<<len(sites)):
   literals={i for j,i in enumerate(sites) if (mask>>j)&1};p=[];history=[];u=0;score=np.zeros(len(seeds));a=np.full(len(seeds),29,dtype=np.int64);b=a.copy()
   for i,c in enumerate(cipher):
    if i in literals:r=np.zeros(len(seeds),dtype=np.int64)
    else:
     key=seeds[:,u].astype(np.int64) if u<k else sum(history[-k:])%29
     r=(c-key)%29;history.append(r);u+=1
    # Scalar local score table; sum per rune+boundary as scalar reference above.
    score+=weights[a,b,r];a,b=b,r
    if i in ends:score+=weights[a,b,29];a,b=b,np.full(len(seeds),29,dtype=np.int64)
    p.append(r)
   pp=np.stack(p,axis=1).astype(np.uint8) if p else np.empty((len(seeds),0),dtype=np.uint8)
   allscore.append(score);allplain.append(pp);allused.append(u);maskarr.append(mask)
   # Independent scalar decoder checks deterministic seeds plus fresh samples per mask.
   for si in sorted({0,len(seeds)-1,len(seeds)//2,*[rng.randrange(len(seeds)) for _ in range(3)]}):
    sc,pl,uu=scalar(cipher,seeds[si].tolist(),literals,ends,weights);assert sc==score[si] and pl==pp[si].tolist() and uu==u
  scores=np.stack(allscore);plains=np.stack(allplain);best=float(scores.max());winners=np.argwhere(scores==best);order=np.argsort(-scores.ravel(),kind='stable')[:32];leaders=[]
  for index in order:
   mask,si=np.unravel_index(index,scores.shape);u=allused[mask];leaders.append(dict(mask=int(mask),seed=seeds[si].tolist(),seed_prefix=seeds[si,:min(k,u)].tolist(),unused_seed_suffix_count=29**max(0,k-u),literal_positions=[p for j,p in enumerate(sites) if (int(mask)>>j)&1],plain=plains[mask,si].tolist(),normal_count=u,score=float(scores[mask,si])))
  f=O/(case['id']+'.npz');np.savez_compressed(f,seeds=seeds,scores=scores,plains=plains,normal_count=np.array(allused),masks=np.array(maskarr));total+=scores.size
  r=dict(**case,best=best,complete_seed_mask_paths=int(scores.size),maximizing_complete_seed_mask_paths=len(winners),top32_complete_seed_paths=leaders,npz_sha256=hashlib.sha256(f.read_bytes()).hexdigest());manifest.append(r)
 (O/'expected-manifest.json').write_text(json.dumps(dict(cases=manifest,total_complete_seed_mask_paths=total,seconds=time.monotonic()-start,method='Full Cartesian seed enumeration and independent F-mask enumeration; no DP/state merging and no optimized C05 import. Scalar checks per mask, exact raw score/plain arrays retained.',score_grouping='Scalar fold adds rune then boundary separately; optimized LM.extend may group two increments and differ in last bits. Compare float weights with explicit tolerance, integer/zero exactly.'),indent=2)+'\n');print(json.dumps(dict(cases=len(manifest),total_complete_seed_mask_paths=total,seconds=time.monotonic()-start)))
if __name__=='__main__':main()
