"""Independent proof replay from original runes and scalar five-bit integer bounds."""
import pathlib,json,gzip,collections,hashlib,time
B=pathlib.Path('exploration/persistent-01/worker-s');source=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json');pages=json.loads(source.read_text());record=json.loads(gzip.decompress((B/'S11-real.json.gz').read_bytes()));assert hashlib.sha256(source.read_bytes()).hexdigest()==record['source_sha256'];proof=record['result']['proof'];seen=set();leaves=collections.Counter();examples={};start=time.monotonic()
def check(nodeid,one,assigned):
 assert nodeid not in seen;seen.add(nodeid);node=proof[nodeid]
 if node[0]=='D':
  _,v,left,right=node;assert 0<=v<29 and v not in assigned;check(left,one|{v},assigned|{v});check(right,one,assigned|{v});return
 if node[0]=='K':assert len(one)+29-len(assigned)<14;leaves['cardinality']+=1;return
 assert node[0]=='P';page=pages[node[1]];xs=page['indices'];witnesses=[]
 for phase in range(5):
  for pos in range(phase,len(xs)-4,5):
   # All unassigned/zero symbols minimized to zero: if minimum>=26,
   # no completion can make this group a legal0..25code.
   minimum=0
   for rune in xs[pos:pos+5]:minimum=2*minimum+int(rune in one)
   if minimum>=26:
    witnesses.append({'phase':phase,'start':pos,'minimum_code':minimum,'runes':xs[pos:pos+5],'source_char_positions':page['source_char_positions'][pos:pos+5]});break
  else:raise AssertionError(('unproved phase',nodeid,phase))
 leaves[f'page{page["page"]}']+=1;examples.setdefault(str(page['page']),{'proof_node':nodeid,'known_one_runes':sorted(one),'violations_all_phases':witnesses})
assert record['result']['status']=='UNSAT';check(record['result']['root'],set(),set());assert len(seen)==len(proof)
controlchecks=[]
for count in [14,15]:
 c=json.loads(gzip.decompress((B/f'S11-control{count}.json.gz').read_bytes()));mapping=c['result']['ones'];assert mapping.bit_count()==14
 for xs,decoded,truth in zip(c['runes'],c['decoded'],c['truth_pages']):
  phase=decoded['phase'];values=[]
  for pos in range(phase,len(xs)-4,5):
   value=0
   for r in xs[pos:pos+5]:value=2*value+((mapping>>r)&1)
   assert value<=25;values.append(value)
  assert values==[g['value'] for g in decoded['groups']]
  for g in truth['groups']:
   value=0
   for r in xs[g['start']:g['start']+5]:value=2*value+((c['ones_truth']>>r)&1)
   assert value==g['value']
 controlchecks.append({'truth_ones_count':count,'pages':len(c['runes']),'SAT_witness_and_truth_arithmetic':'PASS'})
r={'status':'PASS','proof_nodes':len(seen),'leaf_counts':dict(leaves),'first_page_leaf_examples':examples,'controls':controlchecks,'seconds':time.monotonic()-start};(B/'S11-independent-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='first_page_leaf_examples'},indent=2))
