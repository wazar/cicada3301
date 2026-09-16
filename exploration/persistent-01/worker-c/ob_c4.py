"""Nonadditive disjoint-alphabet digraph fractionation and partition-free constraint."""
import json,time,gzip
import numpy as np
from p03_frozen import O,ROOT,parse,TRAIN,CHECK,dump
from ob_c1 import nullpages
PARTS=[('contiguous',list(range(14)),list(range(14,29))),('parity',list(range(0,29,2)),list(range(1,29,2)))]
def encode(values,a,b):return np.array([v for x in values for v in (a[int(x)//len(b)],b[int(x)%len(b)])])
def decode(c,a,b,phase=0):
 out=[];invalid=[]
 for i in range(phase,len(c)-1,2):
  if c[i] not in a or c[i+1] not in b:out.append(None);invalid.append(i)
  else:out.append(a.index(c[i])*len(b)+b.index(c[i+1]))
 return out,invalid
def bound(pages):
 adj=np.zeros((29,29),dtype=float)
 for c in pages:
  adj+=np.bincount(c[:-1]*29+c[1:],minlength=841).reshape(29,29)
 adj=adj+adj.T;degree=adj.sum(1);active=degree>0;n=adj[active][:,active]/np.sqrt(degree[active,None]*degree[None,active]);eigen=np.linalg.eigvalsh(n);low=float(eigen[0]);return dict(min_normalized_eigenvalue=low,min_within_partition_fraction=max(0.,(1+low)/2),max_cross_partition_fraction=min(1.,(1-low)/2),transitions=int(adj.sum()/2),adjacency=adj.astype(int).tolist())
def true_within(pages,a):
 aset=set(a);return sum(sum((int(x) in aset)==(int(y) in aset) for x,y in zip(c[:-1],c[1:])) for c in pages)/sum(len(c)-1 for c in pages)
def main():
 out=O/'ob-c4';out.mkdir(exist_ok=True);rng=np.random.default_rng(330120);t=time.monotonic();controls=[]
 for name in TRAIN+CHECK:
  p=parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text())[0]
  for label,a,b in PARTS:
   c=encode(p,a,b);back,invalid=decode(c.tolist(),a,b);assert back==p and not invalid;z=bound([c]);assert z['min_within_partition_fraction']<1e-12;controls.append(dict(name=name,partition=label,exact=True,runes=len(c),bound=z['min_within_partition_fraction']))
 # Uniform210 source exercises allsymbols;stutterchannel accountsfor sparse repeats.
 synthetic=[]
 for noise in [0.,.005,.05,.20,.50]:
  src=rng.integers(0,210,5000);label,a,b=PARTS[0];base=encode(src,a,b);c=[]
  for v in base:
   c.append(int(v))
   if rng.random()<noise:c.append(int(v))
  c=np.array(c);z=bound([c]);actual=true_within([c],a);assert z['min_within_partition_fraction']<=actual+1e-12;synthetic.append(dict(stutter_probability=noise,source_values=src.tolist(),cipher=c.tolist(),known_partition_within=actual,spectral_bound=z['min_within_partition_fraction'],repeat_rate=float(np.mean(c[1:]==c[:-1]))))
 dump(out/'source-controls.json',controls);dump(out/'synthetic-controls.json',synthetic)
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());ps=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']];cs=[np.array(p['indices']) for p in ps];real=bound(cs);q=sum(np.sum(c[1:]==c[:-1]) for c in cs)/sum(len(c)-1 for c in cs);lengths=list(map(len,cs));nulls=[]
 with gzip.open(out/'fixed-pair-maps.jsonl.gz','wt') as f:
  for page,c in zip(ps,cs):
   for label,a,b in PARTS:
    for phase in [0,1]:
     decoded,invalid=decode(c.tolist(),a,b,phase);f.write(json.dumps(dict(page=page['original_page'],partition=label,alphabet_a=a,alphabet_b=b,phase=phase,cipher=c.tolist(),decoded_values=decoded,invalid_pair_starts=invalid,valid_pairs=len(decoded)-len(invalid),total_pairs=len(decoded)))+'\n')
 for ix in range(200):
  gen=bound(nullpages(lengths,q,rng));perm=bound([rng.permutation(c) for c in cs]);nulls.append(dict(id=ix,generative=gen['min_within_partition_fraction'],permutation=perm['min_within_partition_fraction']))
 dump(out/'nulls.json',nulls);dump(out/'real-graph.json',real)
 result=dict(strategy='outside-box-v1',model='base210 source block ->disjoint14x15symbol pair;2fixedpartitions x2phases',pages=len(cs),runes=sum(lengths),real_repeat_rate=float(q),min_error_fraction_any_partition=real['min_within_partition_fraction'],max_valid_alternation_fraction_any_partition=real['max_cross_partition_fraction'],source_controls=len(controls),synthetic=[{k:v for k,v in x.items() if k not in ['source_values','cipher']} for x in synthetic],null_ranges={typ:[min(x[typ] for x in nulls),max(x[typ] for x in nulls)] for typ in ['generative','permutation']},seconds=time.monotonic()-t,proof='For normalized adjacency N, z=D^.5s with s in +/-1, z^TNz>=lambda_min*z^Tz. Cut/W<=(1-lambda_min)/2. Therefore fraction samepartition >=(1+lambda_min)/2 forEVERY partition, notfittedalphabet.',limits='Numerical eigenvalue bound; disjointalternatingalphabets plus sparse stutter only; overlappingalphabets/general fractionation notexcluded. Sourceindex values encodeas0..28 subset210;uniform210synthetic exercisesfullcode.')
 dump(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
