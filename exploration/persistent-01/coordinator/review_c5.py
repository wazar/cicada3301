"""Independent scalar replay of saved paired-unit outputs, no search."""
from pathlib import Path
import json,gzip,collections,math,hashlib
R=Path(__file__).resolve().parents[3];P=R/'exploration/persistent-01/worker-c';O=Path(__file__).parent

def decode(c,d,phase):
 out=[]
 for i in range(phase,len(c)-1,2):
  a,b=c[i:i+2];ordered=[v for v in (range(29) if d==1 else range(28,-1,-1)) if v!=a]
  out.append(0 if a==b else ordered.index(b)+1)
 return out
controls=json.loads((P/'ob-c5/controls.json').read_text())
for x in controls:
 assert decode(x['cipher'],x['direction'],0)==x['input']
 assert all(x['cipher'][i]!=x['cipher'][i-1] for i in range(2,len(x['cipher']),2))
counts=collections.defaultdict(collections.Counter);pages={};maps=0
with gzip.open(P/'ob-c5/full-pair-maps.jsonl.gz','rt') as f:
 for line in f:
  x=json.loads(line);v=decode(x['cipher'],x['direction'],x['phase']);assert v==x['decoded_source_runes'];counts[x['direction'],x['phase']].update(v);pages[x['page']]=x['cipher'];maps+=1
  positions=list(range(x['phase'],x['phase']+2*len(v),2));assert positions==x['carrier_positions'];assert x['edge_unpaired_positions']==[i for i in range(len(x['cipher'])) if i not in {j for k in positions for j in [k,k+1]}]
entropies={str(k):-sum((n/sum(c.values()))*math.log2(n/sum(c.values())) for n in c.values()) for k,c in counts.items()};minimum=min(entropies.values());s=json.loads((P/'ob-c5/summary.json').read_text());assert abs(minimum-min(v['entropy'] for v in s['real_models']))<1e-12
violations=both=0
for c in pages.values():
 ns=collections.Counter(i%2 for i in range(len(c)-1) if c[i]==c[i+1]);v=min(ns[0],ns[1]);violations+=v;both+=v>0
assert violations==s['real_repeat_constraints']['min_violations_even_with_free_page_phase'] and both==s['real_repeat_constraints']['pages_with_both_parities']
nulls=json.loads((P/'ob-c5/nulls.json').read_text());tails={t:(1+sum(v[t]['min_entropy']<=minimum for v in nulls))/(1+len(nulls)) for t in ['generative','permutation']}
for t in tails:assert tails[t]==s['comparisons'][t]['entropy_lower_tail_p']
h=json.loads((P/'ob-c5-recovery/held-null-entropies.json').read_text());hp=(1+sum(v<=min(x['entropy'] for x in s['held_models']) for v in h))/(len(h)+1);assert hp==s['held_min_entropy_p']
out=dict(controls=len(controls),discovery_maps=maps,pages=len(pages),entropy_minimum=minimum,null_tails=tails,held_tail=hp,unavoidable_cross_pair_repeats=violations,pages_with_both_repeat_parities=both,limits='Independent replay of saved outputs and null summaries, not independent source transcription or rerun of generative null. Strict pair-carrier model only; no plaintext conclusion.')
(O/'C5-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
