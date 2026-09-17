import pathlib,sys,importlib.util,json,gzip,random,math,hashlib
from oracle import forward,inverse
R=pathlib.Path(__file__).parent;P=R.parent/'worker-p';Q=P/'P15';sys.path.insert(0,str(P))
import p15 as s
load=lambda p:json.load(gzip.open(p,'rt'))
(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in [P/'p15.py',Q/'CARD.md']+sorted(Q.glob('*.gz')):
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
def emit(ctx,p,end):
 score=0.
 for x in [p,29] if end else [p]:
  v=(s.lm.c[0][(x,)]+.5)/(s.lm.t[0][()]+15)
  v=(s.lm.c[1][ctx[-1:]+(x,)]+8*v)/(s.lm.t[1][ctx[-1:]]+8)
  v=(s.lm.c[2][ctx+(x,)]+5*v)/(s.lm.t[2][ctx]+5)
  score+=math.log(v);ctx=(ctx[-1],x)
 return ctx,score
trans=[]
for ix in range(100):
 rng=random.Random(62050+ix);key=[rng.randrange(29) for _ in range(ix%10)];prev=[None,0,7,28][ix%4];start=ix%(len(key)+1)
 for c in range(29):
  ref=inverse(c,prev,key,start);got,diag=s.transitions(c,prev,start,key)
  ref=sorted(ref,key=lambda e:(e['plain'],e['after']));got.sort(key=lambda e:e[:2]);assert len(ref)==len(got)
  for a,b in zip(ref,got):
   assert (a['plain'],a['after'],len(a['repeated']),len(a['invalid']))==b[:4];assert abs(math.log(float(a['prob']))-b[4])<1e-12
  trans.append({'case':ix,'cipher':c,'key':key,'previous':prev,'start':start,'paths':len(got)})
# Exhaustive forward event trees over candidate plaintext, no production inverse/DP reuse.
cases=[]
for ix in range(60):
 rng=random.Random(62150+ix);key=[rng.randrange(29) for _ in range(6)];c=[rng.randrange(29) for _ in range(3)];ends={0,2};paths=[];stack=[(0,0,(29,29),0.,[],[])]
 while stack:
  i,j,ctx,score,plain,accepts=stack.pop()
  if i==len(c):paths.append((score,plain,accepts));continue
  for p in range(29):
   for e in forward(p,c[i-1] if i else None,key,j):
    if e['output']!=c[i]:continue
    cc,w=emit(ctx,p,i in ends);stack.append((i+1,e['after'],cc,score+w+math.log(float(e['prob'])),plain+[p],accepts+[e['after']-1]))
 paths.sort(reverse=True,key=lambda e:e[0]);got=s.decode(c,ends,{'key':key},16)
 assert len(got['alternatives'])==min(16,len(paths))
 for a,b in zip(got['alternatives'],paths):assert abs(a['total']-b[0])<1e-11
 cases.append({'case':ix,'key':key,'cipher':c,'paths':len(paths),'scores':[p[0] for p in paths[:16]]})
# Check transformed operands against previously independently verified base arrays.
base=load(R.parent/'review-19/snapshots/keys.json.gz')
for cell in s.CELLS:
 b=next(k for k in base if k['id']==cell['id']);assert cell['key']==[(b['sign']*v)%29 for v in b['key']]
controls=[];pathcount=positions=0;maxerr=0
for ix in range(4):
 file=Q/f'fixture-{ix}.json.gz'
 if not file.exists():continue
 f=load(file);cell=next(c for c in s.CELLS if c['id']==f['cell_id']);key=cell['key'];rng=random.Random(f['seed']);cipher=[];j=0;events=[];unfinished=[]
 for p in f['plain']:
  ev=[]
  while j<len(key):
   value=p^key[j];u=None
   if value>=29:kind='invalid'
   elif cipher and value==cipher[-1]:
    u=rng.random();kind='soft-reject' if u<.83 else 'accept-repeat'
   else:kind='accept'
   ev.append({'draw':j,'key':key[j],'proposal':value,'kind':kind,'random':u});j+=1
   if kind in ('accept','accept-repeat'):cipher.append(value);events.append(ev);break
  else:unfinished=ev;break
 e=f['encoder'];assert cipher==e['cipher'] and events==e['events'] and j==e['used'];assert e['complete']==(len(cipher)==len(f['plain']))
 source=pathlib.Path(f['source']['path']);raw=source.read_text();assert hashlib.sha256(source.read_bytes()).hexdigest()==f['source']['sha256']
 abc='ᚠᚢᚦᚩᚱᚳ᷃ᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'.replace('᷃','')
 offsets=[j for j,ch in enumerate(raw) if ch in abc];assert offsets==f['source']['character_offsets'] and [abc.index(raw[j]) for j in offsets]==f['plain']
 if e['complete']:
  r=load(Q/f'control-{ix}.json.gz');a=r['top16']['alternatives'][0];truth=load(Q/f'truth-top16-{ix}.json.gz');accepted=[ev[-1]['draw'] for ev in events]
  controls.append({'ix':ix,'errors':[i for i,(p,q) in enumerate(zip(a['plain'],f['plain'])) if p!=q],'key_recovered':r['rows'][0]['id']==cell['id'],'truepath_ranks':[i+1 for i,a in enumerate(truth['alternatives']) if a['plain']==f['plain'] and a['accepted']==accepted],'used':j})
# Verify every available saved path and true-cell top16 via acceptance-position constraints.
for path in sorted(Q.glob('*.json.gz')):
 if path.name in [f'control-{i}.json.gz' for i in range(4)] or path.name.startswith(('real-','null-')):
  z=load(path);c=z['cipher'];ends=z['ends'];groups=[(next(k for k in s.CELLS if k['id']==row['id']),row['decode']['alternatives']) for row in z['rows']]
  if z['top16']:groups.append((next(k for k in s.CELLS if k['id']==z['rows'][0]['id']),z['top16']['alternatives']))
 elif path.name.startswith('truth-top16-'):
  ix=int(path.name.split('-')[-1].split('.')[0]);f=load(Q/f'fixture-{ix}.json.gz');c=f['encoder']['cipher'];ends=f['ends'];groups=[(next(k for k in s.CELLS if k['id']==f['cell_id']),load(path)['alternatives'])]
 else:continue
 for cell,alts in groups:
  for a in alts:
   j=0;ctx=(29,29);score=0.;lp=0.;soft=invalid=repeats=0
   for i,(p,accept) in enumerate(zip(a['plain'],a['accepted'])):
    prev=c[i-1] if i else None;key=cell['key']
    for k in range(j,accept):
     v=p^key[k]
     if v>=29:invalid+=1
     else:assert v==prev;lp+=math.log(.83);soft+=1
    assert p^key[accept]==c[i] and c[i]<29
    if c[i]==prev:lp+=math.log(.17);repeats+=1
    ctx,w=emit(ctx,p,i in ends);score+=w;j=accept+1
   assert j==a['used'];err=abs(score+lp-a['total']);maxerr=max(maxerr,err);assert err<1e-9
   if 'replay' in a:
    rep=a['replay'];assert (invalid,soft,repeats)==(rep['invalid'],rep['soft'],rep['accepted_repeats']);assert abs(lp-rep['log_probability'])<1e-12
   pathcount+=1;positions+=len(c)
out={'status':'PASS','transition_cases':trans,'tiny_cases':cases,'controls':controls,'paths_replayed':pathcount,'positions_replayed':positions,'max_score_error':maxerr}
(R/'result.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ('transition_cases','tiny_cases')})
