"""Independent exhaustive path enumeration for fixed reset DP, including exhaustion."""
import pathlib,random,json,sys
O=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(O));import marked_exact as D

def brute(c,key,sign,periodic,start,ends,resets,score):
 rows=[]
 def walk(i,pos,ctx,sc,plain,lit):
  if i==len(c):rows.append(dict(total=sc,plain=plain,literal_positions=lit,position=pos,used=len(c)-len(lit)));return
  if i in resets:pos=0
  choices=[]
  if periodic or pos<len(key):choices.append(((c[i]+sign*key[pos])%29,(pos+1)%len(key) if periodic else pos+1,False))
  if c[i]==0:choices.append((0,pos,True))
  for r,np,l in choices:
   ss,w=score(ctx,r,i in ends);walk(i+1,np,ss,sc+w,plain+[r],lit+[i] if l else lit)
 walk(0,start%len(key) if periodic else start,(29,29),0.,[],[]);return sorted(rows,key=lambda x:x['total'],reverse=True)

def main():
 rng=random.Random(260917307);count=0;paths=0;empty=0;maxerror=0.
 for n in range(0,10):
  for j in range(80):
   c=[rng.choice([0,0,0,1,2,4]) for _ in range(n)];key=[rng.randrange(29) for _ in range(rng.randrange(1,7))];periodic=bool(j%2);start=rng.randrange(len(key)+1);sign=[-1,1][(j//2)%2];ends={i for i in range(n) if rng.randrange(3)==0};resets={i for i in range(n) if rng.randrange(4)==0};table=[rng.randrange(-9,3) for _ in range(30**3)] if j%3 else [0]*(30**3)
   def score(ctx,r,end):
    v=table[ctx[0]*900+ctx[1]*30+r];ss=(ctx[1],r)
    if end:v+=table[ss[0]*900+ss[1]*30+29];ss=(ss[1],29)
    return ss,v
   expected=brute(c,key,sign,periodic,start,ends,resets,score);count+=1;paths+=len(expected)
   try:actual,diag=D.decode(c,key,score,sign=sign,periodic=periodic,start=start,ends=ends,reset_before=resets)
   except ValueError:
    assert not expected;empty+=1;continue
   assert len(actual)==min(16,len(expected))
   for x,y in zip(actual,expected):
    error=abs(x['total']-y['total']);maxerror=max(maxerror,error);assert error==0
    cc,pos,used=D.encipher(x['plain'],key,sign,x['literal_positions'],periodic=periodic,start=start,reset_before=resets);assert (cc,pos,used)==(c,x['position'],x['used'])
 out=dict(cases=count,exhaustive_paths=paths,no_path_cases=empty,max_score_error=maxerror,scope='integer local scores including allties; both signs, periods, finite exhaustion, starts,resets at0/multiplepositions, consecutiveF and boundaries',status='PASS')
 (O/'A07-selftest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
