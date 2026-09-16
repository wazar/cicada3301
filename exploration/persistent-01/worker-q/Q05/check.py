import pathlib,json,gzip,math
R=pathlib.Path(__file__).parent;d=json.load(gzip.open(R/'evidence.json.gz','rt'));primes=d['prime_table']
def phi(n):
 left=n;out=n;p=2
 while left>1:
  if left%p==0:
   out=out//p*(p-1)
   while left%p==0:left//=p
  p+=1
 return out
def val(v):
 n=1
 for p,e in zip(primes,v):
  for _ in range(e):n*=p
 return n
for j,t in enumerate(d['results']):
 raw=[r for w in d['regions'][j]['units'] for r in w];n=math.prod(primes[r] for r in raw);assert n==int(t['input_integer']);expected=phi(n);assert expected==int(t['predicted_integer'])==val(t['predicted_exponents']);actual=math.prod(primes[r] for w in d['regions'][j+1]['units'] for r in w);assert actual==int(t['actual_next_integer']);assert t['accepted']==(expected==actual);assert [i for i,(x,y) in enumerate(zip(t['predicted_exponents'],t['actual_next_exponents'])) if x!=y]==[w['rune_index'] for w in t['mismatch_witnesses']]
for c in d['controls']:
 for j in range(4):
  a=val(c['states'][j]);b=val(c['states'][j+1]);assert phi(a)==b;assert math.prod(primes[r] for r in c['encoded_words'][j+1])==b;assert val(c['transitions'][j]['single_factor_corruption'])!=b
out={'status':'PASS','actual_relations_replayed':4,'inverse_control_relations_replayed':16,'corruptions_rejected':16};(R/'check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
