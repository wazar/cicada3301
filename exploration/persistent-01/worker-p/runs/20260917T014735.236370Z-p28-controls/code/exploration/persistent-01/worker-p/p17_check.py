import gzip,json,random,re,pathlib
R=pathlib.Path(__file__).resolve().parent;O=R/'P17';ROOT=R.parents[2]
load=lambda n:json.load(gzip.open(O/(n+'.json.gz'),'rt'))
source=load('source');raw=(O/'pg45315.txt').read_bytes().decode('utf-8-sig');assert raw==source['raw']
singles=dict(zip('FUTHORCGWHNIJPS TBEMLDAXY'.replace(' ',''),[])) if False else {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,'D':23,'A':24,'Y':26,'V':1,'K':5,'Z':15,'Q':5}
doubles={'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'EA':28}
for w in source['words']:
 a,b=w['span'];assert raw[a:b]==w['text'];text=w['text'].replace("'",'').replace('’','').upper();i=0;out=[]
 while i<len(text):
  if text[i:i+2] in doubles:out.append(doubles[text[i:i+2]]);i+=2
  else:out.append(singles[text[i]]);i+=1
 assert out==w['runes']
lengths=source['lengths'];assert lengths==[len(w['runes']) for w in source['words']]
cache={}
def independent(seqs):
 lo=0;hi=min(len(lengths),max(map(len,seqs)))
 while lo<hi:
  n=(lo+hi+1)//2
  if n not in cache:cache[n]={tuple(lengths[j:j+n]) for j in range(len(lengths)-n+1)}
  if any(tuple(seq[j:j+n]) in cache[n] for seq in seqs for j in range(len(seq)-n+1)):lo=n
  else:hi=n-1
 return lo
controls=load('controls');checked=0
for ix,c in enumerate(controls):
 assert independent(c['sequences'])==c['best'];rng=random.Random(331700+ix)
 for pp,target in zip(c['permutations'],c['null']):
  expected=[rng.sample(range(len(x)),len(x)) for x in c['sequences']];assert pp==expected;sh=[[x[i] for i in p] for x,p in zip(c['sequences'],pp)];assert independent(sh)==target;checked+=1
 assert c['tail']==(1+sum(v>=c['best'] for v in c['null']))/100
actual=load('actual');maps=json.loads((ROOT/'exploration/persistent-01/worker-f/F06-maps.json').read_text());seqs=[[w['end']-w['start'] for w in m['words']] for m in maps];assert seqs==actual['real_sequences'];assert independent(seqs)==actual['max_exact_units'];rng=random.Random(331719)
for pp,target in zip(actual['permutations'],actual['null']):
 assert pp==[rng.sample(range(len(x)),len(x)) for x in seqs]
 sh=[[x[i] for i in p] for x,p in zip(seqs,pp)];assert independent(sh)==target;checked+=1
assert actual['tail']==(1+sum(v>=actual['max_exact_units'] for v in actual['null']))/1000
for h in actual['hits']:
 n=h['length'];j=h['source_start'];i=h['page_start'];assert lengths[j:j+n]==seqs[h['page_index']][i:i+n];a,b=h['source_span'];assert raw[a:b]==h['source_text']
result=dict(status='PASS',source_words=len(lengths),independent_mapping=True,null_maxima_verified=checked,control_and_actual_maxima_verified=3,source_span_hits=len(actual['hits']),max_exact_units=actual['max_exact_units'],tail=actual['tail'])
(O/'check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
