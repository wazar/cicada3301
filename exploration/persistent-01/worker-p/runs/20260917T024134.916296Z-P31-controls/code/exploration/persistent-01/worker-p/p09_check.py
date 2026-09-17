import p09 as q
import random,math,json
p=q.p;p.gate();models,env,cells,parse=p.setup();lm=q.FreeLM();env['lm']=lm;brute=[]
for ix in range(40):
 rng=random.Random(335109+ix);key=[rng.randrange(4) for _ in range(14)];c=[rng.randrange(4) for _ in range(4)];sign=[-1,1][ix%2];paths=[]
 def rec(i,j,plain,skips):
  if i==4:
   value=lm.score(plain,[])*4+sum(skips)*math.log(.83)+sum(c[z]==c[z-1] for z in range(1,4))*math.log(.17);paths.append((value,plain,skips));return
  for accept in range(j,len(key),2):
   if i==0 and accept!=j:continue
   x=(c[i]+sign*key[accept])%29;rejected=list(range(j,accept,2))
   if rejected and any((x-sign*key[z])%29!=c[i-1] for z in rejected):continue
   rec(i+1,accept+1,plain+[x],skips+[len(rejected)])
 rec(0,0,[],[]);paths.sort(key=lambda x:x[0],reverse=True);d=env['decode'](c,set(),dict(key=key,sign=sign),retain=16);assert len(d['alternatives'])==min(16,len(paths));assert all(abs(a['joint_total']-b[0])<1e-10 for a,b in zip(d['alternatives'],paths));brute.append(dict(index=ix,paths=len(paths),max=paths[0][0]))
checked=0
for ix in range(4):
 d=json.loads((q.R/('control-'+str(ix)+'.json')).read_text());f=d['fixture'];assert f==p.read('control-'+str(ix))['fixture'];n=len(f['plain']);m=len(f['ends']);assert d['relocated_ends']==[math.ceil(j*n/m)-1 for j in range(1,m+1)]
 for name,res in d['results'].items():
  model=lm if name=='free' else models['latin'];ends=[] if name=='free' else d['relocated_ends']
  for row in res['rows']:
   a=row['decode']['alternatives'][0];cell=next(x for x in cells if x['id']==row['id']);j=0;c=f['cipher']
   for i,(x,r,t) in enumerate(zip(c,a['plain'],a['reject_counts'])):
    for z in range(t):assert i and (r-cell['sign']*cell['key'][j+2*z])%29==c[i-1]
    j+=2*t;assert (r-cell['sign']*cell['key'][j])%29==x;j+=1
   assert j==a['used'];score=model.score(a['plain'],set(ends))*(n+len(ends))+sum(a['reject_counts'])*math.log(.83)+sum(c[i]==c[i-1] for i in range(1,n))*math.log(.17);assert abs(score-a['joint_total'])<1e-9;checked+=1
  assert lm.score(f['plain'],set(d['original_ends']))==lm.score(f['plain'],set(d['relocated_ends']))
# Explicit distribution normalization over29 outputs, including sentinel contexts.
maxerr=0
for a in range(30):
 for b in range(30):maxerr=max(maxerr,abs(sum(math.exp(lm.extend((a,b),r)[1]) for r in range(29))-1))
assert maxerr<1e-12
q.dump('check',dict(status='PASS',brute=brute,replayed_outputs=checked,unchanged_fixtures=4,normalization_contexts=900,max_probability_sum_error=maxerr,no_real_search=True));print('PASS',checked,maxerr)
