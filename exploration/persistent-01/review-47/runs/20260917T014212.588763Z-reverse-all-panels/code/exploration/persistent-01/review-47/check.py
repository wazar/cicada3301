import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,numpy as np,hashlib
R=Path(__file__).parent;B=R.parent;P=B/'worker-p/P27';OLD=B/'worker-p/P26';pages=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda x:x['page']);template=[p['indices'] for p in pages];lengths=list(map(len,template));M=~np.eye(29,dtype=bool);ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';maxerr=0.;maxgrad=0.;maxeig=0.;candcount=0;hashes={};summaries=[]
def probs(a):
 w=np.exp(np.r_[a,0]-max(np.r_[a,0]));mat=np.zeros((29,29))
 for x in range(29):
  ids=[i for i in range(29) if i!=x];mat[x,ids]=w[ids]/sum(w[ids])
 return mat

def split(arr):
 return [x.tolist() for x in np.split(arr,np.cumsum(lengths)[:-1])]
def inspect(name):
 global maxerr,maxgrad,maxeig,candcount
 jf=P/(name+'.json');nf=P/(name+'.npz');r=json.loads(jf.read_text());z=dict(np.load(nf));oldj=OLD/(name+'.json');oldn=OLD/(name+'.npz');old=json.loads(oldj.read_text());data=dict(np.load(oldn));seqs=split(data['cipher']);assert data['lengths'].tolist()==lengths
 assert hashlib.sha256(oldj.read_bytes()).hexdigest()==r['original_json_sha256'] and hashlib.sha256(oldn.read_bytes()).hexdigest()==r['original_npz_sha256']
 for path in [jf,nf]:hashes[path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
 counts=[]
 for subset in [seqs[23:],seqs[:23]]:
  C=np.zeros((29,29),int)
  for s in subset:
   for a,b in zip(s,s[1:]):
    if a!=b:C[a,b]+=1
  counts.append(C)
 C,H=counts;assert C.tolist()==r['train_counts'] and H.tolist()==r['held_counts'];assert C.sum()==r['train_events'] and H.sum()==r['held_events'];BP=probs(r['baseline']['a']);lp=np.zeros((29,29));lp[M]=np.log(BP[M]);obj=-sum((C*lp).flat)/C.sum();g=np.zeros(29)
 for x in range(29):g+=C[x].sum()*BP[x]-C[x]
 g/=C.sum();err=max(abs(obj-r['baseline']['objective']),max(abs(g[:28]-r['baseline']['gradient'])));maxerr=max(maxerr,err);maxgrad=max(maxgrad,float(max(abs(g[:28]))));assert err<1e-12;qualified=bool(r['baseline']['success'] and max(abs(g[:28]))<=2e-6);assert qualified==r['baseline']['qualified'];tr=float((C*lp).sum());he=float((H*lp).sum());assert abs(tr-r['baseline_train_ll'])<1e-9 and abs(he-r['baseline_held_ll'])<1e-9
 A=C+.5*M;A=A/A.sum(1)[:,None];orders={}
 for e in r['eigenvectors']:
  v=np.array(e['real'])+1j*np.array(e['imag']);ev=complex(*e['eigenvalue']);res=float(max(abs(A@v-ev*v)));maxeig=max(maxeig,res);assert res<1e-12;ph=np.angle(v)%(2*np.pi);ix=sorted(range(29),key=lambda i:(ph[i],i));gaps=[(ph[ix[j+1]]-ph[ix[j]]) for j in range(28)]+[ph[ix[0]]+2*np.pi-ph[ix[-1]]];accept=ev.imag>1e-8 and min(abs(v))>1e-10;assert accept==e['accepted'];assert abs(min(gaps)-e['minimum_phase_gap'])<1e-14 and sum(x<=1e-10 for x in gaps)==e['near_ties']
  if accept:
   at=ix.index(0);cyc=tuple(ix[at:]+ix[:at]);assert list(cyc)==e['cycle'];orders.setdefault(cyc,[]).append(e['index'])
 assert sorted(orders)==[tuple(c['cycle']) for c in r['candidates']];candcount+=len(orders)
 for k,c in enumerate(r['candidates']):
  cyc=c['cycle'];f=np.argsort(cyc);assert f.tolist()==c['f'] and orders[tuple(cyc)]==c['eigen_indices'];tc=np.zeros(29,int);hc=np.zeros(29,int)
  for a in range(29):
   for b in range(29):tc[(f[b]-f[a])%29]+=C[a,b];hc[(f[b]-f[a])%29]+=H[a,b]
  q=np.r_[0,(tc[1:]+.5)/(C.sum()+14)];assert tc.tolist()==c['train_counts'] and hc.tolist()==c['held_counts'] and np.array_equal(q,c['q']);t=float(tc[1:]@np.log(q[1:]));h=float(hc[1:]@np.log(q[1:]));assert max(abs(t-c['train_ll']),abs(h-c['held_ll']),abs(h-he-c['held_gain']))<1e-9
  dec=[]
  for s in seqs:dec+=[255]+[(int(f[b])-int(f[a]))%29 for a,b in zip(s,s[1:])]
  assert dec==z['decoded'][k].tolist()
  if 'cycle' in r:
   true=np.argsort(r['cycle']);tuples=[]
   for a in range(1,29):
    hist=np.bincount((f-a*true)%29,minlength=29)
    tuples.extend((int(hist[b]),a,b) for b in range(29))
   best=max(n for n,a,b in tuples);got=r['order_recovery'][k];assert got['maximum_matches']==best and got['affine_maps']==[[a,b] for n,a,b in tuples if n==best] and got['exact']==(best==29);assert got['anchored_maximum_matches']==max(n for n,a,b in tuples if b==0)
 selected=min(range(len(r['candidates'])),key=lambda j:(-r['candidates'][j]['train_ll'],r['candidates'][j]['cycle'])) if r['candidates'] else None;assert selected==r['selected'];assert r['qualified']==(qualified and selected is not None)
 if selected is not None:assert r['held_gain']==r['candidates'][selected]['held_gain']
 assert r['forward_gain']==old['held_gain'] and r['both_qualified']==(old['qualified'] and r['qualified'])
 assert r['sum_gain']==r['held_gain']+old['held_gain']
 def agreement(first,second):
  f=np.argsort(first);g=np.argsort(second);scores=[]
  for a in range(1,29):
   bins=np.bincount((f-a*g)%29,minlength=29);scores.extend((int(bins[b]),a,b) for b in range(29))
  best=max(n for n,a,b in scores);return dict(maximum_matches=best,affine_maps=[[a,b] for n,a,b in scores if n==best],anchored_maximum_matches=max(n for n,a,b in scores if b==0),exact=best==29)
 assert agreement(r['candidates'][r['selected']]['cycle'],old['candidates'][old['selected']]['cycle'])==r['affine_agreement']
 if 'cycle' in old:assert [agreement(c['cycle'],old['cycle']) for c in r['candidates']]==r['truth_affine_agreement']
 return r
for i in range(5):
 name=f'control-{i}' if i<4 else 'actual';main=inspect(name);ns=[inspect(name+f'-null-{j:03}') for j in range(99 if i<4 else 199)];unknown=sum(not n['both_qualified'] for n in ns);ge=sum(n['both_qualified'] and n['sum_gain']>=main['sum_gain'] for n in ns);ga=sum(n['both_qualified'] and n['affine_agreement']['maximum_matches']>=main['affine_agreement']['maximum_matches'] for n in ns);s=json.loads((P/(name+'-summary.json')).read_text());bounds=[(1+ge)/(len(ns)+1),(1+ge+unknown)/(len(ns)+1)];assert s['tail_interval']==bounds and s['tail']==(bounds[0] if not unknown else None) and s['secondary_agreement_tail']==((1+ga)/(len(ns)+1) if not unknown else None);summaries.append(dict(name=name,forward=main['forward_gain'],reverse=main['held_gain'],sum_gain=main['sum_gain'],agreement=main['affine_agreement'],tail=s['tail'],secondary=s['secondary_agreement_tail']));print(name,s['tail'],flush=True)
(R/'inputs.json').write_text(json.dumps(hashes,indent=2));out=dict(status='PASS',panels=600,candidates=candcount,max_gradient=maxgrad,max_baseline_error=maxerr,max_eigen_residual=maxeig,rows=summaries);(R/'result.json').write_text(json.dumps(out,indent=2));print(out)
