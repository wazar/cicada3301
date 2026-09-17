import collections,gzip,json,math,pathlib,random,sys,time
import p14 as base
R=base.R;ROOT=base.ROOT;O=R/'P15';lm=base.lm;parse=base.parse;S=.83
CELLS=[dict(id=c['id'],key=[(c['sign']*v)%29 for v in c['key']]) for c in base.CELLS]
def dump(name,x):
 with gzip.open(O/(name+'.json.gz'),'wt') as f:json.dump(x,f)
def encoder(plain,key,seed):
 rng=random.Random(seed);c=[];events=[];j=0
 for i,p in enumerate(plain):
  ev=[]
  while j<len(key):
   z=p^key[j];q=None
   if z>=29:kind='invalid'
   elif c and z==c[-1]:
    q=rng.random();kind='soft-reject' if q<S else 'accept-repeat'
   else:kind='accept'
   ev.append(dict(draw=j,key=key[j],proposal=z,kind=kind,random=q));j+=1
   if kind.startswith('accept'):c.append(z);events.append(ev);break
  else:return dict(complete=False,cipher=c,events=events,unfinished=ev,used=j,failed_plain_index=i)
 return dict(complete=True,cipher=c,events=events,used=j)

def transitions(c,prev,j,key):
 out=[];tested=0;maxquery=-1;eof=0
 for p in range(29):
  soft=0;invalid=0
  for a in range(j,len(key)):
   z=p^key[a];tested+=1;maxquery=max(maxquery,a)
   if z>=29:invalid+=1;continue
   repeat=prev is not None and z==prev
   if z==c:out.append((p,a+1,soft,invalid,soft*math.log(S)+(math.log(1-S) if repeat else 0)))
   if not repeat:break
   soft+=1
  else:eof+=1
 return out,dict(tested=tested,maxquery=maxquery,eof=eof)

def decode(c,ends,cell,retain=1):
 states={(0,(29,29)):[(0.,b'',())]};history=[];maxquery=-1;eof=0
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list);cache={};prev=c[i-1] if i else None
  for (j,ctx),paths in states.items():
   if j not in cache:
    cache[j],d=transitions(v,prev,j,cell['key']);maxquery=max(maxquery,d['maxquery']);eof+=d['eof']
   for p,u,s,iv,prob in cache[j]:
    ss,w=lm.extend(ctx,p,i in ends)
    for score,plain,accepts in paths:nxt[(u,ss)].append((score+w+prob,plain+bytes([p]),accepts+(u-1,)))
  states={}
  for state,paths in nxt.items():paths.sort(key=lambda x:x[0],reverse=True);states[state]=paths[:retain]
  history.append([i,len(states),sum(map(len,states.values()))])
  if not states:return dict(feasible=False,first_failed=i,alternatives=[],history=history,max_queried=maxquery,eof_hypotheses=eof)
 ordered=sorted([(sc,p,a,u) for (u,ctx),paths in states.items() for sc,p,a in paths],key=lambda x:x[0],reverse=True)
 return dict(feasible=True,alternatives=[dict(score=sc/(len(c)+len(ends)),total=sc,plain=list(p),accepted=list(a),used=u) for sc,p,a,u in ordered[:retain]],history=history,max_queried=maxquery,eof_hypotheses=eof,max_terminal_used=max(x[3] for x in ordered))

def replay(c,a,key):
 j=0;events=[];prob=0
 for i,(v,p,accept) in enumerate(zip(c,a['plain'],a['accepted'])):
  row=[];prev=c[i-1] if i else None
  for zidx in range(j,accept+1):
   z=p^key[zidx]
   if zidx==accept:
    assert z<29 and z==v;kind='accept-repeat' if prev is not None and z==prev else 'accept'
    if kind=='accept-repeat':prob+=math.log(1-S)
   elif z>=29:kind='invalid'
   else:assert prev is not None and z==prev;kind='soft-reject';prob+=math.log(S)
   row.append(dict(draw=zidx,key=key[zidx],proposal=z,kind=kind))
  events.append(row);j=accept+1
 assert j==a['used'];return dict(events=events,log_probability=prob,invalid=sum(x['kind']=='invalid' for e in events for x in e),soft=sum(x['kind']=='soft-reject' for e in events for x in e),accepted_repeats=sum(e[-1]['kind']=='accept-repeat' for e in events))
def search(name,c,ends):
 base.gate();start=time.monotonic();rows=[]
 for cell in CELLS:
  d=decode(c,ends,cell)
  for a in d['alternatives']:a['replay']=replay(c,a,cell['key'])
  rows.append(dict(id=cell['id'],score=d['alternatives'][0]['score'] if d['feasible'] else None,decode=d))
 rows.sort(key=lambda x:float('-inf') if x['score'] is None else x['score'],reverse=True)
 top=None
 if rows[0]['score'] is not None:
  cell=next(x for x in CELLS if x['id']==rows[0]['id']);top=decode(c,ends,cell,16);assert abs(top['alternatives'][0]['score']-rows[0]['score'])<1e-12
  for a in top['alternatives']:a['replay']=replay(c,a,cell['key'])
 r=dict(name=name,cipher=c,ends=sorted(ends),rows=rows,top16=top,seconds=time.monotonic()-start);dump(name,r);return r

