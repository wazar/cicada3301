import pathlib,gzip,json,collections
import numpy as np
R=pathlib.Path(__file__).parent; d=json.load(gzip.open(R/'Q01-evidence.json.gz','rt')); train=d['train'];held=d['held']; counts=d['counts'];offs=np.cumsum([0]+counts);base=[w for r in d['regions'] for w in r['units']];fits=0
for case in [d['real'],d['baseline']]+d['controls']+d['ordinary']:
 units=case.get('units',base);coef=np.array([[sum(x*pow(a,len(w)-i-1,29) for i,x in enumerate(w[:-1]))%29 for w in units] for a in range(1,29)])
 t=case['terminals']
 def check(t,out):
  global fits
  v=(coef+np.array(t))%29
  tr=[[sum(row[j]==b for j in train) for b in range(29)] for row in v]
  he=[[sum(row[j]==b for j in held) for b in range(29)] for row in v]
  assert tr==out['training_matrix'] and he==out['held_matrix']
  candidates=[(-tr[a][b],a+1,b) for a in range(28) for b in range(29)]
  _,a,b=min(candidates);assert (a,b)==(out['a'],out['b']); assert he[a-1][b]==out['held_hits']
  assert [(b-int(coef[a-1,j]))%29 for j in held]==out['predictions'];fits+=1
 check(t,case['fit'])
 for shifts,out in zip(case['shifts'],case['null_parameters']):
  tt=[]
  for j,s in enumerate(shifts):
   z=t[offs[j]:offs[j+1]];tt.extend(z[-s:]+z[:-s] if s else z)
  check(tt,out)
 assert case['tail']==(1+sum(v['held_hits']>=case['fit']['held_hits'] for v in case['null_parameters']))/(1+len(case['shifts']))
out={'verified_fits':fits,'all_candidate_score_cells':fits*28*29*2,'source_coordinates_retained':sum(len(r['rune_coordinates']) for r in d['regions'])};(R/'Q01-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
