import json, hashlib, gzip
from pathlib import Path
R=Path(__file__).resolve().parents[3]; A=R/'exploration/persistent-01/worker-a'; O=Path(__file__).resolve().parent
paths=0;runes=0

def replay(row,alt,cipher,resets):
 global paths,runes
 key=row['cell']['key'];sign=row['cell']['sign'];state=key[:];output=[]
 assert len(alt['plain'])==len(alt['skips'])==len(cipher)
 assert min(key)>=0 and len(key)>=4
 for i,(p,sk) in enumerate(zip(alt['plain'],alt['skips'])):
  if i in resets:state=key[:]
  previous=output[-1] if i and i not in resets else None
  assert 0<=sk<=3 and (previous is not None or sk==0)
  for draw in range(sk+1):
   k=state[0];state=state[1:]+[p];v=(p-sign*k)%29
   if draw<sk: assert v==previous
   else:output.append(v)
 assert output==cipher
 assert state==alt['state_end']
 assert len(cipher)+sum(alt['skips'])==alt['key_draws']
 paths+=1;runes+=len(cipher)

def pointers(p,c,key,sign,causal):
 # states hold next draw index, independent convention from worker last-accepted index.
 states={0};history=[]
 for i,(plain,target) in enumerate(zip(p,c)):
  stream=key+(p[:i] if causal else p)
  available=set(states);accepted=set()
  for rejects in range(4):
   again=set()
   for at in available:
    if at>=len(stream):continue
    value=(plain-sign*stream[at])%29
    if value==target:accepted.add(at+1)
    if i and rejects<3 and value==c[i-1]:again.add(at+1)
   available=again
  states=accepted;history.append(sorted(j-1 for j in states))
 return history

archive=json.loads((A/'publication/cycle2/manifest.json').read_text());archivebytes=0
for f in archive['files']:
 original=(R/f['source']).read_bytes();pub=(R/f['publication']).read_bytes()
 assert hashlib.sha256(original).hexdigest()==f['source_sha256']
 assert hashlib.sha256(pub).hexdigest()==f['publication_sha256']
 recovered=gzip.decompress(pub) if f['encoding']=='gzip-of-source' else pub
 assert recovered==original
 archivebytes+=len(pub)
files=['event-clock/controls-results.json','event-clock/pilot-results.json','field-reset/controls-results.json','field-reset/pilot-results.json']
rows=0;hypotheses=0;control_results=[]
for name in files:
 data=json.loads((A/name).read_text())
 for row in data['results']:
  rows+=1;hypotheses+=row['key_hypotheses'];resets=set(row.get('resets',[]));c=row['cipher']
  for entry in row['top20']:
   for alt in entry['alternatives']: replay(entry,alt,c,resets)
  prefix=row['prefix_top'];cut=row.get('cut',row['continuation'].get('cut'))
  for alt in prefix['alternatives']: replay(prefix,alt,c[:cut],resets)
  for alt in row['continuation']['alternatives']:replay(row['continuation'],alt,c,resets)
  if row['mode']=='plant' and (name.startswith('event') or row['model']=='source13_reset'):
   assert row['searched_best_errors']==row['continuation_errors']==0
   assert row['true_key_rank']==1 and row['true_path_top16']
   control_results.append({'source':row.get('source'), 'page':row.get('page'), 'model':row.get('model','event-clock'), 'exact_search_recovery':True})
reference=json.loads((A/'event-clock/representability.json').read_text())['results']
truths=[r for r in json.loads((A/'event-clock/controls-results.json').read_text())['results'] if r['mode']=='plant']
witnesses=[]
for truth,saved in zip(truths,reference):
 assert truth['source']==saved['source'];item={'source':truth['source']}
 for causal,label in [(True,'accepted_output_causal'),(False,'accepted_output_known_future')]:
  hist=pointers(truth['truth'],truth['cipher'],truth['plant_cell']['key'],truth['plant_cell']['sign'],causal)
  assert hist==saved[label]['pointer_sets']
  first=next((i for i,h in enumerate(hist) if not h),None)
  assert first==saved[label]['first_impossible']
  item[label]={'first_impossible':first,'previous_pointer_set':hist[first-1] if first else None}
 witnesses.append(item)
result={'retained_paths_reencrypted':paths,'rune_visits':runes,'search_rows':rows,'full_hypotheses_represented':hypotheses,'search_not_rerun':True,'controls':control_results,'pointer_witnesses':witnesses,'archive_files':len(archive['files']),'archive_bytes':archivebytes,'scope':'Independent arithmetic replay only. Search rank comes from saved ordered outputs; no statistical or real-solution claim.'}
(O/'A-event-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
