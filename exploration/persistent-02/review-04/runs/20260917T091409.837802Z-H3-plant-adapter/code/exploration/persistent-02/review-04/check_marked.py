"""Independent complete-mask H3 reset DP check, including arbitrary context."""
import pathlib,sys,random,itertools,json,numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];sys.path.insert(0,str(R/'exploration/persistent-02/section'));import marked_exact as M
sys.path.insert(0,str(R/'exploration/persistent-02/decoder'));import exact as E
def main():
 rng=random.Random(9170408);nr=np.random.default_rng(9170408);records=[];paths=0;exhausted=0;nondefault=0;noreset=0
 for case in range(850):
  n=rng.randrange(0,12);c=[rng.choice([0,0,0,3,9,28]) for _ in range(n)];key=[rng.randrange(29) for _ in range(rng.randrange(1,7))];sign=rng.choice([-1,1]);periodic=bool(rng.randrange(2));start=rng.randrange(len(key)+1);ctx=tuple(rng.randrange(30) for _ in range(2));ends={i for i in range(n) if rng.random()<.3};resets={i for i in range(n) if rng.random()<.25};retain=rng.choice([1,2,7,16,33]);w=nr.integers(-15,5,size=(30,30,30)).astype(float)/7
  if case%5==0:w[:]=0
  if case%7==0:resets=set(range(n))
  if case%11==0:resets=set()
  if case%13==0:key=[0]*len(key)
  def extend(s,r,end):
   score=float(w[s+(r,)]);s=(s[1],r)
   if end:score+=float(w[s+(29,)]);s=(s[1],29)
   return s,score
  expected=[];fs=[i for i,v in enumerate(c) if v==0]
  for bits in itertools.product([False,True],repeat=len(fs)):
   lit={i for i,b in zip(fs,bits) if b};pos=start%len(key) if periodic else start;used=0;tokens=list(ctx);plain=[];total=0.;mask=0
   for i,v in enumerate(c):
    if i in resets:pos=0
    if i not in lit and not periodic and pos>=len(key):break
    r=0 if i in lit else (v+sign*key[pos])%29;sc=float(w[tuple(tokens[-2:])+(r,)]);tokens.append(r)
    if i in ends:sc+=float(w[tuple(tokens[-2:])+(29,)]);tokens.append(29)
    total+=sc;plain.append(r);mask=2*mask+(i in lit)
    if i not in lit:used+=1;pos=(pos+1)%len(key) if periodic else pos+1
   else:expected.append(dict(total=total,plain=plain,literal_positions=sorted(lit),used=used,position=pos,mask=str(mask)))
  expected.sort(key=lambda x:(-x['total'],int(x['mask'])));paths+=len(expected)
  try:got,diag=M.decode(c,key,extend,sign=sign,periodic=periodic,start=start,ends=ends,retain=retain,context=ctx,reset_before=resets)
  except ValueError:assert not expected;exhausted+=1;records.append(dict(case=case,exhausted=True));continue
  assert len(got)==min(retain,len(expected));assert [x['total'] for x in got]==[x['total'] for x in expected[:retain]];by={x['mask']:x for x in expected}
  for x in got:
   assert {k:x[k] for k in by[x['mask']]}==by[x['mask']]
   assert M.encipher(x['plain'],key,sign,set(x['literal_positions']),periodic=periodic,start=start,reset_before=resets)==(c,x['position'],x['used'])
  nondefault+=ctx!=(29,29)
  if not resets:
   old,_=E.decode(c,key,extend,sign=sign,periodic=periodic,start=start,ends=ends,retain=retain,context=ctx);assert [x['total'] for x in old]==[x['total'] for x in got];noreset+=1
  records.append(dict(case=case,paths=len(expected),reset_before=sorted(resets),initial_context=ctx,retained=len(got)))
 out=dict(passed=True,cases=850,exhaustive_paths=paths,exhausted=exhausted,legal_nondefault_context_cases=nondefault,no_reset_olddecoder_comparisons=noreset,records=records,scope='Bothsigns,finite/periodic,reset0/all/subsets/none,arbitrarycontexts,boundarytiming,exhaustion,allties,zero-keys,floatweights,retain1..33;independentcomplete-maskstates/scores.')
 (O/'marked-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
