import pathlib,json,gzip,hashlib,math,collections,re
R=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).resolve().parent;D=R/'exploration/persistent-01/worker-i/p11'
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
quad=dict((a,int(b)) for a,b in (l.split() for l in (R/'liber-primus/data/english_quadgrams.txt').read_text().splitlines()));total=sum(quad.values());quad={a:math.log10(b/total) for a,b in quad.items()};floor=math.log10(.01/total)
c=collections.Counter();t=collections.Counter()
for src in json.loads((D/'manifest.json').read_text())['frozen_lm_sources']:
 seq=[]
 for word in re.findall('['+ABC+']+',(R/src['path']).read_text()):seq.extend(ABC.index(a) for a in word);seq.append(29)
 seq=[29,29]+seq
 for i in range(2,len(seq)):
  for n in range(3):ctx=tuple(seq[i-n:i]);t[ctx]+=1;c[ctx+(seq[i],)]+=1
# Distinct scalar rescorer, shared frozen tables/training data by design.
def score(a,ends):
 p=a['plain'];s=''.join(TOK[x] for x in p);q=sum(quad.get(s[i:i+4],floor) for i in range(len(s)-3))/max(1,len(s)-3)
 seq=[]
 for i,x in enumerate(p):seq.append(x);seq.extend([29] if i in ends else [])
 seq=[29,29]+seq;ss=0
 for i in range(2,len(seq)):
  x=seq[i];v=(c[(x,)]+.5)/(t[()]+15)
  for n,alpha in [(1,8),(2,5)]:ctx=tuple(seq[i-n:i]);v=(c[ctx+(x,)]+alpha*v)/(t[ctx]+alpha)
  ss+=math.log(v)
 rune=ss/(len(seq)-2)
 assert abs(q-a['english'])<1e-9 and abs(rune-a['rune_lm'])<1e-9
 return max(abs(q-a['english']),abs(rune-a['rune_lm']))
n=0;err=0
summary=json.loads((D/'summary.json').read_text())
for model in ['english','rune']:
 for mode in ['real','null']:
  ix=summary['models'][model][mode]['leading_cell']['ordinal'];r=json.loads(gzip.decompress((D/'search'/f'cell-{ix:05}.json.gz').read_bytes()))['output'][mode]
  for mm in r['models']:
   for a in mm['alternatives']:err=max(err,score(a,r['ends']));n+=1
for name,off,sign in [('0_welcome',37,-1),('p56_an_end',91,1)]:
 ends=json.loads((D/'controls'/f'{name}-fixture.json').read_text())['ends']
 for model in ['english','rune']:
  ix=off*2+(sign==1);r=json.loads(gzip.decompress((D/'controls'/f'{name}-{model}'/f'{ix:03}.json.gz').read_bytes()))
  for a in r['alternatives']:err=max(err,score(a,ends));n+=1
runs=[]
for p in (D.parent/'runs').glob('*/command.json'):
 r=json.loads(p.read_text())
 if any('p11.py'==pathlib.Path(x).name for x in r['command']):
  assert r['outcome']=='PASS' and r['exit_code']==0 and r['timeout_seconds']<=900
  for src in r['sources_inputs']:
   if pathlib.Path(src['path']).name in ['p11.py','search.py','p03_frozen.py']:
    b=(R/src['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==src['sha256'];snapshot=p.parent/'code'/src['path'];assert snapshot.read_bytes()==b
  runs.append(dict(run=p.parent.name,seconds=r['duration_seconds']))
result=dict(status='PASS',rescore_paths=n,max_score_difference=err,search_runs=runs,shared_dependencies='Same frozen English quadgram data and five solved-source texts; independent scalar score implementation, no worker arithmetic import.')
(O/'rescore-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
