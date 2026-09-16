import pathlib,gzip,json
R=pathlib.Path(__file__).parent;d=json.load(gzip.open(R/'Q02-evidence.json.gz','rt'));words=[[v for w in r['units'] for v in w] for r in d['regions']];bodies=[[sum(x*pow(a,len(w)-i-1,29) for i,x in enumerate(w[:-1]))%29 for w in words] for a in range(1,29)];assert bodies==d['bodies'];n=0
for case in d['controls']+[d['real']]:
 scores=[]
 for perm,fit in zip(d['permutations'],case['fits']):
  t=[case['terminals'][j] for j in perm];tr=[];he=[]
  for row in bodies:
   v=[(x+y)%29 for x,y in zip(row,t)];tr.append([v[:3].count(b) for b in range(29)]);he.append([v[3:].count(b) for b in range(29)])
  assert tr==fit['training_matrix'] and he==fit['held_matrix'];_,a,b=min((-tr[a][b],a,b) for a in range(28) for b in range(29));assert (a+1,b)==(fit['a'],fit['b']);assert he[a][b]==fit['held_hits'];assert [(b-x)%29 for x in bodies[a][3:]]==fit['predictions'];scores.append(he[a][b]);n+=1
 assert case['tail']==sum(s>=scores[0] for s in scores)/120
 assert case['minimum_attainable_tail']==scores.count(max(scores))/120
out={'verified_fits':n,'verified_score_cells':n*28*29*2};(R/'Q02-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
