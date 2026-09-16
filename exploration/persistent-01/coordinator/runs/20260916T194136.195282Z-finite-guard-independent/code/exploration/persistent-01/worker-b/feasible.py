import pathlib,importlib.util,heapq,itertools,json,time,gzip,collections,zlib,random
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('baseline',OUT/'search.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
def decode(c,k,sgn,periodic,score,width=256):
 assert not periodic
 suffix=[0]*(len(c)+1)
 for i in range(len(c)-1,-1,-1):suffix[i]=suffix[i+1]+(c[i]!=0)
 states=[('',0.,0,0,[],[])]
 for i,x in enumerate(c):
  ns=[]
  for t,s,n,j,p,path in states:
   choices=[]
   if j<len(k):choices.append(((x+sgn*k[j])%29,j+1,path))
   if x==0:choices.append((0,j,path+[i]))
   for r,jj,pp in choices:
    if len(k)-jj<suffix[i+1]:continue
    tt,ss,nn=score.add(t,s,n,r);ns.append((tt,ss,nn,jj,p+[r],pp))
  states=heapq.nlargest(width,ns,key=lambda z:z[1]/z[2] if z[2] else -999)
  if not states:return []
 return [dict(plain=p,path=path,used=j,score=s/n if n else -999) for t,s,n,j,p,path in states[:16]]
def exact(c,k,score):
 out=[];sites=[i for i,x in enumerate(c) if x==0]
 for bits in itertools.product((False,True),repeat=len(sites)):
  path={x for x,bit in zip(sites,bits) if bit};p=[];used=0
  for i,x in enumerate(c):
   if i in path:p.append(0)
   elif used<len(k):p.append((x-k[used])%29);used+=1
   else:break
  if len(p)==len(c):out.append(dict(plain=p,path=sorted(path),used=used,score=score(p)))
 return out
def controls():
 sc=b.old.Score();count=0
 for n in range(1,7):
  for cc in itertools.product((0,1),repeat=n):
   for length in range(n+1):
    k=[(3*i+7)%29 for i in range(length)];ex=exact(cc,k,sc);got=decode(cc,k,-1,False,sc,256);count+=1
    assert bool(ex)==bool(got)
    if got:assert abs(max(x['score'] for x in ex)-got[0]['score'])<1e-10
    if len(ex)<=16:assert {(tuple(x['path']),tuple(x['plain'])) for x in ex}=={(tuple(x['path']),tuple(x['plain'])) for x in got}
 class Hostile:
  def add(self,t,s,n,r):return '',s+(100 if r!=0 else 0),n+1
 c=[0,1];k=[1];old=b.old.decode(c,k,-1,False,Hostile(),1);new=decode(c,k,-1,False,Hostile(),1);assert not old and new
 b.save('feasible-controls.json',dict(exhaustive_cases=count,width=256,hostile_old=old,hostile_new=new))
def main():
 controls();rs,pages,jobs=b.setup();sc=b.old.Score();ids=set()
 for f in OUT.glob('*-scores.jsonl.gz'):
  if f.name.startswith('feasible'):continue
  for line in gzip.open(f,'rt'):
   x=json.loads(line)
   if x['score'] is None:ids.add(x['id'])
 b.save('feasible-ids.json',sorted(ids))
 for seed in (None,92001):
  pg={p:c[:] for p,c in pages.items()}
  if seed is not None:
   for p,c in pg.items():random.Random(seed+p).shuffle(c)
  tag='feasible-'+('real' if seed is None else 'null92001');top=[];start=time.monotonic()
  with gzip.open(OUT/(tag+'-scores.jsonl.gz'),'wt') as f:
   for idx in sorted(ids):
    j=jobs[idx];key=rs[j['route']]['key'][j['offset']:];states=decode(pg[j['page']],key,j['sign'],False,sc);assert states
    pp=states[0]['plain'];nn=len(pp);co=collections.Counter(pp);row=dict(id=idx,**j,score=states[0]['score'],ioc_times_n=sum(v*(v-1) for v in co.values())/(nn-1),min_distinct32=min((len(set(pp[t:t+32])) for t in range(nn-31)),default=None),zlib_ratio=len(zlib.compress(bytes(pp)))/nn,nonEnglishLM=None);f.write(json.dumps(row)+'\n')
    if len(top)<20 or row['score']>top[-1]['score']:
     top.append(dict(**row,key=key,alternatives=states,text=''.join(b.old.TOK[r] for r in pp)));top.sort(key=lambda x:x['score'],reverse=True);top=top[:20]
  b.save(tag+'-results.json',dict(attempted=len(ids),seconds=time.monotonic()-start,top=top))
 print('DONE',len(ids))
if __name__=='__main__':main()
