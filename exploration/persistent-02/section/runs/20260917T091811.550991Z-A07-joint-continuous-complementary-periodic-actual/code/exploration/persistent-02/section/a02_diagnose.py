"""Diagnose prefix ranking and greedy page decisions on already frozen plants only."""
import pathlib,json,gzip,sys
O=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(O));import a02 as A
lm=A.A.M.LM();results=[]
for name in A.A.M.CHECK:
 d=json.load(gzip.open(O/'A02'/f'control-{name}.json.gz','rt'));c=d['cipher'];truth=d['truth'];ends=set(d['ends']);cell=d['plant'];n=d['spans'][0][1];prefix=d['prefix_top'][0]['alternatives'];row=dict(case=name,policy=cell['policy'],prefix_truth_ranks=[i+1 for i,x in enumerate(prefix) if x['plain']==truth[:n]],prefix_ranking=[dict(rank=i+1,score=x['score'],used=x['used'],errors=sum(a!=b for a,b in zip(x['plain'],truth[:n])),literal_positions=x['literal_positions']) for i,x in enumerate(prefix)])
 # Oracle-context local diagnostics isolate local scoring from inherited wrong state.
 context=(29,29);used=0;parts=[]
 for a,b in d['spans']:
  if cell['policy']=='page-reset':used=0
  start=used;p=truth[a:b];e={i-a for i in ends if a<=i<b};lit={i for i,v in enumerate(p) if v==0 and (a+i)%3!=1};cc,used=A.A.forward(p,cell['key'],cell['sign'],lit,used);assert cc==c[a:b]
  alts,diag=A.Finite.kbest(c[a:b],e,cell['key'],cell['sign'],lm,start_used=start,start_context=context);true_total=0.;s=context
  for i,v in enumerate(p):s,w=lm.extend(s,v,i in e);true_total+=w
  parts.append(dict(span=[a,b],truth_start_used=start,truth_end_used=used,truth_context=list(context),truth_score=true_total/(len(p)+len(e)),truth_plain_ranks=[i+1 for i,x in enumerate(alts) if x['plain']==p],best_errors=sum(x!=y for x,y in zip(alts[0]['plain'],p)),alternatives=alts,diagnostics=diag));context=s
 row['oracle_context_parts']=parts
 if cell['policy']=='continuous':
  alts,diag=A.Finite.kbest(c,ends,cell['key'],cell['sign'],lm);row['joint_complete']=dict(truth_plain_ranks=[i+1 for i,x in enumerate(alts) if x['plain']==truth],best_errors=sum(x!=y for x,y in zip(alts[0]['plain'],truth)),alternatives=alts,diagnostics=diag)
 results.append(row)
(O/'A02'/'control-ranking-diagnostics.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps([dict(case=x['case'],prefix_truth=x['prefix_truth_ranks'],local_truth=[p['truth_plain_ranks'] for p in x['oracle_context_parts']],joint_truth=x.get('joint_complete',{}).get('truth_plain_ranks')) for x in results]))
