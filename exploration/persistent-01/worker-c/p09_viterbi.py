"""Exact best literal-F path for a fixed periodic key and Markov rune LM."""
import itertools,json,time,random
from p03_frozen import O,ROOT,LM,beam,dump,parse

def viterbi(c,ends,key,sign,lm,start_context=(29,29),start_used=0):
 # Safe equivalence: same key phase and last two emitted LM tokens => identical futures.
 states={(start_used%len(key),start_context):(0.,start_used,b'',())};expanded=0;merged=0;maxstates=1
 for i,v in enumerate(c):
  nxt={}
  for (_,s),(sc,u,p,path) in states.items():
   for literal in ([False,True] if v==0 else [False]):
    r=0 if literal else (v+sign*key[u%len(key)])%29;ss,w=lm.extend(s,r,i in ends);uu=u+(not literal);statekey=(uu%len(key),ss);candidate=(sc+w,uu,p+bytes([r]),path+(i,) if literal else path);expanded+=1
    if statekey in nxt:merged+=1
    if statekey not in nxt or candidate[0]>nxt[statekey][0]:nxt[statekey]=candidate
  states=nxt;maxstates=max(maxstates,len(states))
 ordered=sorted(states.values(),key=lambda x:x[0],reverse=True)
 return [dict(score=x[0]/(len(c)+len(ends)),used=x[1],plain=list(x[2]),literal_positions=list(x[3])) for x in ordered[:16]],dict(expanded=expanded,merged=merged,maxstates=maxstates,retention='one exact best path per phase/context endpoint; endpoints are NOT global top16 paths')
def exhaustive(c,ends,key,sign,lm):
 sites=[i for i,x in enumerate(c) if x==0];rows=[]
 for bits in itertools.product([0,1],repeat=len(sites)):
  path={s for s,b in zip(sites,bits) if b};u=0;p=[]
  for i,v in enumerate(c):
   if i in path:p.append(0)
   else:p.append((v+sign*key[u%len(key)])%29);u+=1
  rows.append(dict(score=lm.score(p,ends),plain=p,path=sorted(path)))
 return sorted(rows,key=lambda x:x['score'],reverse=True)
def main():
 out=O/'p09';out.mkdir(exist_ok=True);lm=LM();rng=random.Random(330109);checks=[];start=time.monotonic()
 for ix in range(100):
  n=rng.randrange(5,20);c=[rng.randrange(29) if rng.random()>.4 else 0 for _ in range(n)];ends={i for i in range(n) if rng.random()<.25}|{n-1};key=[rng.randrange(29) for _ in range(rng.randrange(1,9))];sign=rng.choice([-1,1]);a,d=viterbi(c,ends,key,sign,lm);ex=exhaustive(c,ends,key,sign,lm);assert abs(a[0]['score']-ex[0]['score'])<1e-12;checks.append(dict(case=ix,cipher=c,ends=sorted(ends),key=key,sign=sign,masks=len(ex),score=a[0]['score'],diag=d))
 dump(out/'exhaustive-controls.json',checks);rows=[]
 for case in json.loads((O/'p08/results.json').read_text()):
  if 'truth' not in case:continue
  c=case['cipher'];ends=set(case['ends']);key=case['truth_key'];split=case['split'];a,d=viterbi(c,ends,key,-1,lm);b,db=beam(c,ends,key,-1,lm,32);row=dict(id=case['id'],exact=a,exact_diag=d,beam=b,beam_diag=db,truth=case['truth'],truth_score=lm.score(case['truth'],ends),truth_path=case['truth_path'],exact_errors=sum(x!=y for x,y in zip(a[0]['plain'],case['truth'])),beam_errors=sum(x!=y for x,y in zip(b[0]['plain'],case['truth'])));rows.append(row)
 dump(out/'held-controls.json',rows)
 # Re-adjudicate all already searched real/null P03 keys without quadgram admission.
 from p03_frozen import cells
 cs=cells(16,True);results=[]
 for pid in [0,17,49,55]:
  base=json.loads((O/'allpages'/f'real-{pid}.json').read_text());c=base['cipher'];ends=set(base['ends']);leaders=[]
  for cell in cs:
   a,d=viterbi(c,ends,cell['key'],cell['sign'],lm);leaders.append(dict(id=cell['id'],score=a[0]['score'],endpoints=a,diag=d))
  leaders.sort(key=lambda x:x['score'],reverse=True);results.append(dict(page=pid,cells=len(cs),best_beam_score=base['best']['score'],best_exact_score=leaders[0]['score'],all_scores=[dict(id=x['id'],score=x['score']) for x in leaders],top=leaders[:5]));dump(out/'real-results.json',results)
 print(json.dumps(dict(exhaustive_controls=len(checks),enumerated_masks=sum(x['masks'] for x in checks),held_controls=[dict(id=x['id'],exact_errors=x['exact_errors'],beam_errors=x['beam_errors'],truth_score=x['truth_score'],exact_score=x['exact'][0]['score'],maxstates=x['exact_diag']['maxstates']) for x in rows],real=[dict(page=r['page'],beam=r['best_beam_score'],exact=r['best_exact_score']) for r in results],seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
