"""Two-rune homophonic rank code: transmitted carrier, then source-bearing partner."""
import json,gzip,time
import numpy as np
from p03_frozen import O,ROOT,parse,TRAIN,CHECK,dump
from ob_c1 import nullpages
def encode(p,d,rng):
 alphabet=list(range(29))[::d];c=[]
 for x in p:
  choices=[v for v in alphabet if not c or v!=c[-1]];a=int(rng.choice(choices));b=a if x==0 else [v for v in alphabet if v!=a][int(x)-1];c.extend([a,b])
 return np.array(c)
def decode(c,d,phase):
 alpha=list(range(29))[::d];where={v:i for i,v in enumerate(alpha)};p=[]
 for i in range(phase,len(c)-1,2):
  a,b=int(c[i]),int(c[i+1]);p.append(0 if a==b else 1+where[b]-(where[b]>where[a]))
 return np.array(p)
def metrics(pages):
 rows=[]
 for d in [-1,1]:
  for phase in [0,1]:
   decoded=[decode(c,d,phase) for c in pages];counts=np.bincount(np.concatenate(decoded),minlength=29);probs=counts/counts.sum();nz=probs>0;entropy=float(-np.sum(probs[nz]*np.log2(probs[nz])));pair=np.zeros((29,29),dtype=int)
   for p in decoded:pair+=np.bincount(p[:-1]*29+p[1:],minlength=841).reshape(29,29)
   prob=pair/pair.sum();den=prob.sum(0)[None,:]*prob.sum(1)[:,None];nz=prob>0;mi=float(np.sum(prob[nz]*np.log2(prob[nz]/den[nz])));rows.append(dict(direction=d,phase=phase,entropy=entropy,lag_mi=mi,counts=counts.tolist()))
 return rows
def repeats(pages):
 rows=[]
 for c in pages:
  pos=np.flatnonzero(c[1:]==c[:-1]);a=int(np.sum(pos%2==0));b=len(pos)-a;rows.append(dict(within_phase0=a,within_phase1=b,min_impossible_repeat_count=min(a,b)))
 return dict(total=sum(x['within_phase0']+x['within_phase1'] for x in rows),min_violations_even_with_free_page_phase=sum(x['min_impossible_repeat_count'] for x in rows),pages_with_both_parities=sum(x['min_impossible_repeat_count']>0 for x in rows),rows=rows)
def main():
 out=O/'ob-c5';out.mkdir(exist_ok=True);rng=np.random.default_rng(330122);t=time.monotonic();controls=[];held=[]
 for name in TRAIN+CHECK:
  p=np.array(parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text())[0])
  for d in [-1,1]:
   c=encode(p,d,rng);back=decode(c,d,0);assert np.array_equal(p,back);rep=repeats([c]);assert rep['min_violations_even_with_free_page_phase']==0;assert np.sum(c[1:]==c[:-1])==np.sum(p==0);controls.append(dict(name=name,direction=d,input=p.tolist(),cipher=c.tolist(),exact=True,repeat_stats=rep))
   if name in CHECK and d==1:held.append(c)
 dump(out/'controls.json',controls);hs=metrics(held)
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());ps=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']];cs=[np.array(p['indices']) for p in ps];real=metrics(cs);rep=repeats(cs);lengths=list(map(len,cs));q=sum(np.sum(c[1:]==c[:-1]) for c in cs)/sum(len(c)-1 for c in cs);nulls=[]
 with gzip.open(out/'full-pair-maps.jsonl.gz','wt') as f:
  for page,c in zip(ps,cs):
   for d in [-1,1]:
    for phase in [0,1]:
     p=decode(c,d,phase);used=set(range(phase,phase+2*len(p)));f.write(json.dumps(dict(page=page['original_page'],direction=d,phase=phase,cipher=c.tolist(),decoded_source_runes=p.tolist(),carrier_positions=list(range(phase,phase+2*len(p),2)),edge_unpaired_positions=[i for i in range(len(c)) if i not in used]))+'\n')
 for ix in range(200):
  gen=nullpages(lengths,q,rng);perm=[rng.permutation(c) for c in cs];nulls.append(dict(id=ix,generative=dict(min_entropy=min(x['entropy'] for x in metrics(gen)),repeat=repeats(gen)),permutation=dict(min_entropy=min(x['entropy'] for x in metrics(perm)),repeat=repeats(perm))))
 dump(out/'nulls.json',nulls);hqs=sum(np.sum(c[1:]==c[:-1]) for c in held)/sum(len(c)-1 for c in held);hnull=[min(x['entropy'] for x in metrics(nullpages(list(map(len,held)),hqs,rng))) for _ in range(200)];comparisons={}
 for typ in ['generative','permutation']:
  v=[x[typ]['min_entropy'] for x in nulls];comparisons[typ]=dict(entropy_lower_tail_p=(1+sum(z<=min(x['entropy'] for x in real) for z in v))/201,entropy_range=[min(v),max(v)])
 res=dict(strategy='outside-box-v1',model='carrier from29symbols excludingprevious partner;source0 emitscarrier again;source1..28 choosesorderedalphabetexcludingcarrier',complexity='2directions x2fixedpairphases,~log2(28)randombits per sourcesymbol carriedexplicitly;no additivepad/key search',real_models=real,held_models=hs,held_min_entropy_p=(1+sum(x<=min(z['entropy'] for z in hs) for x in hnull))/201,real_repeat_constraints=rep,comparisons=comparisons,seconds=time.monotonic()-t,limits='Rankprojection discardsobservedcarrier andhalveslength;notbijection onpairspace, entropychange expectedandcalibrated. Carrieravoidance forbidscrosspair repeats evenifunknownphaseperpage. Generalrandomhomophonic codebooks untested.')
 dump(out/'summary.json',res);print(json.dumps({k:v for k,v in res.items() if k!='real_repeat_constraints'}|dict(repeats={k:v for k,v in rep.items() if k!='rows'})))
if __name__=='__main__':main()
