"""Nonadditive adaptive move-to-front coder; key-independent recurrent ranks."""
import json,gzip,time,hashlib
import numpy as np
from p03_frozen import O,ROOT,parse,TRAIN,CHECK,dump
from ob_c1 import ORDERS,nullpages

def enc(p,r,d):
 a=[(r+d*i)%29 for i in range(29)];out=[]
 for x in p:
  rank=(int(x)+1)%29;c=a.pop(rank);out.append(c);a.insert(0,c)
 return np.array(out)
def dec(c,r=0,d=1):
 a=[(r+d*i)%29 for i in range(29)];rank=[];seen=set();valid=[]
 for x in c:
  x=int(x);idx=a.index(x);rank.append(idx);valid.append(x in seen);seen.add(x);a.pop(idx);a.insert(0,x)
 return np.array(rank),np.array(valid)
def metric(pages):
 counts=np.zeros(29,dtype=int);pair=np.zeros((29,29),dtype=int);retained=0
 for c in pages:
  rank,valid=dec(c);mask=valid&(rank!=0);counts+=np.bincount(rank[mask],minlength=29);retained+=int(mask.sum());adj=valid[:-1]&valid[1:];pair+=np.bincount((rank[:-1]*29+rank[1:])[adj],minlength=841).reshape(29,29)
 prob=counts/counts.sum();nz=prob>0;ent=float(-np.sum(prob[nz]*np.log2(prob[nz])));p=pair/pair.sum();den=p.sum(0)[None,:]*p.sum(1)[:,None];nz=p>0;mi=float(np.sum(p[nz]*np.log2(p[nz]/den[nz])))
 return dict(nonrepeat_seen_rank_entropy=ent,seen_rank_lag1_mi=mi,counts=counts.tolist(),retained_nonrepeat=retained,pair_count=int(pair.sum()))
def main():
 out=O/'ob-c2';out.mkdir(exist_ok=True);rng=np.random.default_rng(330118);t=time.monotonic();controls=[];groups={}
 for name in TRAIN+CHECK:
  f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');p=np.array(parse(f.read_text())[0]);groups[name]=p
  for r,d in [(0,1),(7,-1),(28,1)]:
   c=enc(p,r,d);rank,valid=dec(c,r,d);assert np.array_equal((rank-1)%29,p);assert np.array_equal(c[1:]==c[:-1],p[1:]==28)
   for rr,dd in ORDERS:
    other,ov=dec(c,rr,dd);assert np.array_equal(ov,valid);assert np.array_equal(other[valid],rank[valid])
   controls.append(dict(name=name,order=[r,d],runes=len(p),exact=True,initial_orders_tested=58,seen_ranks_invariant=True,source_sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 dump(out/'controls.json',controls);held=[enc(groups[n],7,-1) for n in CHECK];hs=metric(held)
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());ps=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']];cs=[np.array(p['indices']) for p in ps];real=metric(cs);lengths=list(map(len,cs));q=sum(np.sum(c[1:]==c[:-1]) for c in cs)/sum(n-1 for n in lengths);hlengths=list(map(len,held));hq=sum(np.sum(c[1:]==c[:-1]) for c in held)/sum(n-1 for n in hlengths)
 with gzip.open(out/'full-output-maps.jsonl.gz','wt') as f:
  for p,c in zip(ps,cs):
   for r,d in ORDERS:
    rank,valid=dec(c,r,d);f.write(json.dumps(dict(page=p['original_page'],order=[r,d],cipher=c.tolist(),source_rank=rank.tolist(),plaintext_canonical_indices=((rank-1)%29).tolist(),initial_independent_positions=np.flatnonzero(valid).tolist(),mapping='rank at eachposition before movetofront;inputrune=(rank-1)mod29;allfirstoccurrences excludedfromstatistics'))+'\n')
 nulls=[];hnull=[]
 for ix in range(200):
  nulls.append(dict(id=ix,generative=metric(nullpages(lengths,q,rng)),permutation=metric([rng.permutation(c) for c in cs])));hnull.append(metric(nullpages(hlengths,hq,rng)))
 dump(out/'nulls.json',nulls);dump(out/'held-nulls.json',hnull)
 compares={}
 for typ in ['generative','permutation']:
  en=[x[typ]['nonrepeat_seen_rank_entropy'] for x in nulls];mi=[x[typ]['seen_rank_lag1_mi'] for x in nulls];compares[typ]=dict(entropy_p=(1+sum(v<=real['nonrepeat_seen_rank_entropy'] for v in en))/201,mi_p=(1+sum(v>=real['seen_rank_lag1_mi'] for v in mi))/201,entropy_range=[min(en),max(en)],mi_range=[min(mi),max(mi)])
 res=dict(strategy='outside-box-v1',model='move-to-front rankencoder,29symbolpermutationstate;rank0rareEA mappedsource28',real=real,held=hs,held_entropy_p=(1+sum(v['nonrepeat_seen_rank_entropy']<=hs['nonrepeat_seen_rank_entropy'] for v in hnull))/201,held_mi_p=(1+sum(v['seen_rank_lag1_mi']>=hs['seen_rank_lag1_mi'] for v in hnull))/201,comparisons=compares,pages=len(cs),runes=sum(lengths),seconds=time.monotonic()-t,limits='Mainstatistics useonlyseen-symbol positions, invariant to ANY initialalphabet; firstoccurrence sourcevalues remainambiguous. Arbitrary fixed relabelling changesnoentropy/MI. SourceEnglishcontrols;otherhighentropyinputs notexcluded. Two selectedstatistics notjointtest.')
 dump(out/'summary.json',res);print(json.dumps(res))
if __name__=='__main__':main()
