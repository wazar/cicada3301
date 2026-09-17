from pathlib import Path
import importlib.util,itertools,json,gzip,random,re,hashlib,datetime,sys,time
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'exploration/persistent-01';P=B/'worker-p/P23'
spec=importlib.util.spec_from_file_location('gp',ROOT/'liber-primus/src/lp/gematria.py');gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)
TOKENS=[[] for _ in range(29)]
for i,r,t,p in gp.GEMATRIA:TOKENS[i].append(t)
for c,i in {'V':1,'K':5,'Q':5,'Z':15}.items():TOKENS[i].append(c)
SORTED=sorted([(t,i) for i,ts in enumerate(TOKENS) for t in ts],key=lambda x:-len(x[0]))
def guard():
 assert not (B/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):
 b=json.dumps(x,separators=(',',':')).encode()
 if n.endswith('.gz'):
  with gzip.open(P/n,'wb') as f:f.write(b)
 else:(P/n).write_bytes(b+b'\n')
def first(s):
 for t,i in SORTED:
  if s.startswith(t):return t,i
 raise ValueError
def membership(runes):
 states={};history=[];count={};witness={}
 if not runes:return dict(feasible=True,latin='',path_count=1,states=[])
 for t in TOKENS[runes[0]]:states[t]=True;count[t]=1;witness[t]=t
 history.append(dict(states=list(states),counts=count.copy()))
 for pos,r in enumerate(runes[1:],1):
  nxt={};nc={};nw={};transitions=[]
  for old in states:
   for t in TOKENS[r]:
    chosen,idx=first(old+t);valid=chosen==old and idx==runes[pos-1]
    transitions.append(dict(previous=old,current=t,greedy_token=chosen,greedy_rune=idx,valid=valid))
    if valid:
     nxt[t]=True;nc[t]=nc.get(t,0)+count[old]
     if t not in nw:nw[t]=witness[old]+t
  if not nxt:return dict(feasible=False,states=history,failure_position=pos,transition_obstruction=transitions,latin=None,path_count=0)
  states,count,witness=nxt,nc,nw;history.append(dict(states=list(states),counts=count.copy()))
 latin=next(iter(witness.values()));assert gp.keyword_to_indices(latin)==runes
 return dict(feasible=True,latin=latin,path_count=sum(count.values()),states=history)
def controls():
 guard();single=[]
 for i,ts in enumerate(TOKENS):
  for t in ts:assert gp.keyword_to_indices(t)==[i];single.append(dict(spelling=t,rune=i))
 rows=[];pairs=[]
 for n in [2,3]:
  ok=bad=0;paths=0
  for rs in itertools.product(range(29),repeat=n):
   r=list(rs);brute=[]
   for ss in itertools.product(*(TOKENS[x] for x in r)):
    s=''.join(ss)
    if gp.keyword_to_indices(s)==r:brute.append(s)
   result=membership(r);assert result['feasible']==bool(brute) and result['path_count']==len(brute)
   if brute:ok+=1
   else:bad+=1
   paths+=len(brute)
   if n==2:pairs.append(dict(runes=r,result=result,brute=brute))
  rows.append(dict(length=n,cases=29**n,feasible=ok,infeasible=bad,valid_spelling_paths=paths))
 save('pair-controls.json.gz',pairs)
 rng=random.Random(523100);randoms=[]
 for _ in range(400):
  s=''.join(rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(rng.randrange(81)));r=gp.keyword_to_indices(s);m=membership(r);assert m['feasible'];randoms.append(dict(latin=s,runes=r,result=m))
 save('random-controls.json.gz',randoms)
 edge=[]
 for s in ['TH','T H','th','EO','OE','AE','IA','EA','NG','V','K','Q','Z','UVC KQSZ','ING','IO']:
  r=gp.keyword_to_indices(s);assert membership(r)['feasible'];edge.append(dict(input=s,output=r))
 assert not membership([16,8])['feasible'] and membership([16])['feasible'] and membership([8])['feasible']
 source=[]
 for name in ['0_welcome','jpg107-167','p56_an_end','p57_parable']:
  f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=f.read_text();words=[]
  for m in re.finditer('['+''.join(gp.RUNES)+']+',raw):
   original=[gp.RUNE_TO_IDX[x] for x in m.group()];latin=''.join(gp.IDX_TO_TRANS[x] for x in original);rendered=gp.keyword_to_indices(latin);result=membership(rendered);assert result['feasible']
   chars=[]
   for pos in range(m.start(),m.end()):chars.extend([pos]*len(gp.RUNE_TO_TRANS[raw[pos]]))
   words.append(dict(source_span=[m.start(),m.end()],original=original,latin=latin,latin_source_chars=chars,rendered=rendered,result=result,resegmented=original!=rendered))
  source.append(dict(name=name,path=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),words=words))
 save('source-controls.json.gz',source);save('controls-summary.json',dict(single_spellings=single,exhaustive=rows,random_count=400,edgecases=edge,reset_TH=dict(together=gp.keyword_to_indices('TH'),apart=[gp.keyword_to_indices('T'),gp.keyword_to_indices('H')]),source_summary=[dict(name=x['name'],words=len(x['words']),resegmented=sum(w['resegmented'] for w in x['words'])) for x in source]))
 print((P/'controls-summary.json').read_text())
def actual():
 assert (P/'controls-summary.json').exists();pages=[p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]];rows=[]
 for page in pages:
  units=[]
  for ui,w in enumerate(page['words']):
   r=page['indices'][w['start']:w['end']];m=membership(r)
   out=dict(unit=ui,bounds=[w['start'],w['end']],runes=r,source_char_positions=page['source_char_positions'][w['start']:w['end']],result=m)
   if not m['feasible']:
    k=m['failure_position'];out['witness_pair']=dict(runes=r[k-1:k+1],source_rune_indices=[w['start']+k-1,w['start']+k],source_char_positions=out['source_char_positions'][k-1:k+1])
   units.append(out)
  rows.append(dict(page=page['page'],units=units,feasible=sum(x['result']['feasible'] for x in units),infeasible=sum(not x['result']['feasible'] for x in units)))
 save('actual.json',rows);save('summary.json',dict(rows=[dict(page=r['page'],units=len(r['units']),feasible=r['feasible'],infeasible=r['infeasible']) for r in rows],renderer_sha256=hashlib.sha256((ROOT/'liber-primus/src/lp/gematria.py').read_bytes()).hexdigest()))
 print((P/'summary.json').read_text())
if __name__=='__main__':
 guard();t=time.monotonic();{'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
