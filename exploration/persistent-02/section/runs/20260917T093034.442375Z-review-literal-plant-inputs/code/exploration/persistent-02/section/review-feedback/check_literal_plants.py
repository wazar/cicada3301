from pathlib import Path
import sys,json,random,hashlib,gzip,numpy as np
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/feedback';sys.path.insert(0,str(D));import reset_plants as A
x=json.loads((D/'C08/plants.json').read_text());src=R/x['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==x['source_sha256'];orig=[s for s in json.loads(src.read_text())['controls'] if s['id'].startswith('periodic-')];rng=random.Random(2026092300)
for s,t in zip(x['cases'],orig):
 seed=[rng.randrange(29) for _ in range(2)];assert seed==s['seed'] and s['truth']==t['truth'] and s['ends']==t['ends'] and s['reset_before']==t['reset_before'] and s['literal_positions']==t['truth_literal_positions'];h=[];c=[]
 for i,p in enumerate(s['truth']):
  if i in s['reset_before']:h=[]
  if i in s['literal_positions']:assert p==0;c.append(0)
  else:c.append((p+(seed[len(h)] if len(h)<2 else sum(h[-2:])))%29);h.append(p)
 assert c==s['cipher']
for name in ['p03','complementary']:assert np.array_equal(A.model(name),np.load(R/f'exploration/persistent-02/decoder/reset-feedback/model-{name}.npz')['L'])
folder=D/'C08/p03-plant00';summary=folder/'summary.json';result=dict(plants=8,model_tables_identical=True,source_hash=True,pilot_complete=summary.exists())
if summary.exists():
 d=x['cases'][0];L=A.model('p03');parts=[json.load(gzip.open(folder/f'part{j:02}.json.gz','rt')) for j in range(29)];maxerr=0;paths=0
 for j,part in enumerate(parts):
  assert part['partition']==j and part['seed_count']==29
  for a in part['alternatives']:
   assert a['seed'][0]==j;h=[];c=[];v=0.;aa=bb=29
   for i,p in enumerate(a['plain']):
    if i in d['reset_before']:h=[]
    if i in a['literal_positions']:assert p==0;c.append(0)
    else:c.append((p+(a['seed'][len(h)] if len(h)<2 else sum(h[-2:])))%29);h.append(p)
    v+=L[aa,bb,p];aa,bb=bb,p
    if i in d['ends']:v+=L[aa,bb,29];aa,bb=bb,29
   assert c==d['cipher'];assert abs(v-a['total'])<1e-8;maxerr=max(maxerr,abs(v-a['total']));paths+=1
 s=json.loads(summary.read_text());assert s['maximum']==max(p['maximum'] for p in parts);assert s['seed_count']==sum(p['seed_count'] for p in parts)==841
 result.update(passed=True,paths=paths,max_error=maxerr,seed_partitions=29,pilot_selected_errors=s['selected_rune_errors'],pilot_truth_retained=s['truth_in_retained'])
(Path(__file__).parent/'literal-plant-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
