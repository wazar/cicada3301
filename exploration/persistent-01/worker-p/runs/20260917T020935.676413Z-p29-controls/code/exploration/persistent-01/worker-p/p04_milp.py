import pathlib,json,gzip,datetime,time,platform,warnings
import numpy as np
import scipy
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix,save_npz
D=pathlib.Path('exploration/persistent-01/worker-p/P04');B=D.parents[1];e=json.load(gzip.open(D/'support-evidence.json.gz','rt'));start=time.monotonic()
def guard():
 assert not (B/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
# Explicit general formulation, sparse coefficient matrix retained independently of solver.
def build(support,choices,label):
 letters=[ord(c)-65 for c in support];L=len(letters);variables=[dict(kind='assign',rune=r,letter=l) for r in range(29) for l in letters];offsets=[]
 for p,opts in zip(e['pages'],choices):
  offsets.append(len(variables));variables.extend(dict(kind='choice',page=p['page'],index=j,counts=c['counts'],aliases=c.get('aliases',[])) for j,c in enumerate(opts))
 row=[];col=[];val=[];rhs=[];rows=[]
 def eq(items,b,desc):
  k=len(rhs);rhs.append(b);rows.append(desc)
  for j,v in items:row.append(k);col.append(j);val.append(v)
 for r in range(29):eq([(r*L+i,1) for i in range(L)],1,dict(kind='one_letter',rune=r))
 for pi,(p,opts,off) in enumerate(zip(e['pages'],choices,offsets)):
  actual=dict(p['output_counts_by_rune']);eq([(off+j,1) for j in range(len(opts))],1,dict(kind='one_window',page=p['page']))
  for li,l in enumerate(letters):eq([(r*L+li,actual[r]) for r in range(29)]+[(off+j,-c['counts'][l]) for j,c in enumerate(opts)],0,dict(kind='count',page=p['page'],letter=l))
 A=coo_matrix((np.array(val,float),(row,col)),shape=(len(rhs),len(variables))).tocsc();save_npz(D/(label+'-matrix.npz'),A);np.save(D/(label+'-rhs.npy'),np.array(rhs));(D/(label+'-model.json')).write_text(json.dumps(dict(support=support,variables=variables,rows=rows),indent=2));return A,np.array(rhs),variables
def run(support,choices,label,limit):
 guard();A,rhs,vars=build(support,choices,label);opts=dict(disp=True,presolve=True,time_limit=float(limit),mip_rel_gap=0.0,threads=1);ts=time.monotonic();res=milp(np.zeros(len(vars)),integrality=np.ones(len(vars)),bounds=Bounds(np.zeros(len(vars)),np.ones(len(vars))),constraints=LinearConstraint(A,rhs,rhs),options=opts);out=dict(label=label,options=opts,status=int(res.status),message=res.message,success=bool(res.success),seconds=time.monotonic()-ts,rows=A.shape[0],variables=A.shape[1],nonzero=A.nnz,x=None if res.x is None else res.x.tolist(),node_count=getattr(res,'mip_node_count',None),mip_gap=getattr(res,'mip_gap',None));out['classification']='INFEASIBLE' if res.status==2 else 'UNKNOWN'
 if res.x is not None:
  x=np.rint(res.x);assert np.max(abs(res.x-x))<1e-6 and np.all((x==0)|(x==1)) and np.array_equal(A@x,rhs);out['classification']='FEASIBLE';out['integer_x']=x.astype(int).tolist()
 (D/(label+'-result.json')).write_text(json.dumps(out,indent=2));print('RESULT',json.dumps({k:v for k,v in out.items() if k not in ['x','integer_x']}),flush=True);return out
# actual-output planted common codebook on canonical consonantsB,C,D
support='BCD';letters=[ord(c)-65 for c in support];positive=[]
for p in e['pages']:
 cnt=[0]*26
 for r,num in p['output_counts_by_rune']:cnt[letters[r%3]]+=num
 positive.append([dict(counts=cnt,aliases=[dict(control=True)])])
a=run(support,positive,'positive',10);assert a['classification']=='FEASIBLE'
negative=json.loads(json.dumps(positive));old=negative[0][0]['counts'][1];negative[0][0]['counts'][1]=1;negative[0][0]['counts'][2]+=old-1;assert min(v for r,v in e['pages'][0]['output_counts_by_rune'])>1
b=run(support,negative,'negative',10);assert b['classification']=='INFEASIBLE'
assert not set.intersection(*[{'BCD'} if i!=1 else {'CD'} for i in range(5)])
results=[]
for i,support in enumerate(e['common_supports']):
 limit=max(0,120-(time.monotonic()-start))
 if limit<.1:results.append(dict(support=support,classification='UNKNOWN',reason='aggregate_budget'));continue
 choices=[p['groups'][support] for p in e['pages']];r=run(support,choices,f'real-{i}',limit);r['support']=support;results.append(r)
out=dict(scipy=scipy.__version__,python=platform.python_version(),aggregate_seconds=time.monotonic()-start,thread_limit=1,controls=[{k:v for k,v in q.items() if k not in ['x','integer_x']} for q in [a,b]],real=[{k:v for k,v in q.items() if k not in ['x','integer_x']} for q in results]);(D/'results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
