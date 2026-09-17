import gzip,json,pathlib,hashlib,random,sys
import p14 as p
O=p.O
load=lambda n:json.load(gzip.open(O/(n+'.json.gz'),'rt'))
records=[];allcap=[]
for name in ['control-'+str(i) for i in range(4)]+['real']+['null-'+str(i) for i in range(19)]:
 r=load(name);cuts=r['cuts'];bounds=[0]+cuts+[len(r['cipher'])]
 for mode,rows in [('continuous',r['rows']),('reset',r['reset'])]:
  for row in rows:
   cell=next(x for x in p.CELLS if x['id']==row['id']);d=row['decode'];allcap.append([name,mode,row['id'],d['max_queried'],d['cap_excluded']])
   for a in d['alternatives']:
    score=0.;ctx=(29,29);u=0
    for i,(plain,t) in enumerate(zip(a['plain'],a['reject_counts'])):
     if i in cuts:ctx=(29,29)
     if mode=='reset' and i in cuts:u=0
     prev=None if i==0 or(mode=='reset' and i in cuts) else r['cipher'][i-1]
     accept=u+2*t
     assert all((plain-cell['sign']*cell['key'][z])%29==prev for z in range(u,accept,2))
     assert (plain-cell['sign']*cell['key'][accept])%29==r['cipher'][i]
     ctx,w=p.lm.extend(ctx,plain,i in r['ends']);score+=w+t*p.math.log(.83)+(p.math.log(.17) if prev is not None and prev==r['cipher'][i] else 0);u=accept+1
    assert abs(score-a['total'])<1e-9 and u==a['used']
 if name=='real':
  a=r['top16']['alternatives'][0];records.append(dict(name=name,cell=r['rows'][0]['id'],pages=[dict(page=i,plain=a['plain'][lo:hi],reject_counts=a['reject_counts'][lo:hi],input_interval=[lo,hi],start_key=a['walk'][lo]['start'],after_key=a['walk'][hi-1]['after']) for i,(lo,hi) in enumerate(zip(bounds,bounds[1:]))],all_scores=[dict(id=x['id'],score=x['score']) for x in r['rows']],reset_scores=[dict(id=x['id'],score=x['decode']['alternatives'][0]['score']) for x in r['reset']]))
controls=[]
for i in range(4):
 f=load('fixture-'+str(i));r=load('control-'+str(i));a=r['top16']['alternatives'][0];errs=[j for j,(x,y) in enumerate(zip(a['plain'],f['plain'])) if x!=y];truthskips=[len(e['rejected']) for e in f['events']]
 controls.append(dict(ix=i,errors=errs,truth_plain_top16_ranks=[j+1 for j,a in enumerate(r['top16']['alternatives']) if a['plain']==f['plain']],truth_exactpath_top16_ranks=[j+1 for j,a in enumerate(r['top16']['alternatives']) if a['plain']==f['plain'] and a['reject_counts']==truthskips],used=f['used']))
 # Exact character-to-rune mappings added without changing any text or end positions.
 maps=[]
 for source in f['maps']:
  raw=(p.ROOT/source['path']).read_text();indices=[dict(char_offset=j,rune_id=p.parse(ch)[0][0],packet_index=source['start']+k) for k,(j,ch) in enumerate((j,ch) for j,ch in enumerate(raw) if ch in p.parse.__globals__['ABC'])]
  assert [x['rune_id'] for x in indices]==f['plain'][source['start']:source['start']+source['length']];maps.append(dict(source=source,indices=indices))
 p.dump('control-source-map-'+str(i),maps)
# Tiny forced boundary rejection. At cut1, previous c=3; x=3 with key1=0 rejects, key2 burned, key3=1 accepts2.
cell=dict(key=[0,0,19,1,2,3],sign=1);plain=[3,3];cipher,ev,u=p.encoder(plain,cell['key'],1,1);assert cipher==[3,2] and ev[1]['rejected']==[1] and ev[1]['burned']==[2] and ev[1]['accepted']==3
w=p.walk(cipher,dict(plain=plain,reject_counts=[0,1],used=u),[1],cell);p.dump('forced-boundary',dict(cell=cell,plain=plain,cipher=cipher,events=ev,walk=w,cut=1))
p.dump('check',dict(status='PASS',rows=len(allcap),cap=max(x[3] for x in allcap),excluded=sum(x[4] for x in allcap),cap_rows=allcap,controls=controls,real=records))
print(json.dumps(dict(status='PASS',rows=len(allcap),max_queried=max(x[3] for x in allcap),excluded=sum(x[4] for x in allcap),controls=controls)))
