import pathlib,json,gzip,math,collections,hashlib
P=pathlib.Path(__file__).resolve().parent;D=sorted(json.loads((P/'R01-input.json').read_text()),key=lambda p:p['page']);files=['R03-pilot-full.jsonl.gz','R03-controls-0-12-full.jsonl.gz','R03-stress-full.jsonl.gz','R03-real-full.jsonl.gz'];seen=0;maxerr=0;nullrecords=0
for fn in files:
 with gzip.open(P/fn,'rt') as f:
  for line in f:
   row=json.loads(line);vs=row['streams'];r=row['fit'];tr=[[0]*29 for _ in range(29)];he=[[0]*29 for _ in range(29)];hist=[.5]*29
   for i,a in enumerate(vs):
    truth=D[i]['indices'];assert [x==y for x,y in zip(a,a[1:])]==[x==y for x,y in zip(truth,truth[1:])]
    if i%2==0:
     for v in a:hist[v]+=1
    c=tr if i%2==0 else he
    for x,y in zip(a,a[1:]):
     if x!=y:c[x][y]+=1
   assert tr==r['train_counts'] and he==r['held_counts'];w=[v/sum(hist) for v in hist];assert max(abs(x-y) for x,y in zip(w,r['weights']))<1e-14
   assert len(r['pairs'])==14 and len({x for pair in r['pairs'] for x in pair})==28
   def score(c):
    out=list(map(sum,c));z=0
    for a,b in r['pairs']:
     e=out[a]*w[b]/(1-w[a])+out[b]*w[a]/(1-w[b]);z+=(c[a][b]+c[b][a]-e)/math.sqrt(e)
    return z
   err=max(abs(score(tr)-r['solver']['objective']),abs(score(he)-r['held_stat']));maxerr=max(maxerr,err);assert err<1e-10
   assert r['held_count']==sum(he[a][b]+he[b][a] for a,b in r['pairs']);assert r['solver']['status']==0 and r['solver']['gap']==0
   seen+=1;nullrecords+=row['kind']=='null'
x=json.loads((P/'R03-real-results.json').read_text())['panels'][0];pairs={tuple(p) for p in x['pairs']};witness=[]
for p in D[1::2]:
 for i,(a,b) in enumerate(zip(p['indices'],p['indices'][1:])):
  if tuple(sorted((a,b))) in pairs:witness.append(dict(page=p['page'],rune_indices=[i,i+1],source_char_positions=p['source_char_positions'][i:i+2],values=[a,b]))
assert len(witness)==x['held_count'];(P/'R03-real-witnesses.json').write_text(json.dumps(witness,indent=2)+'\n')
z=dict(panels_checked=seen,null_records=nullrecords,max_scalar_error=maxerr,real_witnesses=len(witness),files=[dict(path=fn,sha256=hashlib.sha256((P/fn).read_bytes()).hexdigest()) for fn in files]);(P/'R03-replay-results.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z))
