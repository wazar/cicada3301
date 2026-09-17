"""Exact fixed-key segment mask enumeration; integer collision objective."""
from collections import Counter
class Unresolved(RuntimeError):pass

def segment(cipher,key,sign,periodic,*,position=0,counts=None,mask_cap=65536):
 c=list(cipher);key=list(key)
 assert sign in [-1,1] and key and all(type(x)==int and 0<=x<29 for x in c+key)
 initial=[0]*29 if counts is None else list(counts);assert len(initial)==29 and all(type(x)==int and x>=0 for x in initial)
 sites=[i for i,v in enumerate(c) if v==0];masks=1<<len(sites)
 if masks>mask_cap:raise Unresolved(f'{masks} masks exceed exact cap {mask_cap}')
 rows=[];rejected=0
 for bits in range(masks):
  at=position%len(key) if periodic else position;hist=initial.copy();plain=[];literal=[];score=0;f=0;legal=True
  for i,v in enumerate(c):
   islit=v==0 and bool((bits>>f)&1)
   if v==0:f+=1
   if islit:r=0;literal.append(i)
   else:
    if not periodic and at>=len(key):legal=False;break
    r=(v+sign*key[at])%29;at=(at+1)%len(key) if periodic else at+1
   score+=2*hist[r];hist[r]+=1;plain.append(r)
  if legal:rows.append(dict(mask=bits,plain=plain,literal_positions=literal,position=at,counts=hist,score=score))
  else:rejected+=1
 if not rows:raise Unresolved('no legal finite-key mask')
 maximum=max(r['score'] for r in rows);best=[r for r in rows if r['score']==maximum]
 groups={}
 for r in best:groups.setdefault((r['position'],tuple(r['counts'])),[]).append(r['mask'])
 if len(groups)>100000:raise Unresolved('too many exact tied future states')
 return dict(length=len(c),mask_count=masks,legal=len(rows),rejected=rejected,maximum=maximum,best_masks=[r['mask'] for r in best],future_states=[dict(position=p,counts=list(h),masks=ms) for (p,h),ms in groups.items()],rows=rows)

def splits(n,resets):
 points=sorted({0,n}|{i for i in resets if 0<i<n});return list(zip(points,points[1:]))
def denom(n,resets):return sum((b-a)*(b-a-1) for a,b in splits(n,resets))
def gridcase(c,resets,cut,cell,periodic):
 assert 0<cut<len(c);key=cell['key'];sign=cell['sign'];full=[];prefix=[]
 for a,b in splits(len(c),resets):
  x=segment(c[a:b],key,sign,periodic);full.append(dict(start=a,stop=b,result=x))
  if a<cut:prefix.append(dict(start=a,stop=min(b,cut),result=x if b<=cut else segment(c[a:cut],key,sign,periodic)))
 fullscore=sum(x['result']['maximum'] for x in full);prescore=sum(x['result']['maximum'] for x in prefix)
 # Prefix completed segments remain factored. The unfinished last one carries all tied states.
 partial=next((x for x in full if x['start']<cut<x['stop']),None);continuations=[]
 if partial:
  pr=prefix[-1]['result'];later=[x for x in full if x['start']>=partial['stop']];latermax=sum(x['result']['maximum'] for x in later)
  for st in pr['future_states']:
   tail=segment(c[cut:partial['stop']],key,sign,periodic,position=st['position'],counts=st['counts'])
   continuations.append(dict(prefix_masks=st['masks'],initial_position=st['position'],initial_counts=st['counts'],first_stop=partial['stop'],tail=tail,total=tail['maximum']+latermax))
 else:
  later=[x for x in full if x['start']>=cut];continuations.append(dict(prefix_masks=None,first_stop=cut,tail=None,total=sum(x['result']['maximum'] for x in later)))
 return dict(cell_id=cell['id'],full=full,prefix=prefix,full_maximum=fullscore,prefix_maximum=prescore,full_denominator=denom(len(c),resets),prefix_denominator=denom(cut,resets),continuation_denominator=denom(len(c),resets)-denom(cut,resets),continuations=continuations,continuation_maximum=max(x['total'] for x in continuations),prefix_complete_tie_product=__import__('math').prod(len(x['result']['best_masks']) for x in prefix),full_tie_product=__import__('math').prod(len(x['result']['best_masks']) for x in full))
