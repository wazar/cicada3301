"""Identical C05 packets/algorithm with one previously frozen complementary model."""
import extend as ex
import sys,json,pathlib,hashlib,itertools,numpy as np
sys.path.insert(0,str(ex.R/'exploration/persistent-02/decoder'))
import complementary
import plant_literal,actual_literal
O=ex.O/'C06';O.mkdir(exist_ok=True);source=ex.R/'exploration/persistent-02/decoder/complementary-model.json'
lm=complementary.LM();L=np.array([lm.step((a,b),c)[1] for a,b,c in itertools.product(range(30),repeat=3)]).reshape(30,30,30)
ex.q.lm=lm;ex.q.L=L
pins=dict(model=str(source.relative_to(ex.R)),model_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),table_sha256=hashlib.sha256(L.tobytes()).hexdigest(),plant_source='exploration/persistent-02/feedback/C05/plants.json',plant_sha256=hashlib.sha256((ex.O/'C05/plants.json').read_bytes()).hexdigest())
if not (O/'model.json').exists():
 (O/'model.json').write_text(json.dumps(pins,indent=2)+'\n');np.savez_compressed(O/'model.npz',logprob=L);(O/'plants.json').write_bytes((ex.O/'C05/plants.json').read_bytes())
else:assert json.loads((O/'model.json').read_text())==pins and (O/'plants.json').read_bytes()==(ex.O/'C05/plants.json').read_bytes()
plant_literal.O=O;actual_literal.O=ex.O/'C06-actual';actual_literal.O.mkdir(exist_ok=True)
if __name__=='__main__':
 if sys.argv[1]=='plants':
  for ix in map(int,sys.argv[2:]):plant_literal.run(ix)
 elif sys.argv[1]=='actual':
  for ix in map(int,sys.argv[2:]):actual_literal.run(ix)
 elif sys.argv[1]=='summary':actual_literal.summary()
