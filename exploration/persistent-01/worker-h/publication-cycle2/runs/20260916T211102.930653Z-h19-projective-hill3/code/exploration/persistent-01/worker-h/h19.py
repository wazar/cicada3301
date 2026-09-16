import pathlib,json,numpy as np,hashlib,gzip,datetime,time,sys
R=pathlib.Path(__file__).parent;M=[m for m in json.load(open(R.parent/'worker-f/F06-maps.json')) if m['page'] in [0,1,2,3,5]];C=[np.array(m['indices'],dtype=int) for m in M];rng=np.random.default_rng(2026091739)
D=np.array([[1,a,b] for a in range(29) for b in range(29)]+[[0,1,b] for b in range(29)]+[[0,0,1]],dtype=np.int64);assert D.shape==(871,3)
def inverse(m):
 a=np.c_[m.copy()%29,np.eye(3,dtype=int)]
 for i in range(3):
  j=next(j for j in range(i,3) if a[j,i]);a[[i,j]]=a[[j,i]];a[i]=a[i]*pow(int(a[i,i]),-1,29)%29
  for k in range(3):
   if k!=i:a[k]=(a[k]-a[k,i]*a[i])%29
 return a[:,3:]
def det(m):
 a,b,c=m;return int(np.dot(a,np.cross(b,c)))%29
def normalize(v):return tuple((v*pow(int(next(x for x in v if x)),-1,29)%29).tolist())
K=np.array([[1,1,1],[1,2,3],[1,4,9]]);KI=inverse(K);assert np.array_equal(K@KI%29,np.eye(3,dtype=int));truth={normalize(v) for v in KI};direction_index={tuple(v):i for i,v in enumerate(D.tolist())};truthindices={direction_index[v] for v in truth};calls=0

