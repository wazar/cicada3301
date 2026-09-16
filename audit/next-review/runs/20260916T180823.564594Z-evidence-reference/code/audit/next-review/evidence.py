"""Reference arithmetic and retained-evidence check, no puzzle decoding."""
import pathlib,json,hashlib,math,datetime
R=pathlib.Path(__file__).resolve().parents[2];O=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
before={str(p.relative_to(R)):sha(p) for owner in ['experiment-01','f-interruption-01','alphanumeric-01'] for p in (R/'audit'/owner).rglob('*') if p.is_file()}
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
cbase='audit/f-interruption-01/';p=read(cbase+'results/20260916T180408.121651Z-pilot.json');m=read(cbase+'results/20260916T180434.839675Z-main.json')
refs=[]
for ref in p['reference']:
 base=R/'audit/parallel-01/reference/sources';cipher=[ABC.index(r) for r in (base/(ref['name']+'.txt')).read_text() if r in ABC];expected=[ABC.index(r) for r in (base/('solved_'+ref['name']+'.txt')).read_text() if r in ABC]
 labels={'0_welcome':[4,5,6,7,10,11,14,18,20,21,25],'jpg107-167':[2,3],'p56_an_end':[4]}[ref['name']]
 keycycles={'0_welcome':[23,10,1,10,9,10,16,26],'jpg107-167':[0,10,4,0,1,19,0,18,4,18,9,0,18]}
 if ref['name'] in keycycles:
  cycle=keycycles[ref['name']];key=[cycle[i%len(cycle)] for i in range(len(cipher))]
 else:
  primes=[];n=2
  while len(primes)<len(cipher):
   if all(n%d for d in range(2,math.isqrt(n)+1)):primes.append(n)
   n+=1
  key=[v-1 for v in primes]
 assert key==ref['key'];seen=j=0;plain=[]
 for i,c in enumerate(cipher):
  seen+=c==0;literal=c==0 and seen in labels
  plain.append(0 if literal else (c-key[j])%29)
  assert j==ref['trace'][i]['key_before'];j+=not literal
  assert j==ref['trace'][i]['key_after']
 assert plain==expected==ref['plain']
 refs.append({'name':ref['name'],'exact_runes':len(plain),'key_values_consumed':j})
counts={g:int(v) for g,v in (line.split() for line in (R/'liber-primus/data/english_quadgrams.txt').read_text().splitlines())};N=sum(counts.values())
def score(arr):
 t=''.join(TOK[v] for v in arr)
 return sum(math.log10(counts.get(t[i:i+4],.01)/N) for i in range(len(t)-3))/(len(t)-3) if len(t)>=4 else -999.
ranks=[]
for row in p['cases']+m['cases']:
 case=row['fixture'];ex=row['exhaustive'];truth=next(s for s in ex if s['path']==case['interrupt'])
 for s in ex:assert score(s['plain'])==s['score']
 rank=1+sum(s['score']>truth['score'] for s in ex)
 for b in row['beams']:assert rank==b['summary']['true_path_global_rank']
 ranks.append({'case':case['name'],'rank':rank,'compatible_paths':len(ex),'distinct_plaintexts':len({tuple(s['plain']) for s in ex})})
# Check every executed A case's frozen ordering, trace arithmetic and decisions without rerunning the beam.
A='audit/experiment-01/';spec=read(A+'preregistration.json');cases=[]
for path in sorted((R/A/'outputs').glob('*/case-*.json')):
 c=json.loads(path.read_text());ordinal=c['ordinal'];assert c['cell']==spec['positive_cells'][ordinal//20] and c['case']==ordinal%20
 for page,trace in enumerate(c['encryption_state_trace']):
  for i,t in enumerate(trace):
   assert t['plain']==c['plaintext'][page][i] and t['cipher']==c['ciphertext'][page][i]
   for attempt in t['attempts']:assert attempt['candidate_cipher']==(t['plain']-c['cell']['sign']*c['plant_key'][attempt['key_index']])%29
 assert c['passed']==(c['required_exact'] and c['selected_exact'] and c['planted_is_tied_top'])
 cases.append(ordinal)
assert sorted(cases)==list(range(67))
# Frozen inputs and actual execution source snapshots match current bytes.
snapshot_checks=[]
for owner,run in [('experiment-01','20260916T180521.681117Z-experiment-01-main'),('f-interruption-01','20260916T180434.710356Z-main-repaired')]:
 d=R/'audit'/owner/'runs'/run;meta=json.loads((d/'command.json').read_text())
 for row in meta['sources_inputs']:
  if row.get('exists'):assert sha(row['path'])==row['sha256']
  snap=d/'code'/row['path']
  if snap.is_file():assert hashlib.sha256(snap.read_bytes()).hexdigest()==row['sha256']
 snapshot_checks.append({'run':run,'input_hash_count':len(meta['sources_inputs'])})
after={p:sha(p) for p in before};assert before==after
out={'reference_checks':refs,'score_checks':ranks,'all_A_cases_checked':len(cases),'execution_snapshot_checks':snapshot_checks,'source_artifact_hashes_before':before,'source_artifact_hashes_after':after,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (O/'evidence-checks.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if 'hashes' not in k},indent=2))
