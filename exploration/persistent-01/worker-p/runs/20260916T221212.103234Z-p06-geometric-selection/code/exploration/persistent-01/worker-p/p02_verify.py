import json,gzip,pathlib,collections
D=pathlib.Path('exploration/persistent-01/worker-p/P02');assert not pathlib.Path('exploration/persistent-01/STOP').exists()
with gzip.open(D/'evidence.json.gz','rt') as f:e=json.load(f)
pairs=[(i,j) for b in [0,4] for i in range(b,b+4) for j in range(i+1,b+4)]
def dp(ss):
 best=0
 for p,q in pairs:
  for b in [ss[q],ss[q][::-1]]:
   old=[0]*(len(b)+1)
   for v in ss[p]:
    nxt=[0]*(len(b)+1)
    for j,w in enumerate(b):
     if v==w:nxt[j+1]=old[j]+1;best=max(best,nxt[j+1])
    old=nxt
 return best
assert dp(e['sequences'])==e['real']['best'];mapped=[]
for h in e['real']['hits']:
 p,q=h['pair'];i,j=h['starts'];n=h['length'];ii=list(range(i,i+n));jj=list(range(len(e['sequences'][q])-1-j,len(e['sequences'][q])-1-j-n,-1)) if h['reverse'] else list(range(j,j+n));a=[e['sequences'][p][x] for x in ii];b=[e['sequences'][q][x] for x in jj];assert a==b
 mapped.append(dict(pages=[e['mapping'][p]['page'],e['mapping'][q]['page']],reverse=h['reverse'],lengths=a,units=[ii,jj],unit_source_maps=[[e['mapping'][page]['words'][x] for x in ids] for page,ids in [(p,ii),(q,jj)]]))
checks=0
for ps,val in zip(e['real']['permutations'],e['real']['null']):
 assert all(sorted(p)==list(range(len(a))) for a,p in zip(e['sequences'],ps));ss=[[a[j] for j in p] for a,p in zip(e['sequences'],ps)];assert dp(ss)==val;checks+=1
control_checks=0
for r in e['controls']:
 a=r['sequences'];i,j=r['planted_starts'];n=r['size'];assert a[0][i:i+n]==(a[1][j:j+n][::-1] if r['reverse'] else a[1][j:j+n]);assert dp(a)==r['best'];control_checks+=1
out=dict(real=e['real']['best'],real_nulls_independent_dp=checks,control_plants_independent_dp=control_checks,mapped_hits=mapped,tail=(1+sum(v>=e['real']['best'] for v in e['real']['null']))/1000,null_histogram=dict(sorted(collections.Counter(e['real']['null']).items())))
(D/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='mapped_hits'},indent=2))
