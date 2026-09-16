"""P03 direct-rune delimiter ngram model; no inherited language scorer imports."""
import pathlib,json,re,math,collections,random,time,hashlib,argparse
O=pathlib.Path(__file__).resolve().parent;ROOT=O.parents[2]
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
TRAIN=['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229']
CHECK=['0_welcome','jpg107-167','p56_an_end','p57_parable']
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def parse(raw):
 words=re.findall('['+ABC+']+',raw);p=[];ends=set()
 for w in words:p.extend(ABC.index(x) for x in w);ends.add(len(p)-1)
 return p,ends
class LM:
 def __init__(self):
  self.c=[collections.Counter() for _ in range(3)];self.t=[collections.Counter() for _ in range(3)];self.files=[]
  for name in TRAIN:
   f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=f.read_text();self.files.append(dict(path=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
   p,ends=parse(raw);s=(29,29)
   for i,r in enumerate(p):
    for x in ([r,29] if i in ends else [r]):
     for n in range(3):ctx=s[-n:] if n else ();self.c[n][ctx+(x,)]+=1;self.t[n][ctx]+=1
     s=(s[-1],x)
  self.cache={}
 def step(self,s,x):
  key=s+(x,)
  if key not in self.cache:
   v=(self.c[0][(x,)]+.5)/(self.t[0][()]+15)
   for n,alpha in [(1,8),(2,5)]:ctx=s[-n:];v=(self.c[n][ctx+(x,)]+alpha*v)/(self.t[n][ctx]+alpha)
   self.cache[key]=math.log(v)
  return (s[-1],x),self.cache[key]
 def extend(self,s,r,end):
  s,v=self.step(s,r)
  if end:s,w=self.step(s,29);v+=w
  return s,v
 def score(self,p,ends):
  s=(29,29);v=0
  for i,r in enumerate(p):s,w=self.extend(s,r,i in ends);v+=w
  return v/(len(p)+len(ends))
def beam(c,ends,key,sign,lm,width=64,truth=None):
 # total, context, consumed key, plaintext, literal path
 states=[(0.,(29,29),0,b'',())];firstpruned=None;expanded=0
 for i,v in enumerate(c):
  nxt=[]
  for sc,s,u,p,path in states:
   for literal in ([False,True] if v==0 else [False]):
    r=0 if literal else (v+sign*key[u%len(key)])%29;ss,w=lm.extend(s,r,i in ends)
    nxt.append((sc+w,ss,u+(not literal),p+bytes([r]),path+(i,) if literal else path))
  expanded+=len(nxt);nxt.sort(key=lambda x:x[0],reverse=True);states=nxt[:width]
  if truth is not None and firstpruned is None and not any(x[4]==tuple(t for t in truth if t<=i) for x in states):firstpruned=i
 return [dict(score=x[0]/(len(c)+len(ends)),plain=list(x[3]),literal_positions=list(x[4]),used=x[2]) for x in states[:16]],dict(expanded=expanded,first_truth_pruned=firstpruned)
def cells(count=16,allphases=False):
 keys=json.loads((ROOT/'exploration/overnight-01/worker-a/r02/keys.json').read_text())['keys'][:count]
 return [dict(id=f"{k['id']}:{phase}:{sign}",key_id=k['id'],phase=phase,sign=sign,key=k['key'][phase:]+k['key'][:phase]) for k in keys for phase in (range(len(k['key'])) if allphases else [0,1]) for sign in [-1,1]]
def search(c,ends,lm,cs,truth_id=None,truth=None,width=64):
 rows=[]
 for cell in cs:
  alts,d=beam(c,ends,cell['key'],cell['sign'],lm,width,truth if cell['id']==truth_id else None)
  rows.append(dict(id=cell['id'],score=alts[0]['score'],alternatives=alts,diagnostics=d))
 rows.sort(key=lambda r:r['score'],reverse=True)
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--width',type=int,default=64);ap.add_argument('--label',default='pilot');ap.add_argument('--real-all',action='store_true');ap.add_argument('--keys',type=int,default=16);a=ap.parse_args();out=O/a.label;out.mkdir(exist_ok=True);lm=LM();cs=cells(a.keys,a.real_all);dump(out/'model.json',dict(train=TRAIN,check=CHECK,sources=lm.files,method='rune trigram interpolated Dirichlet smoothing .5 unigram,8 bigram,5 trigram; boundary token29; nats per emitted token',width=a.width,cells=cs));rng=random.Random(330103);t=time.monotonic();results=[]
 def run(label,c,ends,truth=None,truth_id=None,path=None):
  rows=search(c,ends,lm,cs,truth_id,path,a.width);top=rows[0];res=dict(label=label,n=len(c),cipher=c,ends=sorted(ends),evaluated=len(rows),best=top,score_ids=[dict(id=r['id'],score=r['score']) for r in rows],top=rows[:5])
  if truth is not None:
   tr=next(r for r in rows if r['id']==truth_id);res.update(truth=truth,truth_id=truth_id,truth_path=path,truth_score=lm.score(truth,ends),truth_key_rank=1+sum(r['score']>tr['score'] for r in rows),best_errors=sum(x!=y for x,y in zip(top['alternatives'][0]['plain'],truth)),planted_alternatives=tr['alternatives'],planted_errors=sum(x!=y for x,y in zip(tr['alternatives'][0]['plain'],truth)),truth_in_top16=any(r['plain']==truth for r in tr['alternatives']),truth_path_diagnostics=tr['diagnostics'])
  dump(out/(label+'.json'),res);results.append({k:res[k] for k in ['label','n','evaluated','truth_key_rank','best_errors','planted_errors','truth_in_top16'] if k in res}|dict(best_score=top['score'],elapsed=time.monotonic()-t));dump(out/'summary.json',results);print(json.dumps(results[-1]),flush=True)
 for ix,name in enumerate([] if a.real_all else CHECK):
  f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');plain,ends=parse(f.read_text());plant=cs[(ix*12+8)%len(cs)];key=plant['key'];u=0;c=[];path=[]
  for i,p in enumerate(plain):
   if p==0 and i%3!=1:c.append(0);path.append(i)
   else:c.append((p-plant['sign']*key[u%len(key)])%29);u+=1
  run('control-'+name,c,ends,plain,plant['id'],path)
  wrong=c.copy();rng.shuffle(wrong);run('null-'+name,wrong,ends)
 # Frozen physical discovery pages, independent of ordinary/quadgram ranking. Full-page F search.
 data=ROOT/'audit/parallel-01/inputs/dataset.json';cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());assert hashlib.sha256(data.read_bytes()).hexdigest()==cfg['dataset_sha256']
 pages={p['original_page']:p for p in json.loads(data.read_text())['pages']}
 for pid in (sorted(x for x in pages if x<=55 and x!=50 and x not in cfg['reserved_original_pages']) if a.real_all else [0,17,55]):
  assert pid not in cfg['reserved_original_pages'];p=pages[pid];parsed,ends=parse('/'.join(l['raw'] for l in p['lines']));assert parsed==p['indices'];run('real-'+str(pid),parsed,ends);c=parsed.copy();rng.shuffle(c);run('real-null-'+str(pid),c,ends)
 print(json.dumps(dict(done=True,seconds=time.monotonic()-t)))
if __name__=='__main__':main()
