from pathlib import Path
import itertools,json,random,hashlib,importlib.util,collections
import numpy as np
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/coordinator/histogram-reset';sp=importlib.util.spec_from_file_location('hist_sampler',D/'sample.py');A=importlib.util.module_from_spec(sp);sp.loader.exec_module(A)
records=[]
for c in [(1,1,2,2),(0,1,2,1,2),(1,1,2,2,3),(0,1,2,3,1),(1,2,1,3,2),(0,1,0)]:
 eq=[a==b for a,b in zip(c,c[1:])];states=sorted({v for v in itertools.permutations(c) if [x==0 for x in v]==[x==0 for x in c] and [a==b for a,b in zip(v,v[1:])]==eq});index={v:i for i,v in enumerate(states)};free=[i for i,x in enumerate(c) if x];den=len(free)**2;K=np.zeros((len(states),)*2,dtype=object)
 for row,v in enumerate(states):
  for i in free:
   for j in free:
    proposal=list(v);proposal[i],proposal[j]=proposal[j],proposal[i];valid=[a==b for a,b in zip(proposal,proposal[1:])]==eq;expect=proposal if valid else list(v);got=list(v);assert A.step(got,i,j,eq)==valid and got==expect;K[row,index[tuple(expect)]]+=1
 assert np.array_equal(K,K.T) and all(sum(row)==den for row in K)
 Q=K@K@K;total=0;low=0
 for a,b,cidx in itertools.product(range(len(states)),repeat=3):
  mass=sum(Q[a,h]*Q[h,b]*Q[h,cidx] for h in range(len(states)))
  for order in itertools.permutations([a,b,cidx]):assert mass==sum(Q[order[0],h]*Q[h,order[1]]*Q[h,order[2]] for h in range(len(states)))
  total+=mass;low+=mass*(1+int(b>=a)+int(cidx>=a)<=1)
 assert total==len(states)*den**9 and low*3<=total
 records.append(dict(states=len(states),source=c,den=den,chain_steps=3,triple_mass=int(total),low_rank_mass=int(low)))
x=json.loads((D/'panels.json').read_text());source=json.loads((R/x['source']).read_text());assert hashlib.sha256((R/x['source']).read_bytes()).hexdigest()==x['source_sha256'];assert hashlib.sha256((D/'sample.py').read_bytes()).hexdigest()==x['sampler_sha256'];traces=np.load(R/x['trace_file']);assert hashlib.sha256((R/x['trace_file']).read_bytes()).hexdigest()==x['trace_sha256'];steps=0;walks=0
for ci,case in enumerate(x['cases']):
 original=case['panels'][0]
 if ci==0:src=source['actual'];assert original==src['panels'][0]
 else:src=next(s for s in source['controls'] if s['id']==case['source_control_id']);assert original==src['cipher'] and case['truth']==src['truth'] and case['seed']==src['seed']
 assert case['ends']==src['ends'] and case['reset_before']==src['reset_before'];eq=[a==b for a,b in zip(original,original[1:])];free=[i for i,a in enumerate(original) if a];inventory=collections.Counter(original)
 for endpoint in case['panels']+[case['hub']]:assert collections.Counter(endpoint)==inventory and [a==0 for a in endpoint]==[a==0 for a in original] and [a==b for a,b in zip(endpoint,endpoint[1:])]==eq
 for j in range(20):
  name=f'case{ci}_'+('hub' if j==0 else f'spoke{j:02}');pairs=traces[name+'_pairs'];accepted=traces[name+'_accepted'];meta=case['traces'][j];assert len(pairs)==len(accepted)==meta['proposals']==71600 and int(accepted.sum())==meta['accepted'];assert meta['seed']==2026092400+100*ci+j
  if j not in [0,1,19]:continue
  state=original.copy() if j==0 else case['hub'].copy();rr=random.Random(meta['seed']);changed=0
  for (ii,jj),ok in zip(pairs,accepted):
   i=int(ii);j2=int(jj);assert i==free[rr.randrange(len(free))] and j2==free[rr.randrange(len(free))];diff=state[i]!=state[j2];state[i],state[j2]=state[j2],state[i];valid=True
   for edge in {i-1,i,j2-1,j2}:
    if 0<=edge<len(state)-1 and (state[edge]==state[edge+1])!=eq[edge]:valid=False
   assert valid==bool(ok)
   if not valid:state[i],state[j2]=state[j2],state[i]
   changed+=int(valid and diff);steps+=1
  assert state==(case['hub'] if j==0 else case['panels'][j]) and changed==meta['changed'];walks+=1
out=dict(passed=True,tiny=records,real_endpoints=105,trace_metadata=100,complete_replayed_walks=walks,replayed_proposals=steps,hashes_verified=True);(Path(__file__).parent/'histogram-sampler-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='tiny'}))
