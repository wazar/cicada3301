from pathlib import Path
import sys,json,gzip,hashlib,itertools,math
R=Path(__file__).parent;P=R.parent/'worker-p';sys.path.insert(0,str(P));import p18 as s
load=lambda path:json.load(gzip.open(path,'rt'));source=load(R/'source-replay.json.gz');key=source['runes'];assert s.KEY==key;km=load(P/'P18/key-map.json.gz');assert km['key']==key
for i,m in enumerate(km['map']):
 ref=source['rune_maps'][i];assert m['word']==ref['word'] and m['rune_in_word']==ref['word_rune'] and m['char_span']==source['words'][ref['word']]['span']
(R/'snapshots').mkdir(exist_ok=True)
inputs={}
for p in [P/'p18.py',P/'P18/CARD.md',R.parent/'worker-c/frozen_finite.py',R.parent/'worker-c/p03_frozen.py']+sorted((P/'P18').glob('*.json.gz')):
 if 'aggregate' in p.name:continue
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 if p.name in ['p18.py','CARD.md','frozen_finite.py','p03_frozen.py']:(R/'snapshots'/p.name).write_bytes(b)
(R/'precheck-inputs.json').write_text(json.dumps(inputs,indent=2))
def score(plain,ends):
 ctx=(29,29);out=0.
 for i,p in enumerate(plain):
  for x in [p,29] if i in ends else [p]:
   v=(s.lm.c[0][(x,)]+.5)/(s.lm.t[0][()]+15);v=(s.lm.c[1][ctx[-1:]+(x,)]+8*v)/(s.lm.t[1][ctx[-1:]]+8);v=(s.lm.c[2][ctx+(x,)]+5*v)/(s.lm.t[2][ctx]+5);out+=math.log(v);ctx=(ctx[-1],x)
 return out/(len(plain)+len(ends))
def replay(f,job,a):
 used=0;plain=[];literal=set(a['literal_positions'])
 assert len(literal)==len(a['literal_positions'])
 for i,c in enumerate(f['cipher']):
  if i in literal:assert c==0;plain.append(0)
  else:assert job['offset']+used<len(key);plain.append((c+job['sign']*key[job['offset']+used])%29);used+=1
 assert plain==a['plain'] and used==a['used'];assert abs(score(plain,set(f['ends']))-a['score'])<1e-11
 return used
boundary=[]
for c,k in [([0],[]),([1],[]),([0,1],[2]),([1,0],[2]),([0,0],[0]),([1,0,2],[3,4]),([0],[0]),([0,0,1,0],[8])]:
 for sign in [-1,1]:
  ends={len(c)-1};sites=[i for i,x in enumerate(c) if x==0];expected=[]
  for bits in itertools.product([False,True],repeat=len(sites)):
   lit={i for i,b in zip(sites,bits) if b};u=0;p=[]
   for i,v in enumerate(c):
    if i in lit:p.append(0)
    elif u<len(k):p.append((v+sign*k[u])%29);u+=1
    else:break
   if len(p)==len(c):expected.append(score(p,ends))
  expected.sort(reverse=True);got,diag=s.finite(c,ends,k,sign,s.lm,16);assert len(got)==len(expected) and all(abs(a['score']-v)<1e-12 for a,v in zip(got,expected));boundary.append({'cipher':c,'key':k,'sign':sign,'valid_paths':len(expected),'scores':expected})
control=[]
for ix in range(4):
 f=load(P/f'P18/fixture-{ix}.json.gz');t=f['truth'];path=Path(f['source']['path']);raw=path.read_text();assert hashlib.sha256(path.read_bytes()).hexdigest()==f['source']['sha256'];abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';positions=[j for j,x in enumerate(raw) if x in abc];plain=[abc.index(raw[j]) for j in positions];assert plain==t['plain'] and positions==f['source']['character_offsets'];u=0;c=[];lit=[]
 for i,p in enumerate(plain):
  if p==0 and i%3!=1:c.append(0);lit.append(i)
  else:c.append((p-t['sign']*key[t['offset']+u])%29);u+=1
 assert c==f['cipher'] and lit==t['literal_positions'] and u==t['used'];n_nonzero=sum(v!=0 for v in c);jobs=s.grid(f);assert len(jobs)==2*(len(key)-n_nonzero+1)
 for job in jobs[-2:]:
  row=s.cell(f,job,16);assert len(row['alternatives'])==1;replay(f,job,row['alternatives'][0])
  beyond=key[job['offset']+1:];alts,diag=s.finite(c,set(f['ends']),beyond,job['sign'],s.lm,1);assert not alts and diag['infeasible']
 # Exact signed keyprefix equivalence class for the complete planted consumption.
 prefix=[t['sign']*v%29 for v in key[t['offset']:t['offset']+u]];aliases=[]
 for sign in [-1,1]:
  for offset in range(len(key)-u+1):
   if all((sign*key[offset+j])%29==v for j,v in enumerate(prefix)):aliases.append({'offset':offset,'sign':sign})
 control.append({'ix':ix,'cells':len(jobs),'last_offset':jobs[-1]['offset'],'used':u,'true_prefix_aliases':aliases})
pilot=load(P/'P18/pilot.json.gz');n=0
for group in pilot:
 f=load(P/f"P18/fixture-{group['name'].split('-')[1]}.json.gz");jobs=s.grid(f);assert group['ids']==[i*len(jobs)//64 for i in range(64)]
 for row in group['rows']:
  assert row['job']==jobs[row['id']]
  for a in row['alternatives']:replay(f,row['job'],a);n+=1
out={'status':'PASS','finite_boundary_cases':boundary,'controls':control,'pilot_paths':n,'key_length':len(key)};(R/'precheck.json').write_text(json.dumps(out,indent=2));print(out['controls'],n,'pilot paths PASS')
