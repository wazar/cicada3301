import pathlib,json,math,hashlib,gzip
R=pathlib.Path(__file__).parent;aa=[a for a in range(2,28) if math.gcd(a,28)==1];tests=0;signatures=[]
def order(v):
 if v==0:return 0
 return next(k for k in [1,2,4,7,14,28] if pow(v,k,29)==1)
for a in aa:
 table=[]
 for previous in range(29):
  e=pow(a,previous,28);inverse=next(k for k in range(1,28) if e*k%28==1)
  for c in range(29):
   p=pow(c,e,29);assert pow(p,inverse,29)==c;assert order(c)==order(p);tests+=1;table.append(p)
 signatures.append(hashlib.sha256(bytes(table)).hexdigest())
r=dict(bases=aa,state_symbol_checks=tests,inverse_and_multiplicative_order_invariant=True,unique_operator_tables=len(set(signatures)),table_sha256=signatures)
(R/'H18-algebra-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
