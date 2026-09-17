import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,hashlib
R=Path(__file__).parent;B=R.parent;Q=B/'coordinator/Q09-reciprocal';NEW=B/'coordinator/Q10-reciprocal-stability';F=B/'worker-f/F06-maps.json';pages=sorted(json.loads(F.read_text()),key=lambda p:p['page']);templates=[p['indices'] for p in pages];assert len(pages)==45 and not {4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in pages};ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
inv=[0]+[next(y for y in range(1,29) if x*y%29==1) for x in range(1,29)];assert all((inv[inv[(a+b)%29]]-b)%29==a for a in range(29) for b in range(29));hashes={};maxg=maxerr=0.;panels=0;drawcount=0

def mat(theta,model):
 weights=np.exp(np.r_[theta,0.]-max(np.r_[theta,0.]));out=np.zeros((29,29))
 for x in range(29):
  raw=[0 if y==x else weights[y if model==0 else (inv[y]-x)%29] for y in range(29)];out[x]=np.array(raw)/sum(raw)
 return out

def read(name):
 p=Q/(name+'.json.gz');data=p.read_bytes();hashes[p.name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)};return json.loads(gzip.decompress(data))
def audit(r):
 global maxg,maxerr,panels
 panels+=1;seqs=r['cipher'];assert len(seqs)==45;C=[]
 for seq,t,dec in zip(seqs,templates,r['decoded']):
  assert len(seq)==len(t) and seq[0]==t[0] and dec==[255]+[(inv[b]-a)%29 for a,b in zip(seq,seq[1:])];assert [a==b for a,b in zip(seq,seq[1:])]==[a==b for a,b in zip(t,t[1:])]
 for subset in [seqs[23:],seqs[:23]]:
  c=np.zeros((29,29),int)
  for seq in subset:
   for a,b in zip(seq,seq[1:]):
    if a!=b:c[a,b]+=1
  C.append(c)
 assert C[0].tolist()==r['train_counts'] and C[1].tolist()==r['held_counts'];held=[]
 for model,f in enumerate(r['fits']):
  P=mat(f['theta'],model);g=np.zeros(29);obj=0.;h=0
  for x in range(29):
   for y in range(29):
    if y==x:assert f['log_probabilities'][x][y]==0;continue
    lp=np.log(P[x,y]);assert abs(lp-f['log_probabilities'][x][y])<1e-12;obj-=C[0][x,y]*lp;h+=C[1][x,y]*lp;index=y if model==0 else (inv[y]-x)%29;g[index]+=C[0][x].sum()*P[x,y]-C[0][x,y]
  obj/=C[0].sum();g/=C[0].sum();err=max(abs(obj-f['objective']),float(abs(g[:28]-f['gradient']).max()));maxerr=max(maxerr,err);maxg=max(maxg,float(abs(g[:28]).max()));assert err<1e-12;assert f['qualified']==bool(f['success'] and abs(g[:28]).max()<=2e-6);assert abs(h-r['held_ll'][model])<1e-8;held.append(h)
 assert abs(held[1]-held[0]-r['held_gain'])<1e-8 and r['qualified']==all(f['qualified'] for f in r['fits'])


def profile(theta):
 w=np.exp(np.r_[theta,0.]-max(np.r_[theta,0.]));return w/sum(w)
def js(a,b):
 entropy=lambda v:-sum(float(x)*np.log(float(x)) for x in v);return float(entropy((a+b)/2)-(entropy(a)+entropy(b))/2)
original_hashes=json.loads((B/'review-54/inputs.json').read_text());rows=[];reference=[]
for path in sorted(NEW.glob('*.json.gz')):
 name=path.name[:-8];n=json.loads(gzip.decompress(path.read_bytes()));oldpath=Q/path.name;old=json.loads(gzip.decompress(oldpath.read_bytes()));h=hashlib.sha256(oldpath.read_bytes()).hexdigest();assert h==n['source_sha256']==original_hashes[path.name]['sha256'];hashes['reverse/'+path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
 r=dict(old,train_counts=old['held_counts'],held_counts=old['train_counts'],fits=n['fits'],held_ll=n['reverse_held_ll'],held_gain=n['reverse_gain'],qualified=all(f['qualified'] for f in n['fits']));audit(r);assert n['qualified']==(old['qualified'] and r['qualified']);assert n['forward_gain']==old['held_gain'] and n['combined_gain']==old['held_gain']+n['reverse_gain']
 a=profile(old['fits'][1]['theta']);b=profile(n['fits'][1]['theta']);assert max(abs(a-n['forward_q']))<1e-15 and max(abs(b-n['reverse_q']))<1e-15;d=js(a,b);assert abs(d-n['js_divergence'])<2e-15
 if old['extra'] and 'q' in old['extra']:
  assert max(abs(x-y) for x,y in zip([js(a,np.array(old['extra']['q'])),js(b,np.array(old['extra']['q']))],n['source_js']))<2e-15
 rows.append(n);entry=dict(name=name,directions=[])
 for direction,counts,ll in [('forward',old['held_counts'],old['held_ll']),('reverse',old['train_counts'],n['reverse_held_ll'])]:
  events=sum(map(sum,counts));uniform=-events*np.log(28);gains=[x-uniform for x in ll];assert abs(gains[1]-gains[0]-(old['held_gain'] if direction=='forward' else n['reverse_gain']))<1e-9;entry['directions'].append(dict(direction=direction,events=events,uniform_ll=float(uniform),destination_minus_uniform=float(gains[0]),reciprocal_minus_uniform=float(gains[1])))
 entry['combined_destination_minus_uniform']=sum(x['destination_minus_uniform'] for x in entry['directions']);entry['combined_reciprocal_minus_uniform']=sum(x['reciprocal_minus_uniform'] for x in entry['directions']);reference.append(entry)
summary=json.loads((NEW/'summary.json').read_text());assert panels==600
for s in summary['summary']:
 main=next(r for r in rows if r['name']==s['main']);nulls=[r for r in rows if r['name'].startswith(s['main']+'-null')];assert len(nulls)==s['nulls'];bad=sum(not r['qualified'] for r in nulls);assert bad==s['unknown']
 for metric,lower in [('combined_gain',False),('js_divergence',True)]:
  ge=sum(r['qualified'] and (r[metric]<=main[metric] if lower else r[metric]>=main[metric]) for r in nulls);bounds=[(1+ge)/(len(nulls)+1),(1+ge+bad)/(len(nulls)+1)];assert s['statistics'][metric]['interval']==bounds and s['statistics'][metric]['tail']==(bounds[0] if not bad else None)
(R/'constant-reference.json').write_text(json.dumps(reference,indent=2));(R/'inputs.json').write_text(json.dumps(hashes,indent=2));(R/'result.json').write_text(json.dumps(dict(status='PASS',reverse_panels=panels,fits=2*panels,max_gradient=maxg,max_objective_gradient_error=maxerr,summary=summary['summary'],actual_uniform_comparison=next(x for x in reference if x['name']=='actual')),indent=2));print(next(x for x in reference if x['name']=='actual'))
