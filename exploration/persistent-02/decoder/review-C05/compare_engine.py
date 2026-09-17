"""Compare frozen seed×mask enumeration to C05 only after expected files exist."""
import pathlib,sys,json,hashlib,itertools,time
import numpy as np
O=pathlib.Path(__file__).parent;ROOT=O.parents[3]
expected=json.loads((O/'expected-manifest.json').read_text());frozen_hash=hashlib.sha256((O/'expected-manifest.json').read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT/'exploration/persistent-02/feedback'));from literal_feedback import Engine
sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'));from p03_frozen import LM
from enumerate import scalar
lm=LM();models={}
for mode in ['integer','zero','p03']:
 models[mode]=np.array([0. if mode=='zero' else float(-((a*31+b*7+c*13)%17)) if mode=='integer' else lm.step((a,b),c)[1] for a,b,c in itertools.product(range(30),repeat=3)]).reshape(30,30,30)
rows=[];maxerr=0.;t=time.monotonic()
for ix,case in enumerate(expected['cases']):
 weights=models[case['score']];block=1+ix%4;got=Engine(case['k'],weights).solve(case['cipher'],case['ends'],retain=16,block=block);error=abs(got['maximum']-case['best']);assert error<1e-10,(case['id'],got['maximum'],case['best']);maxerr=max(maxerr,error);raw=np.load(O/(case['id']+'.npz'));sites=[i for i,x in enumerate(case['cipher']) if x==0]
 for a in got['alternatives']:
  seed=[0 if x is None else x for x in a['seed']];score,plain,used=scalar(case['cipher'],seed,set(a['literal_positions']),set(case['ends']),weights);assert plain==a['plain'] and abs(score-a['total'])<1e-10;assert used==a['normal_symbols'];assert sum(x is None for x in a['seed'])==max(0,case['k']-used);assert a['unspecified_seed_completions']==29**max(0,case['k']-used)
  si=sum(v*29**(case['k']-1-j) for j,v in enumerate(seed));mask=sum(1<<j for j,p in enumerate(sites) if p in a['literal_positions']);assert raw['plains'][mask,si].tolist()==a['plain'] and abs(float(raw['scores'][mask,si])-a['total'])<1e-10
  # Every unspecified suffix sample re-decodes identically; all completions counted by29^missing.
  alternate=[28 if x is None else x for x in a['seed']];ss,pp,uu=scalar(case['cipher'],alternate,set(a['literal_positions']),set(case['ends']),weights);assert pp==plain and ss==score
 rows.append(dict(id=case['id'],maximum=got['maximum'],absolute_error=error,block=block,peak_states=got['peak_states'],alternatives_checked=len(got['alternatives']),snapshot_bytes=got['snapshot_bytes'],peak_backtrace_arrays_bytes=got['peak_backtrace_arrays_bytes']))
# Changing checkpoint spacing must preserve full path representatives, not just scores.
check=[]
for k in [2,3]:
 c=[0,7,0,0,4,8,0,0];ends={1,3,6};base=Engine(k,models['p03']).solve(c,ends,block=1)
 for block in [2,3,4,7,32]:
  got=Engine(k,models['p03']).solve(c,ends,block=block);assert got['alternatives']==base['alternatives'];check.append(dict(k=k,block=block,peak_states=got['peak_states']))
try:Engine(2,models['p03'],max_states=1).solve([0,1],set())
except MemoryError as e:guard=str(e)
else:raise AssertionError('expected hard guard')
result=dict(passed=True,expected_manifest_sha256=frozen_hash,engine_sha256=hashlib.sha256((ROOT/'exploration/persistent-02/feedback/literal_feedback.py').read_bytes()).hexdigest(),case_count=len(rows),complete_enumerated_seed_mask_paths=expected['total_complete_seed_mask_paths'],max_abs_score_error=maxerr,cases=rows,checkpoint_invariance=check,state_guard=guard,seconds=time.monotonic()-t,limits='Best global score and every returned representative validated. Returned final-state representatives are not global top16. Memory guard applies retained-state count after candidate arrays allocated, not hard RSS cap. Review not blind to proposal, frozen expected cases preceded implementation inspection.')
(O/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['cases','checkpoint_invariance']},indent=2))
