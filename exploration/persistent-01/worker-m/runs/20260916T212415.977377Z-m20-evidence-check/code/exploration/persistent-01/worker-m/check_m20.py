import pathlib,json,gzip,math,numpy as np
import m20
R=pathlib.Path(__file__).parent
with gzip.open(R/'M20-real.json.gz','rt') as f:e=json.load(f)
r=e['result'];vs=[np.array(x) for x in e['cipher']];q=np.array(r['train_options'][r['train_option']]['q']);mat=np.array(r['matrix']);inverse=np.array(r['inverse']);assert np.array_equal(mat@inverse%29,np.eye(3,dtype=int))
for o in r['test_options']:
 ix=np.array(o['indices']);b=vs[2][ix];z=np.array([[sum(int(bi[k])*int(row[k]) for k in range(3))%29 for row in mat] for bi in b]);assert z.tolist()==o['outputs'];assert np.array_equal(z@inverse.T%29,b)
 for label,key in [('prefix','prefix_gain'),('suffix','suffix_gain')]:
  zz=z[o[label+'_mask']];score=sum(math.log(29*q[j,int(x)]) for row in zz for j,x in enumerate(row))/(3*len(zz));assert abs(score-o[key])<1e-12
# Counterfactual replacing every test suffix rune cannot affect train matrix, q, or prefix phase choice.
vv=[x.copy() for x in vs];cut=len(vv[2])//2;vv[2][cut:]=(np.arange(len(vv[2])-cut)*13+7)%29;s=m20.search(vv,True)
assert s['train_options']==r['train_options'];assert s['matrix']==r['matrix'];assert s['test_phase']==r['test_phase'];assert [x['prefix_gain'] for x in s['test_options']]==[x['prefix_gain'] for x in r['test_options']]
assert len(e['null'])==999;tail=(1+sum(x['score']>=r['score'] for x in e['null']))/1000;assert tail==e['tail']
controls=json.load(open(R/'M20-controls.json'))
for c in controls:
 with gzip.open(R/('M20-control-'+str(c['control'])+'.json.gz'),'rt') as f:x=json.load(f)
 assert len(x['null'])==199;assert c['tail']==(1+sum(n['score']>=x['result']['score'] for n in x['null']))/200
 for j,span in enumerate(c['source_spans']):
  plain=np.array(c['plain'][j]).reshape(-1,3);n=len(plain);cipher=np.array(x['cipher'][j])[span['phase']:span['phase']+3*n].reshape(-1,3);assert np.array_equal((plain@np.array(c['K']).T+np.array(c['affine_shift']))%29,cipher);assert np.array_equal((cipher-np.array(c['affine_shift']))@np.array(c['inverse']).T%29,plain)
report=dict(matrix_inverse=True,independent_scalar_test_replay=True,counterfactual_suffix_selection_isolation=True,exact_control_reencryption=6,null_tails_recounted=True,real_null_exceedances=sum(x['score']>=r['score'] for x in e['null']),real_test_blocks=r['test_options'][r['test_phase']]['suffix_blocks'])
(R/'M20-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
