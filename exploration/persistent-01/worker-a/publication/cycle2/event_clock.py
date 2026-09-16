"""Event-clock plaintext feedback; bounded rejected draws, no future material."""
import argparse,json,random,time,importlib.util,hashlib,collections
import p01
s=p01.s;O=p01.O;ROOT=p01.ROOT
SOURCES=['solved_0_welcome.txt','solved_jpg107-167.txt','solved_p56_an_end.txt','solved_p57_parable.txt']

def encode(p,key,sign,seed):
 rng=random.Random(seed);state=list(key);cipher=[];skips=[]
 for r in p:
  count=0
  while True:
   k=state.pop(0);state.append(r);c=(r-sign*k)%29
   if cipher and c==cipher[-1] and count<3 and rng.random()<.83:count+=1;continue
   cipher.append(c);skips.append(count);break
 return cipher,skips

def forward(p,key,sign,skips):
 state=collections.deque(key);out=[]
 for r,count in zip(p,skips):
  assert 0<=count<=3
  for j in range(count+1):
   k=state.popleft();state.append(r);c=(r-sign*k)%29
   if j<count:assert out and c==out[-1]
   else:out.append(c)
 return out,list(state)

def beam(c,key,sign,q,width=128,truth=None,initial=None,previous=None):
 states=[initial or (-999.,0.,0,'',tuple(key),b'',b'')];offset=len(states[0][5]);first_pruned=None;expanded=0;pruned=0
 for i,v in enumerate(c):
  prev=c[i-1] if i else previous;nxt=[]
  for _,total,n,suffix,state,p,skips in states:
   for d in range(4 if prev is not None else 1):
    r=(v+sign*state[d])%29
    if any((r-sign*state[j])%29!=prev for j in range(d)):continue
    ss,tt,nn=q.extend(suffix,total,n,r);newstate=state[d+1:]+(r,)*(d+1)
    nxt.append((tt/max(1,nn-3),tt,nn,ss,newstate,p+bytes([r]),skips+bytes([d])))
  expanded+=len(nxt);nxt.sort(key=lambda x:x[0],reverse=True);pruned+=max(0,len(nxt)-width);states=nxt[:width]
  if truth is not None and first_pruned is None and not any(x[5]==bytes(truth[0][:offset+i+1]) and x[6]==bytes(truth[1][:offset+i+1]) for x in states):first_pruned=offset+i
 alts=[dict(score=x[0],plain=list(x[5]),skips=list(x[6]),state_end=list(x[4]),key_draws=len(x[5])+sum(x[6])) for x in states[:16]]
 return alts,dict(expanded=expanded,pruned=pruned,first_truth_pruned=first_pruned,width=width)

def initial_for(c,key,sign,alt,q):
 out,state=forward(alt['plain'],key,sign,alt['skips']);assert out==c
 suffix='';total=0.;n=0
 for r in alt['plain']:suffix,total,n=q.extend(suffix,total,n,r)
 return (total/max(1,n-3),total,n,suffix,tuple(state),bytes(alt['plain']),bytes(alt['skips']))

