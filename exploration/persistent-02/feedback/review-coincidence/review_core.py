"""Independent scalar complete-mask evaluator; no author decrypt/scoring calls."""
import itertools,random,json,pathlib,importlib.util,math
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];src=R/'exploration/persistent-02/section/coincidence/core.py';spec=importlib.util.spec_from_file_location('author',src);author=importlib.util.module_from_spec(spec);spec.loader.exec_module(author)
rng=random.Random(2026092304)
def enum(c,key,sign,periodic,resets,cut):
 sites=[i for i,x in enumerate(c) if x==0];paths=[]
 for bits in itertools.product([0,1],repeat=len(sites)):
  mask={i for i,b in zip(sites,bits) if b};p=[];at=0;seg=[];s=-1
  for i,x in enumerate(c):
   if i==0 or i in resets:at=0;s+=1
   if i in mask:y=0
   else:
    if not periodic and at>=len(key):break
    y=(x+sign*key[at%len(key)])%29;at+=1
   p.append(y);seg.append(s)
  else:
   full=sum(p[i]==p[j] and seg[i]==seg[j] for i in range(len(p)) for j in range(len(p)) if i!=j)
   pre=sum(p[i]==p[j] and seg[i]==seg[j] for i in range(cut) for j in range(cut) if i!=j)
   paths.append(dict(plain=p,mask=sorted(mask),full=full,prefix=pre))
 return paths
fixtures=[]
for ix in range(150):
 n=2+ix%8;c=[0 if rng.random()<.65 else rng.randrange(29) for _ in range(n)];key=[rng.randrange(29) for _ in range(1+ix%5)];periodic=ix%3!=0;sign=[-1,1][ix%2];cut=1+ix%(n-1);resets={i for i in range(n) if rng.random()<.25};paths=enum(c,key,sign,periodic,resets,cut)
 fixtures.append(dict(index=ix,cipher=c,key=key,periodic=periodic,sign=sign,cut=cut,resets=sorted(resets),expected_paths=paths))
# Preserve independent expected paths before calling author implementation.
(O/'core-fixtures.json').write_text(json.dumps(fixtures,separators=(',',':'))+'\n');results=[]
for x in fixtures:
 try:r=author.gridcase(x['cipher'],x['resets'],x['cut'],dict(key=x['key'],sign=x['sign'],id=str(x['index'])),x['periodic'])
 except author.NoLegalPath:
  assert not x['expected_paths'];results.append(dict(index=x['index'],no_legal=True));continue
 paths=x['expected_paths'];assert paths;fm=max(p['full'] for p in paths)
 # Prefix may admit paths whose finite key later exhausts; independently enumerate prefix too.
 prepaths=enum(x['cipher'][:x['cut']],x['key'],x['sign'],x['periodic'],x['resets'],x['cut']);pm=max(p['full'] for p in prepaths)
 admiss=[p for p in paths if p['prefix']==pm]
 cm=max((p['full']-p['prefix'] for p in admiss),default=None)
 assert (fm,pm,cm)==(r['full_maximum'],r['prefix_maximum'],r['continuation_maximum'])
 assert sum(p['full']==fm for p in paths)==r['full_tie_product']
 assert sum(p['full']==pm for p in prepaths)==r['prefix_tie_product']
 # Every segment row independently decrypts and has exact pair-count score.
 for group in r['full']+r['prefix']:
  a,b=group['start'],group['stop'];expect=enum(x['cipher'][a:b],x['key'],x['sign'],x['periodic'],[],b-a)
  assert len(expect)==group['result']['legal']
  for row in group['result']['rows']:assert any(p['plain']==row['plain'] and p['mask']==row['literal_positions'] and p['full']==row['score'] for p in expect)
 results.append(dict(index=x['index'],full=fm,prefix=pm,continuation=cm,legal_paths=len(paths)))
# Exact-cap refusal, not pruning.
try:author.segment([0]*4,[1],-1,True,mask_cap=8);raise AssertionError('missing refusal')
except author.Unresolved:pass
(O/'core-review.json').write_text(json.dumps(dict(status='PASS',cases=results,cap_refusal=True),indent=2)+'\n');print('PASS',len(results))
