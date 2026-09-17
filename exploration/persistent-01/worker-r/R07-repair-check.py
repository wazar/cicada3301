import pathlib,json,numpy as np
P=pathlib.Path(__file__).resolve().parent;ns={'__file__':str(P/'R07.py')};exec((P/'R07.py').read_text().split('args=argparse.ArgumentParser()')[0],ns)
rng=np.random.default_rng(479999);A=rng.integers(1,100,(29,29)).astype(float);np.fill_diagonal(A,0);z=rng.normal(0,.2,28);H=ns['hessian'](z,A);numerical=np.empty((28,28));eps=1e-5
for j in range(28):
 e=np.zeros(28);e[j]=eps;numerical[:,j]=(ns['obj'](z+e,A)[1]-ns['obj'](z-e,A)[1])/(2*eps)
err=float(np.max(abs(H-numerical)));assert err<1e-8
loc=json.loads((P/'R07-failure-location.json').read_text());probs=[]
for f in loc['baseline_fit']['baseline_fits']:
 th=np.array(f['theta']);lp=np.broadcast_to(th,(29,29)).copy();np.fill_diagonal(lp,-np.inf);lp-=ns['logsumexp'](lp,axis=1)[:,None];probs.append(np.exp(lp))
vs,_=ns['generate'](np.array(probs),loc['failed_seed']);tr,he=ns['counts'](vs);fits=[]
for C in tr:
 f,_=ns['fitweights'](C);fits.append(f)
assert max(x['pre_gradient_max'] for x in fits)>1e-7
out=dict(hessian_max_error=err,failed_seed=loc['failed_seed'],streams=vs,train_counts=tr.tolist(),fits=fits);(P/'R07-repair-check.json').write_text(json.dumps(out,indent=2)+'\n');print('HESSIAN ERROR',err,'PREPOST',[(f['pre_gradient_max'],f['gradient_max']) for f in fits])
