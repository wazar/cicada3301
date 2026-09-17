from pathlib import Path
import ast,json,gzip,itertools,math
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'exploration/persistent-01';P=B/'worker-p/P23'
assert not (B/'STOP').exists()
tree=ast.parse((ROOT/'liber-primus/src/lp/gematria.py').read_text())
table=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GEMATRIA' for t in n.targets))
canonical={i:t for i,r,t,p in table};spells={i:[t] for i,t in canonical.items()}
for t,i in [('V',1),('K',5),('Q',5),('Z',15)]:spells[i].append(t)
doubles={t:i for i,t in canonical.items() if len(t)==2};singles={t:i for i,ts in spells.items() for t in ts if len(t)==1}
def parse(s):
 s=s.upper().replace(' ','');r=[];i=0
 while i<len(s):
  if s[i:i+2] in doubles:r.append(doubles[s[i:i+2]]);i+=2
  else:r.append(singles[s[i]]);i+=1
 return r
forbidden=[];cert=[]
for a,b in itertools.product(range(29),repeat=2):
 cases=[]
 for s,t in itertools.product(spells[a],spells[b]):
  # First token consumes s iff either s is a digraph or cross-boundary pair is not a digraph.
  valid=len(s)==2 or (s+t)[:2] not in doubles
  cases.append(dict(left=s,right=t,valid=valid,parsed=parse(s+t)))
 assert len({c['valid'] for c in cases})==1,'Alias-dependent feasibility would require generic DP'
 if not cases[0]['valid']:forbidden.append((a,b));cert.append(dict(pair=[a,b],all_spelling_options=cases))
forbidden=set(forbidden)
def check(r,m):
 bad=[i for i in range(1,len(r)) if (r[i-1],r[i]) in forbidden]
 assert m['feasible']==(not bad)
 if bad:assert m['failure_position']==bad[0] and m['path_count']==0
 else:
  assert parse(m['latin'])==r
  assert m['path_count']==math.prod(len(spells[x]) for x in r)
def load(n):
 with gzip.open(P/n,'rt') as f:return json.load(f)
for x in load('pair-controls.json.gz'):check(x['runes'],x['result'])
for x in load('random-controls.json.gz'):assert parse(x['latin'])==x['runes'];check(x['runes'],x['result'])
summary=json.loads((P/'controls-summary.json').read_text())
for x in summary['edgecases']:assert parse(x['input'])==x['output']
triples=0
for rs in itertools.product(range(29),repeat=3):
 actual=any(parse(''.join(t))==list(rs) for t in itertools.product(*(spells[x] for x in rs)))
 predicted=all(pair not in forbidden for pair in zip(rs,rs[1:]));assert actual==predicted;triples+=1
abc=''.join(r for i,r,t,p in table)
for src in load('source-controls.json.gz'):
 raw=(ROOT/src['path']).read_text()
 for w in src['words']:
  lo,hi=w['source_span'];r=[abc.index(x) for x in raw[lo:hi]]
  assert r==w['original'];latin=''.join(canonical[x] for x in r)
  assert latin==w['latin'] and parse(latin)==w['rendered']
  chars=[]
  for i in range(lo,hi):chars.extend([i]*len(canonical[abc.index(raw[i])]))
  assert chars==w['latin_source_chars'];check(w['rendered'],w['result'])
pages={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]}
rows=json.loads((P/'actual.json').read_text());witnesses=[]
for page in rows:
 source=pages[page['page']]
 for w in page['units']:
  start,end=w['bounds'];r=source['indices'][start:end]
  assert r==w['runes'] and source['source_char_positions'][start:end]==w['source_char_positions'];check(r,w['result'])
  if not w['result']['feasible']:
   i=w['result']['failure_position'];assert w['witness_pair']['runes']==r[i-1:i+1]
   assert w['witness_pair']['source_rune_indices']==[start+i-1,start+i]
   witnesses.append(dict(page=page['page'],unit=w['unit'],**w['witness_pair'],spellings=[spells[x] for x in r[i-1:i+1]]))
(P/'independent-certificate.json').write_text(json.dumps(dict(pass_all=True,forbidden_pair_count=len(forbidden),triples_checked=triples,alias_feasibility_invariant=True,forbidden_pair_certificates=cert,actual_witnesses=witnesses),indent=2)+'\n')
print(json.dumps(dict(pass_all=True,forbidden_pairs=len(forbidden),triples=triples,actual_infeasible_units=len(witnesses))))
