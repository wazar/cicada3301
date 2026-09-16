import pathlib,json,gzip,hashlib,math,collections,re,zlib,statistics,tarfile,datetime
import numpy as np
R=pathlib.Path(__file__).resolve().parents[3]; O=pathlib.Path(__file__).resolve().parent; D=R/'exploration/persistent-01/worker-i/p11'; P=D/'publication'
def j(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def gz(p):return json.loads(gzip.decompress(p.read_bytes()))
def stop():assert not (R/'exploration/persistent-01/STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'; TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
def parse(t):
 p=[];e=[]
 for w in re.findall('['+ABC+']+',t):p.extend(ABC.index(x) for x in w);e.append(len(p)-1)
 return p,e
cfg=j(R/'exploration/persistent-01/config.json'); data=R/'audit/parallel-01/inputs/dataset.json';assert sha(data.read_bytes())==cfg['dataset_sha256']
pages={p['original_page']:p for p in j(data)['pages'] if p['original_page']<=55 and p['original_page'] not in cfg['reserved_original_pages']};assert len(pages)==45
# Independent smallest-prime-factor recurrence, distinct from worker phi sieve.
spf=list(range(15001))
for p in range(2,123):
 if spf[p]==p:
  for n in range(p*p,15001,p):
   if spf[n]==n:spf[n]=p
phi=[0,1]
for n in range(2,15001):
 p=spf[n];m=n//p;phi.append(phi[m]*(p if m%p==0 else p-1))
assert all(phi[n]==sum(math.gcd(n,k)==1 for k in range(1,n+1)) for n in range(1,129))
k=[v%29 for v in phi[1:]];stored=np.load(D/'phi.npz');assert stored['integer_phi'].tolist()==phi[1:] and stored['mod29'].tolist()==k
manifest=j(P/'raw-retention-manifest.json'); summary=j(D/'summary.json'); coverage=j(P/'coverage-counts.json'); source=j(D/'manifest.json')
assert sha(np.array(k,dtype=np.int64).tobytes())==source['phi_hash']
for r in manifest['code_and_scorer_hashes']+source['frozen_lm_sources']+j(D/'pilot-source-manifest.json')['additional_source_hashes']:
 assert sha((R/r['path']).read_bytes())==r['sha256'],r['path']
for r in j(R/'exploration/persistent-01/worker-c/p03-frozen-manifest.json'):
 if r['path'].endswith('p03_frozen.py') or r['path'] in [x['path'] for x in source['frozen_lm_sources']]:assert sha((R/r['path']).read_bytes())==r['sha256']
queue=[dict(offset=o,sign=s,page=p) for o in range(128) for s in [-1,1] for p in pages];assert queue==j(D/'queue.json');assert sha(json.dumps(queue,sort_keys=True).encode())==source['queue_sha256']
inputs={}
for pid,p in pages.items():
 c,e=parse('/'.join(l['raw'] for l in p['lines']));assert c==p['indices'];nz=[i for i,v in enumerate(c) if v];v=np.array(c)[nz];np.random.default_rng(190020+pid).shuffle(v);null=c.copy()
 for i,x in zip(nz,v):null[i]=int(x)
 assert [i for i,x in enumerate(null) if x==0]==[i for i,x in enumerate(c) if x==0] and sorted(null)==sorted(c)
 inputs[pid]={'real':c,'null':null,'ends':e}
 assert len({tuple(s*x%29 for x in k[o:o+len(c)]) for o in range(128) for s in [-1,1]})==256
selected=set(manifest['retained_cell_ordinals']);assert len(selected)==223
counts={m:{s:0 for s in ['english','rune']} for m in ['real','null']}; scores=collections.defaultdict(list);leaders={};replays=0

def replay(a,c,ends,o,s):
 global replays
 p=a['plain']; literal=a['literal_positions'];assert len(p)==len(c) and literal==sorted(set(literal));literal=set(literal);u=0;before=[];after=[];out=[]
 for i,v in enumerate(p):
  assert 0<=v<29;before.append(u)
  if i in literal:assert v==0;out.append(0)
  else:out.append((v-s*k[o+u])%29);u+=1
  after.append(u)
 assert out==c and u==a['used'] and before==a['key_index_before'] and after==a['key_index_after'] and a['reencryption']
 assert a['boundary_consumption']==[dict(site=i,before=before[i],after=after[i],absolute_after=o+after[i]) for i in ends]
 replays+=1

def stats(p):
 n=len(p);c=collections.Counter(p)
 return dict(ioc_times_n=sum(v*(v-1) for v in c.values())/max(1,n-1),min_distinct_32=min(len(set(p[i:i+32])) for i in range(max(1,n-31))),zlib_ratio=len(zlib.compress(bytes(p)))/max(1,n),nonenglish_lm=None)
with gzip.open(P/'all-cell-selected-statistics.jsonl.gz','rt') as f:
 for ix,line in enumerate(f):
  if ix%256==0:stop()
  row=json.loads(line);mr=manifest['raw_shards'][ix];b=(R/mr['path']).read_bytes();assert len(b)==mr['bytes'] and sha(b)==mr['sha256'];r=json.loads(gzip.decompress(b));cell=queue[ix];assert r['ordinal']==row['ordinal']==ix and r['cell']==cell and all(row[x]==v for x,v in cell.items())
  if ix in selected:assert (P/'retained-candidate-cells'/f'cell-{ix:05}.json.gz').read_bytes()==b
  for mode,rr in r['output'].items():
   assert rr['cipher']==inputs[cell['page']][mode] and rr['ends']==inputs[cell['page']]['ends'];assert {m['model'] for m in rr['models']}=={'english','rune'}
   for m in rr['models']:
    model=m['model'];a=m['alternatives'][0];assert all(x['score']>=y['score'] for x,y in zip(m['alternatives'],m['alternatives'][1:]));counts[mode][model]+=len(m['alternatives'])
    expected=dict(score=a['score'],english=a['english'],rune_lm=a['rune_lm'],statistics=a['statistics'],runes_sha256=sha(bytes(a['plain'])),n=len(a['plain']),used=a['used'],literal_count=len(a['literal_positions']),alternatives=len(m['alternatives']),reencryption_all=all(z['reencryption'] for z in m['alternatives']),diagnostics=m['diagnostics'])
    assert row['outputs'][mode][model]==expected;assert a['statistics']==stats(a['plain']);assert abs(a['score']-a['english' if model=='english' else 'rune_lm'])<1e-9
    scores[(mode,model)].append((a['score'],ix,cell['page'])); lk=(mode,model,cell['page'])
    if lk not in leaders or a['score']>leaders[lk][0]:leaders[lk]=(a['score'],ix)
    if ix in selected:
     for a in m['alternatives']:replay(a,rr['cipher'],rr['ends'],cell['offset'],cell['sign'])
  if ix%2048==0:print('raw_rows_verified',ix+1,flush=True)
assert ix+1==len(manifest['raw_shards'])==11520
assert counts==manifest['retained_alternative_counts']==coverage['actual_retained_paths'];assert sum(map(sum,[v.values() for v in counts.values()]))==686080
assert sum(x['bytes'] for x in manifest['raw_shards'])==manifest['raw_bytes']==187082357
metrics={}; chosen=set(v[1] for v in leaders.values())
for model in ['english','rune']:
 diffs=[]
 for mode in ['real','null']:
  ss=sorted(scores[(mode,model)],key=lambda x:x[0],reverse=True);expected=summary['models'][model][mode];assert ss[0][0]==expected['maximum'];assert ss[0][1]==expected['leading_cell']['ordinal'];assert [x[1] for x in ss[:20]]==expected['top20_ordinals'];chosen.update(x[1] for x in ss[:20])
 for pid in pages:diffs.append(leaders[('real',model,pid)][0]-leaders[('null',model,pid)][0]);assert sum(x[2]==pid for x in scores[('real',model)])==256
 metrics[model]=dict(real_max=max(x[0] for x in scores[('real',model)]),null_max=max(x[0] for x in scores[('null',model)]),wins=sum(d>0 for d in diffs),median=statistics.median(diffs))
assert chosen==selected
selected_replays=replays; controls={}
# Verify tar content against all local complete controls, without extraction.
with tarfile.open(P/'full-controls.tar.gz') as tar:
 for member in tar.getmembers():
  if member.isfile():assert tar.extractfile(member).read()==(D/member.name).read_bytes()
for name in ['0_welcome','p56_an_end']:
 fixture=j(D/'controls'/f'{name}-fixture.json');plain,ends=parse((R/'audit/parallel-01/reference/sources'/f'solved_{name}.txt').read_text());assert plain==fixture['plain'] and ends==fixture['ends'];assert fixture['literal_positions']==[i for i,x in enumerate(plain) if x==0]
 u=0;cipher=[]
 for x in plain:
  if x==0:cipher.append(0)
  else:cipher.append((x-fixture['sign']*k[fixture['offset']+u])%29);u+=1
 assert cipher==fixture['cipher'] and u==fixture['used']
 for model in ['english','rune']:
  keyrows=[];pathn=0;truth=None
  for ix,(o,s) in enumerate((o,s) for o in range(128) for s in [-1,1]):
   r=gz(D/'controls'/f'{name}-{model}'/f'{ix:03}.json.gz');assert r['offset']==o and r['sign']==s and r['model']==model
   for a in r['alternatives']:replay(a,cipher,ends,o,s)
   pathn+=len(r['alternatives']);keyrows.append(dict(offset=o,sign=s,score=r['alternatives'][0]['score']))
   if (o,s)==(fixture['offset'],fixture['sign']):truth=r
  saved=j(D/'controls'/f'{name}-{model}-summary.json');keyrows.sort(key=lambda r:r['score'],reverse=True);assert keyrows==saved['ranked_keys'];assert (keyrows[0]['offset'],keyrows[0]['sign'])==(fixture['offset'],fixture['sign']);assert truth['alternatives'][0]['plain']==plain;assert saved['truth_key_rank']==1 and saved['planted_top_rune_errors']==0 and saved['truth_in_top16'];assert pathn==coverage['controls'][f'{name}-{model}']['retained_paths'];controls[f'{name}-{model}']=dict(cells=256,paths=pathn,rank=1,errors=0)
# Complete leading outputs plus next two alternatives, unchanged transliteration.
texts=[]
for model in ['english','rune']:
 for mode in ['real','null']:
  ix=max(scores[(mode,model)])[1];r=gz(D/'search'/f'cell-{ix:05}.json.gz');m=next(m for m in r['output'][mode]['models'] if m['model']==model)
  texts.append(dict(mode=mode,model=model,cell=r['cell'],alternatives=[dict(score=a['score'],text=''.join(TOK[v] for v in a['plain']),plain=a['plain'],literal_positions=a['literal_positions'],used=a['used']) for a in m['alternatives'][:3]]))
(O/'leading-outputs.json').write_text(json.dumps(texts,indent=2)+'\n')
result=dict(status='PASS',rows=11520,beams=46080,paths=counts,actual_paths=686080,selected_cells=223,selected_reencrypted_paths=selected_replays,control_reencrypted_paths=replays-selected_replays,controls=controls,metrics=metrics,raw_bytes=187082357,phi_verified_values=15000,gcd_verified_values=128,null_pages_verified=45,aliases=0,alias_definition=coverage['alias_definition'],scope='All compact/raw rows; independent selected/full-control replay, not full raw-path replay or rerun search; no independent language training evidence.')
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
