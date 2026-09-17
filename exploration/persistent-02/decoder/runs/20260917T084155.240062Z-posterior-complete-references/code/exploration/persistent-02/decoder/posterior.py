"""Exact sum-product on fixed-key literal-F path DAG; model weights, not truth probabilities."""
import math,time
NEG=float('-inf')
def add(a,b):
 if a==NEG:return b
 if b==NEG:return a
 return max(a,b)+math.log1p(math.exp(-abs(a-b)))
def lse(values):
 v=NEG
 for x in values:v=add(v,x)
 return v
def value(logp):return dict(log_probability=None if logp==NEG else logp,probability=0. if logp==NEG else math.exp(logp))
def analyze(c,key,extend,*,sign=-1,periodic=True,start=0,ends=(),context=(29,29),cuts=()):
 c=tuple(c);key=tuple(key);ends=frozenset(ends);cuts=set(cuts)|{0,len(c)}
 if not key or any(type(x)!=int or not 0<=x<29 for x in c+key):raise ValueError('invalid rune/key')
 if type(sign)!=int or sign not in [-1,1]:raise ValueError('sign')
 if type(start)!=int or start<0 or (not periodic and start>len(key)):raise ValueError('start')
 if len(context)!=2 or any(type(x)!=int or not 0<=x<=29 for x in context):raise ValueError('context')
 if any(type(i)!=int or not 0<=i<len(c) for i in ends):raise ValueError('ends')
 if any(type(i)!=int or not 0<=i<=len(c) for i in cuts):raise ValueError('cuts')
 tick=time.monotonic();initial=(start%len(key) if periodic else start,*context);forward=[{initial:0.}];edges=[];counts={initial:1};nedge=0
 for i,r in enumerate(c):
  nxt={};es=[];nc={}
  for state,score in forward[-1].items():
   pos,a,b=state;choices=[]
   if periodic or pos<len(key):choices.append(((r+sign*key[pos])%29,(pos+1)%len(key) if periodic else pos+1,False))
   if r==0:choices.append((0,pos,True))
   for emitted,pos2,lit in choices:
    ctx,w=extend((a,b),emitted,i in ends);w=float(w)
    if not math.isfinite(w):raise ValueError('finite score required')
    dest=(pos2,*ctx);nxt[dest]=add(nxt.get(dest,NEG),score+w);nc[dest]=nc.get(dest,0)+counts[state];es.append((state,dest,w,lit))
  if not nxt:raise ValueError('no legal path')
  forward.append(nxt);counts=nc;edges.append(es);nedge+=len(es)
 logz=lse(forward[-1].values());backward=[None]*(len(c)+1);backward[-1]={s:0. for s in forward[-1]}
 for i in range(len(c)-1,-1,-1):
  row={}
  for src,dest,w,lit in edges[i]:row[src]=add(row.get(src,NEG),w+backward[i+1].get(dest,NEG))
  backward[i]=row
 assert abs(backward[0][initial]-logz)<1e-8
 branches=[]
 for i,r in enumerate(c):
  if r!=0:continue
  logs=[NEG,NEG]
  for src,dest,w,lit in edges[i]:logs[int(lit)]=add(logs[int(lit)],forward[i][src]+w+backward[i+1].get(dest,NEG)-logz)
  assert abs(sum(math.exp(x) for x in logs)-1)<1e-8
  branches.append(dict(position=i,ordinary=value(logs[0]),literal=value(logs[1])))
 joins=[]
 for i in sorted(cuts):
  phases={};states=[]
  for state,alpha in forward[i].items():
   lp=alpha+backward[i].get(state,NEG)-logz;phases[state[0]]=add(phases.get(state[0],NEG),lp);states.append(dict(position=state[0],context=list(state[1:]),**value(lp)))
  assert abs(sum(math.exp(v) for v in phases.values())-1)<1e-8
  joins.append(dict(cut_after_rune_count=i,states=states,key_positions=[dict(position=p,**value(v)) for p,v in sorted(phases.items())]))
 return dict(log_partition=logz,number_of_legal_decision_paths=str(sum(counts.values())),branch_marginals=branches,joins=joins,max_live_states=max(map(len,forward)),retained_transition_edges=nedge,seconds=time.monotonic()-tick,scope='Normalized exp(local-score sum) over legal decision paths; duplicate plaintext paths distinct, no calibrated plaintext confidence. Log-domain float arithmetic; extreme marginal probabilities may underflow but log probabilities retained.')

def beam_pool(c,key,lm,*,sign=-1,periodic=True,start=0,ends=(),context=(29,29),width=64):
 # Deliberate byte/path-copy mirror of old P03 beam, retaining its entire final pool.
 states=[(0.,context,start,b'',())];ends=set(ends)
 for i,v in enumerate(c):
  nxt=[]
  for score,ctx,u,p,path in states:
   for lit in ([False,True] if v==0 else [False]):
    if not lit and not periodic and u>=len(key):continue
    r=0 if lit else (v+sign*key[u%len(key)])%29;ss,w=lm.extend(ctx,r,i in ends)
    nxt.append((score+w,ss,u+int(not lit),p+bytes([r]),path+(i,) if lit else path))
  states=sorted(nxt,key=lambda x:x[0],reverse=True)[:width]
 return [dict(total=sc,plain=list(p),literal_positions=list(path),used=u-start) for sc,ctx,u,p,path in states]
def mass(paths,logz):
 keys=[tuple(r['literal_positions']) for r in paths];assert len(keys)==len(set(keys))
 lp=lse(r['total'] for r in paths)-logz
 assert lp<1e-8
 return dict(retained_paths=len(paths),log_mass=lp,mass=math.exp(lp),lost_mass=-math.expm1(min(0.,lp)),scope='Probability mass under stated normalized decision-path weights; not confidence of correct plaintext.')
