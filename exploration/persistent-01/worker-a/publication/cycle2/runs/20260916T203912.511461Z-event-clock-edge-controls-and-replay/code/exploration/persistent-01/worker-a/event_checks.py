"""Exact small-state arithmetic controls and clearly labeled post-pilot replay stats."""
import itertools,json,time
import event_clock as e
s=e.s;O=e.O

def exact(c,key,sign,q):
 states=[(list(key),[],[])]
 for i,v in enumerate(c):
  ns=[]
  for state,plain,path in states:
   for d in range(4 if i else 1):
    r=(v+sign*state[d])%29
    queue=list(state);ok=True
    for j in range(d+1):
     attempt=(r-sign*queue.pop(0))%29;queue.append(r)
     if j<d and attempt!=c[i-1]:ok=False;break
    if ok and attempt==v:ns.append((queue,plain+[r],path+[d]))
  states=ns
 return sorted([dict(plain=p,skips=path,score=q(p)) for state,p,path in states],key=lambda x:x['score'],reverse=True)

def main():
 q=s.Score();count=0;start=time.monotonic()
 for n in range(1,6):
  for c in itertools.product([0,1],repeat=n):
   for key in [[0,1,2,3],[1]*4,[1]*5]:
    for sign in [-1,1]:
     ex=exact(c,key,sign,q);got,diag=e.beam(list(c),key,sign,q);assert abs(ex[0]['score']-got[0]['score'])<1e-10
     for row in got:assert e.forward(row['plain'],key,sign,row['skips'])[0]==list(c)
     if len(ex)<=16:assert {(tuple(r['plain']),tuple(r['skips'])) for r in ex}=={(tuple(r['plain']),tuple(r['skips'])) for r in got}
     count+=1
 c,sk=e.encode([0,0],[1]*5,-1,5);assert c==[1,1] and sk==[0,3];assert e.forward([0,0],[1]*5,-1,sk)[0]==c
 checked=[]
 for name in ['controls','pilot']:
  results=json.loads((O/'event-clock'/f'{name}-results.json').read_text())['results']
  for result in results:
   top={json.dumps(x['cell'],sort_keys=True):x for x in result['top20']}
   for row in result['all_scores']:
    cell=row['cell'];alts,diag=e.beam(result['cipher'],cell['key'],cell['sign'],q);assert abs(alts[0]['score']-row['score'])<1e-10
    old=top.get(json.dumps(cell,sort_keys=True))
    if old:assert alts==old['alternatives']
    checked.append(dict(source_result=name,mode=result['mode'],page=result.get('original_page'),source=result.get('source'),cell=cell,score=row['score'],statistics=s.stats(alts[0]['plain'])))
 out=dict(exact_small_cases=count,forced_accept=dict(cipher=c,skips=sk),replay_cells=len(checked),elapsed=time.monotonic()-start,limitation='Original event control/pilot rows omitted the requested structural statistics. These are diagnostic replays after the pilot, not original-time measurements or new coverage; all original scores and retained alternatives reproduced. Future event sweeps persist stats in each row.',rows=checked);s.dump(O/'event-clock/checks-and-replay-stats.json',out);print(count,len(checked),time.monotonic()-start)
if __name__=='__main__':main()
