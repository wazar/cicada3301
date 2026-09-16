from pathlib import Path
from collections import Counter
import json,gzip,random,hashlib
O=Path(__file__).resolve().parent;B=O.parents[1]
def read(name):
 with gzip.open(O/(name+'.json.gz'),'rt') as f:return json.load(f)
maps=json.loads((B/'worker-f/F06-maps.json').read_text());ids=[m['page'] for m in maps];seqs=[[w['end']-w['start'] for w in m['words']] for m in maps];pairs=[(i,ids.index(v+1)) for i,v in enumerate(ids) if v+1 in ids]
def longest(a,b):
 best=0
 for shift in range(1-len(b),len(a)):
  i=max(shift,0);j=max(-shift,0);run=0
  while i<len(a) and j<len(b):
   run=run+1 if a[i]==b[j] else 0;best=max(best,run);i+=1;j+=1
 return best
def scan(panel):return max(longest(panel[a],panel[b][::-1] if reverse else panel[b]) for a,b in pairs for reverse in [False,True])
result=json.loads((O/'result.json').read_text());real=read('real-evidence');assert scan(seqs)==result['real_max']==real['max_units'];spans=0
for row in real['matches']:
 a=ids.index(row['left_page']);b=ids.index(row['right_page']);assert longest(seqs[a],seqs[b][::-1] if row['reverse'] else seqs[b])==row['max_units']
 for s in row['spans']:
  assert [seqs[a][i] for i in s['left_units']]==[seqs[b][i] for i in s['right_units']]==s['lengths'];assert len(s['lengths'])==row['max_units'];assert s['left_source_units']==[maps[a]['words'][i] for i in s['left_units']];assert s['right_source_units']==[maps[b]['words'][i] for i in s['right_units']];spans+=1
controls=[];panels={'real':seqs}
for row in result['controls']:
 index=row['index'];c=read('control-'+str(index));panels['control-'+str(index)]=c['lengths'];assert list(map(len,c['lengths']))==list(map(len,seqs))
 for lens,runes in zip(c['lengths'],c['runes']):assert sum(lens)==len(runes) and all(a!=b for a,b in zip(runes,runes[1:]))
 meta=c['metadata']
 if meta['kind']=='planted_copy':
  a=ids.index(meta['left_page']);b=ids.index(meta['right_page']);i=meta['left_start'];j=meta['right_start'];k=meta['length'];left=c['lengths'][a][i:i+k];right=c['lengths'][b][j:j+k];assert left==(right[::-1] if meta['reverse'] else right);assert row['max_units']>=k
 if index in [0,7,8,23,24,25,26,27]:assert scan(c['lengths'])==row['max_units']
 for null in row['nulls']:assert len(null['stats'])==99 and (1+sum(x>=row['max_units'] for x in null['stats']))/100==null['tail']
 controls.append(dict(index=index,max_units=row['max_units'],tails=[x['tail'] for x in row['nulls']]))
rawcases=[]
for name,cal in [('real',result['real_nulls'])]+[(f'control-{i}',result['controls'][i]['nulls']) for i in [0,8,16,24]]:
 for null in cal:
  family=null['family'];rng=random.Random(null['seed']);count=0
  with gzip.open(O/null['path'],'rt') as f:
   for line in f:
    record=json.loads(line);assert record['rep']==count and record['stat']==null['stats'][count];panel=[]
    for seq,saved in zip(panels[name],record['orders']):
     blocks=[[i] for i in range(len(seq))] if family==0 else [list(range(i,min(i+4,len(seq)))) for i in range(0,len(seq),4)];order=list(range(len(blocks)));rng.shuffle(order);flat=[i for b in order for i in blocks[b]];assert order==saved['block_order'] and flat==saved['unit_order'];panel.append([seq[i] for i in flat]);assert Counter(panel[-1])==Counter(seq)
    if count in [0,null['count']-1]:assert scan(panel)==record['stat']
    count+=1
  assert count==null['count'];rawcases.append(dict(name=name,family=family,records_replayed=count))
for null in result['real_nulls']:assert (1+sum(x>=result['real_max'] for x in null['stats']))/1000==null['tail']
out=dict(status='PASS',real_span_records=spans,independent_real_pair_orientation_maxima=66,full_controls_independently_scanned=8,raw_null_streams=rawcases,controls=controls,real_tails=[x['tail'] for x in result['real_nulls']],actual_panel_count=1+sum(x['count'] for x in result['real_nulls'])+sum(1+sum(x['count'] for x in r['nulls']) for r in result['controls']))
assert out['actual_panel_count']==result['total_panels'];(O/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['controls','raw_null_streams']},indent=2))
