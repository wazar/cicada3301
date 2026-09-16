"""Outside-box-v1: invertible rank-deletion finite-state code; no additive pad."""
import json,pathlib,time,gzip,hashlib,os
import numpy as np
from p03_frozen import O,ROOT,ABC,parse,TRAIN,CHECK,dump
ORDERS=[(r,d) for r in range(29) for d in [-1,1]]
def encode(p,r,d):
 alpha=[(r+d*j)%29 for j in range(29)];c=[int(p[0])]
 for v in p[1:]:c.append(c[-1] if v==28 else [x for x in alpha if x!=c[-1]][int(v)])
 return np.array(c,dtype=np.int64)
def decode(c,r,d):
 pos=((c-r)*d)%29;out=np.empty_like(c);out[0]=c[0];out[1:]=np.where(c[1:]==c[:-1],28,pos[1:]-(pos[1:]>pos[:-1]));return out

def metrics(pages,keep=False):
 rows=[]
 for r,d in ORDERS:
  decoded=[decode(c,r,d) for c in pages];x=np.concatenate([p[1:] for p in decoded]);counts=np.bincount(x[x!=28],minlength=28)[:28];probs=counts/counts.sum();nz=probs>0;entropy=float(-np.sum(probs[nz]*np.log2(probs[nz])))
  # Lag1 mutualinformation excludes eachpage's unencodedseed, keeps escape observations.
  pair=np.zeros((29,29),dtype=np.int64)
  for p in decoded:
   if len(p)>2:pair+=np.bincount(p[1:-1]*29+p[2:],minlength=841).reshape(29,29)
  joint=pair/pair.sum();den=joint.sum(0)[None,:]*joint.sum(1)[:,None];nonzero=joint>0;mi=float(np.sum(joint[nonzero]*np.log2(joint[nonzero]/den[nonzero])))
  row=dict(rotation=r,direction=d,nonrepeat_entropy=entropy,lag1_mutual_information=mi,nonrepeat_histogram=counts.tolist())
  if keep:row['decoded']=[p.tolist() for p in decoded]
  rows.append(row)
 return rows
def summary(rows):return dict(min_entropy=min(r['nonrepeat_entropy'] for r in rows),max_lag1_mi=max(r['lag1_mutual_information'] for r in rows))
def nullpages(lengths,q,rng):
 out=[]
 for n in lengths:
  steps=rng.integers(1,29,n);steps[rng.random(n)<q]=0;steps[0]=rng.integers(29);out.append(np.cumsum(steps)%29)
 return out

def main():
 out=O/'ob-c1';out.mkdir(exist_ok=True);start=time.monotonic();rng=np.random.default_rng(330117);controls=[];groups={}
 for name in TRAIN+CHECK:
  f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');p=np.array(parse(f.read_text())[0]);groups[name]=p
  for r,d in [(0,1),(7,-1),(28,1)]:
   c=encode(p,r,d);back=decode(c,r,d);assert np.array_equal(p,back);assert sum(c[1:]==c[:-1])==sum(p[1:]==28);controls.append(dict(name=name,order=[r,d],source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),length=len(p),exact=True,doublets=int(sum(c[1:]==c[:-1])),escape_count=int(sum(p[1:]==28))))
 dump(out/'arithmetic-controls.json',controls)
 # Controlled search withsourcegroup disjointfrom calibrationreferences; all58orders reallyscored.
 held=[encode(groups[name],7,-1) for name in CHECK];held_rows=metrics(held,True);htruth=next(r for r in held_rows if (r['rotation'],r['direction'])==(7,-1));dump(out/'held-search.json',dict(groups=CHECK,train_groups=TRAIN,rows=held_rows,truth_order=[7,-1],truth_entropy_rank=1+sum(r['nonrepeat_entropy']<htruth['nonrepeat_entropy']-1e-12 for r in held_rows),truth_rank_ties=sum(abs(r['nonrepeat_entropy']-htruth['nonrepeat_entropy'])<1e-12 for r in held_rows),source_plain=[groups[name].tolist() for name in CHECK]))
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());data=ROOT/'audit/parallel-01/inputs/dataset.json';assert hashlib.sha256(data.read_bytes()).hexdigest()==cfg['dataset_sha256'];ps=[p for p in json.loads(data.read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']];cs=[np.array(p['indices']) for p in ps];lengths=list(map(len,cs));q=sum(np.sum(c[1:]==c[:-1]) for c in cs)/sum(n-1 for n in lengths);real=metrics(cs,True);dump(out/'real-statistics.json',[{k:v for k,v in r.items() if k!='decoded'} for r in real]);real_summary=summary(real)
 with gzip.open(out/'full-decoded-maps.jsonl.gz','wt') as f:
  for row in real:
   for page,p in zip(ps,row['decoded']):f.write(json.dumps(dict(original_page=page['original_page'],rotation=row['rotation'],direction=row['direction'],cipher=page['indices'],decoded_rank_indices=p,mapping='position i>=1 has previouscipher at i-1;rank=position_in_rotated_directional_alphabet_after_removing_previous;escape28 whenrepeat;firstsymbolunchanged'))+'\n')
 nulls=[];heldnulls=[]
 hlengths=list(map(len,held));hq=sum(np.sum(c[1:]==c[:-1]) for c in held)/sum(n-1 for n in hlengths)
 for ix in range(200):
  synthetic=nullpages(lengths,q,rng);permuted=[rng.permutation(c) for c in cs];nulls.append(dict(id=ix,generative=summary(metrics(synthetic)),permutation=summary(metrics(permuted))));heldnulls.append(summary(metrics(nullpages(hlengths,hq,rng))))
  if (ix+1)%20==0:print(json.dumps(dict(nulls=ix+1,seconds=time.monotonic()-start)),flush=True)
 dump(out/'nulls.json',nulls);dump(out/'held-nulls.json',heldnulls)
 hs=summary(held_rows);comparisons={}
 for typ in ['generative','permutation']:
  ent=[n[typ]['min_entropy'] for n in nulls];mi=[n[typ]['max_lag1_mi'] for n in nulls];comparisons[typ]=dict(entropy_lower_tail_p=(1+sum(x<=real_summary['min_entropy'] for x in ent))/201,mi_upper_tail_p=(1+sum(x>=real_summary['max_lag1_mi'] for x in mi))/201,entropy_null_range=[min(ent),max(ent)],mi_null_range=[min(mi),max(mi)])
 result=dict(strategy='outside-box-v1',assignment='OB-C',pid=os.getpid(),pages=len(cs),runes=sum(lengths),orders=len(ORDERS),model='previouscipher-deletion alphabet rank code;escape28;firstseedunchanged',real_repeat_rate=float(q),real=real_summary,held=hs,held_entropy_p=(1+sum(x['min_entropy']<=hs['min_entropy'] for x in heldnulls))/201,held_mi_p=(1+sum(x['max_lag1_mi']>=hs['max_lag1_mi'] for x in heldnulls))/201,comparisons=comparisons,seconds=time.monotonic()-start,limits='58orders jointly calibrated,2statistics notjoint combined test;reference Englishsource only;highentropy/externally encrypted inputs notexcluded;permutation changes doubletrate,generative matchesit')
 dump(out/'summary.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':main()
