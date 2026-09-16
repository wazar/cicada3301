import numpy as np,pathlib,json,gzip,datetime
R=pathlib.Path(__file__).parent;M=json.load(open(R/'F01-maps.json'));rng=np.random.default_rng(2026091713);seq=[];labs=[];strata=[];fold=[]
for m in M:
 x=np.array(m['indices']);y=np.array(m['labels'][2]);y[0]=0;s={}
 for w in m['words']:
  for i in range(w['start'],w['end']):
   if i==0:continue
   k=(min(i-w['start'],4),min(w['end']-w['start'],8));s.setdefault(k,[]).append(i)
 seq.append(x);labs.append(y);strata.append([np.array(v) for v in s.values()]);fold.append(m['page']%3)
def table(i,y):return np.bincount(y[1:]*29+seq[i][1:],minlength=58).reshape(2,29)
def gs(t):
 e=t.sum(1)[:,None]*t.sum(0)[None,:]/t.sum();ok=t>0;return float(2*np.sum(t[ok]*np.log(t[ok]/e[ok])))
def scan(ys):
 tt=np.array([table(i,y) for i,y in enumerate(ys)]);total=tt.sum(0);pred=0.;parts=[]
 for f in range(3):
  tr=tt[np.array(fold)!=f].sum(0)+1;test=tt[np.array(fold)==f].sum(0);p=tr/tr.sum(1)[:,None];v=float(np.sum(test[1]*np.log(p[1]/p[0])));pred+=v;parts.append(v)
 return [gs(total),pred],parts
real,parts=scan(labs);null=[];labelmaps=[]
for rep in range(1999):
 if rep%100==0:
  assert not (R.parent/'STOP').exists()
  assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 ys=[]
 for y,ss in zip(labs,strata):
  z=np.zeros_like(y)
  for s in ss:
   n=int(y[s].sum());z[rng.choice(s,n,replace=False)]=1
  ys.append(z)
 null.append(scan(ys)[0]);labelmaps.append([np.flatnonzero(y).tolist() for y in ys])
null=np.array(null);tails=(1+(null>=real).sum(0))/2000;t=np.array([table(i,y) for i,y in enumerate(labs)]);total=t.sum(0);e=total.sum(1)[:,None]*total.sum(0)[None,:]/total.sum();movable=sum(int(y[s].sum()) for y,ss in zip(labs,strata) for s in ss if 0<y[s].sum()<len(s));nstart=sum(int(y.sum()) for y in labs)
result={'real':real,'fold_scores':parts,'tails':tails.tolist(),'bonferroni2':np.minimum(1,2*tails).tolist(),'start_count':nstart,'movable_starts':movable,'counts_by_rune':total.tolist(),'expected':e.tolist(),'leave_one_page_out':[{'page':m['page'],'G_without':gs(total-t[i]),'delta':real[0]-gs(total-t[i])} for i,m in enumerate(M)],'counts':{'real':1,'null':1999},'seed':2026091713}
with gzip.open(R/'F03-evidence.json.gz','wt') as f:json.dump({'null':null.tolist(),'null_start_maps':labelmaps,'source':'F01-maps.json','strata':[[s.tolist() for s in ss] for ss in strata]},f)
(R/'F03-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
