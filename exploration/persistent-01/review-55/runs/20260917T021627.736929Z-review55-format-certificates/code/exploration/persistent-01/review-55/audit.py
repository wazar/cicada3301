from pathlib import Path
import json,gzip,hashlib,random,itertools,math
R=Path(__file__).resolve().parents[3];B=R/'exploration/persistent-01';N=B/'worker-n/N13';S=B/'worker-s';O=B/'review-55';F=B/'worker-f/F06-maps.json';pages=[p for p in json.loads(F.read_text()) if p['page'] in [0,1]];flat=[x for p in pages for x in p['indices']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
files=[F]+[p for p in N.iterdir() if p.is_file() and p.name!='MANIFEST.json']+[S/x for x in ['S16-CARD.md','S16-controls.json.gz','S16-result.json','s16.py','s16_verify.py']];snap=[dict(path=str(p.relative_to(R)),sha256=sha(p)) for p in files];save('inputs.json',snap)
def enc(x):
 L=x.bit_length();k=L.bit_length()-1;return ('0'*k)+format(L,'b')+format(x,'b')[1:]
def dec(bits):
 first=bits.find('1');assert first>=0;lengthbits=bits[first:2*first+1];assert len(lengthbits)==first+1;L=int(lengthbits,2);tail=bits[2*first+1:];assert len(tail)==L-1;return (1<<(L-1))+(int(tail,2) if tail else 0)
T={L:len(enc(1<<(L-1))) for L in range(1,321)};assert all(T[L]==L+2*int(math.log2(L)) for L in T);assert all(T[L+1]>T[L] for L in range(1,320));assert T[31]==39 and T[32]==42 and 40 not in T.values()
for x in range(1,65536):assert dec(enc(x))==x
for L in range(1,321):assert dec(enc((1<<L)-1))==(1<<L)-1 and len(enc((1<<L)-1))==T[L]
admissible={str(n):next((L for L in T if T[L]==5*n),None) for n in range(1,33)};required=set()
for n,L in admissible.items():
 if L:
  bits=enc(1<<(L-1));required.update(int(bits[j:j+5],2) for j in range(0,len(bits),5))
excluded=sorted(set(range(32))-required)[:3];assert excluded==[5,7,19] and len(required)==24
ctrl=json.loads(gzip.decompress((N/'controls-repaired.json.gz').read_bytes()));assert ctrl['admissible']==admissible and ctrl['excluded']==excluded;patterns=sorted(set(range(32))-set(excluded));rng=random.Random(1713092026);labels=list(range(29));rng.shuffle(labels);assert labels==ctrl['labels'] and patterns==ctrl['patterns'];mp=dict(zip(patterns,labels));proposals=0
expectedgrid=[(n,rep) for n in range(1,33) if admissible[str(n)] for rep in range(30)];assert [(x['n'],x['rep']) for x in ctrl['controls']]==expectedgrid
for row in ctrl['controls']:
 L=admissible[str(row['n'])];assert row['L']==L
 for k,p in enumerate(row['proposals']):
  start=rng.randrange(len(flat));salt=rng.getrandbits(max(1,L-1));v=0
  for j in range(max(1,L//4+1)):v=v*29+flat[(start+j)%len(flat)]
  integer=(1<<(L-1))+((v^salt)% (1<<(L-1)));bits=enc(integer);chunks=[int(bits[j:j+5],2) for j in range(0,len(bits),5)];accepted=all(x in mp for x in chunks);assert p==dict(source_start=start,salt=salt,integer=integer,chunks=chunks,accepted=accepted);assert accepted==(k==len(row['proposals'])-1);proposals+=1
 assert row['bits']==bits and row['runes']==[mp[x] for x in chunks] and dec(bits)==integer and len(bits)==5*row['n']
failed=json.loads((N/'failed-control.json').read_text());assert (failed['n'],failed['L'],failed['rep'])==(14,60,0) and len(failed['completed_controls'])==360 and len(failed['proposals'])==10000
# Retained rejected source integers prove mandatory forbidden header chunk, independently of RNG.
for p in failed['proposals']:
 bits=enc(p['integer']);assert p['integer'].bit_length()==60;chunks=[int(bits[j:j+5],2) for j in range(0,len(bits),5)];assert chunks==p['chunks'] and 30 in chunks[:3] and not p['accepted']
logs=sorted([json.loads(p.read_text()) for p in N.glob('runs/*/command.json')],key=lambda d:d['started_utc']);assert [x['exit_code'] for x in logs]==[1,1,0,0]
actual=json.loads((N/'actual.json').read_text());assert actual['source_sha256']==sha(F);bad=[]
for d,p in zip(actual['pages'],pages):
 expectedbad=[];assert d['page']==p['page'] and d['units']==len(p['words'])
 for i,w in enumerate(p['words']):
  n=w['end']-w['start'];L=next((L for L in T if T[L]==5*n),None);row=d['all_units'][i];assert row['word']==i and row['map']==w and row['runes']==p['indices'][w['start']:w['end']] and row['length']==n and row['bits']==5*n and row['integer_bitlength']==L
  if L is None:
   q=next(x for x in d['violations'] if x['word']==i);assert q['lower_L']==31 and q['lower_T']==39 and q['upper_L']==32 and q['upper_T']==42 and n==8;expectedbad.append(i)
 assert len(expectedbad)==len(d['violations']);bad.append(dict(page=p['page'],word_indices=expectedbad))
# Independent direct total-order tests for canonical necklaces.
c=json.loads(gzip.decompress((S/'S16-controls.json.gz').read_bytes()));assert c['source_sha256']==sha(F);rng=random.Random(1709202616)
def least(word,order):
 key={x:j for j,x in enumerate(order)};rotations=[word[j:]+word[:j] for j in range(len(word))];return min(range(len(word)),key=lambda j:[key[x] for x in rotations[j]])
def valid(words,order):return all(word==word[least(word,order):]+word[:least(word,order)] for word in words)
def inequalities(words):
 es=[]
 for wi,w in enumerate(words):
  for rot in range(1,len(w)):
   a=w[rot:]+w[:rot];m=next((k for k,(x,y) in enumerate(zip(w,a)) if x!=y),None)
   if m is not None:es.append(dict(word_index=wi,rotation=rot,mismatch=m,a=w[m],b=a[m]))
 return es
for j,row in enumerate(c['panels']):
 p=pages[j%2];order=list(range(29));rng.shuffle(order);assert order==row['order'] and row['page']==p['page'] and row['rep']==j//2;raw=[[rng.randrange(29) for _ in range(w['end']-w['start'])] for w in p['words']];rot=[least(w,order) for w in raw];canonical=[w[k:]+w[:k] for w,k in zip(raw,rot)];assert raw==row['raw_circles'] and rot==row['rotations'] and canonical==row['canonical'];assert valid(canonical,row['result']['order']) and row['result']['feasible'];assert inequalities(canonical)==row['result']['edges']
tinies=[]
for n,length,paired in [(3,4,True),(4,3,False)]:
 words=[list(x) for z in range(1,length+1) for x in itertools.product(range(n),repeat=z)];orders=list(itertools.permutations(range(n)));sets=[{j for j,o in enumerate(orders) if valid([w],o)} for w in words];groups=itertools.combinations_with_replacement(range(len(words)),2) if paired else [(i,) for i in range(len(words))];total=feasible=0
 for ids in groups:
  possible=set(range(len(orders)))
  for i in ids:possible &= sets[i]
  total+=1;feasible+=bool(possible)
 tinies.append(dict(n=n,maxlen=length,word_count=len(words),orders=len(orders),panels=total,feasible=feasible))
assert tinies==c['tiny']
for x in c['bad']:assert not any(valid(x['words'],o) for o in itertools.permutations(range(3)))
a=json.loads((S/'S16-result.json').read_text());assert a['source_sha256']==sha(F);cycles=[]
for row,p in zip(a['pages'],pages):
 words=[p['indices'][w['start']:w['end']] for w in p['words']];assert row['words']==words;es=inequalities(words);actuales=[{k:e[k] for k in ['word_index','rotation','mismatch','a','b']} for e in row['result']['edges']];assert es==actuales;cycle=row['result']['cycle'];assert len(cycle)==3 and cycle[0]==cycle[-1] and cycle[0]!=cycle[1]
 for k,e in enumerate(row['result']['witness']):
  w=words[e['word_index']];wm=p['words'][e['word_index']];rot=e['rotation'];j=e['mismatch'];assert w[:j]==(w[rot:]+w[:rot])[:j];assert [w[j],w[(j+rot)%len(w)]]==cycle[k:k+2];assert e['word_map']==wm and e['runes']==w and e['source_a']==p['source_char_positions'][wm['start']+j] and e['source_b']==p['source_char_positions'][wm['start']+(j+rot)%len(w)]
 cycles.append(dict(page=p['page'],cycle=cycle,edges=len(es),witness=row['result']['witness']))
assert all(sha(R/x['path'])==x['sha256'] for x in snap)
save('result.json',dict(pass_all=True,N13=dict(roundtrips=65535,length_endpoints=640,repaired_controls=len(ctrl['controls']),proposals=proposals,retained_failed_proposals=10000,required_pattern_count=24,excluded=excluded,failures_preserved=[x['exit_code'] for x in logs],actual_violations=bad),S16=dict(controls=40,tiny=tinies,cycles=cycles),limits='Necessary conditions only; no cipher-family or language exclusion.'))
print('N13/S16 PASS')
