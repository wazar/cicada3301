from pathlib import Path
import sys,json,random,hashlib,itertools,numpy as np
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/decoder/reset-feedback';sys.path.insert(0,str(D));from common import models
x=json.loads((D/'inputs.json').read_text());a=json.loads((R/'exploration/persistent-02/section/A07-inputs.json').read_text());sources=[s for s in a['controls'] if s['family']=='periodic'];rng=random.Random(260917409);j=0
for si,s in enumerate(sources):
 for k in ([2,3,4,5,6,7,8] if si<4 else [5,6,7,8]):
  row=x['controls'][j];seed=[rng.randrange(29) for _ in range(k)];assert row['seed']==seed and row['truth']==s['truth'] and row['ends']==s['ends'] and row['reset_before']==s['reset_before'];hist=[];c=[]
  for i,p in enumerate(s['truth']):
   if i in s['reset_before']:hist=[]
   v=seed[len(hist)] if len(hist)<k else sum(hist[-k:]);c.append((p+v)%29);hist.append(p)
  assert c==row['cipher'];j+=1
assert j==len(x['controls'])==44
for path,h in x['source_pins'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h
nulls=json.loads((R/'exploration/persistent-02/decoder/null-calibration-inputs.json').read_text())['packets'];packet=json.loads((R/'exploration/persistent-02/section/section-packet.json').read_text());assert x['actual']['panels']==[packet['body']['runes']]+[p[13:] for p in nulls];assert x['actual']['ends']==packet['body']['explicit_ends'];assert x['actual']['reset_before']==[141,262,284,337,381,421,518]
errors={}
for name,lm in models():
 L=np.load(D/f'model-{name}.npz')['L'];err=max(abs(float(L[a,b,c])-lm.step((a,b),c)[1]) for a,b,c in itertools.product(range(30),repeat=3));assert err==0;errors[name]=err
out=dict(passed=True,plants=j,pins=len(x['source_pins']),panels=20,model_cells=54000,errors=errors);(Path(__file__).parent/'reset-input-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
