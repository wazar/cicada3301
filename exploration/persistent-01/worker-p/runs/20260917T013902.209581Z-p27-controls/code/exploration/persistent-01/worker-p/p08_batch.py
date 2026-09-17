import p08 as p
import random,json,time
p.gate();models,env,cells,parse=p.setup();packets=[]
for ix in range(4):
 d=p.read('control-'+str(ix));f=d['fixture'];packets.append(dict(label='control-'+str(ix),cipher=f['cipher'],ends=f['ends'],observed={k:v['rows'] for k,v in d['results'].items()},fixture=f))
assert all(p.read('control-'+str(ix))['results']['latin']['best_errors']==0 for ix in range(4))
ms=json.loads((p.ROOT/'exploration/persistent-01/worker-f/F06-maps.json').read_text())
for pid in [0,17]:
 m=next(m for m in ms if m['page']==pid);c,ends=parse(m['raw_joined']);assert c==m['indices'];packets.append(dict(label='real-'+str(pid),cipher=c,ends=sorted(ends),map=m))
summary=[]
for packetix,q in enumerate(packets):
 p.gate();start=time.monotonic();c=q['cipher'];ends=q['ends'];observed=q.get('observed') or {k:p.search(c,ends,m,env,cells) for k,m in models.items()};seed=330208+packetix;rng=random.Random(seed);nulls=[]
 for rep in range(19):
  p.gate();a=[rng.randrange(29)]
  for i in range(1,len(c)):
   if c[i]==c[i-1]:a.append(a[-1])
   else:
    v=rng.randrange(28);a.append(v+(v>=a[-1]))
  assert [x==y for x,y in zip(a,a[1:])]==[x==y for x,y in zip(c,c[1:])]
  rows={k:p.search(a,ends,m,env,cells) for k,m in models.items()};nulls.append(dict(rep=rep,cipher=a,models=rows))
 scores={k:v[0]['score'] for k,v in observed.items()};tails={k:(1+sum(x['models'][k][0]['score']>=scores[k] for x in nulls))/20 for k in models};delta=scores['latin']-scores['english'];dt=(1+sum(x['models']['latin'][0]['score']-x['models']['english'][0]['score']>=delta for x in nulls))/20
 p.save(q['label']+'-batch',dict(packet=q,observed=observed,nulls=nulls,seed=seed,rng_after=repr(rng.getstate()),scores=scores,tails=tails,delta=delta,delta_tail=dt));row=dict(label=q['label'],n=len(c),repeats=sum(x==y for x,y in zip(c,c[1:])),scores=scores,tails=tails,delta=delta,delta_tail=dt,best_cells={k:v[0]['id'] for k,v in observed.items()},seconds=time.monotonic()-start);summary.append(row);p.dump('batch-summary',summary);print(json.dumps(row),flush=True)
