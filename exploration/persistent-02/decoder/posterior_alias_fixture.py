import math,json
from posterior import analyze
from compare import LM,O
lm=LM();examples=[]
for cipher,key,periodic,expected_paths,literal_probability in [([0,1,0,2,0],[0],True,8,.5),([0,0,0],[0,0],False,7,4/7)]:
 ends={len(cipher)-1};r=analyze(cipher,key,lm.extend,periodic=periodic,ends=ends,cuts=range(len(cipher)+1));score=lm.score(cipher,ends)*(len(cipher)+len(ends));assert int(r['number_of_legal_decision_paths'])==expected_paths;assert abs(r['log_partition']-(score+math.log(expected_paths)))<1e-12
 assert all(abs(b['literal']['probability']-literal_probability)<1e-12 for b in r['branch_marginals']);examples.append(dict(cipher=cipher,key=key,periodic=periodic,distinct_plaintexts=1,expected_paths=expected_paths,expected_literal_probability=literal_probability,result=r))
out=dict(passed=True,examples=examples,scope='All legal paths produce identical plaintext; sum-product mass is over decisions, not distinct plaintext. Finite exhaustion conditions the branch distribution.');(O/'posterior-alias-fixture.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
