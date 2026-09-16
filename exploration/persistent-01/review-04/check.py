import pathlib,json,gzip,hashlib,collections,heapq,itertools,math,datetime
R=pathlib.Path.cwd(); O=R/'exploration/persistent-01/review-04'; J=R/'exploration/persistent-01/worker-j'
def guard():
 assert not (O.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def read(n):return json.loads((J/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def collision(ns):return sum(n*(n-1)//2 for n in ns)
def cost(n,k):
 # Independently: sum of max(n-j*k,0) over positive j (balanced load pair count).
 m=(n-1)//k
 return m*n-k*m*(m+1)//2
def alloc(ns,slots=29):
 ns=[n for n in ns if n]; assert len(ns)<=slots
 ks=[1]*len(ns);heap=[(-(cost(n,1)-cost(n,2)),i) for i,n in enumerate(ns)];heapq.heapify(heap)
 for _ in range(slots-len(ns)):
  _,i=heapq.heappop(heap);ks[i]+=1;k=ks[i];n=ns[i];heapq.heappush(heap,(-(cost(n,k)-cost(n,k+1)),i))
 return sum(cost(n,k) for n,k in zip(ns,ks)),ks

guard(); manifest=read('CHECKPOINT-MANIFEST.json')
for f in manifest['files']:assert sha(R/f['path'])==f['sha256'],f['path']
print('HASH_ACK',sha(J/'CHECKPOINT-MANIFEST.json'),'files',len(manifest['files']),flush=True)
# All small compositions, independently enumerated allocation frontier.
small=0
for m in range(1,5):
 for ns in itertools.product(range(1,7),repeat=m):
  for slots in range(m,m+4):
   best=min(sum(cost(n,k) for n,k in zip(ns,ks)) for ks in itertools.product(range(1,slots-m+2),repeat=m) if sum(ks)==slots)
   assert alloc(ns,slots)[0]==best;small+=1
for n in range(1,1000):
 cs=[cost(n,k) for k in range(1,31)]
 assert all(cs[i]-cs[i+1]>=cs[i+1]-cs[i+2] for i in range(28))
print('small_exhaustive',small,flush=True)
D=read('j01-results.json'); C=read('j02-results.json'); E=read('j03-exact-checkpoint.json'); V=read('j02-verify-results.json')
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
T=[x['transliteration'] for x in json.loads((R/'KNOWLEDGE.json').read_text())['gematria_primus']['table']]
assert T==read('j03-results.json')['transliteration']
texts={};latin={};maps={}
for c in D['controls']:
 if c['mode']!='original':continue
 p=R/'audit/parallel-01/reference/sources'/('solved_'+c['name']+'.txt')
 assert sha(p)==next(x['sha256'] for x in D['source_files'] if x['path']==str(p.relative_to(R)))
 raw=[ABC.index(x) for x in p.read_text() if x in ABC];s=[(i+1)%29 for i in raw];assert s==c['source'];texts[c['name']]=s
 latin[c['name']]=[ord(ch)-65 for i in raw for ch in T[i]]
 maps[c['name']]=[{'source_rune_index':ix,'rune':i,'letter_offset':j} for ix,i in enumerate(raw) for j in range(len(T[i]))]
for profile,names in zip(C['profiles'],[list(texts)[:5],list(texts)[5:]]):
 counts=collections.Counter(x for name in names for x in texts[name]);ns=[counts[i] for i in range(29)]
 assert names==profile['groups'] and ns==profile['counts']
 assert [n/sum(ns) for n in ns]==profile['probabilities']
assert [p['page'] for p in D['real']]==[0,1,3,7,17]
for p,a in zip(D['real'],C['actual']):
 assert collision(collections.Counter(p['cipher']).values())==a['pairs']; assert len(p['cipher'])==a['n']
# All stored windows re-derived from original solved files; greedy independent of worker DP.
models={};cached={};windowtotal=0
for label,src in [('j02',texts),('j03',latin)]:
 guard();W=json.load(gzip.open(J/(label+'-windows.json.gz'),'rt'));cached[label]=W
 if label=='j03':
  for t in W['texts']:assert t['source']==latin[t['name']] and t['source_map']==maps[t['name']]
 dist={0:1};den=1;conj=1;stats=[];worst=0
 for n,ws,a in zip(W['lengths'],W['windows'],C['actual']):
  expected=[(name,start) for name,s in src.items() if len(s)>=max(W['lengths']) for start in range(len(s)-n+1)]
  assert expected==[(w['group'],w['start']) for w in ws]
  hist=collections.Counter()
  for w in ws:
   cc=collections.Counter(src[w['group']][w['start']:w['start']+n]);cts=[cc[i] for i in range(29 if label=='j02' else 26)]
   assert cts==w['counts'];v,ks=alloc(cts);assert v==w['bound'];hist[v]+=1;windowtotal+=1
  nd=collections.Counter()
  for s,c in dist.items():
   for x,d in hist.items():nd[s+x]+=c*d
  dist=nd;den*=len(ws);assert sum(dist.values())==den;worst=max(worst,den)
  hit=sum(c for v,c in hist.items() if v<=a['pairs']);conj*=hit
  stats.append({'page':a['page'],'n':n,'windows':len(ws),'minimum':min(hist),'compatible':hit,'source_weights':dict(collections.Counter(w['group'] for w in ws))})
 num=sum(c for v,c in dist.items() if v<=sum(a['pairs'] for a in C['actual']))
 ref=next(x for x in E if x['model']==label)
 assert (num,den,conj)==(ref['aggregate_numerator'],ref['denominator'],ref['conjunction_numerator'])
 models[label]={'aggregate_numerator':num,'denominator':den,'conjunction_numerator':conj,'aggregate':num/den,'conjunction':conj/den,'stats':stats,'max_nonnegative_intermediate_total':worst,'below_int64':worst<2**63}
 print(label,json.dumps(models[label]),flush=True)
# Verify all retained random draw counts/bounds (RNG recurrence intentionally not duplicated).
samples=collections.defaultdict(list); pagechecks=0
with gzip.open(J/'j02-sampling.jsonl.gz','rt') as f:
 for line in f:
  x=json.loads(line)
  if len(samples[x['model']])%500==0:guard()
  for i,(cts,b,a) in enumerate(zip(x['counts'],x['bounds'],C['actual'])):
   assert sum(cts)==a['n'] and min(cts)>=0 and alloc(cts)[0]==b;pagechecks+=1
   if x['model']=='contiguous_windows':
    w=cached['j02']['windows'][i][x['window_indices'][i]];assert cts==w['counts'] and b==w['bound']
  assert sum(x['bounds'])==x['total'];samples[x['model']].append(x['total'])
for s in C['summaries']:
 vals=sorted(samples[s['model']]);assert len(vals)==9999 and min(vals)==s['total_bound_quantiles'][0] and vals[4999]==s['total_bound_quantiles'][3]
 assert sum(v<=5196 for v in vals)==s['compatible_bound_count']==0
# Every saved attained allocation, including actual-size follow-up and J03.
attain=0
for c in C['controls']+V['controls']+read('j03-results.json')['controls']:
 cts=c.get('counts',c.get('window',{}).get('counts'));k=c['allocation'];value=alloc(cts,c.get('slots',29))[0]
 assert value==c['bound']==collision(collections.Counter(c['cipher']).values())
 assert sum(cost(n,s) for n,s in zip([x for x in cts if x],k))==value;attain+=1
# Recompute every sensitivity witness; resolve selected p17 window from source independently.
w=min(cached['j02']['windows'][-1],key=lambda x:x['bound']);assert w==V['p17_min_window'];edits=[]
for i,c in enumerate(w['counts']):
 if not c:continue
 for j in range(29):
  if i==j:continue
  cc=w['counts'].copy();cc[i]-=1;cc[j]+=1;v,k=alloc(cc);edits.append({'from':i,'to':j,'bound':v})
assert edits==V['one_edit_results'];hits=[e for e in edits if e['bound']<=1256]
assert len(hits)==52 and min(e['bound'] for e in edits)==1252
out={'manifest_sha256':sha(J/'CHECKPOINT-MANIFEST.json'),'manifest_files':len(manifest['files']),'small_exhaustive_cases':small,'all_window_checks':windowtotal,'sampled_page_bounds_checked':pagechecks,'sample_counts':{k:len(v) for k,v in samples.items()},'attainment_controls':attain,'models':models,'sensitivity':{'window':w,'compatible_edits':len(hits),'minimum':1252,'witness':min(edits,key=lambda e:e['bound'])},'source_files':D['source_files'],'documented_gp_table':'KNOWLEDGE.json gematria_primus.table','gp_table_sha256':sha(R/'KNOWLEDGE.json')}
(O/'results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',json.dumps({k:v for k,v in out.items() if k not in ['models','source_files','sensitivity']}),flush=True)
