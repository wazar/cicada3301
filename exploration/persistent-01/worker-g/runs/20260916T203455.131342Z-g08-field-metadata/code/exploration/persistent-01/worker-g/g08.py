import json,pathlib,random
O=pathlib.Path(__file__).parent;ROOT=O.parents[2];D=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text());P={p['original_page']:p for p in D['pages']if p['original_page']in[3,7]};primes=[n for n in range(2,110)if all(n%d for d in range(2,int(n**.5)+1))];assert len(primes)==29;rng=random.Random(30808)
def number(v):
 z=0
 for x in v:z=z*29+x
 return z
out={'seed':30808,'pairs':[],'total_comparisons':0,'controls':[]}
for page,hs,he,bs,be in [(3,0,16,16,119),(3,119,122,122,217),(7,194,208,0,194)]:
 h=P[page]['indices'][hs:he];b=P[page]['indices'][bs:be];targets={'length':len(b),'index_sum':sum(b),'prime_sum':sum(primes[v]for v in b),'distinct_count':len(set(b))};vals=[number(h),number(h[::-1])];matches=[[direction,name]for direction,v in enumerate(vals)for name,n in targets.items()if v==n];null=[]
 for _ in range(1000):
  v=h.copy();rng.shuffle(v);numbers=[number(v),number(v[::-1])];null.append({'values':numbers,'match_count':sum(n==t for n in numbers for t in targets.values())})
 for name,t in targets.items():
  d=[];z=t
  for _ in h:d.append(z%29);z//=29
  if not z:assert number(d[::-1])==t;out['controls'].append({'length':len(h),'target':name,'truth':t,'encoded':d[::-1]})
 out['pairs'].append({'page':page,'header_range':[hs,he],'body_range':[bs,be],'header_source_positions':P[page]['source_char_positions'][hs:he],'body_source_positions':P[page]['source_char_positions'][bs:be],'values':vals,'targets':targets,'matches':matches,'null':null});out['total_comparisons']+=8
(O/'g08-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'total_comparisons':out['total_comparisons'],'controls':len(out['controls']),'pairs':[{k:v for k,v in p.items()if k not in ['null','header_source_positions','body_source_positions']}for p in out['pairs']],'null_total_hits':sum(n['match_count']for p in out['pairs']for n in p['null'])},indent=2))
