import pathlib,json,random,gzip,re,datetime,hashlib,time
D=pathlib.Path('exploration/persistent-01/worker-p/P02');rng=random.Random(130102)
def gate():
 assert not pathlib.Path('exploration/persistent-01/STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
M=[x for x in json.load(open('exploration/persistent-01/worker-f/F06-maps.json')) if x['page'] in [0,1,2,3,5,6,7,8]];assert [x['page'] for x in M]==[0,1,2,3,5,6,7,8]
seq=[[w['end']-w['start'] for w in m['words']] for m in M];pairs=[(i,j) for b in [0,4] for i in range(b,b+4) for j in range(i+1,b+4)];calls=0
# Start each exact run only at a diagonal mismatch/boundary; every possible maximum occurs at one such start.
def scan(ss,retain=False):
 global calls
 calls+=1;best=0;hits=[]
 for p,q in pairs:
  a=ss[p]
  for rev in [False,True]:
   b=ss[q][::-1] if rev else ss[q];ix={}
   for j,v in enumerate(b):ix.setdefault(v,[]).append(j)
   for i,v in enumerate(a):
    for j in ix.get(v,[]):
     if i and j and a[i-1]==b[j-1]:continue
     k=1
     while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]:k+=1
     if k>best:best=k;hits=[]
     if retain and k==best:hits.append(dict(pair=[p,q],starts=[i,j],reverse=rev,length=k))
 return best,hits
def shuffle(ss):
 pp=[rng.sample(range(len(a)),len(a)) for a in ss];return [[a[i] for i in p] for a,p in zip(ss,pp)],pp
def test(ss,n):
 best,hits=scan(ss,True);ns=[];ps=[]
 for r in range(n):
  if r%50==0:gate()
  x,p=shuffle(ss);ns.append(scan(x)[0]);ps.append(p)
 return dict(best=best,hits=hits,tail=(1+sum(v>=best for v in ns))/(n+1),null=ns,permutations=ps)
# independent tiny brute force control
for rep in range(20):
 a=[[rng.randrange(1,5) for _ in range(7)] for _ in range(8)];br=0
 for p,q in pairs:
  for b in [a[q],a[q][::-1]]:
   for i in range(7):
    for j in range(7):
     k=0
     while i+k<7 and j+k<7 and a[p][i+k]==b[j+k]:k+=1
     br=max(br,k)
 assert scan(a)[0]==br
out={};out['real']=test(seq,999);out['controls']=[]
for size in [6,10,20,min(len(seq[0]),len(seq[1]))]:
 for rev in [False,True]:
  for rep in range(10):
   gate();a,_=shuffle(seq);i=rng.randrange(len(a[0])-size+1);j=rng.randrange(len(a[1])-size+1);pattern=a[0][i:i+size];a[1][j:j+size]=pattern[::-1] if rev else pattern
   r=test(a,99);r.update(size=size,reverse=rev,rep=rep,sequences=a,planted_starts=[i,j],truth_covered=any(h['pair']==[0,1] and h['reverse']==rev and h['length']>=size and h['starts'][0]<=i<h['starts'][0]+h['length'] for h in r['hits']));out['controls'].append(r)
 print('controlsize',size,flush=True)
path=pathlib.Path('liber-primus/data/keys/armada18/mabinogion_vol1_guest_edwards_ed.txt');raw=path.read_text();words=list(re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",raw));lengths=[len(re.sub("['’]",'',w.group())) for w in words];out['prose']=[];cursor=0
for rep in range(20):
 a=[];starts=[]
 for s in seq:a.append(lengths[cursor:cursor+len(s)]);starts.append(cursor);cursor+=len(s)
 r=test(a,99);r.update(rep=rep,unit_starts=starts,sequences=a,source_char_spans=[[words[i].start(),words[i+len(s)-1].end()] for i,s in zip(starts,seq)]);out['prose'].append(r)
out['mapping']=M;out['sequences']=seq;out['prose_source']=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest());out['calls']=calls
with gzip.open(D/'evidence.json.gz','wt') as f:json.dump(out,f)
summary=dict(real={k:v for k,v in out['real'].items() if k not in ['null','permutations']},unit_counts=list(map(len,seq)),pairs=pairs,calls=calls,controls=[])
for size in [6,10,20,59]:
 for rev in [False,True]:
  c=[r for r in out['controls'] if r['size']==size and r['reverse']==rev];summary['controls'].append(dict(size=size,reverse=rev,n=len(c),truth_covered=sum(r['truth_covered'] for r in c),detected=sum(r['tail']<=.05 for r in c),tails=[r['tail'] for r in c]))
summary['prose']=dict(n=20,detected=sum(r['tail']<=.05 for r in out['prose']),maxima=[r['best'] for r in out['prose']],tails=[r['tail'] for r in out['prose']]);summary['null_range']=[min(out['real']['null']),max(out['real']['null'])]
(D/'results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
