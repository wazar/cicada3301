from pathlib import Path
import ast,json,gzip,hashlib,itertools,random,re,math,importlib.util
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;P=B/'worker-p/P23';source=ROOT/'liber-primus/src/lp/gematria.py';tree=ast.parse(source.read_text());table=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GEMATRIA' for t in n.targets));spells=[[t] for i,r,t,p in table]
for c,i in [('V',1),('K',5),('Q',5),('Z',15)]:spells[i].append(c)
ABC=''.join(r for i,r,t,p in table);canonical=[t for i,r,t,p in table];lex={t:i for i,ss in enumerate(spells) for t in ss};trie={}
for token,value in lex.items():
 node=trie
 for ch in token:node=node.setdefault(ch,{})
 node['output']=value

def parse(text):
 s=text.upper().replace(' ','');out=[];i=0
 while i<len(s):
  node=trie;j=i;last=None
  while j<len(s) and s[j] in node:
   node=node[s[j]];j+=1
   if 'output' in node:last=(j,node['output'])
  if last is None:raise ValueError
  i,v=last;out.append(v)
 return out
spec=importlib.util.spec_from_file_location('review39_gp',source);gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)
# Enumerate complete A-Z spellings up to max tokenlength, checking no missing accepted one-output aliases.
one={}
for length in [1,2]:
 for chars in itertools.product('ABCDEFGHIJKLMNOPQRSTUVWXYZ',repeat=length):
  s=''.join(chars);actual=gp.keyword_to_indices(s);assert parse(s)==actual
  if len(actual)==1:one[s]=actual[0]
assert one==lex and len(one)==33
(R/'snapshots').mkdir(exist_ok=True);inputs={}
for path in list(P.iterdir())+[source,B/'worker-p/p23.py',B/'worker-f/F06-maps.json']:
 if path.is_file():
  raw=path.read_bytes();inputs[str(path)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
  if path.suffix!='.gz':(R/'snapshots'/path.name).write_bytes(raw)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2));forbidden=set();cert=[];pairs=json.load(gzip.open(P/'pair-controls.json.gz','rt'))
for pair in pairs:
 a,b=pair['runes'];valid=[];proof=[]
 for x,y in itertools.product(spells[a],spells[b]):
  parsed=parse(x+y);assert parsed==gp.keyword_to_indices(x+y);okay=parsed==[a,b];proof.append(dict(left=x,right=y,valid=okay,parsed=parsed))
  if okay:valid.append(x+y)
 assert valid==pair['brute'];assert len({r['valid'] for r in proof})==1
 if not valid:forbidden.add((a,b));cert.append(dict(pair=[a,b],all_spelling_options=proof))
assert len(forbidden)==14

def membership_check(rs,m):
 failure=next((i for i in range(1,len(rs)) if (rs[i-1],rs[i]) in forbidden),None);assert m['feasible']==(failure is None)
 if not rs:assert m['path_count']==1 and m['latin']=='' and m['states']==[];return
 stop=len(rs) if failure is None else failure;paths=1
 for i,r in enumerate(rs[:stop]):
  expected=dict(states=spells[r],counts={s:paths for s in spells[r]});assert m['states'][i]==expected;paths*=len(spells[r])
 assert len(m['states'])==stop
 if failure is None:assert m['path_count']==paths and parse(m['latin'])==rs
 else:
  assert m['failure_position']==failure and m['path_count']==0 and m['latin'] is None
  for row in m['transition_obstruction']:
   text=row['previous']+row['current'];token=max((t for t in lex if text.startswith(t)),key=len);assert token==row['greedy_token'] and lex[token]==row['greedy_rune'] and not row['valid']
for pair in pairs:membership_check(pair['runes'],pair['result'])
triplefeasible=0;triplepaths=0
for rs in itertools.product(range(29),repeat=3):
 valid=0
 for parts in itertools.product(*(spells[r] for r in rs)):
  text=''.join(parts);decoded=parse(text);assert decoded==gp.keyword_to_indices(text);valid+=decoded==list(rs)
 predicted=all((x,y) not in forbidden for x,y in zip(rs,rs[1:]));assert bool(valid)==predicted;assert valid==(math.prod(len(spells[r]) for r in rs) if predicted else 0);triplefeasible+=bool(valid);triplepaths+=valid
rng=random.Random(523100);randoms=json.load(gzip.open(P/'random-controls.json.gz','rt'))
for row in randoms:
 s=''.join(rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(rng.randrange(81)));assert s==row['latin'] and parse(s)==row['runes'];membership_check(row['runes'],row['result'])
summary=json.loads((P/'controls-summary.json').read_text())
for row in summary['edgecases']:assert parse(row['input'])==row['output']==gp.keyword_to_indices(row['input'])
assert parse('TH')==parse('T H')==[2] and parse('T')+parse('H')==[16,8]
sourcewords=0
for src in json.load(gzip.open(P/'source-controls.json.gz','rt')):
 f=ROOT/src['path'];raw=f.read_text();assert hashlib.sha256(f.read_bytes()).hexdigest()==src['sha256'];matches=list(re.finditer('['+ABC+']+',raw));assert len(matches)==len(src['words'])
 for match,row in zip(matches,src['words']):
  original=[ABC.index(c) for c in match.group()];latin=''.join(canonical[i] for i in original);positions=[pos for pos in range(match.start(),match.end()) for _ in canonical[ABC.index(raw[pos])]];assert row['source_span']==[match.start(),match.end()] and row['original']==original and row['latin']==latin and row['latin_source_chars']==positions and row['rendered']==parse(latin);assert row['resegmented']==(original!=parse(latin));membership_check(row['rendered'],row['result']);sourcewords+=1
D={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]};witnesses=[]
for page in json.loads((P/'actual.json').read_text()):
 p=D[page['page']];assert len(page['units'])==len(p['words'])
 for i,(row,w) in enumerate(zip(page['units'],p['words'])):
  rs=p['indices'][w['start']:w['end']];assert row['unit']==i and row['bounds']==[w['start'],w['end']] and row['runes']==rs and row['source_char_positions']==p['source_char_positions'][w['start']:w['end']];membership_check(rs,row['result'])
  if not row['result']['feasible']:
   k=row['result']['failure_position'];pair=dict(runes=rs[k-1:k+1],source_rune_indices=[w['start']+k-1,w['start']+k],source_char_positions=p['source_char_positions'][w['start']+k-1:w['start']+k+1]);assert pair==row['witness_pair'];witnesses.append(dict(page=page['page'],unit=i,**pair,spellings=[spells[r] for r in pair['runes']]))
existing=json.loads((P/'independent-certificate.json').read_text());assert cert==existing['forbidden_pair_certificates'] and witnesses==existing['actual_witnesses'];out={'status':'PASS','complete_single_spellings':len(one),'pair_cases':841,'forbidden_pairs':len(forbidden),'triple_cases':29**3,'triple_feasible':triplefeasible,'triple_valid_paths':triplepaths,'source_words':sourcewords,'forbidden_pair_certificates':cert,'actual_witnesses':witnesses};(R/'result.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['forbidden_pair_certificates','actual_witnesses']})
