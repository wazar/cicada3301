from pathlib import Path
import json,gzip,hashlib,math,random,itertools,heapq
import numpy as np
O=Path('exploration/persistent-01/worker-p/P30');D=Path(__file__).parent;GP='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';src=Path('audit/parallel-01/reference/sources')
def parse(s):
 p=[];e=[];active=False;pos=[]
 for i,ch in enumerate(s+' '):
  if ch in GP:p.append(GP.index(ch));pos.append(i);active=True
  elif active:e.append(len(p)-1);active=False
 return p,e,pos
counts=np.zeros((30,30,30),dtype=int);bi=np.zeros((30,30),int);uni=np.zeros(30,int)
for name in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229']:
 p,ee,_=parse((src/('solved_'+name+'.txt')).read_text());a=b=29
 for i,r in enumerate(p):
  for v in ([r,29] if i in ee else [r]):counts[a,b,v]+=1;bi[b,v]+=1;uni[v]+=1;a,b=b,v
lp=np.empty((30,30,30))
for a,b,v in itertools.product(range(30),repeat=3):
 q=(uni[v]+.5)/(sum(uni)+15);q=(bi[b,v]+8*q)/(sum(bi[b])+8);q=(counts[a,b,v]+5*q)/(sum(counts[a,b])+5);lp[a,b,v]=math.log(q)
# use native nested lists to avoid NumPy scalar overhead
L=lp.tolist()
def score(p,ends):
 a=b=29;total=0.
 for i,v in enumerate(p):
  total+=L[a][b][v];a,b=b,v
  if i in ends:total+=L[a][b][29];a,b=b,29
 return total/(len(p)+len(ends))
def ringdecode(c,lits,key,sign):
 ring=list(key);head=0;p=[];used=0
 for i,v in enumerate(c):
  if i in lits:assert v==0;x=0
  else:x=(v-sign*ring[head])%29;ring[head]=x;head=(head+1)%len(ring);used+=1
  p.append(x)
 return p,used,ring[head:]+ring[:head]
keys=json.loads((O/'keys.json').read_text());old=json.loads(Path('exploration/overnight-01/worker-a/r02/keys.json').read_text())['keys'][:16];expected=[]
for k in old:
 for ph in range(len(k['key'])):
  for si in (-1,1):expected.append({'id':f"{k['id']}:{ph}:{si}",'key_id':k['id'],'phase':ph,'sign':si,'key':k['key'][ph:]+k['key'][:ph]})
