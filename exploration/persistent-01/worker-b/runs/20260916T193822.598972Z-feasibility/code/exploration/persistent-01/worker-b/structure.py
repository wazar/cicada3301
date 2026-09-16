import pathlib,json,random,math,time,importlib.util,gzip
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('bsearch',OUT/'search.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
rs,pages,jobs=m.setup();source=np.array(m.old.payload());lags=(1,8,32)
def routes(b):
 out={}
 for name,z in rs.items():
  # Frozen source_indices omit rejected bytes: reconstruct spatial route from its mod29 sibling.
  indices=rs[name.replace('reject232','mod29')]['source_indices'];raw=b[indices]
  out[name]=(raw if name.endswith('mod29') else raw[raw<232])%29
 return out
actual=routes(source)
assert all(list(actual[k])==v['key'] for k,v in rs.items())
def measure(pg,keys,detail=False):
 vals=[]
 for route,key in keys.items():
  for lag in lags:
   num=var=selected=hits=0;parts=[]
   for p,c in pg.items():
    n=len(c)
    if n>len(key) or n<=lag:continue
    c=np.array(c);eq=(c[lag:]==c[:-lag]);mask=key[lag:n]==key[:n-lag];a=int(np.sum(mask));h=int(np.sum(eq&mask));base=float(np.mean(eq));v=a*base*(1-base)
    num+=h-a*base;var+=v;selected+=a;hits+=h
    if detail:parts.append(dict(page=p,pairs=a,hits=h,baseline=base))
   vals.append(dict(route=route,lag=lag,z=num/math.sqrt(var) if var else 0,pairs=selected,hits=hits,parts=parts))
 return sorted(vals,key=lambda z:z['z'],reverse=True)
def main():
 t=time.monotonic();real=measure(pages,actual,True);null=[]
 rng=np.random.default_rng(9200501)
 for rep in range(499):null.append(measure(pages,routes(rng.permutation(source)))[0]['z'])
 controls=[]
 # Actual searched route selection on independently generated cipher; all source-sufficient discovery lengths.
 for bias in (1/29,.25,.6):
  samples=[]
  for rep in range(20):
   truth=list(actual)[rep%len(actual)];key=actual[truth];pg={};prob=np.array([(1-bias)/28]*29);prob[0]=bias
   for p,c in pages.items():
    if len(c)<=len(key):pg[p]=list((rng.choice(29,len(c),p=prob)+key[:len(c)])%29)
   scores=measure(pg,actual);samples.append(dict(truth=truth,top=scores[0],truth_best=max(z['z'] for z in scores if z['route']==truth),detected=scores[0]['z']>float(np.quantile(null,.95))))
  controls.append(dict(bias=bias,detected=sum(z['detected'] for z in samples),trials=20,samples=samples))
 result=dict(real=real,null_maxima=null,pvalue_max=(1+sum(x>=real[0]['z'] for x in null))/(len(null)+1),controls=controls,seconds=time.monotonic()-t,null_seed=9200501,limits='Fixed natural-start additive finite keys; no literal-F path search; equal-key collision statistic only; no English ranking.')
 m.save('structure-results.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('real','null_maxima','controls')}));print(real[0])
if __name__=='__main__':main()
