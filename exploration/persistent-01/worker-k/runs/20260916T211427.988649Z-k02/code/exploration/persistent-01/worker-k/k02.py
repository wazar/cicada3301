import k01 as k
import numpy as np,json
O=k.O;R=k.R;k.rng=np.random.default_rng(33010112)
def procedure(cs,detail=False):
 v=np.zeros(8);t=np.zeros(8);models=[];lams=[k.fit0(c[:len(c)//2])[1] for c in cs]
 for p in range(1,9):
  ct=np.ones((p,29))
  for c in cs:
   a=len(c)//2;ct+=np.bincount((np.arange(a)%p)*29+c[:a],minlength=p*29).reshape(p,29)
  q=ct/ct.sum(axis=1)[:,None];row={'period':p,'probabilities':q.tolist(),'pages':[]}
  for c,lam in zip(cs,lams):
   n=len(c);a=n//2;b=3*n//4;ix=np.arange(n)
   lp=np.log(q[ix[1:]%p,c[1:]])+np.where(c[1:]==c[:-1],np.log(lam),0)-np.log(1+(lam-1)*q[ix[1:]%p,c[:-1]])
   vv=float(lp[a-1:b-1].sum());tt=float(lp[b-1:].sum());v[p-1]+=vv;t[p-1]+=tt
   if detail:row['pages'].append({'train_stop':a,'validation_stop':b,'repeat_weight':lam,'validation_logprob':vv,'test_logprob':tt})
  if detail:models.append(row)
 best=int(np.argmax(v));out={'selected_period':best+1,'validation_gain':(v-v[0]).tolist(),'test_gain':(t-t[0]).tolist(),'statistic':float(t[best]-t[0])}
 if detail:out['fitted']=models
 return out
k.procedure=procedure
k.check();src=[]
for name in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229','0_welcome','jpg107-167','p56_an_end','p57_parable']:
 f=R/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');src.append({'name':name,'sha256':k.sha(f),'indices':[k.ABC.index(x) for x in f.read_text() if x in k.ABC]})
controls=[]
for panel,ids in [('first5',list(range(5))),('last4',list(range(5,9)))]:
 for mode in ['original','shuffled','rotated']:
  ps=[np.array(src[i]['indices']) for i in ids]
  if mode=='shuffled':ps=[k.rng.permutation(p) for p in ps]
  if mode=='rotated':ps=[np.roll(p,len(p)//3) for p in ps]
  for period in [1,3,8]:
   keys=np.array([k.rng.permutation(29) for _ in range(period)]);cs=[keys[np.arange(len(p))%period,p] for p in ps];r=k.evaluate(cs,99);controls.append({'panel':panel,'mode':mode,'period':period,'source_indices':[p.tolist() for p in ps],'permutations':keys.tolist(),'ciphers':[c.tolist() for c in cs],'result':r});print(panel,mode,period,r['selected_period'],r['statistic'],r['p'],flush=True)
d=json.loads((O/'k01-results.json').read_text());cs=[np.array(p['indices']) for p in d['real']]
for period in [3,8]:
 ps=[k.rng.integers(0,29,len(c)) for c in cs];keys=np.array([k.rng.permutation(29) for _ in range(period)]);ciphers=[keys[np.arange(len(p))%period,p] for p in ps];rr=k.evaluate(ciphers,99);controls.append({'panel':'uniform','mode':'iid','period':period,'source_indices':[p.tolist() for p in ps],'permutations':keys.tolist(),'ciphers':[c.tolist() for c in ciphers],'result':rr})
r=k.evaluate(cs,399);out={'seed':33010112,'sources':src,'controls':controls,'real':d['real'],'input_hash':d['input_hash'],'map_hash':d['map_hash'],'result':r,'counts':{'control_model_fits':20*100*8,'real_model_fits':400*8,'decoded_candidates':0,'path_expansions':0}};(O/'k02-results.json').write_text(json.dumps(out));print('REAL',r['selected_period'],r['statistic'],r['p'])
