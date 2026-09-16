"""Exhaustive tiny graph checks and perpage/digraph boundary sensitivity."""
import itertools,json,time
import numpy as np
from p03_frozen import O,ROOT,dump
from ob_c4 import bound
def main():
 out=O/'ob-c4';rng=np.random.default_rng(330121);tests=[]
 for ix in range(100):
  n=int(rng.integers(2,9));w=rng.integers(0,6,(n,n));edges=[np.array([i,j]) for i in range(n) for j in range(i,n) for _ in range(int(w[i,j]))]
  if not edges:edges=[np.array([0,1])]
  z=bound(edges);actual=min(sum(s[e[0]]==s[e[1]] for e in edges)/len(edges) for s in itertools.product([0,1],repeat=n));assert z['min_within_partition_fraction']<=actual+1e-12;tests.append(dict(id=ix,vertices=n,edge_multiset=[e.tolist() for e in edges],exact_min_within=actual,spectral_lower_bound=z['min_within_partition_fraction']))
 dump(out/'exhaustive-graph-controls.json',tests)
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());ps=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']];rows=[]
 for p in ps:
  c=np.array(p['indices']);z=bound([c]);q=float(np.mean(c[1:]==c[:-1]));edges={}
  for i,(x,y) in enumerate(zip(c[:-1],c[1:])):
   if x!=y:edges.setdefault(tuple(sorted((int(x),int(y)))),i)
  triangle=next((v for v in itertools.combinations(range(29),3) if all(tuple(sorted(e)) in edges for e in itertools.combinations(v,2))),None)
  witness=None if triangle is None else [dict(runes=list(e),position=edges[tuple(sorted(e))]) for e in itertools.combinations(triangle,2)]
  pairs=[]
  for phase in [0,1]:
   chunks=[c[i:i+2] for i in range(phase,len(c)-1,2)];b=bound(chunks);repeat=sum(x[0]==x[1] for x in chunks)/len(chunks);pairs.append(dict(phase=phase,pairs=len(chunks),min_within_bound=b['min_within_partition_fraction'],repeat_fraction=repeat,reject_strict_disjoint_pairs=b['min_within_partition_fraction']>1e-10))
  rows.append(dict(page=p['original_page'],min_within_bound=z['min_within_partition_fraction'],repeat_rate=q,bound_exceeds_stutter_only=z['min_within_partition_fraction']>q+1e-10,nonself_triangle_witness=witness,within_pairs=pairs))
 dump(out/'pagewise-boundary-checks.json',rows);print(json.dumps(dict(exhaustive_graphs=len(tests),allpage_bounds_exceed_stutter=sum(x['bound_exceeds_stutter_only'] for x in rows),total_pages=len(rows),pages_with_triangle=sum(x['nonself_triangle_witness'] is not None for x in rows),withinpair_reject_both_phases=sum(all(p['reject_strict_disjoint_pairs'] for p in x['within_pairs']) for x in rows),remaining_pair_pages=[x['page'] for x in rows if not all(p['reject_strict_disjoint_pairs'] for p in x['within_pairs'])])))
if __name__=='__main__':main()
