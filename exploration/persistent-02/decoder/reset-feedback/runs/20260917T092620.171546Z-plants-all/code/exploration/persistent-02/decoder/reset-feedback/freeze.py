import random,json,itertools,numpy as np
from common import O,R,P,guard,dump,pins,models,digest
from model import encipher
def main():
 guard();assert not (O/'inputs.json').exists();source=P/'section/A07-inputs.json';a=json.loads(source.read_text());sources=[x for x in a['controls'] if x['family']=='periodic'];assert len(sources)==8;rng=random.Random(260917409);controls=[]
 for si,s in enumerate(sources):
  for k in ([2,3,4,5,6,7,8] if si<4 else [5,6,7,8]):
   seed=[rng.randrange(29) for _ in range(k)];p=s['truth'];reset=s['reset_before'];controls.append(dict(id=f'{si}-{s["id"]}-k{k}',source_index=si,source=s['source'],k=k,seed=seed,truth=p,cipher=encipher(p,seed,reset),ends=s['ends'],reset_before=reset,source_control_id=s['id']))
 packet=json.loads((P/'section/section-packet.json').read_text());nulls=json.loads((P/'decoder/null-calibration-inputs.json').read_text());panels=[packet['body']['runes']]+[x[13:] for x in nulls['packets']];assert len(panels)==20 and all(len(c)==716 for c in panels)
 reset=[x['reset_before_section_rune']-13 for x in json.loads((P/'section/inspection/major-marks/manifest.json').read_text()) if x['reset_before_section_rune']>13];assert reset==[141,262,284,337,381,421,518]
 tables=[]
 for name,lm in models():
  L=np.array([lm.step((a,b),c)[1] for a,b,c in itertools.product(range(30),repeat=3)]).reshape(30,30,30);np.savez_compressed(O/f'model-{name}.npz',L=L);tables.append(dict(name=name,table_sha256=__import__('hashlib').sha256(L.tobytes()).hexdigest(),training_files=getattr(lm,'files',None)))
 obj=dict(seed=260917409,source_pins=pins(),models=tables,controls=controls,actual=dict(panels=panels,ends=packet['body']['explicit_ends'],reset_before=reset,prefix_length=249,band=[5,6,7,8],comparator_source='existing B05 wholepackets sliced13; Fsites/equalitymask heldfixed; no histogram/first-rune conditioning'),scope='NOliteralF; same sharedfeedbackseed restarted at allfixedmarks; smallk instrumentcontrols only; actual gated onfreshreview')
 dump('inputs.json',obj);print(json.dumps(dict(controls=len(controls),models=len(tables),panels=len(panels),input_sha256=digest(O/'inputs.json'))))
if __name__=='__main__':main()
