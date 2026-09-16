"""Exact k-best periodic F paths, suffix2/phase sufficient state; frozen LM."""
import json,itertools,random,time,collections
from p03_frozen import O,ROOT,LM,beam,dump,parse,cells
from p09_viterbi import exhaustive

def kbest(c,ends,key,sign,lm,retain=16,start_context=(29,29),start_used=0):
 states={(start_used%len(key),start_context):[(0.,start_used,b'',())]};expanded=0;pruned=0;maxstates=1;maxpaths=1
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list)
  for (_,s),paths in states.items():
   for literal in ([False,True] if v==0 else [False]):
    # Same phase/context means same emittedrune and scoreincrement for all histories.
    r=0 if literal else (v+sign*key[paths[0][1]%len(key)])%29;ss,w=lm.extend(s,r,i in ends)
    for sc,u,p,path in paths:
     uu=u+(not literal);nxt[(uu%len(key),ss)].append((sc+w,uu,p+bytes([r]),path+(i,) if literal else path));expanded+=1
  states={}
  for state,paths in nxt.items():
   paths.sort(key=lambda x:x[0],reverse=True);pruned+=max(0,len(paths)-retain);states[state]=paths[:retain]
  maxstates=max(maxstates,len(states));maxpaths=max(maxpaths,sum(map(len,states.values())))
 ordered=sorted(itertools.chain.from_iterable(states.values()),key=lambda x:x[0],reverse=True)[:retain]
 return [dict(score=x[0]/(len(c)+len(ends)),used=x[1],plain=list(x[2]),literal_positions=list(x[3])) for x in ordered],dict(expanded=expanded,dominated_paths_discarded=pruned,maxstates=maxstates,maxpaths=maxpaths,retain=retain,exact='global topk path scores; scoreties may select any tied path')
def main():
 out=O/'p10';out.mkdir(exist_ok=True);lm=LM();rng=random.Random(330110);checks=[];t=time.monotonic()
 for ix in range(100):
  n=rng.randrange(5,20);c=[rng.randrange(29) if rng.random()>.4 else 0 for _ in range(n)];ends={i for i in range(n) if rng.random()<.25}|{n-1};key=[rng.randrange(29) for _ in range(rng.randrange(1,9))];sign=rng.choice([-1,1]);a,d=kbest(c,ends,key,sign,lm);ex=exhaustive(c,ends,key,sign,lm);assert len(a)==min(16,len(ex));assert max(abs(x['score']-y['score']) for x,y in zip(a,ex))<1e-12;checks.append(dict(case=ix,cipher=c,ends=sorted(ends),key=key,sign=sign,masks=len(ex),alternatives=a,exhaustive_top16=ex[:16],diag=d))
 dump(out/'exhaustive-controls.json',checks)
 # New frozen contiguous clue tranche selected by ID, not decoding scores.
 cs=[x for x in cells(32,True) if int(x['key_id'].split(':')[1])>=16];dump(out/'cells.json',cs)
 cases=[]
 for src in sorted((O/'allpages').glob('real-*.json')):
  if src.name.startswith('real-null-'):continue
  base=json.loads(src.read_text());c=base['cipher'];ends=set(base['ends']);cases.append((src.stem,c,ends));sh=c.copy();rng.shuffle(sh);cases.append((src.stem+'-null',sh,ends))
 summaries=[]
 for label,c,ends in cases:
  rows=[]
  for cell in cs:
   a,d=kbest(c,ends,cell['key'],cell['sign'],lm);b,db=beam(c,ends,cell['key'],cell['sign'],lm,64);rows.append(dict(id=cell['id'],score=a[0]['score'],beam_score=b[0]['score'],gain=a[0]['score']-b[0]['score'],exact=a,beam=b,diag=d,beam_diag=db))
  rows.sort(key=lambda x:x['score'],reverse=True);res=dict(id=label,cipher=c,ends=sorted(ends),all_scores=[{k:r[k] for k in ['id','score','beam_score','gain']} for r in rows],top=rows[:5],improved=[r for r in rows if r['gain']>1e-12],key_searches=len(cs),path_expansions=sum(r['diag']['expanded'] for r in rows),beam_expansions=sum(r['beam_diag']['expanded'] for r in rows));dump(out/(label+'.json'),res);summary=dict(id=label,keys=len(cs),best=rows[0]['score'],best_beam=max(r['beam_score'] for r in rows),improved=len(res['improved']),maxgain=max(r['gain'] for r in rows),path_expansions=res['path_expansions'],elapsed=time.monotonic()-t);summaries.append(summary);dump(out/'summary.json',summaries);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
