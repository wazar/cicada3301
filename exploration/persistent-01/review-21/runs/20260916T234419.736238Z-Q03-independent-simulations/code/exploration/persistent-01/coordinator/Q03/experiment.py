from pathlib import Path
import json,random,collections,sys,hashlib,datetime,gzip,time
R=Path(__file__).parent;B=R.parents[1];sys.path.insert(0,str(B/'worker-c'));from p03_frozen import parse
MAP=Path('exploration/persistent-01/worker-f/F06-maps.json');M=json.loads(MAP.read_text())
def gate():
 assert not(B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def codec(text,L,R,decode=False):
 L=list(L);R=list(R);out=[];n=len(L);mid=n//2
 for x in text:
  j=(L if decode else R).index(x);out.append((R if decode else L)[j]);L=L[j:]+L[:j];L.insert(mid,L.pop(1));R=R[j:]+R[:j];R=R[1:]+R[:1];R.insert(mid,R.pop(2))
 return out,L,R
def independent(text,left,right,decode=False):
 a=collections.deque(left);b=collections.deque(right);out=[];mid=len(a)//2
 for x in text:
  i=list(a if decode else b).index(x);out.append(list(b if decode else a)[i]);a.rotate(-i);v=a[1];del a[1];a.insert(mid,v);b.rotate(-i-1);v=b[2];del b[2];b.insert(mid,v)
 return out,list(a),list(b)
def stats(x):return [sum(a==b for a,b in zip(x,x[1:])),sum(a==b for a,b in zip(x,x[2:]))]
def sources():
 out=[];meta=[]
 for name in ['0_welcome','jpg107-167','p56_an_end','p57_parable']:
  f=Path('audit/parallel-01/reference/sources')/('solved_'+name+'.txt');x,e=parse(f.read_text());meta.append(dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),start=len(out),length=len(x)));out+=x
 return out,meta
def controls():
 L='HXUCZVAMDSLKPEFJRIGTWOBNYQ';r='PTLNBQDEOYSFAVZKGJRIHWXUMC';pt='WELLDONEISBETTERTHANWELLSAID';ct='OAHQHCNYNXTSZJRRHJBYHQKSOUJY';assert ''.join(codec(pt,L,r)[0])==ct;assert ''.join(codec(ct,L,r,True)[0])==pt
 z,la,ra=codec('A',L,r);assert z==['P'] and ''.join(la)=='PFJRIGTWOBNYQEHXUCZVAMDSLK' and ''.join(ra)=='VZGJRIHWXUMCPKTLNBQDEOYSFA';rng=random.Random(330302);records=[];doubles=0
 for n in (26,29):
  for rep in range(100):
   a=rng.sample(range(n),n);b=rng.sample(range(n),n);plain=[rng.randrange(n) for _ in range(80)];c=codec(plain,a,b);assert c==independent(plain,a,b);assert codec(c[0],a,b,True)[0]==plain;assert independent(c[0],a,b,True)[0]==plain
   relabel=rng.sample(range(n),n);assert codec(c[0],a,[relabel[v] for v in b],True)[0]==[relabel[v] for v in plain]
   for sym in range(n):
    pair=codec([sym,sym],a,b)[0];assert pair[0]!=pair[1];doubles+=1
   records.append(dict(n=n,left=a,right=b,plain=plain,cipher=c[0],relabel=relabel))
 with gzip.open(R/'controls.json.gz','wt') as f:json.dump(dict(status='PASS',published_fixture=True,random_cases=200,doublet_cases=doubles,records=records),f)
 print('controls PASS',len(records),doubles)
def simulate(start,end):
 src,meta=sources();lengths=[len(m['indices']) for m in M];t=time.monotonic();rows=[]
 for rep in range(start,end):
  gate();rng=random.Random(330303+rep);pages=[];total=[0,0]
  for m,n in zip(M,lengths):
   offset=rng.randrange(len(src));plain=[src[(offset+i)%len(src)] for i in range(n)];a=rng.sample(range(29),29);b=rng.sample(range(29),29);c=codec(plain,a,b)[0];ss=stats(c);total=[x+y for x,y in zip(total,ss)];pages.append(dict(page=m['page'],offset=offset,wraps=(offset+n-1)//len(src),left=a,right=b,cipher=c,stats=ss))
  rows.append(dict(rep=rep,seed=330303+rep,stats=total,pages=pages))
 with gzip.open(R/f'panels-{start}-{end}.json.gz','wt') as f:json.dump(dict(source=meta,panels=rows),f)
 print('panels',start,end,'seconds',time.monotonic()-t)
def actual():
 panels=[]
 for name in ['panels-0-20.json.gz','panels-20-500.json.gz']:
  with gzip.open(R/name,'rt') as f:panels+=json.load(f)['panels']
 assert [p['rep'] for p in panels]==list(range(500));actual=[sum(stats(m['indices'])[j] for m in M) for j in range(2)];comp=[]
 for j in range(2):
  x=[p['stats'][j] for p in panels];lo=(1+sum(v<=actual[j] for v in x))/501;hi=(1+sum(v>=actual[j] for v in x))/501;comp.append(dict(statistic=['adjacent_equality','distance2_equality'][j],actual=actual[j],minimum=min(x),maximum=max(x),mean=sum(x)/len(x),lower_rank=lo,upper_rank=hi,two_sided=min(1,2*min(lo,hi)),bonferroni2=min(1,4*min(lo,hi))))
 (R/'results.json').write_text(json.dumps(dict(panels=500,source='four fixed solved texts; contiguous circular slices',comparisons=comp,actual_pages=[dict(page=m['page'],length=len(m['indices']),stats=stats(m['indices'])) for m in M]),indent=2)+'\n');print(json.dumps(comp))
if __name__=='__main__':
 gate();mode=sys.argv[1]
 if mode=='controls':controls()
 elif mode=='simulate':simulate(int(sys.argv[2]),int(sys.argv[3]))
 elif mode=='actual':actual()
