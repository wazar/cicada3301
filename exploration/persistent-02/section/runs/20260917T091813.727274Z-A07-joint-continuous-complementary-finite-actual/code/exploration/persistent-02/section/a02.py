"""Source-backed prime/totient finite streams with same frozen continuation procedure."""
import pathlib,sys,importlib.util,json,itertools,random,gzip,argparse
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2]
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
A=module('a01',O/'a01.py');E=module('exactfinite',R/'exploration/persistent-02/decoder/exact.py')
class Finite:
 @staticmethod
 def kbest(c,ends,key,sign,lm,retain=16,start_context=(29,29),start_used=0):
  out,d=E.decode(c,key,lm.extend,sign=sign,periodic=False,start=start_used,ends=ends,retain=retain,context=start_context)
  for x in out:x['used']+=start_used
  return out,d
A.K=Finite

def check():
 rng=random.Random(9020202);lm=A.M.LM();cases=0;paths=0
 for n in range(1,9):
  for j in range(20):
   c=[rng.choice([0,0,0,1,2,17]) for _ in range(n)];key=[rng.randrange(29) for _ in range(n+2)];ends={i for i in range(n) if rng.randrange(3)==0};start=j%3;sign=[-1,1][j%2];seq=[]
   for mask in itertools.product([False,True],repeat=c.count(0)):
    p=[];u=start;lit=[];mi=0
    for i,v in enumerate(c):
     literal=False
     if v==0:literal=mask[mi];mi+=1
     if literal:p.append(0);lit.append(i)
     else:p.append((v+sign*key[u])%29);u+=1
    seq.append((lm.score(p,ends),p,lit,u))
   seq.sort(reverse=True,key=lambda x:x[0]);out,_=Finite.kbest(c,ends,key,sign,lm,start_used=start);assert len(out)==min(16,len(seq))
   for x,y in zip(out,seq):assert abs(x['score']-y[0])<1e-12;assert A.forward(x['plain'],key,sign,set(x['literal_positions']),start)==(c,x['used'])
   cases+=1;paths+=len(seq)
 out=dict(cases=cases,exhaustive_paths=paths,status='PASS',scope='independent exhaustive finite p03 local-score paths, both signs, nonzero starts, random boundaries; broader exhaustion/ties handled by B')
 (O/'A02'/'selfcheck.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--batch',choices=['check','controls','actual','nulls'],required=True);a=ap.parse_args();out=O/'A02';out.mkdir(exist_ok=True)
 if a.batch=='check':check();return
 lm=A.M.LM();primes=A.REF.primes(800);cells=[dict(id=f'{name}:{sign}',key_id=name,phase=0,sign=sign,key=[(p-delta)%29 for p in primes]) for name,delta in [('primes',0),('totients-of-primes',1)] for sign in [-1,1]];results=[]
 if a.batch=='controls':
  for j,name in enumerate(A.M.CHECK):
   p,ends=A.M.parse((R/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text());n=len(p);cuts=[0,n//3,2*n//3,n];spans=list(zip(cuts,cuts[1:]));cell=cells[j];policy=['continuous','page-reset'][j%2];c=[];u=0
   for x,y in spans:
    if policy=='page-reset':u=0
    pp=p[x:y];literal={i for i,v in enumerate(pp) if v==0 and (i+x)%3!=1};cc,u=A.forward(pp,cell['key'],cell['sign'],literal,u);c.extend(cc)
   results.append(A.run('control-'+name,c,ends,spans,lm,cells,p,dict(**cell,policy=policy),resultdir=out))
 else:
  for variant in ['body','whole']:
   names=[f'actual-{variant}'] if a.batch=='actual' else [f'null-{variant}-{i:02}' for i in range(19)]
   for name in names:
    original=json.load(gzip.open(O/'A01'/(name+'.json.gz'),'rt'));results.append(A.run(name,original['cipher'],set(original['ends']),original['spans'],lm,cells,resultdir=out))
 (out/f'summary-{a.batch}.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
