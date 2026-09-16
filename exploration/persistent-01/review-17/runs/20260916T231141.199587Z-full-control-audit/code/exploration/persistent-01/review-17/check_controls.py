from pathlib import Path
from fractions import Fraction as F
import json,gzip,ast,random,math,hashlib
O=Path(__file__).resolve().parent;Q=O.parent/'worker-q/Q04';P=O.parent/'worker-p/P05';M=json.loads((P/'model.json').read_text());inputs=[]
def load(path):
 inputs.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()));return json.load(gzip.open(path,'rt') if path.suffix=='.gz' else open(path))
packets=load(Q/'packets.json.gz');assert [p['label'] for p in packets]==[x for g in range(4) for x in [f'held-{g}',f'model-{g}']]
assert (Q/'model.json').read_bytes()==(P/'model.json').read_bytes() and (Q/'model.txt').read_bytes()==(P/'model.txt').read_bytes()
assert (Q/'search.cpp').read_bytes()==(O/'kernel-local.cpp').read_bytes()
ns=dict(M=M,F=F,math=math);nodes=[n for n in ast.parse((O/'fixtures.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['branch','score']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'independent-review-objective','exec'),ns)
results=[];draws=0;maps=0;positions=0
for p in packets:
 group=p['group'];old=load(P/f'control-{group}-0.json.gz');assert p['truth']==old['control']['truth'] and p['cut']==old['cut'] and len(p['cipher'])==len(old['cipher'])
 if p['type']=='held_source':
  assert p['cipher']==old['cipher'] and p['plain']==old['control']['plain'] and p['optimizer_seed']==old['seed']
 else:
  assert p['source_seed']==470400+2*group and p['emission_seed']==470401+2*group and p['optimizer_seed']==470800+group
  sr=random.Random(p['source_seed']);er=random.Random(p['emission_seed']);plain=p['plain'];cipher=p['cipher']
  for i,d in enumerate(p['draws']):
   u=sr.random();assert u==d['source_uniform'];draws+=1;probs=M['u'] if i<2 else M['tri'][(plain[i-2]*17+plain[i-1])*17:(plain[i-2]*17+plain[i-1]+1)*17];a=plain[i];lo=sum(math.exp(v) for v in probs[:a]);hi=lo+math.exp(probs[a]);assert lo<=u<hi
   groupmembers=[r for r,v in enumerate(p['truth']) if v==a];u=er.random();draws+=1;assert u==d['initial_uniform'];r=groupmembers[int(len(groupmembers)*u)];assert r==d['initial_rune']
   eligible=i>0 and r==cipher[i-1] and len(groupmembers)>1;assert (d['rejection_uniform'] is not None)==eligible
   if eligible:
    coin=er.random();draws+=1;assert coin==d['rejection_uniform'];assert (d['redraw_uniform'] is not None)==(coin<.83)
    if coin<.83:
     v=er.random();draws+=1;assert v==d['redraw_uniform'];choices=[x for x in groupmembers if x!=r];r=choices[int(len(choices)*v)]
   assert r==d['output']==cipher[i]
 assert [p['truth'][r] for r in p['cipher']]==p['plain']
 out=load(Q/(p['label']+'-result.json.gz'));assert out['packet']==p;summary=out['summary'];alts=out['alternatives'];assert len(alts)==8;scores=[]
 for a in alts:
  assert set(a['map'])==set(range(17)) and set(a['initial_map'])==set(range(17));sc=ns['score'](a['map'],p['cipher'],p['cut']);initial=ns['score'](a['initial_map'],p['cipher'],p['cut']);assert sc['prefix_joint']>=initial['prefix_joint']-1e-8
  for field in ['prefix_joint','prefix_lm','prefix_emission','suffix_joint']:assert abs(sc[field]-a[field])<1e-8
  for field in ['lm_terms','emission_terms']:
   assert len(sc[field])==len(a[field])
   assert max(abs(x-y) for x,y in zip(sc[field],a[field]))<1e-10
  assert sc['plain']==a['decoded'];assert 0<=a['accepted']<=a['valid_proposals']<=5000 and a['nominal_proposals']==5000
  scores.append(sc['prefix_joint']);maps+=1;positions+=len(p['cipher'])
 selected=max(range(8),key=scores.__getitem__);assert selected==summary['selected'];best=alts[selected];truth=ns['score'](p['truth'],p['cipher'],p['cut']);rank=1+sum(v>truth['prefix_joint']+1e-9 for v in scores);assert rank==summary['truth_rank'];assert abs(truth['prefix_joint']-best['prefix_joint']-summary['truth_minus_best_prefix'])<1e-8
 for field,lo,hi in [('plaintext_accuracy',0,len(p['plain'])),('prefix_accuracy',0,p['cut']),('suffix_accuracy',p['cut'],len(p['plain']))]:
  acc=sum(best['decoded'][i]==p['plain'][i] for i in range(lo,hi))/(hi-lo);assert abs(acc-summary[field])<1e-12
 used=set(p['cipher']);assert sorted(set(range(29))-used)==summary['unused_runes'];assert abs(sum(best['map'][r]==p['truth'][r] for r in used)/len(used)-summary['observable_map_accuracy'])<1e-12
 assert sum(x!=y for x,y in zip(best['decoded'],p['plain']))==len(out['selected_wrong_positions'])
 results.append(summary)
out=dict(status='PASS',complete_controls=8,generated_uniform_draws_replayed=draws,restart_maps_scored=maps,positions_scored=positions,nominal_proposals=sum(r['nominal_proposals'] for r in results),valid_proposals=sum(r['valid_proposals'] for r in results),accepted_proposals=sum(r['accepted_proposals'] for r in results),controls=results)
(O/'control-results.json').write_text(json.dumps(out,indent=2));(O/'control-inputs.json').write_text(json.dumps(inputs,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='controls'},indent=2));print(json.dumps([dict(label=r['label'],truth_rank=r['truth_rank'],accuracy=r['plaintext_accuracy'],suffix=r['suffix_accuracy']) for r in results],indent=2))