assert keys==expected;K={k['id']:k for k in keys};maps=json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text());npaths=ncells=expansions=0;maxerr=0.;subsets=[];outcomes=[];snap=[]
for file in [O/'CARD.md',O/'REPORT.md',O/'keys.json',O/'tiny-controls.json',Path('exploration/persistent-01/worker-p/p30.py')]+sorted(O.glob('packet-*')):
 snap.append({'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(D/'inputs.json').write_text(json.dumps(snap,indent=2))
for ix in range(7):
 packet=json.loads((O/f'packet-{ix}.json').read_text());ends=set(packet['ends']);nullmax=[];main=None
 if ix<4:
  sp=Path(packet['source']['path']);assert sp.read_text()==packet['source']['raw'];assert hashlib.sha256(sp.read_bytes()).hexdigest()==packet['source']['sha256'];p,e,pos=parse(sp.read_text());assert p==packet['truth'] and e==packet['ends'];assert packet['truth_literal']==[i for i,v in enumerate(p) if v==0 and i%3!=1];k=K[packet['truth_id']];ring=k['key'].copy();head=0;used=0;cc=[]
  for i,v in enumerate(p):
   evt=packet['events'][i];assert evt['before']==ring[head:]+ring[:head]
   if i in packet['truth_literal']:cv=0
   else:cv=(v+k['sign']*ring[head])%29;ring[head]=v;head=(head+1)%len(ring);used+=1
   cc.append(cv);assert evt['after']==ring[head:]+ring[:head] and evt['used']==used and evt['cipher']==cv and evt['plain']==v
  assert cc==packet['cipher'];(D/f'control-{ix}-source-map.json').write_text(json.dumps({'source':str(sp),'positions':pos}))
 else:
  mp=next(m for m in maps if m['page']==[0,17,55][ix-4]);assert mp==packet['source'];assert mp['indices']==packet['cipher'];assert [w['end']-1 for w in mp['words']]==packet['ends']
 for f in sorted(O.glob(f'packet-{ix}-*.json.gz')):
  r=json.loads(gzip.decompress(f.read_bytes()));c=r['cipher'];assert r['ends']==packet['ends'];seed=r['null_seed']
  if seed is None:assert c==packet['cipher'];main=r
  else:
   j=int(f.name.split('-')[-1].split('.')[0]);assert seed==530200+100*ix+j;rg=random.Random(seed);gen=[]
   for i,v in enumerate(packet['cipher']):
    if not v:gen.append(0)
    elif not i:gen.append(rg.randrange(1,29))
    elif v==packet['cipher'][i-1]:gen.append(gen[-1])
    else:gen.append(rg.choice([a for a in range(1,29) if a!=gen[-1]]))
   assert gen==c;assert [x==0 for x in c]==[x==0 for x in packet['cipher']];assert [a==b for a,b in zip(c,c[1:])]==[a==b for a,b in zip(packet['cipher'],packet['cipher'][1:])];nullmax.append(r['maximum'])
  assert [row['id'] for row in r['cells']]==list(K);alts=[]
  for row in r['cells']:
   ncells+=1;expansions+=row['diagnostics']['expanded'];key=K[row['id']]
   for z in row['alternatives']:
    pp,u,q=ringdecode(c,set(z['literal_positions']),key['key'],key['sign']);assert pp==z['plain'] and u==z['used'] and q==z['final_queue'];err=abs(score(pp,ends)-z['score']);maxerr=max(maxerr,err);assert err<1e-12;npaths+=1;alts.append({'id':key['id'],**z})
   assert row['top_score']==row['alternatives'][0]['score'];assert all(x['score']>=y['score'] for x,y in zip(row['alternatives'],row['alternatives'][1:]))
  alts.sort(key=lambda z:-z['score']);assert alts[0]['score']==r['maximum'];ids=[];groups={}
  for a in alts:
   ident=(tuple(a['plain']),tuple(a['literal_positions']))
   if ident not in groups:groups[ident]=[];ids.append(ident)
   groups[ident].append(a)
  for g,ident in zip(r['global16'],ids[:16]):
   assert {k:v for k,v in g.items() if k!='aliases'}==groups[ident][0];assert g['aliases']==[a['id'] for a in groups[ident]]
 if ix<4:
  truthrow=next(z for z in main['cells'] if z['id']==packet['truth_id']);assert main['control']['truth_key_rank']==1+sum(z['top_score']>truthrow['top_score'] for z in main['cells']);assert main['global16'][0]['plain']==packet['truth'] and main['global16'][0]['literal_positions']==packet['truth_literal'];chosen=packet['truth_id']
 else:
  tail=(1+sum(s>=main['maximum'] for s in nullmax))/20;assert tail==json.loads((O/f'packet-{ix}-summary.json').read_text())['tail'];outcomes.append({'packet':ix,'tail':tail});chosen=main['global16'][0]['id']
 subsets.append((packet,main,next(row for row in main['cells'] if row['id']==chosen)))
 print('packet',ix,'paths',npaths,flush=True)
# Independent bounded beam: circular storage and stable heap selection, serial tie ranks.
def hb(c,ends,key,sign,truth=None):
 states=[(0.,29,29,tuple(key),0,(),())];expanded=0;pruned=None
 for i,v in enumerate(c):
  cand=[]
  for state in states:
   s,a,b,ring,h,p,lits=state
   for lit in range(2 if v==0 else 1):
    if lit:x=0;rr=ring;hh=h
    else:x=(v-sign*ring[h])%29;rr=list(ring);rr[h]=x;rr=tuple(rr);hh=(h+1)%len(rr)
    inc=L[a][b][x];aa,bb=b,x
    if i in ends:inc+=L[aa][bb][29];aa,bb=bb,29
    cand.append((s+inc,aa,bb,rr,hh,p+(x,),lits+(i,) if lit else lits))
  expanded+=len(cand);ranks=heapq.nsmallest(64,range(len(cand)),key=lambda j:(-cand[j][0],j));states=[cand[j] for j in ranks]
  if truth is not None and pruned is None and not any(st[-1]==tuple(v for v in truth if v<=i) for st in states):pruned=i
 return [{'score':s/(len(c)+len(ends)),'plain':list(p),'literal_positions':list(lits),'used':len(p)-len(lits),'final_queue':list(ring[h:]+ring[:h])} for s,a,b,ring,h,p,lits in states[:16]],{'expanded':expanded,'first_truth_pruned':pruned}
beamchecks=[]
for packet,main,row in subsets:
 key=K[row['id']];rr,diag=hb(main['cipher'],set(main['ends']),key['key'],key['sign'],packet.get('truth_literal'));assert diag==row['diagnostics']
 for a,b in zip(rr,row['alternatives']):assert all(a[k]==b[k] for k in a if k!='score');assert abs(a['score']-b['score'])<1e-12
 beamchecks.append({'packet':packet['packet'],'id':row['id'],'diagnostics':diag})
for t in json.loads((O/'tiny-controls.json').read_text()):
 z=[i for i,c in enumerate(t['cipher']) if c==0];ss=[]
 for bits in itertools.product((0,1),repeat=len(z)):
  lits={i for i,b in zip(z,bits) if b};p,u,q=ringdecode(t['cipher'],lits,t['key'],t['sign']);ss.append(score(p,set(t['ends'])))
 assert np.allclose(sorted(ss,reverse=True)[:16],t['scores'],rtol=0,atol=1e-12)
result={'pass':True,'cells':ncells,'paths':npaths,'expansions':expansions,'max_score_error':maxerr,'beam_replays':beamchecks,'tiny_cases':100,'actual':outcomes};(D/'result.json').write_text(json.dumps(result,indent=2));print(result)
