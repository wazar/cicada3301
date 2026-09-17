import pathlib,json,collections,random,gzip,math,datetime,hashlib
B=pathlib.Path('exploration/persistent-01');D=B/'worker-p/P07';assert not (B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00');rng=random.Random(130107)
primes=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
generated=[n for n in range(2,110) if all(n%d for d in range(2,math.isqrt(n)+1))];assert primes==generated
m=json.load(open(B/'worker-g/g06-source-gap-map.json'));data=json.load(open('audit/parallel-01/inputs/dataset.json'));pages={p['original_page']:p for p in data['pages'] if p['original_page'] in [3,7,17]};fields=[];empty=[];marker_maps=[]
for page in [3,7,17]:
 signs=[g for g in m if g['page']==page and g['image']['count']==13];signs.sort(key=lambda g:(g['image']['line'],g['image']['center'][0]));marker_maps.append(dict(page=page,signs=signs))
 for a,b in zip(signs,signs[1:]):
  lo,hi=a['rune_gap'],b['rune_gap'];assert hi>=lo;row=dict(page=page,start=lo,end=hi,bounding_markers=[a,b],source_char_positions=pages[page]['source_char_positions'][lo:hi])
  (fields if hi>lo else empty).append(row)
assert [(f['page'],f['start'],f['end']) for f in fields]==[(3,16,119),(3,119,122),(7,194,208)]
residue_pairs={r:[(i,j) for i in range(29) for j in range(29) if (primes[i]+primes[j])%29==r] for r in range(29)};assert all(residue_pairs.values())
def evaluate(streams):
 profiles=[]
 for page in [3,7]:
  c=streams[page];n=len(c);spans=[f for f in fields if f['page']==page];per=[]
  for shift in range(n):per.append([sum(primes[c[(i+shift)%n]] for i in range(f['start'],f['end']))%29 for f in spans])
  counts=[sum(v==0 for v in r) for r in per];profiles.append(dict(page=page,length=n,residues_by_phase=per,zero_counts=counts,histogram=dict(collections.Counter(counts))))
 hist=collections.Counter()
 for a,x in profiles[0]['histogram'].items():
  for b,y in profiles[1]['histogram'].items():hist[a+b]+=x*y
 actual=[v for p in profiles for v in p['residues_by_phase'][0]];success=sum(v==0 for v in actual);den=math.prod(p['length'] for p in profiles);num=sum(v for k,v in hist.items() if k>=success);assert sum(hist.values())==den
 return dict(residues=actual,successes=success,profiles=profiles,null_histogram=dict(hist),tail_numerator=num,tail_denominator=den,tail=num/den)
streams={p:pages[p]['indices'] for p in [3,7]};real=evaluate(streams);direct=collections.Counter(a+b for a in real['profiles'][0]['zero_counts'] for b in real['profiles'][1]['zero_counts']);assert dict(direct)==real['null_histogram']
controls=[];ordinary=[]
for rep in range(30):
 assert not (B/'STOP').exists();s={p:[rng.randrange(29) for _ in pages[p]['indices']] for p in [3,7]};raw={p:c[:] for p,c in s.items()};patches=[]
 for f in fields:
  page=f['page'];lo,hi=f['start'],f['end'];target=(-sum(primes[v] for v in s[page][lo:hi-2]))%29;pair=rng.choice(residue_pairs[target]);s[page][hi-2:hi]=pair;assert sum(primes[v] for v in s[page][lo:hi])%29==0;patches.append(dict(page=page,positions=[hi-2,hi-1],pair=pair,target=target))
 r=evaluate(s);assert r['successes']==3;controls.append(dict(rep=rep,streams=s,patches=patches,result=r));ordinary.append(dict(rep=rep,streams=raw,result=evaluate(raw)))
out=dict(real=real,streams=streams,fields=fields,empty_fields=empty,marker_maps=marker_maps,controls=controls,ordinary=ordinary,prime_table=primes,pair_coverage={r:len(v) for r,v in residue_pairs.items()},seed=130107)
with gzip.open(D/'evidence.json.gz','wt') as f:json.dump(out,f)
summary=dict(fields=[{k:v for k,v in f.items() if k not in ['bounding_markers','source_char_positions']} for f in fields],real={k:v for k,v in real.items() if k!='profiles'},empty_spans=len(empty),page17_eligible=0,control_count=30,control_exact_checksum=30,control_tail_le005=sum(c['result']['tail']<=.05 for c in controls),control_tails=[c['result']['tail'] for c in controls],ordinary_tail_le005=sum(c['result']['tail']<=.05 for c in ordinary),ordinary_tails=[c['result']['tail'] for c in ordinary],distinct_page_phase_pairs=real['tail_denominator'],evaluation_packets=61)
(D/'results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
