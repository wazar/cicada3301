import pathlib,json,gzip,math,random,hashlib,datetime
R=pathlib.Path(__file__).parent;S=R.parents[1]/'worker-f/F10-evidence.json.gz';source=json.load(gzip.open(S,'rt'));regions=source['regions'];prime=[];candidate=2
while len(prime)<29:
 if all(candidate%d for d in range(2,math.isqrt(candidate)+1)):prime.append(candidate)
 candidate+=1
assert prime==[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
def gate():
 assert not (R.parents[1]/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def vec(word):return [word.count(i) for i in range(29)]
def number(v):return math.prod(p**e for p,e in zip(prime,v))
def inverse(v):return [r for r,e in enumerate(v) for _ in range(e)]
def totient(v):
 result=[0]*29
 for j,(p,e) in enumerate(zip(prime,v)):
  if not e:continue
  result[j]+=e-1;q=p-1
  for k,f in enumerate(prime):
   while q%f==0:result[k]+=1;q//=f
  assert q==1
 return result
def phi_direct(n):
 value=n;remaining=n;factor=2
 while factor*factor<=remaining:
  if remaining%factor==0:
   value=value//factor*(factor-1)
   while remaining%factor==0:remaining//=factor
  factor+=1
 if remaining>1:value=value//remaining*(remaining-1)
 return value
# Independent small numeric controls do not use the exponent transform.
for n in range(1,1001):assert phi_direct(n)==sum(math.gcd(k,n)==1 for k in range(1,n+1))
# Verify exponent transform with all singleton primes and powers before larger controls.
for pidx,p in enumerate(prime):
 for exponent in [1,2,3]:
  v=[0]*29;v[pidx]=exponent;assert number(totient(v))==phi_direct(p**exponent)
words=[[r for w in row['units'] for r in w] for row in regions];rng=random.Random(470500);starts=[words[0]]+[[rng.randrange(29) for _ in range(len(words[0]))] for _ in range(3)];controls=[]
for start in starts:
 gate();states=[vec(start)];trans=[]
 for step in range(4):
  v=states[-1];pred=totient(v);n=number(v);expected=n
  # Whole-integer Euler product: separate arithmetic path, no transformed-vector factoring.
  for p,e in zip(prime,v):
   if e:expected=expected//p*(p-1)
  assert number(pred)==expected and vec(inverse(pred))==pred and pred!=[0]*29;states.append(pred);corrupt=pred.copy();idx=next(i for i,e in enumerate(corrupt) if e);corrupt[idx]-=1;corrupt[(idx+1)%29]+=1;assert corrupt!=pred and number(corrupt)!=expected;trans.append({'expected_integer':str(expected),'single_factor_corruption':corrupt,'corruption_rejected':True})
 controls.append({'start_runes':start,'states':states,'encoded_words':[inverse(v) for v in states],'state_lengths':[sum(v) for v in states],'transitions':trans})
# Actual results only after all arithmetic/inverse controls.
gate();actual=[vec(w) for w in words];results=[]
for j in range(4):
 v=actual[j];pred=totient(v);target=actual[j+1];n=number(v);expected=n
 for p,e in zip(prime,v):
  if e:expected=expected//p*(p-1)
 assert number(pred)==expected
 diffs=[{'prime':p,'rune_index':k,'predicted_exponent':a,'actual_exponent':b} for k,(p,a,b) in enumerate(zip(prime,pred,target)) if a!=b]
 results.append({'from_item':j+1,'to_item':j+2,'accepted':pred==target,'input_integer':str(n),'predicted_integer':str(expected),'actual_next_integer':str(number(target)),'input_exponents':v,'predicted_exponents':pred,'actual_next_exponents':target,'predicted_rune_count':sum(pred),'actual_rune_count':sum(target),'input_bits':n.bit_length(),'predicted_bits':expected.bit_length(),'actual_bits':number(target).bit_length(),'mismatch_witnesses':diffs})
e={'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'source_path':str(S),'prime_table':prime,'regions':regions,'controls':controls,'results':results,'small_integer_controls':1000,'prime_power_controls':87,'corruptions':16,'seed':470500}
with gzip.open(R/'evidence.json.gz','wt') as f:json.dump(e,f)
summary={'accepted_transitions':sum(t['accepted'] for t in results),'complete_object_accepted':all(t['accepted'] for t in results),'control_complete_objects':len(controls),'control_transitions':16,'small_phi_controls':1000,'prime_power_controls':87,'corruptions_rejected':16,'control_lengths':[c['state_lengths'] for c in controls],'transitions':[{k:v for k,v in t.items() if k in ['from_item','to_item','accepted','predicted_rune_count','actual_rune_count','input_bits','predicted_bits','actual_bits','mismatch_witnesses']} for t in results]};(R/'results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