def control(ix):
 name=['0_welcome','jpg107-167','p56_an_end','p57_parable'][ix];path=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=path.read_text();plain,ends=parse(raw);cell=CELLS[ix];seed=331500+ix;e=encoder(plain,cell['key'],seed)
 source=dict(path=str(path.relative_to(ROOT)),sha256=base.hashlib.sha256(path.read_bytes()).hexdigest(),character_offsets=[j for j,ch in enumerate(raw) if ch in parse.__globals__['ABC']]);f=dict(source=source,plain=plain,ends=sorted(ends),cell_id=cell['id'],seed=seed,encoder=e);dump('fixture-'+str(ix),f)
 if not e['complete']:print('INCOMPLETE',ix,flush=True);return
 # Independent scalar loop uses invalid test before any random draw.
 rng=random.Random(seed);cc=[];accepted=[];j=0
 for p in plain:
  while True:
   z=p^cell['key'][j];a=j;j+=1
   if z in (29,30,31):continue
   if cc and z==cc[-1] and rng.random()<.83:continue
   cc.append(z);accepted.append(a);break
 assert cc==e['cipher'] and accepted==[x[-1]['draw'] for x in e['events']] and j==e['used']
 r=search('control-'+str(ix),e['cipher'],ends);a=r['top16']['alternatives'][0] if r['top16'] else None
 truthrow=next(x for x in r['rows'] if x['id']==cell['id']);truthalts=decode(e['cipher'],ends,cell,16);dump('truth-top16-'+str(ix),truthalts)
 result=dict(ix=ix,length=len(plain),complete=True,key_recovered=r['rows'][0]['id']==cell['id'],errors=sum(x!=y for x,y in zip(a['plain'],plain)) if a else len(plain),path_recovered=bool(a and a['accepted']==accepted),truth_plain_ranks=[j+1 for j,a in enumerate(truthalts['alternatives']) if a['plain']==plain],truth_path_ranks=[j+1 for j,a in enumerate(truthalts['alternatives']) if a['plain']==plain and a['accepted']==accepted],used=e['used'],invalid=sum(x['kind']=='invalid' for ev in e['events'] for x in ev),soft=sum(x['kind']=='soft-reject' for ev in e['events'] for x in ev),repeats=sum(a==b for a,b in zip(cc,cc[1:])),seconds=r['seconds'])
 dump('control-summary-'+str(ix),result);print(json.dumps(result),flush=True)

def brute():
 result=[]
 for case in range(80):
  rng=random.Random(331550+case);key=[rng.randrange(29) for _ in range(7)];c=[rng.randrange(29) for _ in range(3)];ends={1,2};paths=[]
  def rec(i,j,ctx,score,plain,accepts):
   if i==len(c):paths.append((score,plain,accepts));return
   for a in range(j,len(key)):
    p=c[i]^key[a]
    if p>=29:continue
    lp=0;good=True
    for q in range(j,a):
     z=p^key[q]
     if z>=29:continue
     if i and z==c[i-1]:lp+=math.log(.83)
     else:good=False;break
    if not good:continue
    if i and c[i]==c[i-1]:lp+=math.log(.17)
    ss,w=lm.extend(ctx,p,i in ends);rec(i+1,a+1,ss,score+w+lp,plain+[p],accepts+[a])
  rec(0,0,(29,29),0.,[],[]);paths.sort(key=lambda x:x[0],reverse=True);d=decode(c,ends,dict(key=key),16)
  assert len(d['alternatives'])==min(16,len(paths));assert all(abs(a['total']-p[0])<1e-11 for a,p in zip(d['alternatives'],paths));result.append(dict(case=case,key=key,cipher=c,paths=len(paths),scores=[p[0] for p in paths[:16]]))
 dump('brute',result)
 probes=[]
 for plain,key,seed in [([28],[1,2,3,0],1),([3,3],[0,0,1],1),([3,3],[0,0],2),([28],[1,2,3],1),([3,3],[0,0],1)]:
  e=encoder(plain,key,seed);probes.append(dict(plain=plain,key=key,seed=seed,result=e))
 assert probes[0]['result']['cipher']==[28] and probes[0]['result']['used']==4
 assert probes[1]['result']['cipher']==[3,2]
 assert probes[2]['result']['cipher']==[3,3]
 assert not probes[3]['result']['complete'] and not probes[4]['result']['complete']
 dump('edge-probes',probes)

def actual():
 maps=json.loads((ROOT/'exploration/persistent-01/worker-f/F06-maps.json').read_text());rng=random.Random(331519);results=[]
 for pid in [0,17]:
  m=next(x for x in maps if x['page']==pid);c,ends=parse(m['raw_joined']);assert c==m['indices'];dump('map-'+str(pid),m);r=search('real-'+str(pid),c,ends);null=[]
  for rep in range(19):
   sh=[rng.randrange(29)]
   for i in range(1,len(c)):
    if c[i]==c[i-1]:sh.append(sh[-1])
    else:v=rng.randrange(28);sh.append(v+(v>=sh[-1]))
   nr=search('null-'+str(pid)+'-'+str(rep),sh,ends);null.append(dict(rep=rep,score=nr['rows'][0]['score'],best=nr['rows'][0]['id']))
  score=r['rows'][0]['score'];row=dict(page=pid,score=score,best=r['rows'][0]['id'],null=null,tail=None if score is None else (1+sum(x['score'] is not None and x['score']>=score for x in null))/20);results.append(row);dump('summary',results);print(json.dumps(row),flush=True)
if __name__=='__main__':
 base.gate();mode=sys.argv[1]
 if mode=='pilot':dump('keys',CELLS);dump('model',lm.files);brute();control(0)
 elif mode=='controls':
  for i in range(1,4):control(i)
 elif mode=='actual':actual()
