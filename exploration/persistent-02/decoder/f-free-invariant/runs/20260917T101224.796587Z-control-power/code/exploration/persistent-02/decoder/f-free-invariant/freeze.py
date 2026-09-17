import pathlib,sys,json,hashlib,importlib.util,numpy as np
from invariant import runs
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];P=R/'exploration/persistent-02';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (O/'inputs.json').exists();source=P/'coordinator/histogram-reset/sample.py';spec=importlib.util.spec_from_file_location('f01_reviewed_sampler',source);s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s);records=[];pins=[source,O/'PREREG.md',O/'invariant.py',P/'coordinator/histogram-reset/panels.json'];out=O/'traces';out.mkdir(exist_ok=True)
 for construction,label in [('C05','excluded'),('C11','emitted')]:
  path=P/f'feedback/{construction}/plants.json';pins.append(path);data=json.loads(path.read_text());cases=[c for c in data['cases'] if len(c['truth'])==716 and c['k'] in (2,3) and c['source'].get('source_id') in ('guest','mill','shelley','blake')];assert len(cases)==8
  for c in cases:
   idx=len(records);seed=2026092800+100*idx;n=100*len(c['cipher']);hub,pa,ok,di=s.walk(c['cipher'],n,seed);panels=[c['cipher']];arrays={'hub_pairs':pa,'hub_accepted':ok};meta=[dict(role='hub',seed=seed,**di)]
   for j in range(1,20):
    v,pa,ok,di=s.walk(hub,n,seed+j);panels.append(v);arrays[f'spoke{j}_pairs']=pa;arrays[f'spoke{j}_accepted']=ok;meta.append(dict(role=f'spoke{j}',seed=seed+j,**di))
   trace=out/f'control{idx:02d}.npz';np.savez_compressed(trace,**arrays);records.append(dict(index=idx,construction=label,original=c,hub=hub,panels=panels,trace=str(trace.relative_to(R)),trace_sha256=H(trace),walks=meta));print(idx,label,c['id'],flush=True)
 actual=json.loads((P/'coordinator/histogram-reset/panels.json').read_text())['cases'][0]['panels'][0];lengths=[b-a for a,b in runs(actual)];geom={}
 for k in (2,3):
  group=[len(range(j,n,k+1)) for n in lengths for j in range(k+1)];geom[k]=dict(ordered_pairs=sum(x*(x-1) for x in group),unordered_pairs=sum(x*(x-1)//2 for x in group),groups_with_pairs=sum(x>=2 for x in group),identity_edges=sum(max(0,n-k-1) for n in lengths))
 obj=dict(controls=records,source_pins={str(p.relative_to(R)):H(p) for p in pins},actual_geometry=dict(n=len(actual),nonF_symbols=sum(lengths),runs=len(lengths),run_lengths=lengths,by_k=geom),actual_scores_computed=False);(O/'inputs.json').write_text(json.dumps(obj,separators=(',',':'))+'\n');print(json.dumps(obj['actual_geometry']))
if __name__=='__main__':main()
