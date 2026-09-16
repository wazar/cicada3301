"""Finite R05 relationships and R06 invertible source-line routes."""
import argparse,gzip,itertools,json,math,time
import numpy as np
from search import ROOT,OWNER,ABC,Score,seqs,dump,record,txt
def routes(page):
 n=len(page['indices']);lines=[list(range(l['rune_start'],l['rune_end'])) for l in page['lines']];assert sum(lines,[])==list(range(n))
 out={'normal':list(range(n)),'reverse':list(range(n-1,-1,-1)),'reverse_lines':sum(lines[::-1],[]),'reverse_within_lines':sum([l[::-1] for l in lines],[]),'boustrophedon':sum([l[::-1] if i%2 else l for i,l in enumerate(lines)],[])}
 for perm in out.values():assert sorted(perm)==list(range(n))
 return out
def methods(n):
 seq=seqs(max(n+2,100));keys={'DIVINITY':[23,10,1,10,9,10,16,26],'FIRFUMFERENFE':[0,10,4,0,1,19,0,18,4,18,9,0,18],'primes':seq['primes'].tolist(),'prime_minus_one':seq['prime_minus_one'].tolist()};return keys
def r06_matrix(c,page,score):
 top=[];rows=[];keys=methods(len(c))
 for route,perm in routes(page).items():
  arr=np.array(c)[perm]
  for a in range(1,29):
   for b in range(29):
    p=(a*arr+b)%29;v=score.exact(p);meta={'route':route,'a':a,'b':b,'method':'affine','id':f'{route}:affine:{a}:{b}'};rows.append([meta['id'],v])
    if len(top)<20 or v>top[-1]['score']:top.append({**meta,'score':v,'rune_indices':p.tolist(),'transliteration':txt(p),'route_to_original':perm});top.sort(key=lambda r:r['score'],reverse=True);top=top[:20]
  for name,key in keys.items():
   for sign in [-1,1]:
    p=(arr+sign*np.array([key[i%len(key)] for i in range(len(c))]))%29;v=score.exact(p);meta={'route':route,'key':key[:len(c)],'sign':sign,'offset':0,'reset':'routed page start','method':name,'id':f'{route}:{name}:{sign}'};rows.append([meta['id'],v])
    if len(top)<20 or v>top[-1]['score']:top.append({**meta,'score':v,'rune_indices':p.tolist(),'transliteration':txt(p),'route_to_original':perm});top.sort(key=lambda r:r['score'],reverse=True);top=top[:20]
 return rows,top
def align(a,b,offset,reset):
 pieces=[]
 pairs=[(list(range(len(a['indices']))),list(range(len(b['indices']))))] if reset=='page' else [(list(range(x['rune_start'],x['rune_end'])),list(range(y['rune_start'],y['rune_end']))) for x,y in zip(a['lines'],b['lines'])]
 for x,y in pairs:
  lo=max(0,-offset);hi=min(len(x),len(y)-offset)
  if hi>lo:pieces.append((x[lo:hi],y[lo+offset:hi+offset]))
 return pieces