def run_search(c,cs,q,truth=None,truth_cell=None):
 rows=[];prefix=[];cut=len(c)//2
 for cell in cs:
  target=truth if cell==truth_cell else None;alts,diag=beam(c,cell['key'],cell['sign'],q,truth=target)
  for a in alts:assert forward(a['plain'],cell['key'],cell['sign'],a['skips'])[0]==c
  rows.append(dict(cell=cell,score=alts[0]['score'],statistics=s.stats(alts[0]['plain']),alternatives=alts,diagnostics=diag))
  pa,pd=beam(c[:cut],cell['key'],cell['sign'],q);prefix.append(dict(cell=cell,score=pa[0]['score'],alternatives=pa,diagnostics=pd))
 rows.sort(key=lambda x:x['score'],reverse=True);prefix.sort(key=lambda x:x['score'],reverse=True);chosen=prefix[0];cell=chosen['cell'];init=initial_for(c[:cut],cell['key'],cell['sign'],chosen['alternatives'][0],q);ca,cd=beam(c[cut:],cell['key'],cell['sign'],q,initial=init,previous=c[cut-1])
 for a in ca:assert forward(a['plain'],cell['key'],cell['sign'],a['skips'])[0]==c
 result=dict(n=len(c),key_hypotheses=len(cs),candidate_decode_calls=2*len(cs)+1,cipher=c,top20=rows[:20],all_scores=[dict(cell=r['cell'],score=r['score'],statistics=r['statistics']) for r in rows],prefix_top=chosen,continuation=dict(cut=cut,cell=cell,alternatives=ca,diagnostics=cd,tail_score=q(ca[0]['plain'][cut:]),selection='Freeze leading first-half key/path/state, then decode suffix; suffix not used to revise prefix'))
 if truth is not None:
  true=next(x for x in rows if x['cell']==truth_cell);result.update(truth=truth[0],truth_skips=truth[1],true_key_rank=rows.index(true)+1,true_path_top16=any(x['plain']==truth[0] and x['skips']==truth[1] for x in true['alternatives']),true_plain_top16=any(x['plain']==truth[0] for x in true['alternatives']),true_key_best_errors=sum(x!=y for x,y in zip(true['alternatives'][0]['plain'],truth[0])),searched_best_errors=sum(x!=y for x,y in zip(rows[0]['alternatives'][0]['plain'],truth[0])),true_key_diagnostics=true['diagnostics'],continuation_errors=sum(x!=y for x,y in zip(ca[0]['plain'][cut:],truth[0][cut:])),continuation_selected_true_key=cell==truth_cell)
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['controls','pilot']);a=ap.parse_args();data,pages,_,_=p01.setup();keys=data['keys'][::16];assert len(keys)==16 and min(len(k['key']) for k in keys)>=4;cs=[dict(key_id=k['id'],key=k['key'],sign=sign) for k in keys for sign in [-1,1]];stage=O/'event-clock';stage.mkdir(exist_ok=True);s.dump(stage/'seed-bound.json',cs);q=s.Score();start=time.monotonic();results=[]
 if a.mode=='controls':
  path=ROOT/'liber-primus/analysis/campaign18_skip/armada2/autokey_skip.py';spec=importlib.util.spec_from_file_location('inherited_autokey',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
  for ix,name in enumerate(SOURCES):
   f=ROOT/'audit/parallel-01/reference/sources'/name;plain=[s.ABC.index(x) for x in f.read_text() if x in s.ABC];cell=cs[2*[1,5,9,13][ix]+ix%2];c,sk=encode(plain,cell['key'],cell['sign'],330117+ix);assert forward(plain,cell['key'],cell['sign'],sk)[0]==c
   for mode in ['plant','null']:
    cc=c.copy()
    if mode=='null':random.Random(330118+ix).shuffle(cc)
    result=run_search(cc,cs,q,(plain,sk) if mode=='plant' else None,cell if mode=='plant' else None);result.update(mode=mode,source=str(f.relative_to(ROOT)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),plant_cell=cell,rejected_draws=sum(sk),doublets=sum(x==y for x,y in zip(cc,cc[1:])))
    if mode=='plant':
     inherited=old.beam_decode_ptautokey(c,cell['key'],cell['sign'],beam_w=128,max_skip=3);result['inherited_true_key']=dict(score=inherited['score'],rune_count=len(inherited['plain_idx']),errors=sum(x!=y for x,y in zip(inherited['plain_idx'],plain))+abs(len(inherited['plain_idx'])-len(plain)),plain=inherited['plain_idx'],note='Unmodified inherited decoder; cumulative beam ranking differs from normalized-prefix event decoder.')
    results.append(result);s.dump(stage/(a.mode+'-results.json'),dict(results=results,elapsed=time.monotonic()-start));print(name,mode,{k:result.get(k) for k in ['true_key_rank','true_path_top16','searched_best_errors','continuation_errors','rejected_draws']},flush=True)
 else:
  assert (stage/'controls-results.json').exists()
  for page in pages:
   if page['original_page'] not in [0,17,55]:continue
   for mode in ['real','null']:
    c=page['indices'].copy()
    if mode=='null':random.Random(330119+page['original_page']).shuffle(c)
    result=run_search(c,cs,q);result.update(mode=mode,original_page=page['original_page']);results.append(result);s.dump(stage/(a.mode+'-results.json'),dict(results=results,elapsed=time.monotonic()-start));print(page['original_page'],mode,result['top20'][0]['score'],result['continuation']['tail_score'],flush=True)
 print('complete',a.mode,time.monotonic()-start,flush=True)
if __name__=='__main__':main()
