"""Exact finite-key F paths with rune LM and viable-prefix pruning."""
import collections,itertools,json,random,time,gzip,argparse
from p03_frozen import O,ROOT,LM,parse,dump

def finite(c,ends,key,sign,lm,retain=16):
 rem=[0]*(len(c)+1)
 for i in range(len(c)-1,-1,-1):rem[i]=rem[i+1]+(c[i]!=0)
 if len(key)<rem[0]:return [],dict(infeasible=True,expanded=0,maxstates=0)
 states={(0,(29,29)):[(0.,b'',())]};expanded=0;maxstates=1;infeasible=0
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list)
  for (u,s),paths in states.items():
   choices=[]
   if u<len(key):choices.append(((v+sign*key[u])%29,u+1,False))
   if v==0:choices.append((0,u,True))
   for r,uu,literal in choices:
    if len(key)-uu<rem[i+1]:infeasible+=len(paths);continue
    ss,w=lm.extend(s,r,i in ends)
    for sc,p,path in paths:nxt[(uu,ss)].append((sc+w,p+bytes([r]),path+(i,) if literal else path));expanded+=1
  states={}
  for st,paths in nxt.items():paths.sort(key=lambda x:x[0],reverse=True);states[st]=paths[:retain]
  maxstates=max(maxstates,len(states))
 ordered=sorted([(sc,u,p,path) for (u,s),paths in states.items() for sc,p,path in paths],key=lambda x:x[0],reverse=True)[:retain]
 return [dict(score=sc/(len(c)+len(ends)),used=u,plain=list(p),literal_positions=list(path)) for sc,u,p,path in ordered],dict(infeasible=False,expanded=expanded,maxstates=maxstates,infeasible_prefixes=infeasible)
def enumerate_finite(c,ends,key,sign,lm):
 sites=[i for i,v in enumerate(c) if v==0];out=[]
 for bits in itertools.product([0,1],repeat=len(sites)):
  path={i for i,b in zip(sites,bits) if b};p=[];u=0
  for i,v in enumerate(c):
   if i in path:p.append(0)
   elif u<len(key):p.append((v+sign*key[u])%29);u+=1
   else:break
  if len(p)==len(c):out.append(dict(score=lm.score(p,ends),plain=p,path=sorted(path)))
 return sorted(out,key=lambda x:x['score'],reverse=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');a=ap.parse_args();out=O/('c15-full' if a.full else 'c15');out.mkdir(exist_ok=True);lm=LM();rng=random.Random(330115);checks=[];t=time.monotonic()
 for ix in range(0 if a.full else 100):
  n=rng.randrange(5,20);c=[rng.randrange(29) if rng.random()>.45 else 0 for _ in range(n)];ends={i for i in range(n) if rng.random()<.25}|{n-1};key=[rng.randrange(29) for _ in range(rng.randrange(0,n+2))];sign=rng.choice([-1,1]);a,d=finite(c,ends,key,sign,lm);ex=enumerate_finite(c,ends,key,sign,lm);assert len(a)==min(16,len(ex));assert all(abs(x['score']-y['score'])<1e-12 for x,y in zip(a,ex));checks.append(dict(case=ix,cipher=c,ends=sorted(ends),key=key,sign=sign,valid_masks=len(ex),top16=a,diag=d))
 dump(out/'exhaustive-controls.json',checks)
 rs=json.loads((ROOT/'exploration/overnight-01/worker-c/routes.json').read_text());grid=[dict(route=r,offset=o,sign=s) for r in rs for o in [0,7,31] for s in [-1,1]];controls=[]
 for ix,name in enumerate([] if a.full else ['p56_an_end','p57_parable']):
  plain,ends=parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text());plant=grid[[17,58][ix]];key=rs[plant['route']]['key'][plant['offset']:];c=[];path=[];u=0
  for i,p in enumerate(plain):
   if p==0 and i%3!=1:c.append(0);path.append(i)
   else:c.append((p-plant['sign']*key[u])%29);u+=1
  rows=[]
  for j in grid:
   a,d=finite(c,ends,rs[j['route']]['key'][j['offset']:],j['sign'],lm);rows.append(dict(job=j,score=a[0]['score'],alternatives=a,diag=d))
  rows.sort(key=lambda x:x['score'],reverse=True);tr=next(r for r in rows if r['job']==plant);controls.append(dict(name=name,plain=plain,cipher=c,ends=sorted(ends),truth=plant,truth_path=path,truth_rank=1+rows.index(tr),top_errors=sum(x!=y for x,y in zip(plain,rows[0]['alternatives'][0]['plain'])),truth_in_top16=any(r['plain']==plain for r in tr['alternatives']),all_scores=[dict(job=r['job'],score=r['score']) for r in rows],top=rows[:5],truth_alternatives=tr['alternatives']))
 dump(out/'controls.json',controls)
 jobs=json.loads((ROOT/'exploration/persistent-01/worker-b/jobs.json').read_text());ids=list(range(len(jobs))) if a.full else sorted({i*len(jobs)//256 for i in range(256)});dump(out/'frozen-ids.json',ids);cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());ps={p['original_page']:p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages']};leaders=[];results=[]
 for null in [False,True]:
  top=[];attempts=0;expanded=0
  with gzip.open(out/('null-scores.jsonl.gz' if null else 'real-scores.jsonl.gz'),'wt') as f:
   for idx in ids:
    j=jobs[idx];assert j['page'] not in cfg['reserved_original_pages'];p=ps[j['page']];c,ends=parse('/'.join(l['raw'] for l in p['lines']));assert c==p['indices']
    if null:random.Random(92001+j['page']).shuffle(c)
    a,d=finite(c,ends,rs[j['route']]['key'][j['offset']:],j['sign'],lm);assert a;expanded+=d['expanded'];attempts+=1;r=dict(id=idx,job=j,score=a[0]['score'],diag=d);f.write(json.dumps(r)+'\n')
    if attempts%1000==0:print(json.dumps(dict(null=null,attempts=attempts,seconds=time.monotonic()-t)),flush=True)
    if len(top)<20 or r['score']>top[-1]['score']:r.update(alternatives=a,cipher=c,ends=sorted(ends));top.append(r);top.sort(key=lambda x:x['score'],reverse=True);top=top[:20]
  res=dict(null=null,attempts=attempts,path_expansions=expanded,seconds=time.monotonic()-t,top=top);results.append(res);dump(out/'results.json',results)
 print(json.dumps(dict(controls=[dict(name=r['name'],truth_rank=r['truth_rank'],top_errors=r['top_errors'],truth_in_top16=r['truth_in_top16']) for r in controls],realnull=[dict(null=r['null'],attempts=r['attempts'],path_expansions=r['path_expansions'],best=r['top'][0]['score']) for r in results],seconds=time.monotonic()-t)))
if __name__=='__main__':main()
