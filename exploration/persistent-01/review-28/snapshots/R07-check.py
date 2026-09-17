import pathlib,json,gzip,math,collections
P=pathlib.Path(__file__).resolve().parent;D=sorted(json.loads((P/'R01-input.json').read_text()),key=lambda p:p['page']);HEAD=[{g['previous'] for g in p['gaps'] if g['type']=='hyphen'} for p in D];checked=0;maxerr=0;maxgrad=0;groups={}
for filename in ['R07-controls-full.jsonl.gz','R07-real-full.jsonl.gz']:
 with gzip.open(P/filename,'rt') as f:
  for line in f:
   row=json.loads(line);vs=row['streams'];z=row['fit'];tr=[[[0]*29 for _ in range(29)] for _ in range(2)];he=[[[0]*29 for _ in range(29)] for _ in range(2)]
   for ordinal,a in enumerate(vs):
    actual=D[ordinal]['indices'];assert len(a)==len(actual);assert [x==y for x,y in zip(a,a[1:])]==[x==y for x,y in zip(actual,actual[1:])];dest=tr if ordinal%2==0 else he
    for i,(x,y) in enumerate(zip(a,a[1:])):
     if x!=y:dest[int(i in HEAD[ordinal])][x][y]+=1
   assert tr==z['train_counts'] and he==z['held_counts'];probs=[]
   for s,F in enumerate(z['baseline_fits']):
    t=F['theta'];v=[math.exp(x-max(t)) for x in t];pr=[[0 if x==y else v[y]/sum(v[k] for k in range(29) if k!=x) for y in range(29)] for x in range(29)];probs.append(pr);A=[[tr[s][x][y]+(0 if x==y else .5/28) for y in range(29)] for x in range(29)];rows=list(map(sum,A));total=sum(rows);grad=[(sum(rows[x]*pr[x][y] for x in range(29))-sum(A[x][y] for x in range(29)))/total for y in range(28)];gg=max(map(abs,grad));maxgrad=max(maxgrad,gg);assert gg<=1e-7 and F['qualified'];assert F['objective']<=F['pre_objective']+1e-12
   pi=z['pi'];assert sorted(pi)==list(range(29)) and all(x!=y for x,y in enumerate(pi));obs=sum(he[1][x][pi[x]] for x in range(29));exp=sum(sum(he[1][x])*probs[1][x][pi[x]] for x in range(29));n=sum(map(sum,he[1]));score=(obs-exp)/n;err=max(abs(exp-z['held_expected']),abs(score-z['score']));maxerr=max(maxerr,err);assert err<1e-10 and obs==z['held_matches'] and n==z['held_eligible'];key=(filename,row['tag']);groups.setdefault(key,[]).append(score);checked+=1
for fn in ['controls','real']:
 out=json.loads((P/f'R07-{fn}-results.json').read_text())
 for i,z in enumerate(out['panels']):
  key=(f'R07-{fn}-full.jsonl.gz','real' if fn=='real' else str(i));g=groups[key];assert len(g)==(400 if fn=='real' else 100);assert (1+sum(s>=g[0] for s in g[1:]))/len(g)==z['p_upper']
r=json.loads((P/'R07-real-results.json').read_text())['panels'][0];pi=r['pi'];witness=[]
for ordinal,p in enumerate(D):
 for g in p['gaps']:
  if g['type']!='hyphen':continue
  i,j=g['previous'],g['next'];x,y=p['indices'][i],p['indices'][j];witness.append(dict(page=p['page'],train=ordinal%2==0,rune_positions=[i,j],source_char_positions=[p['source_char_positions'][i],p['source_char_positions'][j]],gap_text=g['text'],values=[x,y],stutter=x==y,predicted_next=pi[x],eligible_match=(x!=y and y==pi[x])))
(P/'R07-real-gap-witnesses.json').write_text(json.dumps(witness,indent=2)+'\n');out=dict(final_panels_checked=checked,max_expected_score_error=maxerr,max_conditional_gradient=maxgrad,hyphen_gap_records=len(witness));(P/'R07-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
