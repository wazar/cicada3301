import json,pathlib,random,itertools,hashlib
BASE=pathlib.Path('exploration/persistent-01/worker-s');SOURCE=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json');rng=random.Random(1709202606)
pages=[p for p in json.loads(SOURCE.read_text()) if p['page'] in [0,1]]
def compositions(n):
 if n==0:return [()]
 return [(k,)+rest for k in (2,3) if k<=n for rest in compositions(n-k)]
checks=[]
for n in range(2,15):
 independent=[]
 for mask in range(1<<(n-1)):
  cuts=[0]+[i for i in range(1,n) if mask>>(i-1)&1]+[n];sizes=tuple(b-a for a,b in zip(cuts,cuts[1:]))
  if all(k in (2,3) for k in sizes):independent.append(sizes)
 assert sorted(independent)==sorted(compositions(n));checks.append({'length':n,'cut_masks':1<<(n-1),'tilings':len(independent)})
def analyze(xs,words):
 forced={};rows=[];excluded=[]
 for wi,w in enumerate(words):
  seq=xs[w['start']:w['end']]
  if len(seq)==1:excluded.append(wi);continue
  tilings=[]
  for sizes in compositions(len(seq)):
   offset=0;tiles=[]
   for k in sizes:
    tiles.append({'token':seq[offset:offset+k],'positions':[w['start']+offset,w['start']+offset+k]});offset+=k
   assert offset==len(seq);tilings.append(tiles)
  assert tilings
  intersection=set(tuple(t['token']) for t in tilings[0])
  for ts in tilings[1:]:intersection&={tuple(t['token']) for t in ts}
  for token in intersection:
   assert all(any(tuple(t['token'])==token for t in ts) for ts in tilings)
   forced.setdefault(token,[]).append(wi)
  rows.append({'word_index':wi,'map':w,'runes':seq,'all_tilings':tilings,'forced_tokens':sorted(intersection)})
 tokens=sorted(forced,key=lambda x:(len(x),x))
 return {'forced_lower_bound':len(tokens),'rules_out_29':len(tokens)>29,'forced_entries':[{'token':t,'supporting_words':forced[t]} for t in tokens],'certificate30':[{'token':t,'supporting_word':forced[t][0]} for t in tokens[:30]] if len(tokens)>29 else [],'words':rows,'literal_exempt_words':excluded}
controls=[]
for rep in range(30):
 dictionary=[]
 for k,count in [(2,14),(3,15)]:
  chosen=set()
  while len(chosen)<count:chosen.add(tuple(rng.randrange(29) for _ in range(k)))
  dictionary.extend(sorted(chosen))
 cp=[]
 for p in pages:
  xs=[];paths=[]
  for w in p['words']:
   n=w['end']-w['start']
   if n==1:xs.append(rng.randrange(29));paths.append({'literal':xs[-1]});continue
   sizes=rng.choice(compositions(n));tokens=[rng.choice([t for t in dictionary if len(t)==k]) for k in sizes];xs.extend(v for t in tokens for v in t);paths.append({'tokens':tokens})
  result=analyze(xs,p['words']);assert result['forced_lower_bound']<=29
  assert all(tuple(e['token']) in dictionary for e in result['forced_entries'])
  cp.append({'page':p['page'],'runes':xs,'paths':paths,'bound':result['forced_lower_bound'],'forced_entries':result['forced_entries']})
 controls.append({'rep':rep,'dictionary':dictionary,'pages':cp})
real=[]
for p in pages:
 r=analyze(p['indices'],p['words']);r['page']=p['page'];real.append(r)
summary={'seed':1709202606,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'composition_checks':checks,'control_dictionaries':30,'control_pages':60,'all_controls_accept':True,'real':[{'page':r['page'],'forced_lower_bound':r['forced_lower_bound'],'rules_out_29':r['rules_out_29'],'literal_exempt_words':len(r['literal_exempt_words']),'all_tilings_evaluated':sum(len(w['all_tilings']) for w in r['words'])} for r in real]}
(BASE/'S06-result.json').write_text(json.dumps({'summary':summary,'real':real,'controls':controls},indent=2)+'\n');print(json.dumps(summary,indent=2))
