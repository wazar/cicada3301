from pathlib import Path
import json,hashlib,numpy as np
R=Path(__file__).resolve().parents[4];F=R/'exploration/persistent-02/feedback';D=R/'exploration/persistent-02/decoder/reset-feedback';models={n:np.load(D/f'model-{n}.npz')['L'] for n in ['p03','complementary']}
def verify(c,seed,p,lit,resets,ends,L):
 h=[];cc=[];score=0.;a=b=29;parts=[]
 for i,z in enumerate(p):
  if i in resets:h=[]
  if i in lit:assert z==0;cc.append(0)
  else:cc.append((z+(seed[len(h)] if len(h)<len(seed) else sum(h[-len(seed):])))%29);h.append(z)
  score+=L[a,b,z];a,b=b,z
  if i in ends:score+=L[a,b,29];a,b=b,29
  parts.append(float(score))
 assert cc==c;return score,parts
x=json.loads((F/'C10/plants.json').read_text());orig=json.loads((F/'C08/plants.json').read_text())['cases'];keys=json.loads((R/'exploration/persistent-02/section/key-grid.json').read_text())['keys'];paths=0;err=0
for p,h in x['sources'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
for ix,s in enumerate(x['cases']):
 o=orig[ix//2];key=keys[ix%2];assert s['truth']==o['truth'] and s['seed']==key['runes'] and s['ends']==o['ends'] and s['reset_before']==o['reset_before'] and s['literal_positions']==o['literal_positions']
 for n,L in models.items():
  verify(s['cipher'],s['seed'],s['truth'],s['literal_positions'],s['reset_before'],s['ends'],L);z=json.loads((F/f'C10/{n}-plant{ix:02}.json').read_text());assert z['outcome']=='COMPLETE'
  for a in z['result']['alternatives']:
   score,_=verify(s['cipher'],a['seed'],a['plain'],a['literal_positions'],s['reset_before'],s['ends'],L);err=max(err,abs(score-a['total']));assert abs(score-a['total'])<1e-8;paths+=1
H=D/'histogram';pins=json.loads((H/'pins.json').read_text())
for p,h in pins.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
s=json.loads((R/'exploration/persistent-02/coordinator/histogram-reset/panels.json').read_text())['cases'][1];hpaths=0
for path in (H/'cells/case1').glob('00-*.json'):
 row=json.loads(path.read_text());L=models[row['model']];n=716 if row['mode']=='full' else 249
 for a in row['alternatives']:
  score,parts=verify(s['panels'][0],a['seed'],a['plaintext'],[],s['reset_before'],s['ends'],L);fit=parts[n-1];pre=parts[248];norm=n+sum(i<n for i in s['ends']);tailnorm=467+sum(i>=249 for i in s['ends']);assert abs(fit-a['score'])<1e-8 and abs(fit/norm-a['fit_score'])<1e-10 and abs((score-pre)/tailnorm-a['continuation_score'])<1e-10;hpaths+=1
out=dict(passed=True,C10_plants=32,C10_paths=paths,C10_max_error=err,histogram_case=1,histogram_paths=hpaths,pins_checked=len(pins));(Path(__file__).parent/'new-adapter-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
