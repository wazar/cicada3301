import pathlib,json,gzip,time,datetime,sys
import numpy as np
D=pathlib.Path(__file__).resolve().parent;B=D.parents[1]
def gate():
 assert not (B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def save(name,d):
 with gzip.open(D/(name+'.json.gz'),'wt') as f:json.dump(d,f)
def prepare():
 maps=json.loads((B/'worker-f/F06-maps.json').read_text());assert len(maps)==45
 assert not {m['page'] for m in maps}&{4,9,14,19,24,29,34,39,44,54}
 (D/'input.json').write_text(json.dumps(maps));return [m['indices'] for m in maps]
def fit(vs,name):
 gate();started=time.monotonic();cnt=np.zeros((29,2,29));records=[];hist=np.zeros(29)
 for page,v in enumerate(vs):
  a=np.array(v);prev=a[:-1];cur=a[1:];ok=prev!=cur
  state=np.cumsum(a[None,:-1]==np.arange(29)[:,None],axis=1)%2
  records.append((prev[ok],cur[ok],state[:,ok]))
  if page%2==0:
   hist+=np.bincount(cur[ok],minlength=29)
   for marker in range(29):np.add.at(cnt[marker],(state[marker,ok],cur[ok]),1)
 w=(hist+.5)/(hist.sum()+14.5);weights=(cnt+.5)/(cnt.sum(2)[:,:,None]+14.5);gains=np.zeros((29,45));base=0.
 for page,(prev,cur,s) in enumerate(records):
  bl=np.log(w[cur])-np.log1p(-w[prev])
  for m in range(29):gains[m,page]=np.sum(np.log(weights[m,s[m],cur])-np.log1p(-weights[m,s[m],prev])-bl)
 training=gains[:,::2].sum(1);held=gains[:,1::2].sum(1);choice=int(np.argmax(training));den=sum(len(records[i][0]) for i in range(1,45,2));out=dict(name=name,cipher=vs,weights=weights.tolist(),baseline=w.tolist(),train_total=training.tolist(),held_total=held.tolist(),perpage_gain=gains.tolist(),selected_marker=choice,score=float(held[choice]/den),held_nonrepeat_count=den,seconds=time.monotonic()-started);save(name,out);return out
def generate(template,weights,marker,rng):
 vs=[];draws=[]
 for old in template:
  u=rng.random(len(old));state=0;v=[int(np.searchsorted(np.cumsum(weights[0]),u[0]))]
  for i in range(1,len(old)):
   if marker is not None:state^=int(v[-1]==marker)
   if old[i]==old[i-1]:v.append(v[-1]);continue
   w=np.array(weights[state],copy=True);w[v[-1]]=0;w/=sum(w);v.append(min(28,int(np.searchsorted(np.cumsum(w),u[i]))))
  vs.append(v);draws.append(u.tolist())
 return vs,draws
def control(vs,ix):
 rng=np.random.default_rng(330902+ix);w=rng.dirichlet(np.full(29,.5 if ix<6 else 2));w1=w[rng.permutation(29)];marker=int(rng.integers(29));v,u=generate(vs,[w,w1],marker,rng);save('control-'+str(ix)+'-generation',dict(weights=[w.tolist(),w1.tolist()],marker=marker,draws=u,seed=330902+ix));return v,marker
def calibration(vs,r,name,n):
 rng=np.random.default_rng(330901+sum(name.encode()));scores=[]
 for i in range(n):
  v,u=generate(vs,[r['baseline'],r['baseline']],None,rng);q=fit(v,name+'-null-'+str(i));scores.append(q['score']);save(name+'-null-'+str(i)+'-draws',u)
 return dict(name=name,score=r['score'],null=scores,tail=(1+sum(s>=r['score'] for s in scores))/(n+1),selected_marker=r['selected_marker'])
def main():
 vs=prepare()
 if sys.argv[-1]=='pilot':
  v,m=control(vs,0);r=fit(v,'control-0');print(json.dumps(dict(seconds=r['seconds'],forecast440=r['seconds']*440,selected=r['selected_marker'],truth=m)));return
 rows=[]
 for i in range(12):
  v,m=control(vs,i)
  if i==0:
   with gzip.open(D/'control-0.json.gz','rt') as f:r=json.load(f)
   assert r['cipher']==v
  else:r=fit(v,'control-'+str(i))
  a=calibration(v,r,'control-'+str(i),19);a['truth_marker']=m;rows.append(a)
 r=fit(vs,'real');real=calibration(vs,r,'real',199);out=dict(controls=rows,real=real,panels=440,marker_fits=440*29);(D/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
if __name__=='__main__':main()
