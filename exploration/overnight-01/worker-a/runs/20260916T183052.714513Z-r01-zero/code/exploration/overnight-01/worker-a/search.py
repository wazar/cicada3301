"""OVERNIGHT A bounded real-page search. No import-time writes."""
import argparse,collections,gzip,hashlib,importlib.util,json,math,pathlib,random,time,zlib
ROOT=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).resolve().parent
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
def load(p):return json.loads((ROOT/p).read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
class Score:
 def __init__(self):
  counts=dict((g,int(n)) for g,n in (x.split() for x in (ROOT/'liber-primus/data/english_quadgrams.txt').read_text().splitlines()));total=sum(counts.values());self.d={g:math.log10(n/total) for g,n in counts.items()};self.floor=math.log10(.01/total)
 def extend(self,s,total,n,p):
  a=TOK[p];joined=s+a
  for i in range(max(0,len(s)-3),len(joined)-3):total+=self.d.get(joined[i:i+4],self.floor)
  return joined[-3:],total,n+len(a)
 def __call__(self,p):
  s=''.join(TOK[x] for x in p);return sum(self.d.get(s[i:i+4],self.floor) for i in range(len(s)-3))/max(1,len(s)-3)
def fbeam(c,k,sign,q,width=256,retain=16):
 # state=(normalised score, cumulative score, latin length, suffix, used, plaintext bytes, literal sites)
 states=[(-999.,0.,0,'',0,b'',())];pruned=0;ties=0
 for i,v in enumerate(c):
  nxt=[]
  for _,sc,n,s,u,p,path in states:
   for literal in ((False,True) if v==0 else (False,)):
    r=0 if literal else (v+sign*k[u])%29
    ss,ns,nn=q.extend(s,sc,n,r);nxt.append((ns/max(1,nn-3),ns,nn,ss,u+(not literal),p+bytes([r]),path+(i,) if literal else path))
  nxt.sort(key=lambda x:x[0],reverse=True)
  if len(nxt)>width:pruned+=len(nxt)-width;ties+=sum(x[0]==nxt[width-1][0] for x in nxt[width:])
  states=nxt[:width]
 return [dict(score=x[0],plain=list(x[5]),literal_positions=list(x[6]),used=x[4]) for x in states[:retain]],dict(pruned_states=pruned,cutoff_ties_discarded=ties,width=width)
def stats(p):
 cnt=collections.Counter(p);n=len(p)
 return dict(ioc_times_n=sum(v*(v-1) for v in cnt.values())/max(1,n-1),min_distinct_32=min((len(set(p[i:i+32])) for i in range(max(1,n-31))),default=0),zlib_ratio=len(zlib.compress(bytes(p)))/max(1,n),nonenglish_lm=None)
def render(p,page):
 raw='/'.join(x['raw'] for x in page.get('lines',[]));it=iter(p)
 return ''.join(TOK[next(it)] if x in ABC else x for x in raw) if raw else ''.join(TOK[x] for x in p)
def pages():
 cfg=load('exploration/overnight-01/config.json');path=ROOT/'audit/parallel-01/inputs/dataset.json';assert hashlib.sha256(path.read_bytes()).hexdigest()==cfg['dataset_sha256']
 ps=load('audit/parallel-01/inputs/dataset.json')['pages'];ps=[p for p in ps if p['original_page'] not in cfg['reserved_original_pages'] and p['original_page']<=54];assert all(p['rune_count']==len(p['indices']) for p in ps);return ps

def controls(q,keys):
 spec=importlib.util.spec_from_file_location('fcheck',ROOT/'audit/f-interruption-01/check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);refs=m.reference_cases();result=[]
 # Exact arithmetic reference checks plus actual 8-hypothesis selection on one full solved fixture.
 for ref in refs:
  for row in ref['trace']:
   assert row['cipher']==(0 if row['action']=='literal_F' else (row['plain']+ref['key'][row['key_before']])%29)
 ref=refs[0];c=[r['cipher'] for r in ref['trace']];out=[]
 for name,k in keys.items():
  for sign in [-1,1]:
   alts,diag=fbeam(c,k,sign,q);out.append(dict(recipe=name,sign=sign,score=alts[0]['score'],errors=sum(a!=b for a,b in zip(alts[0]['plain'],ref['plain'])),truth_in_top16=any(a['plain']==ref['plain'] for a in alts),alternatives=alts,diagnostics=diag))
 out.sort(key=lambda x:x['score'],reverse=True);plant=next(x for x in out if x['recipe']=='DIVINITY' and x['sign']==-1)
 corrupt=keys['DIVINITY'].copy();corrupt[0]=(corrupt[0]+1)%29;ca,cd=fbeam(c,corrupt,-1,q)
 return dict(reference_arithmetic=[dict(name=r['name'],length=r['length'],exact=True) for r in refs],selection=out,truth_recipe_rank=1+sum(x['score']>plant['score'] for x in out),corrupted_first_key=dict(score=ca[0]['score'],errors=sum(a!=b for a,b in zip(ca[0]['plain'],ref['plain']))))
def recipes():
 k=load('audit/experiment-01/keys.json');assert k['DIVINITY'][:8]==[23,10,1,10,9,10,16,26]
 assert k['FIRFUMFERENFE'][:13]==[0,10,4,0,1,19,0,18,4,18,9,0,18]
 assert k['PRIMES'][:5]==[2,3,5,7,11] and k['TOTIENTS'][:5]==[1,2,4,6,10]
 return k

def main():
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['r01zero','r01rigid','r01f','controls']);ap.add_argument('--seconds',type=int,default=780);a=ap.parse_args();t=time.monotonic();q=Score();ps=pages();keys=recipes();stage=O/a.stage;stage.mkdir(exist_ok=True)
 if a.stage=='controls':dump(stage/'controls.json',controls(q,keys));print('controls complete');return
 cells=[]
 if a.stage=='r01zero':
  for mode in ['literal_f','ordinary']:
   for name in keys:
    for sign in [-1,1]:
     for p in ps:cells.append((mode,name,sign,0,p['original_page']))
 elif a.stage=='r01rigid':
  for name in keys:
   for off in range(8 if name=='DIVINITY' else 13 if name=='FIRFUMFERENFE' else 128):
    for sign in [-1,1]:
     for p in ps:cells.append(('ordinary',name,sign,off,p['original_page']))
  for aa in range(1,29):
   for b in range(29):
    for p in ps:cells.append(('affine',str(aa),b,0,p['original_page']))
 elif a.stage=='r01f':
  for name in keys:
   for off in range(1,8 if name=='DIVINITY' else 13 if name=='FIRFUMFERENFE' else 128):
    for sign in [-1,1]:
     for p in ps:cells.append(('literal_f',name,sign,off,p['original_page']))
 cp=stage/'checkpoint.json';state=json.loads(cp.read_text()) if cp.exists() else {'cursor':0,'top':[]};start=state['cursor'];top=state['top'];lookup={p['original_page']:p for p in ps};outname=stage/f'scores-{start:06d}.jsonl.gz'
 with gzip.open(outname,'wt') as f:
  for ix in range(start,len(cells)):
   mode,name,sign,off,pid=cells[ix];page=lookup[pid];c=page['indices'];key=keys[name][off:] if mode!='affine' else None
   if mode=='literal_f':alts,diag=fbeam(c,key,sign,q);p=alts[0]['plain'];score=alts[0]['score']
   else:p=[(int(name)*v+sign)%29 for v in c] if mode=='affine' else [(v+sign*key[i])%29 for i,v in enumerate(c)];score=q(p);alts=[];diag={}
   r=dict(id=f'{a.stage}:{ix}',mode=mode,recipe=name,sign=sign,offset=off,original_page=pid,n=len(c),score=score,statistics=stats(p));f.write(json.dumps(r)+'\n')
   if len(top)<20 or score>top[-1]['score']:
    r.update(plain=p,transliteration=render(p,page),key=key[:len(c)] if key else None,alternatives=alts,diagnostics=diag,status='UNREVIEWED');top.append(r);top.sort(key=lambda x:x['score'],reverse=True);top=top[:20]
   state=dict(cursor=ix+1,total=len(cells),top=top,stage=a.stage,seconds_this_batch=time.monotonic()-t)
   if (ix+1)%20==0:dump(cp,state);f.flush();print(json.dumps(dict(stage=a.stage,cursor=ix+1,total=len(cells),seconds=round(time.monotonic()-t,2),best=top[0]['score'])),flush=True)
   if time.monotonic()-t>a.seconds:break
 dump(cp,state);dump(stage/'top20.json',top);print(json.dumps(dict(stage=a.stage,cursor=state['cursor'],total=len(cells),elapsed=time.monotonic()-t)),flush=True)
if __name__=='__main__':main()