def search(vs,detail=False):
 global calls
 calls+=1;phases=[]
 for phase in range(3):
  blocks=[];fit=[];valid=[];pre=[];test=[];maps=[];offset=0
  for page,v in enumerate(vs):
   n=(len(v)-phase)//3;b=v[phase:phase+3*n].reshape(n,3);h=n//2;t=2*h//3
   assert t>=1 and h>t and n>h
   blocks.append(b);fit.extend(range(offset,offset+t));valid.extend(range(offset+t,offset+h));pre.extend(range(offset,offset+h));test.extend(range(offset+h,offset+n));maps.append(dict(page_index=page,phase=phase,block_count=n,prefix_blocks=h,fit_blocks=t,leading_runes=list(range(phase)),tail_runes=list(range(phase+3*n,len(v)))));offset+=n
  B=np.concatenate(blocks);Y=B@D.T%29;fit=np.array(fit);valid=np.array(valid);pre=np.array(pre);test=np.array(test)
  counts=np.bincount((Y[fit]+29*np.arange(871)).ravel(),minlength=871*29).reshape(871,29)+1;q=counts/counts.sum(1)[:,None]
  scores=np.mean(np.log(29*q[np.arange(871)[:,None],Y[valid].T]),axis=1);rank=np.argsort(-scores,kind='stable');selected=[]
  for idx in rank:
   if len(selected)<2 or det(D[selected+[int(idx)]]):selected.append(int(idx))
   if len(selected)==3:break
  chosen=D[selected];inv=inverse(chosen);Z=Y[:,selected];assert np.array_equal(Z@inv.T%29,B)
  h=np.array([np.bincount(Z[pre,j],minlength=29)+1 for j in range(3)]);qq=h/h.sum(1)[:,None];suffix=float(np.mean(np.log(29*qq[np.arange(3)[:,None],Z[test].T])))
  row=dict(phase=phase,prefix_score=float(sum(scores[selected])),suffix_score=suffix,selected=selected,matrix=chosen.tolist(),inverse=inv.tolist(),selected_prefix_gains=scores[selected].tolist(),truth_directions_recovered=len(set(selected)&truthindices),maps=maps,train_blocks=len(pre),test_blocks=len(test))
  if detail:row.update(all_prefix_gains=scores.tolist(),output=Z.tolist(),prefix_probabilities=qq.tolist())
  phases.append(row)
 selected_phase=max(range(3),key=lambda i:phases[i]['prefix_score']);return dict(score=phases[selected_phase]['suffix_score'],selected_phase=selected_phase,phases=phases)
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def params(vs):
 pre=[v[:len(v)//2] for v in vs];a=np.concatenate(pre);w=np.bincount(a,minlength=29)+1;w=w/w.sum();pairs=sum(len(v)-1 for v in pre);rep=sum(int(np.sum(v[:-1]==v[1:])) for v in pre)/pairs;mat=[]
 for i in range(29):
  row=w.copy();row[i]=0;row=row/row.sum()*(1-rep);row[i]=rep;mat.append(np.cumsum(row))
 return w,rep,np.array(mat)
def simulate(vs,par):
 w,rep,mat=par;out=[]
 for vv in vs:
  us=rng.random(len(vv));v=np.empty(len(vv),dtype=int);v[0]=np.searchsorted(np.cumsum(w),us[0])
  for i in range(1,len(v)):v[i]=np.searchsorted(mat[v[i-1]],us[i])
  out.append(v)
 return out
def summarize(r):return dict(score=r['score'],selected_phase=r['selected_phase'],selected_rows=r['phases'][r['selected_phase']]['selected'])
# Pilot fullnullcost beforeexpanded work. No real outputselection is inspected here.
gate();par=params(C);pilot=[];t0=time.monotonic()
for _ in range(10):pilot.append(summarize(search(simulate(C,par))))
pilotsec=time.monotonic()-t0;projected=pilotsec/10*(199+6*99);assert projected<850
(R/'H19-pilot.json').write_text(json.dumps(dict(nulls=pilot,seconds=pilotsec,projected_seconds=projected),indent=2))
A='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';sources=[]
for f in pathlib.Path('audit/parallel-01/reference/sources').glob('solved_*.txt'):
 b=f.read_bytes();p=np.array([A.index(c) for c in b.decode() if c in A]);sources.append(dict(path=str(f),sha256=hashlib.sha256(b).hexdigest(),plain=p))
sources=sorted(sources,key=lambda s:(-len(s['plain']),s['path']));sets=[[s] for s in sources[:4]]+[[sources[-1]],sources[:5]];controls=[]
for source_set in sets:
 gate();vs=[];pp=[]
 for s in source_set:
  p=s['plain'];p=p[:len(p)//3*3];c=p.reshape(-1,3)@K.T%29;assert np.array_equal(c@KI.T%29,p.reshape(-1,3));vs.append(c.ravel());pp.append(p.tolist())
 result=search(vs,True);cp=params(vs);ns=[]
 for rep in range(99):
  if rep%20==0:gate()
  ns.append(summarize(search(simulate(vs,cp))))
 controls.append(dict(sources=[{k:v for k,v in s.items() if k!='plain'} for s in source_set],plain=pp,cipher=[v.tolist() for v in vs],result=result,null=ns,tail=(1+sum(n['score']>=result['score'] for n in ns))/100))
assert any(c['tail']<=.05 for c in controls)
gate();real=search(C,True);null=pilot[:]
for rep in range(10,199):
 if rep%10==0:gate()
 null.append(summarize(search(simulate(C,par))))
r=dict(real=real,tail=(1+sum(n['score']>=real['score'] for n in null))/200,null=null,controls=[dict(pages=len(c['sources']),runes=sum(map(len,c['plain'])),score=c['result']['score'],phase=c['result']['selected_phase'],truth_directions_recovered=c['result']['phases'][c['result']['selected_phase']]['truth_directions_recovered'],tail=c['tail']) for c in controls],directions=871,phases=3,real_pages=[m['page'] for m in M],total_search_calls=calls,real_null_searches=199,control_null_searches=594,pilot_seconds=pilotsec,seed=2026091739,null_repeat_probability=par[1])
with gzip.open(R/'H19-evidence.json.gz','wt') as f:json.dump(dict(controls=controls,real_cipher=[c.tolist() for c in C],K=K.tolist(),KI=KI.tolist(),truth_directions=sorted(truthindices)),f)
(R/'H19-result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['real','null']},indent=2));print(summarize(real))
