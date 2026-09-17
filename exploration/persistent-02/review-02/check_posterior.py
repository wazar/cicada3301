"""Fresh independent complete-mask partition/marginal and beam-subset review."""
import pathlib,sys,random,itertools,math,json,collections
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];sys.path.insert(0,str(R/'exploration/persistent-02/decoder'))
import posterior as P
def dump(name,x):(O/name).write_text(json.dumps(x,indent=2)+'\n')
class Model:
 def __init__(self,w):self.w=w
 def extend(self,s,r,end):
  w=float(self.w[s+(r,)]);s=(s[1],r)
  if end:w+=float(self.w[s+(29,)]);s=(s[1],29)
  return s,w
def enumerate_paths(c,key,model,sign,periodic,start,ends,ctx):
 fs=[i for i,v in enumerate(c) if v==0];rows=[]
 for bits in itertools.product([False,True],repeat=len(fs)):
  lit={i for i,b in zip(fs,bits) if b};p=[];history=[ctx];pos=start;score=0.;states=[(pos%len(key) if periodic else pos,*ctx)]
  for i,v in enumerate(c):
   if i not in lit and not periodic and pos==len(key):break
   r=0 if i in lit else (v+sign*key[pos%len(key)])%29;score+=float(model.w[tuple(history[-1])+(r,)]);s=(history[-1][1],r)
   if i in ends:score+=float(model.w[s+(29,)]);s=(s[1],29)
   history.append(s);p.append(r);pos+=i not in lit;states.append((pos%len(key) if periodic else pos,*s))
  else:rows.append(dict(total=score,plain=p,literal_positions=sorted(lit),used=pos-start,states=states))
 return rows
def expected(rows):
 peak=max(x['total'] for x in rows);w=[math.exp(x['total']-peak) for x in rows];z=math.fsum(w);return peak+math.log(z),[x/z for x in w]
def compare(got,rows,c):
 z,weights=expected(rows);assert abs(z-got['log_partition'])<2e-11
 assert int(got['number_of_legal_decision_paths'])==len(rows);err=abs(z-got['log_partition'])
 for b in got['branch_marginals']:
  literal=math.fsum(w for row,w in zip(rows,weights) if b['position'] in row['literal_positions']);err=max(err,abs(literal-b['literal']['probability']));assert abs(literal-b['literal']['probability'])<2e-11;assert abs(1-literal-b['ordinary']['probability'])<2e-11
 for join in got['joins']:
  t=join['cut_after_rune_count'];ss=collections.defaultdict(float);pp=collections.defaultdict(float)
  for row,w in zip(rows,weights):ss[row['states'][t]]+=w;pp[row['states'][t][0]]+=w
  for s in join['states']:assert abs(s['probability']-ss[(s['position'],*s['context'])])<2e-11
  for p in join['key_positions']:assert abs(p['probability']-pp[p['position']])<2e-11
 return err
def main():
 r=random.Random(260917907);nr=np.random.default_rng(260917907);records=[];maxerr=0.;complete_paths=0;legal=0;exhausted=0
 for z in range(650):
  n=r.randrange(11);c=[r.choice([0,0,0,2,7,28]) for _ in range(n)];key=[r.randrange(29) for _ in range(r.randrange(1,7))]
  if z%13==0:key=[0]*len(key)
  sign=r.choice([-1,1]);periodic=r.choice([True,False]);start=r.randrange(len(key)+1);ends={i for i in range(n) if r.random()<.25};context=tuple(r.randrange(30) for _ in range(2));w=nr.integers(-12,5,size=(30,30,30)).astype(float)/3
  if z%7==0:w[:]=0.
  if z%23==0:w*=1000
  model=Model(w);rows=enumerate_paths(c,key,model,sign,periodic,start,ends,context)
  try:got=P.analyze(c,key,model.extend,sign=sign,periodic=periodic,start=start,ends=ends,context=context,cuts=range(n+1))
  except ValueError:assert not rows;exhausted+=1;records.append(dict(case=z,exhausted=True));continue
  assert rows;maxerr=max(maxerr,compare(got,rows,c));complete_paths+=len(rows);legal+=1
  # Independent summation combines each rune+boundary increment separately;
  # global scores differ only by ordinary floating addition order.
  bylit={tuple(x['literal_positions']):x for x in rows}
  pools=[]
  for width in [1,3,64]:
   pool=P.beam_pool(c,key,model,sign=sign,periodic=periodic,start=start,ends=ends,context=context,width=width)
   for x in pool:
    e=bylit[tuple(x['literal_positions'])];assert x['plain']==e['plain'] and x['used']==e['used'];assert abs(x['total']-e['total'])<2e-11
   if pool:
    m=P.mass(pool,got['log_partition']);ez,_=expected(rows);subset=math.fsum(math.exp(x['total']-ez) for x in pool);assert abs(subset-m['mass'])<2e-11
    pools.append(dict(width=width,retained=len(pool),mass=m['mass']))
   else:
    m=P.mass(pool,got['log_partition']);assert m['mass']==0 and m['lost_mass']==1
  cut=n//2;pre=enumerate_paths(c[:cut],key,model,sign,periodic,start,{i for i in ends if i<cut},context);pg=P.analyze(c[:cut],key,model.extend,sign=sign,periodic=periodic,start=start,ends={i for i in ends if i<cut},context=context,cuts=[cut]);maxerr=max(maxerr,compare(pg,pre,c[:cut]))
  records.append(dict(case=z,paths=len(rows),prefix_paths=len(pre),pools=pools))
 dump('posterior-checks.json',dict(passed=True,rng_seed=260917907,cases=650,legal=legal,exhausted=exhausted,complete_paths=complete_paths,max_abs_partition_or_branch_error=maxerr,records=records))
 print('posterior passed',legal,exhausted,complete_paths,maxerr)
if __name__=='__main__':main()
