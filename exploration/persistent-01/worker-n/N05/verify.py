import pathlib,json,gzip,numpy as np
O=pathlib.Path(__file__).resolve().parent
with gzip.open(O/'repaired-evidence.json.gz','rt') as f:e=json.load(f)
X=np.array(e['feature_matrix']);Z=np.array(e['row_design']);base=np.array(e['baseline_positions']);coef=np.array(e['real']['font_corrections']);rows=np.array(e['real']['row_parameters']).ravel();pred=base+X@coef+Z@rows;assert np.allclose(pred,e['real']['prediction']);K=len(e['classes']);delta=np.zeros(X.shape[1]);delta[K:2*K]=[8*(c%2) for c in e['classes']];target=8*np.array(e['class_correlated']['bits']);assert np.array_equal(X@delta,target)
# Saved layout prediction coefficients depend only on training rows and held prefixes.
train=np.array(e['train']);prefix=np.array(e['held_prefix']);held=np.array(e['held_suffix']);assert not set(held)&(set(train)|set(prefix));assert len(set(train)|set(prefix)|set(held))==len(e['records'])
out={'prediction_reconstruction':True,'class_correlated_binary_shift_exactly_in_font_bearing_span':True,'max_equivalence_error':float(np.max(abs(X@delta-target))),'train_prefix_suffix_disjoint_complete':True,'pixel_controls_instances_each':[len(v['measured']) for v in e['pixel_controls']]};(O/'verification.json').write_text(json.dumps(out,indent=2));print(out)
