import pathlib,json,gzip,hashlib,random,sys,math
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];sys.path.insert(0,str(R.parent/'M25'));import m25
old=json.load(open(R/'old-evidence-manifest.json'))
for x in old['files']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
results=json.load(open(R/'results.json'));assert len(results)==43 and len({x['page'] for x in results})==43 and not {0,17,4,9,14,19,24,29,34,39,44,54}&{x['page'] for x in results};keys={x['id']:x for x in json.load(open(R/'keys.json'))};rng=random.Random(330828);total=paths=ex=ret_ex=0;diags=[];leaders=[]
def generated(c):
 out=[rng.randrange(29)]
 for a,b in zip(c,c[1:]):
  if a==b:out.append(out[-1])
  else:q=rng.randrange(28);out.append(q+(q>=out[-1]))
 return out
for row in results:
 c=row['map']['indices'];cases=[('real-'+str(row['page']),c)]+[(n['name'],generated(c)) for n in row['null']]
 for name,expected in cases:
  with gzip.open(R/'evidence'/(name+'.json.gz'),'rt') as f:r=json.load(f)
  assert r['cipher']==expected;assert [a==b for a,b in zip(c,c[1:])]==[a==b for a,b in zip(expected,expected[1:])];ends=set(r['ends']);repeat=sum(a==b for a,b in zip(expected,expected[1:]));den=len(expected)+len(ends)
  for ix,(ident,d) in enumerate([(x['id'],x['decode']) for x in r['rows']]+[(r['rows'][0]['id'],r['top16'])]):
   if ix<4:ex+=d['expanded']
   else:ret_ex+=d['expanded']
   for a in d['alternatives']:
    key=keys[ident];u,w=m25.replay(expected,a['plain'],a['reject_counts'],key['key'],key['sign'],2);assert u==a['used']<=1024;sc=m25.lm.score(a['plain'],ends)+(sum(a['reject_counts'])*math.log(.83)+repeat*math.log(.17))/den;assert abs(sc-a['score'])<1e-12;paths+=1
  total+=1;diag=json.load(open(R/'diagnostics'/(name+'.json')));diags.append(diag)
  if name.startswith('real-'):leaders.append(dict(page=row['page'],score=r['score'],tail=row['tail'],key=r['rows'][0]['id'],plain=r['top16']['alternatives'][0]['plain']))
 assert row['tail']==(1+sum(n['score']>=row['score'] for n in row['null']))/20
assert total==860;out=dict(old554_unchanged=True,fullsearches=total,top1_calls=4*total,top16_calls=total,retainedpaths_replayed=paths,search_path_expansions=ex,retention_path_expansions=ret_ex,exactnulls_regenerated=43*19,tail_counts_replayed=43,max_buffer_index=max(x.get('max_accepted_key_index',-1) for x in diags),max_complete_terminal_used=max(x.get('max_complete_terminal_used',0) for x in diags),exhausted_queries=sum(x.get('exhausted_consumed_state_queries',0) for x in diags),missing_diagnostic_queries=sum('diagnostic_status' in x for x in diags),min_tail_leaders=[x for x in leaders if x['tail']==.05],top5=sorted(leaders,key=lambda x:x['score'],reverse=True)[:5]);(R/'check-result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['min_tail_leaders','top5']},indent=2))
