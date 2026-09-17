import pathlib,json,gzip,hashlib,random,re,sys,time,datetime
O=pathlib.Path(__file__).resolve().parent;B=O.parent;ROOT=B.parents[1];Q=B/'coordinator/Q03';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def gate():
 assert not(B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):(O/(name+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def codec(text,left,right,inverse=False,trace=False):
 l=list(left);r=list(right);n=len(l);m=n//2;out=[];steps=[]
 # Position permutations implement hole shifting from primary prose.
 lp=[0]+list(range(2,m+1))+[1]+list(range(m+1,n));rp=[0,1]+list(range(3,m+1))+[2]+list(range(m+1,n))
 for x in text:
  oldl=l;oldr=r;idx=(l if inverse else r).index(x);y=(r if inverse else l)[idx];out.append(y)
  if trace:steps.append(dict(left=''.join(l),right=''.join(r),input=x,output=y))
  l=[oldl[(idx+j)%n] for j in lp];r=[oldr[(idx+1+j)%n] for j in rp]
 return out,l,r,steps

def stats(x):return [sum(x[i]==x[i+1] for i in range(len(x)-1)),sum(x[i]==x[i+2] for i in range(len(x)-2))]
def controls():
 gate();private=B/'private-originals/coordinator/Q03';pdf=private/'algorithm.pdf';source=json.loads((Q/'source.json').read_text());assert hashlib.sha256(pdf.read_bytes()).hexdigest()==source['sha256']
 text=(private/'algorithm.txt').read_text();left='HXUCZVAMDSLKPEFJRIGTWOBNYQ';right='PTLNBQDEOYSFAVZKGJRIHWXUMC';plain='WELLDONEISBETTERTHANWELLSAID';cipher='OAHQHCNYNXTSZJRRHJBYHQKSOUJY';c,l,r,trace=codec(plain,left,right,trace=True);assert ''.join(c)==cipher and ''.join(codec(cipher,left,right,True)[0])==plain
 rows=re.findall(r'^\s*([A-Z]{26})\s+([A-Z]{26})\s+([A-Z])\s+([A-Z])\s*$',text,re.M);assert len(rows)==len(plain)
 assert all(a['left']==b[0] and a['right']==b[1] and a['input']==b[3] and a['output']==b[2] for a,b in zip(trace,rows))
 c,l,r,_=codec('A',left,right);assert c==['P'] and ''.join(l)=='PFJRIGTWOBNYQEHXUCZVAMDSLK' and ''.join(r)=='VZGJRIHWXUMCPKTLNBQDEOYSFA'
 rng=random.Random(332100);records=[]
 for n in [26,29]:
  for rep in range(100):
   l=rng.sample(range(n),n);r=rng.sample(range(n),n);p=[rng.randrange(n) for _ in range(100)];c,ll,rr,_=codec(p,l,r);assert codec(c,l,r,True)[0]==p
   rel=rng.sample(range(n),n);cc=codec(p,[rel[v] for v in l],r)[0];assert cc==[rel[v] for v in c] and stats(cc)==stats(c)
   pp=codec(c,l,[rel[v] for v in r],True)[0];assert pp==[rel[v] for v in p]
   for v in range(n):
    pair=codec([v,v],l,r)[0];assert pair[0]!=pair[1]
   records.append(dict(n=n,case=rep,left=l,right=r,plain=p,cipher=c,relabelling=rel))
 with gzip.open(Q/'controls.json.gz','rt') as f:up=json.load(f)
 for row in up['records']:
  assert codec(row['plain'],row['left'],row['right'])[0]==row['cipher'];assert codec(row['cipher'],row['left'],row['right'],True)[0]==row['plain']
 with gzip.open(O/'control-records.json.gz','wt') as f:json.dump(records,f)
 dump('controls',dict(status='PASS',source=source,published_trace_rows=len(rows),one_step=True,random_cases=len(records),doublets=sum(x['n'] for x in records),coordinator_controls_replayed=len(up['records'])))
 print('control review PASS',flush=True)

def simulation():
 gate();maps=json.loads((B/'worker-f/F06-maps.json').read_text());cfg=json.loads((B/'config.json').read_text());assert len(maps)==45 and not(set(x['page'] for x in maps)&set(cfg['reserved_original_pages']+[50]));src=[];meta=[]
 for name in ['0_welcome','jpg107-167','p56_an_end','p57_parable']:
  f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=f.read_text();p=[ABC.index(x) for x in raw if x in ABC];meta.append(dict(path=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),start=len(src),length=len(p)));src+=p
 panels=[];checks=[];started=time.monotonic()
 for name in ['panels-0-20.json.gz','panels-20-500.json.gz']:
  with gzip.open(Q/name,'rt') as f:data=json.load(f)
  assert data['source']==meta
  for row in data['panels']:
   gate();rep=row['rep'];rng=random.Random(330303+rep);counts=[0,0];seams=0;wraps=0
   assert row['seed']==330303+rep and len(row['pages'])==45
   for m,page in zip(maps,row['pages']):
    n=len(m['indices']);offset=rng.randrange(len(src));l=rng.sample(range(29),29);r=rng.sample(range(29),29);assert(page['page'],page['offset'],page['left'],page['right'])==(m['page'],offset,l,r)
    p=[src[j%len(src)] for j in range(offset,offset+n)];c=codec(p,l,r)[0];assert c==page['cipher'];ss=stats(c);assert ss==page['stats'];assert page['wraps']==(offset+n-1)//len(src);counts=[a+b for a,b in zip(counts,ss)];wraps+=page['wraps'];seams+=sum((offset+i)%len(src) in {x['start'] for x in meta} for i in range(1,n))
   assert counts==row['stats'];panels.append(counts);checks.append(dict(rep=rep,counts=counts,source_seams=seams,wraps=wraps))
 assert len(panels)==500
 actual=[sum(stats(m['indices'])[j] for m in maps) for j in range(2)];results=json.loads((Q/'results.json').read_text());tails=[]
 for j in range(2):
  values=[x[j] for x in panels];lo=(1+sum(x<=actual[j] for x in values))/501;hi=(1+sum(x>=actual[j] for x in values))/501;calc=dict(actual=actual[j],minimum=min(values),maximum=max(values),mean=sum(values)/500,lower_rank=lo,upper_rank=hi,two_sided=min(1,2*min(lo,hi)),bonferroni2=min(1,4*min(lo,hi)))
  assert all(abs(results['comparisons'][j][k]-v)<1e-12 for k,v in calc.items());tails.append(calc)
 dump('simulation',dict(status='PASS',pages=45,panels=500,outputs_recomputed=22500,source=meta,comparisons=tails,checks=checks,seconds=time.monotonic()-started));print('simulation PASS',time.monotonic()-started,flush=True)
if __name__=='__main__':controls() if sys.argv[1]=='controls' else simulation()
