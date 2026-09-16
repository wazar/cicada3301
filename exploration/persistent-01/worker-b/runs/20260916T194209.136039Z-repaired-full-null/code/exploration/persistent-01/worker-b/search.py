import pathlib,json,importlib.util,gzip,time,random,argparse,datetime,hashlib,zlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('old',ROOT/'exploration/overnight-01/worker-c/search.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def save(name,x):(OUT/name).write_text(json.dumps(x,indent=2)+'\n')
def load(p):return json.loads((ROOT/p).read_text())
def sig(j):return tuple(j[k] for k in ('page','route','offset','sign','periodic'))
def setup():
 rs=load('exploration/overnight-01/worker-c/routes.json');hold=set(load('exploration/persistent-01/config.json')['reserved_original_pages']);pages={p['original_page']:p['indices'] for p in load('audit/parallel-01/inputs/dataset.json')['pages'] if p['original_page'] not in hold and p['original_page']<=55}
 prior={sig(j) for j in load('exploration/overnight-01/worker-c/f-jobs.json')};jobs=[]
 for p,c in pages.items():
  if p in (49,51):continue
  for r,z in rs.items():
   for o in range(max(0,min(256,len(z['key'])-len(c)+c.count(0)+1))):
    for s in (-1,1):
     j=dict(page=p,route=r,offset=o,sign=s,periodic=False)
     if sig(j) not in prior:jobs.append(j)
 return rs,pages,jobs

def run(j,c,rs,sc):return old.decode(c,rs[j['route']]['key'][j['offset']:],j['sign'],False,sc,256)
def controls(rs,sc):
 spec=importlib.util.spec_from_file_location('fc',ROOT/'audit/f-interruption-01/check.py');fc=importlib.util.module_from_spec(spec);spec.loader.exec_module(fc)
 grid=[dict(route=r,offset=o,sign=s) for r in rs for o in (0,7,31) for s in (-1,1)];out=[]
 for n,fix in enumerate(fc.fixtures(False)[:3]):
  truth=grid[(9,43,80)[n]];key=rs[truth['route']]['key'][truth['offset']:];plain=fix['plain'];ints=set(fix['interrupt']);used=0;c=[]
  for i,p in enumerate(plain):
   if i in ints:c.append(0)
   else:c.append((p-truth['sign']*key[used])%29);used+=1
  ranks=[]
  for g in grid:
   states=run(g,c,rs,sc);ranks.append(dict(job=g,score=states[0]['score'],plain=states[0]['plain'],alternatives=states))
  ranks.sort(key=lambda x:x['score'],reverse=True);true=next(z for z in ranks if z['job']==truth)
  null=[]
  for seed in range(3):
   cc=c[:];random.Random(88201+seed).shuffle(cc);results=[dict(job=g,states=run(g,cc,rs,sc)) for g in grid];null.append(dict(seed=88201+seed,cipher=cc,all_scores=[dict(job=z['job'],score=z['states'][0]['score']) for z in results],top=max(results,key=lambda z:z['states'][0]['score'])))
  out.append(dict(truth=truth,cipher=c,plain=plain,path=sorted(ints),searched=96,truth_key_rank=1+ranks.index(true),truth_plain_rank=next((i+1 for i,z in enumerate(true['alternatives']) if z['plain']==plain),None),top_recovery=sum(a==b for a,b in zip(ranks[0]['plain'],plain))/len(plain),all_candidates=ranks,null=null))
 save('controls.json',out)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','controls','search']);ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=100);ap.add_argument('--seconds',type=int,default=850);ap.add_argument('--null-seed',type=int);a=ap.parse_args();rs,pages,jobs=setup()
 if a.mode=='prepare':save('jobs.json',jobs);save('scope.json',dict(total=len(jobs),pages=sorted(set(j['page'] for j in jobs)),counts={p:sum(j['page']==p for j in jobs) for p in pages},routes_sha256=hashlib.sha256((ROOT/'exploration/overnight-01/worker-c/routes.json').read_bytes()).hexdigest()));print(len(jobs));return
 sc=old.Score()
 if a.mode=='controls':controls(rs,sc);return
 tag=f"{a.start}-{a.count}-"+('real' if a.null_seed is None else f'null{a.null_seed}');start=time.monotonic();top=[];attempt=feasible=0
 if a.null_seed is not None:
  for p,c in pages.items():random.Random(a.null_seed+p).shuffle(c)
 with gzip.open(OUT/(tag+'-scores.jsonl.gz'),'wt') as f:
  for idx in range(a.start,min(len(jobs),a.start+a.count)):
   if time.monotonic()-start>=a.seconds or (ROOT/'exploration/persistent-01/STOP').exists() or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00'):break
   j=jobs[idx];states=run(j,pages[j['page']],rs,sc);attempt+=1
   row=dict(id=idx,**j,score=states[0]['score'] if states else None)
   if states:
    pp=states[0]['plain'];nn=len(pp);co=collections.Counter(pp);row.update(ioc_times_n=sum(v*(v-1) for v in co.values())/(nn-1) if nn>1 else None,min_distinct32=min((len(set(pp[t:t+32])) for t in range(nn-31)),default=None),zlib_ratio=len(zlib.compress(bytes(pp)))/nn,nonEnglishLM=None)
   f.write(json.dumps(row)+'\n')
   if states:
    feasible+=1
    if len(top)<20 or row['score']>top[-1]['score']:
     z=dict(**row,alternatives=states,key=rs[j['route']]['key'][j['offset']:],text=''.join(old.TOK[r] for r in states[0]['plain']))
     for state in states:
      pos=set(state['path']);used=0
      for i,p in enumerate(state['plain']):
       if i in pos:assert p==pages[j['page']][i]==0
       else:assert (p-j['sign']*z['key'][used])%29==pages[j['page']][i];used+=1
      assert used==state['used']
     top.append(z);top.sort(key=lambda x:x['score'],reverse=True);top=top[:20]
   if attempt%100==0:f.flush();save(tag+'-checkpoint.json',dict(next_index=idx+1,attempted=attempt,feasible=feasible,seconds=time.monotonic()-start,top=top))
 save(tag+'-results.json',dict(next_index=a.start+attempt,attempted=attempt,feasible=feasible,total=len(jobs),seconds=time.monotonic()-start,top=top));print(tag,attempt,feasible,time.monotonic()-start)
if __name__=='__main__':main()
