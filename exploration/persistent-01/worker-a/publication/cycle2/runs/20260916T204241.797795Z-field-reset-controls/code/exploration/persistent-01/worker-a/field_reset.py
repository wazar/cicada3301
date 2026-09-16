"""Explicit source13-edge reset comparison, preserving the original event experiment."""
import json,random,time,hashlib,argparse
import event_clock as e
s=e.s;O=e.O;ROOT=e.ROOT
MAP=ROOT/'exploration/persistent-01/worker-g/g06-source-gap-map.json'
assert hashlib.sha256(MAP.read_bytes()).hexdigest()=='d9532e234811d2b99a03ef07ad692c8438f934fbedc70749b3be3f8147340443'

def forward(p,key,sign,skips,resets):
 state=list(key);out=[]
 for i,(r,d) in enumerate(zip(p,skips)):
  if i in resets:state=list(key)
  prev=out[-1] if out and i not in resets else None
  assert 0<=d<=3 and (prev is not None or d==0)
  for j in range(d+1):
   c=(r-sign*state.pop(0))%29;state.append(r)
   if j<d:assert c==prev
   else:out.append(c)
 return out,state

def encode(p,key,sign,seed,resets):
 rng=random.Random(seed);state=list(key);c=[];sk=[]
 for i,r in enumerate(p):
  if i in resets:state=list(key)
  prev=c[-1] if c and i not in resets else None;d=0
  while True:
   v=(r-sign*state.pop(0))%29;state.append(r)
   if prev is not None and v==prev and d<3 and rng.random()<.83:d+=1;continue
   c.append(v);sk.append(d);break
 return c,sk

def beam(c,key,sign,q,resets,truth=None,initial=None,previous=None):
 states=[initial or (-999.,0.,0,'',tuple(key),b'',b'')];offset=len(states[0][5]);first=None;expanded=pruned=0
 for i,v in enumerate(c):
  edge=offset+i in resets;prev=None if edge else (c[i-1] if i else previous);nxt=[]
  for _,total,n,suffix,history,p,skips in states:
   state=tuple(key) if edge else history
   for d in range(4 if prev is not None else 1):
    r=(v+sign*state[d])%29
    if any((r-sign*state[j])%29!=prev for j in range(d)):continue
    ss,tt,nn=q.extend(suffix,total,n,r);newstate=state[d+1:]+(r,)*(d+1);nxt.append((tt/max(1,nn-3),tt,nn,ss,newstate,p+bytes([r]),skips+bytes([d])))
  expanded+=len(nxt);nxt.sort(key=lambda x:x[0],reverse=True);pruned+=max(0,len(nxt)-128);states=nxt[:128]
  if truth is not None and first is None and not any(x[5]==bytes(truth[0][:offset+i+1]) and x[6]==bytes(truth[1][:offset+i+1]) for x in states):first=offset+i
 return [dict(score=x[0],plain=list(x[5]),skips=list(x[6]),state_end=list(x[4]),key_draws=len(x[5])+sum(x[6])) for x in states[:16]],dict(expanded=expanded,pruned=pruned,first_truth_pruned=first,width=128)

def initial(c,key,sign,alt,q,resets):
 out,state=forward(alt['plain'],key,sign,alt['skips'],resets);assert out==c;suffix='';total=0.;n=0
 for r in alt['plain']:suffix,total,n=q.extend(suffix,total,n,r)
 return (total/max(1,n-3),total,n,suffix,tuple(state),bytes(alt['plain']),bytes(alt['skips']))

