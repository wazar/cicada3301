from pathlib import Path
import json,random,collections
R=Path('exploration/persistent-01/worker-r');O=Path(__file__).parent;M=json.loads((R/'R01-input.json').read_text());D=json.loads((R/'R01-results.json').read_text());starts=[[w['start'] for w in m['words'] if w['end']-w['start']>=2] for m in M];train=[i for i,m in enumerate(M) if m['page'] in (0,1)];held=[i for i in range(len(M)) if i not in train]
def counts(streams,offsets):
 v=[0]*29
 for i in train:
  for p in starts[i]:v[streams[i][(p+offsets[i])%len(streams[i])]]+=1
 z=min(range(29),key=lambda k:(v[k],k));n=sum(streams[i][(p+offsets[i])%len(streams[i])]==z for i in held for p in starts[i]);return z,v,n
x=[m['indices'] for m in M];z,v,n=counts(x,[0]*45);assert (z,n)==(27,77) and v==D['training_counts'];rng=random.Random(339901)
for row in D['full_procedure_null']['replicates']:
 zz,c,nn=counts(x,[rng.randrange(len(s)) for s in x]);assert (zz,c[zz],nn)==(row['selected_zero'],row['training_min'],row['violations'])
rng=random.Random(330101)
for expected in D['randomization']['counts']:
 total=0
 for i in held:
  off=rng.randrange(len(x[i]));total+=sum(x[i][(p+off)%len(x[i])]==27 for p in starts[i])
 assert total==expected
cc=json.loads((R/'R01-control-streams.json').read_text());assert len(cc)==200
for saved,row in zip(cc,D['controls']):
 streams=[p['indices'] for p in saved['pages']];zz,c,nn=counts(streams,[0]*45);assert (zz,c[zz],nn)==(row['selected_zero'],row['train_min'],row['violations']);rng=random.Random(row['seed']);gen=[]
 for i,m in enumerate(M):
  a=[rng.randrange(29) for _ in x[i]]
  if row['planted']:
   for p in starts[i]:
    if a[p]==27:
     q=rng.randrange(28);a[p]=q+(q>=27)
  gen.append(a)
 assert gen==streams
real2=json.loads((R/'R02-results.json').read_text())['real'];r2=[]
for row in real2:
 m=next(m for m in M if m['page']==row['page']);depart=[[] for _ in range(29)]
 for a,b in zip(m['indices'],m['indices'][1:]):
  if a!=b:depart[a].append(b)
 scores=[sum(c*(c-1)//2 for c in collections.Counter(v).values()) for v in depart];assert sum(scores)==row['score'] and scores==row['source_scores'] and depart==row['departures'];assert max(map(len,depart))<28
 for w in row['witnesses']:
  for field,chars in [('first_rune_index','first_source_chars'),('repeat_rune_index','repeat_source_chars')]:
   j=w[field];assert m['indices'][j:j+2]==[w['predecessor'],w['successor']];assert m['source_char_positions'][j:j+2]==w[chars]
 r2.append(dict(page=m['page'],score=sum(scores),max_departures=max(map(len,depart))))
report=dict(status='PASS',R01_real=(z,n),R01_fixednull=4095,R01_refittednull=4095,R01_controls=200,R02_exact_witnesses=r2,scope='Independent count/RNG/selection replay. R02 control generation not independently repeated; strict real contradiction directly checked. R01 control255null tests condition on once-selected label, distinct from realrefittednull.');(O/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
