import m28 as m,json,gzip,pathlib,hashlib,math,collections,zlib
R=m.R;files=sorted((R/'evidence').glob('*.json.gz'));checked=0;alternatives=0;maxkey=-1;diagnostics=[];countmap={}
for file in files:
 with gzip.open(file,'rt') as f:r=json.load(f)
 c=r['cipher'];ends=set(r['ends']);allpaths=[(x['cell'],x['decode']['alternatives'][0]) for x in r['rows']]+[(r['rows'][0]['cell'],p) for p in r['top16']['alternatives']]
 for cell,p in allpaths:
  logp=0
  for i,(v,x) in enumerate(zip(c,p['plain'])):
   f=cell['a']*c[i-1]%29 if i else 0;prob=0;j=i;survival=1.
   while j<len(m.K):
    candidate=(x-cell['sign']*(m.K[j]+f))%29;maxkey=max(maxkey,j)
    if i and candidate==c[i-1]:
     if candidate==v:prob+=survival*(1-m.S)
     if j==len(m.K)-1:
      if candidate==v:prob+=survival*m.S
      break
     survival*=m.S;j+=1
    else:
     if candidate==v:prob+=survival
     break
   assert prob>0;logp+=math.log(prob)
  lm=m.lm.score(p['plain'],ends);assert abs(p['joint_total']-(lm*(len(c)+len(ends))+logp))<1e-8;assert abs(p['score']-p['joint_total']/(len(c)+len(ends)))<1e-12;checked+=1
  cc=collections.Counter(p['plain']);diagnostics.append(dict(packet=r['name'],cell=cell['id'],path_number=alternatives,length=len(p['plain']),distinct=len(cc),ioc_times_n=29*sum(v*(v-1) for v in cc.values())/max(1,len(c)*(len(c)-1)),compressed_bytes=len(zlib.compress(bytes(p['plain'])))));alternatives+=1
 assert len(r['rows'])==56 and r['score']==max(x['score'] for x in r['rows']);countmap[r['name']]=r['cipher']
maskchecks=0
for name,c in countmap.items():
 if '-null' not in name:continue
 src=countmap[name.rsplit('-null',1)[0]];assert [a==b for a,b in zip(src,src[1:])]==[a==b for a,b in zip(c,c[1:])];maskchecks+=1
assert len(files)==280 and maskchecks==274
fixtures=[]
for i in range(4):
 f=m.fixture(i);assert f['reset_reachable'];fixtures.append(dict(name=f['name'],source_length=len(f['plain']),rejected_draws=sum(sum(u<m.S for j,u in e['decisions']) for e in f['events']),forced_eof=sum(e['forced_eof'] for e in f['events']),cumulative_first_dead=f['cumulative']['first_dead']))
m.dump('diagnostics',diagnostics);m.dump('checks',dict(status='PASS',searches=len(files),all_top1_and_top16_paths=checked,exact_stuttermask_nulls=maskchecks,max_checked_key_index=maxkey,key_length=len(m.K),unsupported_positions=0,finite_fallback_on_controls=0,fixtures=fixtures));print(json.dumps(json.load(open(R/'checks.json'))))