def search(c,cs,q,resets,cut,truth=None,truth_cell=None):
 rows=[];pre=[]
 for cell in cs:
  alts,diag=beam(c,cell['key'],cell['sign'],q,resets,truth if cell==truth_cell else None)
  for a in alts:assert forward(a['plain'],cell['key'],cell['sign'],a['skips'],resets)[0]==c
  rows.append(dict(cell=cell,score=alts[0]['score'],statistics=s.stats(alts[0]['plain']),alternatives=alts,diagnostics=diag));pa,pd=beam(c[:cut],cell['key'],cell['sign'],q,resets);pre.append(dict(cell=cell,score=pa[0]['score'],alternatives=pa,diagnostics=pd))
 rows.sort(key=lambda x:x['score'],reverse=True);pre.sort(key=lambda x:x['score'],reverse=True);chosen=pre[0];cell=chosen['cell'];init=initial(c[:cut],cell['key'],cell['sign'],chosen['alternatives'][0],q,resets);ca,cd=beam(c[cut:],cell['key'],cell['sign'],q,resets,initial=init,previous=c[cut-1])
 for a in ca:assert forward(a['plain'],cell['key'],cell['sign'],a['skips'],resets)[0]==c
 result=dict(cipher=c,resets=sorted(resets),cut=cut,key_hypotheses=len(cs),candidate_decode_calls=2*len(cs)+1,top20=rows[:20],all_scores=[{k:r[k] for k in ['cell','score','statistics']} for r in rows],prefix_top=chosen,continuation=dict(cell=cell,alternatives=ca,tail_score=q(ca[0]['plain'][cut:]),diagnostics=cd))
 if truth is not None:
  tr=next(r for r in rows if r['cell']==truth_cell);result.update(truth=truth[0],truth_skips=truth[1],true_key_rank=rows.index(tr)+1,true_path_top16=any(x['plain']==truth[0] and x['skips']==truth[1] for x in tr['alternatives']),true_key_best_errors=sum(x!=y for x,y in zip(tr['alternatives'][0]['plain'],truth[0])),searched_best_errors=sum(x!=y for x,y in zip(rows[0]['alternatives'][0]['plain'],truth[0])),continuation_errors=sum(x!=y for x,y in zip(ca[0]['plain'][cut:],truth[0][cut:])),continuation_selected_true_key=cell==truth_cell)
 return result

def shuffle_fields(c,edges,seed):
 out=[];rng=random.Random(seed);bounds=[0]+sorted(edges)+[len(c)]
 for a,b in zip(bounds,bounds[1:]):part=c[a:b];rng.shuffle(part);out.extend(part)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['controls','pilot']);a=ap.parse_args();data,pages,_,_=e.p01.setup();lookup={p['original_page']:p for p in pages};cs=json.loads((O/'event-clock/seed-bound.json').read_text());q=s.Score();mapping=json.loads(MAP.read_text());edges={pid:set(r['rune_gap'] for r in mapping if r['page']==pid and r['image']['count']==13 and 0<r['rune_gap']<len(lookup[pid]['indices'])) for pid in [3,7,17]};assert edges=={3:{16,119,122},7:{194},17:set()};cuts={3:119,7:194};stage=O/'field-reset';stage.mkdir(exist_ok=True);results=[];start=time.monotonic();raw=(ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt').read_text();plainall=[s.ABC.index(c) for c in raw if c in s.ABC]
 # Exact no-reset identity against the previously checked event decoder.
 for cell in cs:
  test=[0,1,2,0,3,1,0,2];aa,_=beam(test,cell['key'],cell['sign'],q,set());bb,_=e.beam(test,cell['key'],cell['sign'],q);assert aa==bb
 if a.mode=='pilot':assert (stage/'controls-results.json').exists()
 for ix,pid in enumerate([3,7]):
  p=lookup[pid];truthcell=cs[[2,11][ix]];plain=plainall[:len(p['indices'])]
  if a.mode=='controls':cipher,sk=encode(plain,truthcell['key'],truthcell['sign'],330120+pid,edges[pid]);assert forward(plain,truthcell['key'],truthcell['sign'],sk,edges[pid])[0]==cipher
  else:cipher=p['indices'];sk=None
  for mode in (['plant','null'] if a.mode=='controls' else ['real','null']):
   c=shuffle_fields(cipher,edges[pid],330119+pid) if mode=='null' else cipher
   for model in ['page_continuous','source13_reset']:
    reset=edges[pid] if model=='source13_reset' else set();truth=(plain,sk) if mode=='plant' else None;res=search(c,cs,q,reset,cuts[pid],truth,truthcell if truth else None);res.update(page=pid,mode=mode,model=model,source_boundaries=sorted(edges[pid]));results.append(res);s.dump(stage/(a.mode+'-results.json'),dict(results=results,elapsed=time.monotonic()-start,map_sha256=hashlib.sha256(MAP.read_bytes()).hexdigest(),no_reset_identity_cases=len(cs)));print(pid,mode,model,res['top20'][0]['score'],res.get('searched_best_errors'),res.get('continuation_errors'),flush=True)
 if a.mode=='pilot':
  old=json.loads((O/'event-clock/pilot-results.json').read_text());reuse=[r for r in old['results'] if r['original_page']==17];s.dump(stage/'page17-reused.json',dict(source='event-clock/pilot-results.json',source_sha256=hashlib.sha256((O/'event-clock/pilot-results.json').read_bytes()).hexdigest(),reason='No13-dot internal boundary; both transition models and single-field shuffle equal the original pilot. No new evaluations.',results=reuse))
 print('complete',a.mode,time.monotonic()-start)
if __name__=='__main__':main()
