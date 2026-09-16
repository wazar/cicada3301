import pathlib,json,gzip,numpy as np
import m22
R=pathlib.Path(__file__).parent;controls=json.load(open(R/'controls.json'));real=json.load(open(R/'real.json'));rows=[]
def code(k):
 o=0
 for x in k:o=29*o+x
 return o
for x in controls:
 f=x['fixture'];r=x['result'];split=r['split'];cipher=[];u=0;lit=set(f['literal_positions'])
 for i,p in enumerate(f['plain']):
  if i in lit:assert p==0;cipher.append(0)
  else:cipher.append((p+f['key'][u%len(f['key'])])%29);u+=1
 assert cipher==f['cipher'];scores=np.load(R/'scores'/(r['name']+'.npz'));p=len(f['key']);h=x['heuristic']['best'];h_exact=float(scores['period'+str(p)][code(h['key'])]);assert h_exact>=h['score']-1e-12
 rows.append(dict(name=f['name'],heuristic_beam_gap_at_its_key=h_exact-h['score'],heuristic_key_optimization_gap=float(max(scores['period'+str(p)]))-h_exact,truepath_below_truekey_optimum=x['truthkey_best_path_score']-x['truepath_score'],truth_path_pruned=x['beam_truth_diagnostics']['first_truth_pruned'],exact_train_errors=x['train_errors'],exact_suffix_errors=x['suffix_errors'],heuristic_key_recovered=x['heuristic']['key_recovered']))
# Counterfactual suffix cannot affect exhaustive key arrays, selected prefix or frozen boundary.
r=real[0]['result'];c=r['cipher'].copy();cut=r['split'];c[cut:]=[(i*7+3)%29 for i in range(len(c)-cut)];new,arrays=m22.search(c,set(r['ends']),'check-suffix-mutated');old=np.load(R/'scores'/(r['name']+'.npz'))
for name,a in arrays.items():assert np.array_equal(old[name],a)
assert new['best']==r['best'] and new['training']==r['training'] and new['frozen_boundary']==r['frozen_boundary']
for x in controls+real:
 assert x['tail']==(1+sum(y['score']>=x['result']['score'] for y in x['null']))/(1+len(x['null']))
# Count retained arrays/output cases; evaluate exact projective key aliases exhaustively at stream6.
streams=set();nom=0
for p in [1,2,3]:
 for ix in range(29**p):
  k=m22.key(ix,p);streams.add(tuple((k*6)[:6]));nom+=1
assert nom==25259 and len(streams)==25201
out=dict(controls=rows,exhaustive_alias_check=dict(nominal=nom,unique=len(streams)),suffix_isolation=True,null_tail_recount=True,arithmetic_fixture_replay=12,control_heuristic_calls=sum(x['heuristic']['evaluations'] for x in controls),control_heuristic_path_expansions=sum(x['heuristic']['expanded'] for x in controls),fullsearch_count_primary=440,nominal_key_evaluations_primary=440*nom,unique_stream_evaluations_primary=440*len(streams),additional_fullsearches=dict(pilot=1,suffix_mutation=1))
(R/'check-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
