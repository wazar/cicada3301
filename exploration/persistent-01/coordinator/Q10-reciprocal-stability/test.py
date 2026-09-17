from pathlib import Path
import importlib.util,json,gzip,hashlib,time
O=Path(__file__).resolve().parent;Q=O.parent/'Q09-reciprocal';sp=importlib.util.spec_from_file_location('q09',Q/'test.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);np=m.np
source_files=sorted(Q.glob('*.json.gz'));assert len(source_files)==600
rows=[]
def q(theta):
 a=np.r_[theta,0.];a-=a.max();v=np.exp(a);return v/v.sum()
def js(a,b):
 v=(a+b)/2;return float(.5*np.sum(a*np.log(a/v))+.5*np.sum(b*np.log(b/v)))
for path in source_files:
 m.guard();a=json.load(gzip.open(path,'rt'));C=np.array(a['held_counts']);H=np.array(a['train_counts']);fits=[m.fit(C,k) for k in range(2)];ll=[float((H*np.array(f['log_probabilities'])).sum()) for f in fits];gain=ll[1]-ll[0];qf=q(np.array(a['fits'][1]['theta']));qr=q(np.array(fits[1]['theta']));r=dict(name=a['name'],source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),fits=fits,reverse_held_ll=ll,forward_gain=a['held_gain'],reverse_gain=gain,combined_gain=a['held_gain']+gain,forward_q=qf.tolist(),reverse_q=qr.tolist(),js_divergence=js(qf,qr),qualified=a['qualified'] and all(f['qualified'] for f in fits))
 if a['extra'] and 'q' in a['extra']:r['source_js']=[js(qf,np.array(a['extra']['q'])),js(qr,np.array(a['extra']['q']))]
 with gzip.open(O/path.name,'wt') as f:json.dump(r,f,separators=(',',':'),allow_nan=False)
 rows.append(r)
summary=[]
for stem,n in [('control'+str(i),99) for i in range(4)]+[('actual',199)]:
 a=next(r for r in rows if r['name']==stem);ns=[r for r in rows if r['name'].startswith(stem+'-null')];assert len(ns)==n;unknown=sum(not r['qualified'] for r in ns);stats={}
 for k,lower in [('combined_gain',False),('js_divergence',True)]:
  extreme=sum(r['qualified'] and (r[k]<=a[k] if lower else r[k]>=a[k]) for r in ns)
  stats[k]=dict(value=a[k],tail=(1+extreme)/(n+1) if a['qualified'] and not unknown else None,interval=[(1+extreme)/(n+1),(1+extreme+unknown)/(n+1)] if a['qualified'] else None)
 summary.append(dict(main=stem,forward_gain=a['forward_gain'],reverse_gain=a['reverse_gain'],qualified=a['qualified'],nulls=n,unknown=unknown,statistics=stats,source_js=a.get('source_js')))
result=dict(q09_source_sha256=hashlib.sha256((Q/'test.py').read_bytes()).hexdigest(),panels=len(rows),summary=summary);(O/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
