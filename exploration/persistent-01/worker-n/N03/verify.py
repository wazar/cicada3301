import n03 as n
import numpy as np,json,gzip
with gzip.open(n.O/'evidence.json.gz','rt') as f:r=json.load(f)
cs={p['original_page']:np.array(p['indices']) for p in r['pages']};checked=0
for m in r['real']['matches']:
 a,b=m['pages'];i,j=m['offsets'];L=m['length'];x=cs[a][i:i+L];y=cs[b][j:j+L]
 assert np.array_equal(x[:,None]==x[None,:],y[:,None]==y[None,:]);checked+=1
 if L<64 and i+L<len(cs[a]) and j+L<len(cs[b]):
  x=cs[a][i:i+L+1];y=cs[b][j:j+L+1];assert not np.array_equal(x[:,None]==x[None,:],y[:,None]==y[None,:])
rng=np.random.default_rng(33011439);relabelled=[rng.permutation(29)[cs[p]] for p in n.IDS]
s=n.procedure(relabelled);assert all(s[k]==r['real'][k] for k in ['statistic','seed_matches','pair_maxima'])
(n.O/'verification.json').write_text(json.dumps({'exact_equality_matrix_matches_checked':checked,'all_extensions_maximal':True,'independent_page_relabelling_invariance':True},indent=2));print(checked)
