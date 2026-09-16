import pathlib,json,hashlib,datetime,zlib
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';rng=np.random.default_rng(33010111)
def check():
 assert not(O.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fit0(c):
 q=(np.bincount(c,minlength=29)+1)/(len(c)+29);rr=np.mean(c[1:]==c[:-1]);return q,float(np.clip(rr/np.sum(q*q),.01,2))
def procedure(cs,detail=False):
 v=np.zeros(8);t=np.zeros(8);models=[]
 for c in cs:
  n=len(c);a=n//2;b=3*n//4;_,lam=fit0(c[:a]);ix=np.arange(n);rows=[]
  for p in range(1,9):
   ct=np.bincount((ix[:a]%p)*29+c[:a],minlength=p*29).reshape(p,29)+1;q=ct/ct.sum(axis=1)[:,None]
   # phase offset relabel symmetry checked directly
   ct2=np.bincount(((ix[:a]+1)%p)*29+c[:a],minlength=p*29).reshape(p,29)+1;q2=ct2/ct2.sum(axis=1)[:,None]
   assert np.array_equal(q[ix%p],q2[(ix+1)%p])
   lp=np.log(q[ix[1:]%p,c[1:]])+np.where(c[1:]==c[:-1],np.log(lam),0)-np.log(1+(lam-1)*q[ix[1:]%p,c[:-1]])
   v[p-1]+=lp[a-1:b-1].sum();t[p-1]+=lp[b-1:].sum()
   if detail:rows.append({'period':p,'probabilities':q.tolist(),'validation_logprob':float(lp[a-1:b-1].sum()),'test_logprob':float(lp[b-1:].sum())})
  if detail:models.append({'train_stop':a,'validation_stop':b,'repeat_weight':lam,'models':rows})
 k=int(np.argmax(v));out={'selected_period':k+1,'validation_gain':(v-v[0]).tolist(),'test_gain':(t-t[0]).tolist(),'statistic':float(t[k]-t[0])}
 if detail:out['fitted']=models
 return out

def simulate(c):
 q,lam=fit0(c);out=np.empty(len(c),dtype=int);out[0]=rng.choice(29,p=q)
 for i in range(1,len(c)):
  a=q.copy();a[out[i-1]]*=lam;a/=a.sum();out[i]=rng.choice(29,p=a)
 return out

def evaluate(cs,B):
 r=procedure(cs,True);ns=[]
 for i in range(B):
  if i%20==0:check()
  ns.append(procedure([simulate(c) for c in cs]))
 r['null']=ns;r['p']=(1+sum(x['statistic']>=r['statistic'] for x in ns))/(B+1)
 return r

def metrics(c):
 ct=np.bincount(c,minlength=29);n=len(c);return {'ioc_times_n':float(np.sum(ct*(ct-1))/(n-1)),'min_distinct32':min(len(set(c[i:i+32])) for i in range(n-31)) if n>=32 else None,'zlib_bytes_per_rune':len(zlib.compress(bytes(c.tolist())))/n,'nonenglish_lm':None,'nonenglish_lm_reason':'probability prediction, no decrypted text'}
def main():
 check();cfg=json.loads((O.parent/'config.json').read_text());f=R/'audit/parallel-01/inputs/dataset.json';m=R/'audit/parallel-01/inputs/page-map.json';assert sha(f)==cfg['dataset_sha256'];assert sha(m)==cfg['map_sha256']
 ack={'strategy':'outside-box-v1','deadline_utc':cfg['deadline_utc'],'documents':{s:sha(R/s) for s in ['RESEARCH-STRATEGY.md','CICADA-CONTINUOUS-RESEARCH.md','exploration/persistent-01/config.json']}};(O/'strategy-ack.json').write_text(json.dumps(ack,indent=2))
 controls=[]
 for name in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229','0_welcome','jpg107-167','p56_an_end','p57_parable']:
  f0=R/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');src=np.array([ABC.index(x) for x in f0.read_text() if x in ABC]);
  for mode in ['original','shuffled','rotated']:
   p=src.copy() if mode=='original' else rng.permutation(src) if mode=='shuffled' else np.roll(src,len(src)//3)
   for period in [1,3,8]:
    keys=np.array([rng.permutation(29) for _ in range(period)]);c=keys[np.arange(len(p))%period,p];r=evaluate([c],99);row={'name':name,'source_sha256':sha(f0),'mode':mode,'period':period,'source_indices':p.tolist(),'permutations':keys.tolist(),'cipher':c.tolist(),'metrics':metrics(c),'result':r};controls.append(row)
    with (O/'k01-controls.jsonl').open('a') as ff:ff.write(json.dumps(row)+'\n')
    print(name,mode,period,len(c),r['selected_period'],r['statistic'],r['p'],flush=True)
 pages=[p for p in json.loads(f.read_text())['pages'] if p['original_page'] in [0,1,3,7,17]];assert len(pages)==5
 cs=[np.array(p['indices']) for p in pages];result=evaluate(cs,399)
 out={'seed':33010111,'input_hash':sha(f),'map_hash':sha(m),'real':pages,'metrics':[metrics(c) for c in cs],'result':result,'control_count':len(controls),'counts':{'control_model_fits':len(controls)*100*8,'real_model_fits':400*5*8,'decoded_candidates':0,'path_expansions':0},'control_summary':[{'name':x['name'],'mode':x['mode'],'period':x['period'],'n':len(x['cipher']),'selected':x['result']['selected_period'],'p':x['result']['p'],'statistic':x['result']['statistic']} for x in controls]};(O/'k01-results.json').write_text(json.dumps(out,indent=2));print('REAL',result['selected_period'],result['statistic'],result['p'])
if __name__=='__main__':main()