def metric(diff):
 n=len(diff);counts=np.bincount(diff,minlength=29);collision=float(np.sum(counts*(counts-1))/max(1,n*(n-1)));big=diff[:-1]*29+diff[1:];repeats=len(big)-len(set(big.tolist()));return collision,repeats,int(counts.max())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['r05','r06']);ap.add_argument('--seconds',type=int,default=820);a=ap.parse_args();start=time.monotonic();cfg=json.loads((ROOT/'exploration/overnight-01/config.json').read_text());pages=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page'] not in cfg['reserved_original_pages']];lane=OWNER/a.mode;lane.mkdir(exist_ok=True);statepath=lane/'checkpoint.json';state=json.loads(statepath.read_text()) if statepath.exists() else {'cursor':0,'trials':0,'top':[]};score=Score()
 if a.mode=='r06':
  # One synthetic positive: full exact real search over routes,affines,recipes.
  source=(ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt').read_text();plain=[ABC.index(ch) for ch in source if ch in ABC];fake={'indices':plain,'lines':[{'rune_start':0,'rune_end':len(plain)}]};cipher=[((v-11)*pow(7,-1,29))%29 for v in plain[::-1]];rows,top=r06_matrix(cipher,fake,score);truth=score.exact(plain);dump(lane/'positive_control.json',{'truth_rank':1+sum(v>truth+1e-12 for _,v in rows),'recovered_top20':any(r['rune_indices']==plain for r in top),'top20':top,'source':'solved_0_welcome; reversed and inverse affine7,11'})
  for idx in range(state['cursor'],len(pages)):
   p=pages[idx];out=[]
   for control in [False,True]:
    c=np.random.default_rng(330106+p['original_page']).permutation(p['indices']).tolist() if control else p['indices'];rows,top=r06_matrix(c,p,score);state['trials']+=len(rows)
    for r in top:
     r.update(page=p['original_page'],control=control,status='UNREVIEWED',source_char_positions=p['source_char_positions'],source_delimiters=p['non_rune_tokens']);arr=np.array(c)[r['route_to_original']]
     if r['method']=='affine':assert all((int(v)-r['b'])*pow(r['a'],-1,29)%29==arr[i] for i,v in enumerate(r['rune_indices']))
     else:assert all((v-r['sign']*r['key'][i%len(r['key'])])%29==arr[i] for i,v in enumerate(r['rune_indices']))
    with gzip.open(lane/f'cell-{idx:03}-{int(control)}.json.gz','wt') as f:json.dump({'page':p['original_page'],'control':control,'scores':rows,'top20':top},f)
    if not control:out=top
   state['top']+=out;state['top'].sort(key=lambda r:r['score'],reverse=True);state['top']=state['top'][:20];state.update(cursor=idx+1);dump(statepath,state);print({'mode':a.mode,'cursor':idx+1,'trials':state['trials']},flush=True)
   if time.monotonic()-start>a.seconds:break
 else:
  # Frozen source-defined phrases split only at punctuation/dashes; first8 length8..24.
  source=(ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt').read_text();raw=[];buf=[]
  for ch in source:
   if ch in ABC:buf.append(ABC.index(ch))
   elif ch in './\n':
    if 8<=len(buf)<=24:raw.append(buf)
    buf=[]
  if 8<=len(buf)<=24:raw.append(buf)
  cribs=raw[:8];assert cribs;dump(lane/'cribs.json',{'source':'audit/parallel-01/reference/sources/solved_0_welcome.txt','rule':'first up to8 source punctuation/newline delimited phrases with8..24runes; hyphen retained as word boundary, not combining digraphs','cribs':[{'indices':x,'transliteration':txt(x)} for x in cribs]})
  pairs=list(itertools.combinations(pages,2))
  for idx in range(state['cursor'],len(pairs)):
   aa,bb=pairs[idx];ca=np.array(aa['indices']);cb=np.array(bb['indices']);ra=np.random.default_rng(330105+aa['original_page']).permutation(ca);rb=np.random.default_rng(330105+bb['original_page']).permutation(cb);records=[];local=[]
   for reset in ['page','line_ordinal']:
    for off in range(-16,17):
     pieces=align(aa,bb,off,reset)
     if not pieces:continue
     ai=sum([x for x,y in pieces],[]);bi=sum([y for x,y in pieces],[]);diff=(cb[bi]-ca[ai])%29;null=(rb[bi]-ra[ai])%29;stat=metric(diff);ns=metric(null);boundarya={t['rune_gap'] for t in aa['non_rune_tokens'] if t['character'] in '-.'};boundaryb={t['rune_gap'] for t in bb['non_rune_tokens'] if t['character'] in '-.'};boundary=sum(x in boundarya and y in boundaryb for x,y in zip(ai,bi))/len(ai);id=f'{aa["original_page"]}:{bb["original_page"]}:{reset}:{off}';bestcrib=None
     for ci,crib in enumerate(cribs):
      if len(crib)>len(pieces[0][0]):continue
      for direction in [-1,1]:
       predicted=(np.array(crib)+direction*diff[:len(crib)])%29;v=score.exact(predicted)
       if bestcrib is None or v>bestcrib['score']:bestcrib={'crib_id':ci,'crib_side':'A' if direction==1 else 'B','predicted_side':'B' if direction==1 else 'A','predicted_indices':predicted.tolist(),'transliteration':txt(predicted),'score':v,'noncrib_continuation':'None: key is known only within the assumed crib, so no prediction outside that interval is justified.'}
     rank=(stat[0]-1/29)*math.sqrt(len(ai));records.append([id,len(ai),*stat,*ns,boundary,bestcrib['score'] if bestcrib else None]);state['trials']+=1;meta={'id':id,'pages':[aa['original_page'],bb['original_page']],'offset':off,'reset':reset,'rank_collision_excess_sqrtN':rank,'statistics':{'collision':stat[0],'repeated_bigram_count':stat[1],'max_difference_count':stat[2],'matched_random':ns,'delimiter_coincidence':boundary},'positions_a':ai,'positions_b':bi,'difference_indices':diff.tolist(),'difference_transliteration':txt(diff),'best_crib_implication':bestcrib,'status':'UNREVIEWED','model':'same-sign additive shared key cancels; diff=C_B-C_A=P_B-P_A. Reverse direction negates difference; signs of underlying shared key cancel identically.'};local.append(meta)
   with gzip.open(lane/f'pair-{idx:04}.json.gz','wt') as f:json.dump(records,f)
   state['top']+=local;state['top'].sort(key=lambda r:r['rank_collision_excess_sqrtN'],reverse=True);state['top']=state['top'][:20];state.update(cursor=idx+1);dump(statepath,state)
   if idx%50==0:print({'mode':a.mode,'cursor':idx+1,'trials':state['trials']},flush=True)
   if time.monotonic()-start>a.seconds:break
 dump(lane/'top_candidates.json',state['top'])
if __name__=='__main__':main()
