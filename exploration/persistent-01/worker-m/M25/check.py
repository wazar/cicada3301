import pathlib,json,gzip,math,collections
import m25
R=pathlib.Path(__file__).parent;keys={c['id']:c for c in json.load(open(R/'keys.json'))};ctls=json.load(open(R/'controls.json'));cal=json.load(open(R/'calibration.json'));total=0;paths=0;exp=0;ret_exp=0;infeasible=0
for f in sorted((R/'evidence').glob('*.json.gz')):
 with gzip.open(f,'rt') as h:r=json.load(h)
 c=r['cipher'];ends=set(r['ends']);den=len(c)+len(ends);rep=sum(a==b for a,b in zip(c,c[1:]));allsets=[(row['id'],row['decode']) for row in r['rows']]+[(r['rows'][0]['id'],r['top16'])]
 for ix,(ident,d) in enumerate(allsets):
  if ix<4:exp+=d['expanded']
  else:ret_exp+=d['expanded']
  for a in d['alternatives']:
   key=keys[ident];used,walk=m25.replay(c,a['plain'],a['reject_counts'],key['key'],key['sign'],2);assert used==a['used'];assert len(a['plain'])==len(c);assert (used-len(c))%2==0
   score=m25.lm.score(a['plain'],ends)+(sum(a['reject_counts'])*math.log(.83)+rep*math.log(.17))/den;assert abs(score-a['score'])<1e-12;paths+=1
 assert all(r['rows'][i]['score']>=r['rows'][i+1]['score'] for i in range(3));total+=1
controls=[]
for x in ctls:
 f=x['fixture'];d=x['truth_correctkey_top16'];truecounts=[len(e['rejected']) for e in f['events']];a=d['alternatives'][0];controls.append(dict(name=f['name'],true_rejections=sum(truecounts),actual_terminal_used=f['used'],chosen_terminal_used=a['used'],chosen_trace_exact=a['reject_counts']==truecounts,true_trace_in_top16=any(a['plain']==f['plain'] and a['reject_counts']==truecounts for a in d['alternatives']),reachability_stride1=x['reachability_stride1']['reachable'],reachability_stride2=x['reachability_stride2']['reachable']))
 for j,candidate in enumerate(d['alternatives']):
  u,w=m25.replay(f['cipher'],candidate['plain'],candidate['reject_counts'],f['cell']['key'],f['cell']['sign'],2);assert u==candidate['used']
for row in cal['results']:
 with gzip.open(R/'evidence'/(row['name']+'.json.gz'),'rt') as f:orig=json.load(f)
 for n in row['null']:
  with gzip.open(R/'evidence'/(n['name']+'.json.gz'),'rt') as f:q=json.load(f)
  assert [a==b for a,b in zip(orig['cipher'],orig['cipher'][1:])]==[a==b for a,b in zip(q['cipher'],q['cipher'][1:])]
 assert row['tail']==(1+sum(n['score']>=row['score'] for n in row['null']))/(len(row['null'])+1)
out=dict(fullsearch_files=total,top1_candidate_calls=4*total,winning_top16_calls=total,replayed_retained_paths=paths,top1_path_expansions=exp,top16_path_expansions=ret_exp,controls=controls,conditional_null_masks_exact=True,conditional_tails_recounted=True,conditional_results=[dict(name=x['name'],tail=x['tail'],score=x['score']) for x in cal['results']])
(R/'check-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
