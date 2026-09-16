import gzip,json,math,pathlib
R=pathlib.Path(__file__).resolve().parent
d=json.load(gzip.open(R/'O01-evidence.json.gz','rt'));rows=d['rows'];tests=[d['real']]+d['controls'];out=[]
for t in tests:
 hs=t.get('heads',[r['heads'] for r in rows]);counts=[[1]*8 for _ in range(29)]
 for r,h in zip(rows,hs):
  for x,y in zip(h[:r['train_n']],r['length_bins'][:r['train_n']]):counts[x][y]+=1
 assert counts==t['train_joint_counts']
 totals=[sum(counts[x][y] for x in range(29)) for y in range(8)];g=[]
 for r,h,saved in zip(rows,hs,t['pages']):
  c=r['train_n'];b=[1]*8
  for y in r['length_bins'][:c]:b[y]+=1
  b=[v/sum(b) for v in b]
  for j,(x,y) in enumerate(zip(h[c:],r['length_bins'][c:])):
   p=[counts[x][v]/totals[v]*b[v] for v in range(8)];p=[v/sum(p) for v in p]
   assert max(abs(a-bb) for a,bb in zip(p,saved['predictions'][j]))<1e-12
   g.append(math.log(p[y]/b[y]))
 assert abs(sum(g)/len(g)-t['gain'])<1e-12
 assert t['tail']==(1+sum(x>=t['gain'] for x in t['null']))/(1+len(t['null']))
 out.append({'replayed_gain':sum(g)/len(g),'tail':t['tail'],'test_units':len(g)})
(R/'O01-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
