import json,pathlib,hashlib,numpy as np
O=pathlib.Path(__file__).resolve().parent;L=O.parent/'worker-l';R=O.parents[2]
def read(p):return json.loads(p.read_text())
d=L/'l1-conditional';cal=read(d/'calibration.json');nu=read(d/'null-arrays.json');su=read(d/'summary.json');mu=np.array(cal['mean']);sd=np.array(cal['sd']);z=(np.array(nu['scores'])-mu)/sd;sel=z[:,0].argmin(1);stat=-z[np.arange(len(z)),1,sel];assert np.allclose(stat,nu['statistics']);p=(1+sum(stat>=su['held_statistic']))/(len(stat)+1);assert p==su['wholeprocedure_p']
d=L/'l2';a=read(d/'null-and-controls.json');s=read(d/'summary.json');p2=(1+sum(v[1]>=s['real_scores_train_held'][1] for v in a['null']))/401;assert p2==s['held_p'];x=read(d/'inputs-and-maps.json');assert hashlib.sha256((R/'exploration/persistent-01/worker-f/F06-maps.json').read_bytes()).hexdigest()==x['F06_maps_sha256']
d=L/'l3';a=read(d/'null-and-control-arrays.json');s=read(d/'summary.json');v=s['real_rates_train_held'][1];p3=(1+sum(r['rates'][1]>=v for r in a['null']))/201;p4=(1+sum(r['rates'][1]<=v for r in a['controls']))/201;assert p3==s['held_upper_tail_vs_M1'] and p4==s['held_lower_tail_vs_fitted_swap']
result={'L1_p':p,'L2_p':p2,'L3_M1_p':p3,'L3_swap_p':p4,'F06_input_hash_matches':True};(O/'ranks.json').write_text(json.dumps(result,indent=2));print(result)
