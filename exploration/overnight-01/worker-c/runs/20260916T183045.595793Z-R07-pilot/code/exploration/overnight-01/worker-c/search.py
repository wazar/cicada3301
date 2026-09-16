import pathlib,json,hashlib,math,random,gzip,heapq,time,argparse,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=pathlib.Path(__file__).resolve().parent
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'; TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
def load(p):return json.loads((ROOT/p).read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def payload():
 t=load('audit/alphanumeric-01/v1/transcription.json')['tokens']; a='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx'; b=bytes(60*a.index(x['token'][0])+a.index(x['token'][1]) for x in t)
 assert len(b)==256 and hashlib.sha256(b).hexdigest()=='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290';return b
class Score:
 def __init__(self):
  cnt=dict((a,int(b)) for a,b in (s.split() for s in (ROOT/'liber-primus/data/english_quadgrams.txt').read_text().splitlines()));n=sum(cnt.values());self.p={a:math.log10(b/n) for a,b in cnt.items()};self.floor=math.log10(.01/n)
 def add(self,t,s,n,r):
  for c in TOK[r]:
   t+=c
   if len(t)>=4:s+=self.p.get(t[-4:],self.floor);n+=1
   t=t[-3:]
  return t,s,n
 def __call__(self,p):
  t='';s=n=0
  for r in p:t,s,n=self.add(t,s,n,r)
  return s/n if n else -999

def decode(c,k,sgn,periodic,score,width=0):
 # state: score sum/count, last three transliteration chars, consumed, runes, literal positions
 if not width:
  if not periodic and len(k)<len(c):return []
  p=[(x+sgn*k[i%len(k)])%29 for i,x in enumerate(c)];return [dict(plain=p,path=[],used=len(c),score=score(p))]
 states=[('',0.,0,0,[],[])]
 for i,x in enumerate(c):
  ns=[]
  for t,s,n,j,p,path in states:
   choices=[]
   if periodic or j<len(k):choices.append(((x+sgn*k[j%len(k)])%29,j+1,path))
   if x==0:choices.append((0,j,path+[i]))
   for r,jj,pp in choices:
    tt,ss,nn=score.add(t,s,n,r);ns.append((tt,ss,nn,jj,p+[r],pp))
  states=heapq.nlargest(width,ns,key=lambda z:z[1]/z[2] if z[2] else -999)
  if not states:return []
 return [dict(plain=p,path=path,used=j,score=s/n if n else -999) for t,s,n,j,p,path in states[:16]]
def routes():
 b=payload();out={}
 for axis in ('row','column'):
  for rr in (False,True):
   for cc in (False,True):
    rs=list(range(32))[::(-1 if rr else 1)];cs=list(range(8))[::(-1 if cc else 1)]
    ix=[r*8+c for r in rs for c in cs] if axis=='row' else [r*8+c for c in cs for r in rs]
    for conv in ('mod29','reject232'):
     keep=[i for i in ix if conv=='mod29' or b[i]<232];k=[b[i]%29 for i in keep];out[f'{axis}-r{int(rr)}c{int(cc)}-{conv}']=dict(key=k,source_indices=keep,bytes=[b[i] for i in ix],length=len(k))
 return out

def controls(score):
 spec=importlib.util.spec_from_file_location('fcheck',ROOT/'audit/f-interruption-01/check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);res=[]
 for case in m.fixtures(False)[:3]:
  states=decode(case['cipher'],case['key'],-1,False,score,256);truth=case['plain'];best=states[0];corrupt=case['key'][:];corrupt[0]=(corrupt[0]+1)%29
  # exact independently declared path must reencrypt, regardless of scorer rank
  for sign in (-1,1):
   j=0;p=[]
   for i,c in enumerate(case['cipher']):
    if i in case['interrupt']:p.append(0)
    else:p.append((c+sign*case['key'][j])%29);j+=1
   rebuilt=[];j=0
   for i,r in enumerate(p):
    if i in case['interrupt']:assert r==0;rebuilt.append(0)
    else:rebuilt.append((r-sign*case['key'][j])%29);j+=1
   assert rebuilt==case['cipher']
  res.append(dict(name=case['name'],truth_rank=next((i+1 for i,s in enumerate(states) if s['plain']==truth),None),top_rune_errors=sum(a!=b for a,b in zip(best['plain'],truth)),top=best,corrupt_top=decode(case['cipher'],corrupt,-1,False,score,256)[0]))
 return res

def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['pilot','rigid','f']);ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int);a=ap.parse_args();sc=Score();rs=routes();pages=load('audit/parallel-01/inputs/dataset.json')['pages'];hold=set(load('exploration/overnight-01/config.json')['reserved_original_pages']);pages=[p for p in pages if p['original_page'] not in hold and p['original_page']<=54];pages.sort(key=lambda p:(p['original_page'] not in (49,51),p['original_page']));pd={p['original_page']:p for p in pages}
 if a.mode=='pilot':
  save(OUT/'routes.json',rs);save(OUT/'controls.json',controls(sc));jobs=[dict(page=p['original_page'],route=r,offset=0,sign=s,periodic=False) for p in pages[:2] for r in list(rs)[:2] for s in (-1,1)];width=256
 elif a.mode=='rigid':
  jobs=[dict(page=p['original_page'],route=r,offset=o,sign=s,periodic=per) for p in pages for r,k in rs.items() for per in (False,True) for o in range(min(256,len(k['key']))) if per or len(k['key'])-o>=len(p['indices']) for s in (-1,1)];width=0
 else:
  jobs=load('exploration/overnight-01/worker-c/f-jobs.json');width=256
 selected=jobs[a.start:a.stop];tag=f'{a.mode}-{a.start}-{a.stop if a.stop is not None else len(jobs)}';top=[];t=time.monotonic();count=0
 with gzip.open(OUT/(tag+'-scores.jsonl.gz'),'wt') as f:
  for idx,j in enumerate(selected,a.start):
   k=rs[j['route']]['key'];k=k[j['offset']:]+(k[:j['offset']] if j['periodic'] else []);c=pd[j['page']]['indices'];states=decode(c,k,j['sign'],j['periodic'],sc,width)
   if not states:continue
   z=dict(id=idx,**j,**states[0]);f.write(json.dumps({k:v for k,v in z.items() if k not in ('plain','path')})+'\n');count+=1
   if len(top)<20 or z['score']>top[-1]['score']:
    # independently reencryption checks authoritative rune/path arrays
    path=set(z['path']);used=0
    for i,p in enumerate(z['plain']):
     if i in path:assert p==c[i]==0
     else:assert (p-j['sign']*k[used%len(k)])%29==c[i];used+=1
    z['key']=k;z['alternatives']=states;z['text']=''.join(TOK[x] for x in z['plain']);z['status']='UNREVIEWED';top.append(z);top.sort(key=lambda x:x['score'],reverse=True);top=top[:20]
   if count%100==0:save(OUT/(tag+'-checkpoint.json'),dict(next_index=idx+1,count=count,seconds=time.monotonic()-t,top=top));print(tag,count,round(time.monotonic()-t,2),flush=True)
 save(OUT/(tag+'-results.json'),dict(completed=count,total_jobs=len(jobs),start=a.start,stop=a.stop,seconds=time.monotonic()-t,width=width,top=top));print('DONE',tag,count,time.monotonic()-t)
if __name__=='__main__':main()
