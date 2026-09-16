import pathlib,json,random,math
O=pathlib.Path(__file__).parent;ROOT=O.parents[2];D=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text());P={p['original_page']:p for p in D['pages']if p['original_page']in[3,7,17]};rng=random.Random(30909)
def bm(s):
 C=[1];B=[1];L=0;m=1;b=1
 for n in range(len(s)):
  d=(s[n]+sum(C[i]*s[n-i]for i in range(1,L+1)))%29
  if d==0:m+=1;continue
  T=C.copy();coef=d*pow(b,-1,29)%29
  if len(C)<len(B)+m:C +=[0]*(len(B)+m-len(C))
  for j,x in enumerate(B):C[j+m]=(C[j+m]-coef*x)%29
  if 2*L<=n:L=n+1-L;B=T;b=d;m=1
  else:m+=1
 return C[:L+1]
def examine(s):
 cut=2*len(s)//3;c=bm(s[:cut]);out=s[:cut].copy()
 for i in range(cut,len(s)):out.append(-sum(c[j]*out[i-j]for j in range(1,len(c)))%29)
 correct=sum(a==b for a,b in zip(out[cut:],s[cut:]));n=len(s)-cut;z=(correct-n/29)/math.sqrt(n*(1/29)*(28/29))
 return {'cut':cut,'degree':len(c)-1,'coefficients':c,'forecast':out[cut:],'truth':s[cut:],'matches':correct,'n_predictions':n,'z':z,'exact_low_order':len(c)-1<=8 and correct==n}
def generate(n,d):
 coef=[rng.randrange(29)for _ in range(d)];coef[-1]=rng.randrange(1,29);s=[rng.randrange(29)for _ in range(d)]
 for i in range(d,n):s.append(sum(coef[j]*s[i-j-1]for j in range(d))%29)
 return s,coef
units=[]
for page,lo,hi in [(3,16,119),(3,122,217),(7,0,194),(17,0,len(P[17]['indices'])),(3,0,217),(7,0,208)]:
 s=P[page]['indices'][lo:hi];units.append({'page':page,'range':[lo,hi],'indices':s,'source_positions':P[page]['source_char_positions'][lo:hi],'result':examine(s)})
controls=[]
for unit in units:
 for degree in [4,8]:
  s,c=generate(len(unit['indices']),degree);r=examine(s);assert r['matches']==r['n_predictions'] and r['degree']<=degree
  noisy=s.copy()
  for i in rng.sample(range(len(s)),max(1,len(s)//20)):noisy[i]=(noisy[i]+rng.randrange(1,29))%29
  controls.append({'coefficients':c,'truth':s,'result':r,'noisy':noisy,'noisy_result':examine(noisy)})
null={}
for kind in ['permutation','no_adjacent_repeat']:
 stats=[];details=[]
 for _ in range(200):
  rr=[]
  for unit in units:
   s=unit['indices'].copy()
   if kind=='permutation':rng.shuffle(s)
   else:
    s=[rng.randrange(29)]
    for i in range(1,len(unit['indices'])):
     v=rng.randrange(28);s.append(v+(v>=s[-1]))
   rr.append(examine(s))
  stats.append(max(r['z']for r in rr));details.append([{'degree':r['degree'],'matches':r['matches'],'n_predictions':r['n_predictions']}for r in rr])
 realmax=max(u['result']['z']for u in units);null[kind]={'maxima':stats,'details':details,'upper_tail':(1+sum(v>=realmax for v in stats))/201}
result={'seed':30909,'units':units,'controls':controls,'null':null}
# Sensitivity addition after original run; real/null definitions and RNG sequence above unchanged.
filtered=[]
for degree in [4,8]:
 for unit in units:
  n=len(unit['indices']);raw,coef=generate(n+100,degree);accepted=[];rejected=[]
  for i,v in enumerate(raw):
   if accepted and v==accepted[-1] and rng.random()<.83:rejected.append(i);continue
   accepted.append(v)
   if len(accepted)==n:break
  assert len(accepted)==n
  filtered.append({'degree':degree,'coefficients':coef,'raw':raw,'accepted':accepted,'rejected_raw_offsets':rejected,'result':examine(accepted)})
result['filter_controls']=filtered
(O/'g09-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'units':[{'page':u['page'],'range':u['range'],**{k:v for k,v in u['result'].items()if k not in ['forecast','truth','coefficients']}}for u in units],'exact_controls':len(controls),'noisy_exact':sum(c['noisy_result']['exact_low_order']for c in controls),'null_tails':{k:v['upper_tail']for k,v in null.items()}},indent=2))
