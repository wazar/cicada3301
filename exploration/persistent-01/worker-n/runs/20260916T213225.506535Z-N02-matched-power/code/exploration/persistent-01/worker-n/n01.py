import pathlib,json,hashlib,datetime,gzip
import numpy as np
O=pathlib.Path(__file__).resolve().parent; R=O.parents[2]
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
rng=np.random.default_rng(33011401)
def check():
 assert not (O.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fit(cs):
 c=np.concatenate(cs); q=(np.bincount(c,minlength=29)+1)/(len(c)+29)
 rep=sum(np.sum(x[1:]==x[:-1]) for x in cs); den=sum(max(0,len(x)-1) for x in cs)
 return q,float(np.clip(rep/max(den,1)/(q@q),.01,2))
def pairbase(q,lam):
 p=q[:,None]*q[None,:];p[np.diag_indices(29)]*=lam;return (p/p.sum()).ravel()
def procedure(cs,detail=False):
 q,lam=fit([c[:len(c)//2] for c in cs]);base=pairbase(q,lam); vals=[]; tests=[]; details=[]
 for phase in [0,1]:
  count=np.zeros(841); parts=[]
  for c in cs:
   n=len(c);a=n//2;b=3*n//4;ix=np.arange(phase,n-1,2);ids=29*c[ix]+c[ix+1];tr=ix+1<a;va=(ix>=a)&(ix+1<b);te=ix>=b
   count+=np.bincount(ids[tr],minlength=841);parts.append((c,ix,ids,va,te,tr))
  alt=(count+29*base)/(count.sum()+29);scores=[];maps=[]
  for c,ix,ids,va,te,tr in parts:
   prev=c[np.maximum(ix-1,0)];ap=alt.reshape(29,29).sum(1);bp=base.reshape(29,29).sum(1)
   # external-repeat numerator factors cancel between alternative/baseline
   gain=np.log(alt[ids]/base[ids])-np.where(ix>0,np.log((1+(lam-1)*ap[prev])/(1+(lam-1)*bp[prev])),0)
   scores.append([float(gain[va].sum()),float(gain[te].sum())])
   if detail:maps.append({'pair_starts':ix.tolist(),'pair_labels':ids.tolist(),'train':np.where(tr)[0].tolist(),'validation':np.where(va)[0].tolist(),'test':np.where(te)[0].tolist(),'discarded_runes':sorted(set(range(len(c)))-set(ix[tr|va|te].tolist())-set((ix[tr|va|te]+1).tolist())),'all_pair_gains':gain.tolist()})
  scores=np.array(scores);vals.append(float(scores[:,0].sum()));tests.append(float(scores[:,1].sum()))
  if detail:details.append({'phase':phase,'counts':count.tolist(),'probabilities':alt.tolist(),'maps':maps,'page_scores':scores.tolist()})
 selected=int(np.argmax(vals));out={'validation':vals,'test':tests,'selected_phase':selected,'statistic':tests[selected]}
 if detail:out.update(q=q.tolist(),repeat_weight=lam,baseline=base.tolist(),models=details)
 return out

def simulations(c,B):
 q,lam=fit([c]);a=np.empty((B,len(c)),int);a[:,0]=rng.choice(29,size=B,p=q);tab=np.tile(q,(29,1));tab[np.diag_indices(29)]*=lam;tab/=tab.sum(1)[:,None];cdf=np.cumsum(tab,axis=1)
 for j in range(1,len(c)):a[:,j]=np.sum(rng.random(B)[:,None]>cdf[a[:,j-1]],axis=1)
 return a

def evaluate(cs,B):
 check();r=procedure(cs,True);sims=[simulations(c,B) for c in cs]; ns=[procedure([s[b] for s in sims]) for b in range(B)]
 r.update(null=ns,p=(1+sum(x['statistic']>=r['statistic'] for x in ns))/(B+1),null_simulation_parameters=[{'q':fit([c])[0].tolist(),'repeat_weight':fit([c])[1]} for c in cs])
 return r

def main():
 check();cfg=json.loads((O.parent/'config.json').read_text());f=R/'audit/parallel-01/inputs/dataset.json';m=R/'audit/parallel-01/inputs/page-map.json';assert sha(f)==cfg['dataset_sha256'];assert sha(m)==cfg['map_sha256']
 ack={'strategy':'outside-box-v1','documents':{p:sha(R/p) for p in ['RESEARCH-STRATEGY.md','CICADA-CONTINUOUS-RESEARCH.md']},'model':'shared opaque841 pair bijection, phases0/1','deadline':cfg['deadline_utc']};(O/'strategy-ack.json').write_text(json.dumps(ack,indent=2))
 names=['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229','0_welcome','jpg107-167','p56_an_end','p57_parable'];sources=[]
 for name in names:
  p=R/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');sources.append({'name':name,'path':str(p.relative_to(R)),'sha256':sha(p),'runes':[ABC.index(x) for x in p.read_text() if x in ABC]})
 summaries=[]
 for panel,ss in enumerate([sources[:5],sources[5:]]):
  for phase in [0,1]:
   for key in range(3):
    perm=rng.permutation(841);cs=[];maps=[]
    for s in ss:
     src=np.array(s['runes']);ix=np.arange(0,len(src)-1,2);labs=perm[29*src[ix]+src[ix+1]];c=np.stack([labs//29,labs%29],axis=1).ravel()
     # phase1 adds independent leading rune; plaintext pairs remain untouched
     if phase:c=np.r_[rng.integers(29),c]
     cs.append(c);maps.append({'source_pair_starts':ix.tolist(),'source_tail_discarded':list(range(2*len(ix),len(src))),'prefix_dummy_count':phase})
    result=evaluate(cs,99);row={'panel':panel,'true_phase':phase,'key':key,'sources':ss,'permutation':perm.tolist(),'cipher':[c.tolist() for c in cs],'maps':maps,'result':result}
    path=O/f'N01-control-{panel}-{phase}-{key}.json.gz'
    with gzip.open(path,'wt') as ff:json.dump(row,ff)
    summary={'panel':panel,'phase':phase,'key':key,'lengths':[len(c) for c in cs],'statistic':result['statistic'],'p':result['p'],'selected_phase':result['selected_phase']};summaries.append(summary);print(json.dumps(summary),flush=True)
 pages=[p for p in json.loads(f.read_text())['pages'] if p['original_page'] in [0,1,3,7,17]];assert len(pages)==5
 cs=[np.array(p['indices']) for p in pages]; result=evaluate(cs,399)
 out={'seed':33011401,'input_sha256':sha(f),'map_sha256':sha(m),'real':pages,'result':result,'controls':summaries,'counts':{'controls':12,'control_nulls':1188,'real_nulls':399,'models_per_procedure':2,'total_model_fits':3200,'decryptions':0}}
 with gzip.open(O/'N01-evidence.json.gz','wt') as ff:json.dump(out,ff)
 (O/'N01-summary.json').write_text(json.dumps({'real':{k:result[k] for k in ['validation','test','selected_phase','statistic','p']},'controls':summaries},indent=2));print('REAL',json.dumps({k:result[k] for k in ['validation','test','selected_phase','statistic','p']}),flush=True)
if __name__=='__main__':main()
