import json,gzip,pathlib,hashlib,math,collections,itertools,ast,heapq
import numpy as np
R=pathlib.Path('exploration/persistent-01');O=R/'review-01';reads={};checks=[]
def read(p):
 p=pathlib.Path(p);b=p.read_bytes();reads[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def lines(p):
 p=pathlib.Path(p);b=p.read_bytes();reads[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 return [json.loads(x) for x in gzip.decompress(b).splitlines()]
def close(a,b):assert abs(a-b)<1e-9,(a,b)
def note(id,**kw):checks.append(dict(id=id,status='PASS',**kw))
def ent(c):
 n=sum(c);return -sum(x/n*math.log2(x/n) for x in c if x)
def chi(c):
 n=sum(c);return sum((x-n/len(c))**2/(n/len(c)) for x in c)
def mi(seqs,base=2):
 c=collections.Counter((a,b) for s in seqs for a,b in zip(s,s[1:]));a=collections.Counter();b=collections.Counter();n=sum(c.values())
 for (x,y),z in c.items():a[x]+=z;b[y]+=z
 return sum(z/n*math.log(z*n/(a[x]*b[y]),base) for (x,y),z in c.items())
# All real rune input comes from retained discovery-only maps; do not open dataset/reserves.
c1maps=lines(R/'worker-c/ob-c1/full-decoded-maps.jsonl.gz');cs={x['original_page']:x['cipher'] for x in c1maps};assert len(cs)==45 and not set(cs)&{4,9,14,19,24,29,34,39,44,50,54}
S=read(R/'worker-e/experiment01-result.json');cells=read(R/'worker-e/experiment01-discovery-cells.json');nul=read(R/'worker-e/experiment01-null.json.gz');assert sum(nul['null_hit_counts'])==0
assert sum(max(0,len(p['cells'])-24) for p in cells)==1598
for s in S['sources']:
 v=s['values'];sums=[sum(v[i*5:i*5+5]) for i in range(5)]+[sum(v[j::5]) for j in range(5)]+[sum(v[::6]),sum(v[4:21:4])];assert sums==s['line_sums'] and len(set(sums))==1
note('E01',windows=1598,null_hits=0,line_sums=[s['line_sums'][0] for s in S['sources']])
def inverse(m):
 x=[[v%29 for v in row]+[int(i==j) for j in range(5)] for i,row in enumerate(m)]
 for j in range(5):
  k=next(k for k in range(j,5) if x[k][j]);x[j],x[k]=x[k],x[j];z=pow(x[j][j],-1,29);x[j]=[(v*z)%29 for v in x[j]]
  for k in range(5):
   if k!=j:
    z=x[k][j];x[k]=[(a-z*b)%29 for a,b in zip(x[k],x[j])]
 return [row[5:] for row in x]
mat={}
for i,s in enumerate(S['sources']):
 m=[s['values'][j:j+5] for j in range(0,25,5)];mat[str(i)+'_forward']=m;mat[str(i)+'_inverse']=inverse(m)
e2=read(R/'worker-e/experiment02-evidence.json.gz');r2=read(R/'worker-e/experiment02-result.json');r4=read(R/'worker-e/experiment04-result.json');e4=read(R/'worker-e/experiment04-evidence.json.gz')
for row,out2,out4 in zip(e2['transformed'],r2['candidates'],r4['real_candidates']):
 allv=[];cols=[[] for _ in range(5)]
 for page in row['pages']:
  c=cs[page['page']];v=[]
  for start in range(row['phase'],len(c)-4,5):v.extend(sum(x*y for x,y in zip(rr,c[start:start+5]))%29 for rr in mat[row['matrix']])
  assert v==page['runes'];allv+=v
  for j in range(5):cols[j]+=v[j::5]
 counts=[allv.count(i) for i in range(29)];assert counts==out2['counts'];close(chi(counts),out2['score']);close(sum(chi([v.count(i) for i in range(29)]) for v in cols),out4['score'])
for id,e,r in [('E02',e2,r2),('E04',e4,r4)]:
 mx=[max(v) for v in e['null_all_scores']];p=(1+sum(v>=r['max_score'] for v in mx))/(len(mx)+1);close(p,r['family_p']);assert r['control_truth']['score']>max(max(v) for v in e['control_null_all_scores']);note(id,scalar_outputs_verified=900,family_p=p,control_detected=True)
r3=read(R/'worker-e/experiment03-result.json');assert len(cs)*8==r3['checks']==360
assert all(max(s['values'])>=max(map(len,cs.values()))+1 for s in S['sources']);note('E03',checks=360,complete=0)
r5=read(R/'worker-e/experiment05-result.json');e5=read(R/'worker-e/experiment05-evidence.json.gz');assert max(map(max,e5['null_all_match_counts']))==r5['null_max_match']==12;assert not r5['complete_passes'];note('E05',real_max=max(len(x['matches']) for x in r5['recipes']),null_max=12)
r6=read(R/'worker-e/experiment06-result.json');e6=read(R/'worker-e/experiment06-evidence.json.gz');stats=[]
for obj in e6['decoded']:
 ss=obj['pages'];v=sum(ss,[]);stats.extend([chi([v.count(i) for i in range(29)]),mi(ss,math.e)])
for a,b in zip(stats,r6['real']):close(a,b)
p=[(1+sum(x[j]>=stats[j] for x in e6['null_all_statistics']))/1001 for j in range(4)]
for a,b in zip(p,r6['empirical_tails']):close(a,b)
for ctrl in e6['controls']:
 target=ctrl['target'];v=ctrl['encoded'];primes=[x for x in range(2,110) if all(x%d for d in range(2,int(x**.5)+1))];m=list(range(29)) if ctrl['map']=='index' else primes;assert [sum(m[z] for z in v[i:i+3])%29 for i in range(0,len(v),3)]==target
note('E06',tails=p,bonferroni_min=min(p)*4,control_exact=4)
# Independent rank deletion: construct and search alphabet, no formula from worker code.
c1rows=read(R/'worker-c/ob-c1/real-statistics.json');by=collections.defaultdict(list)
for x in c1maps:
 c=x['cipher'];alpha=[(x['rotation']+x['direction']*j)%29 for j in range(29)];v=[c[0]]+[28 if a==b else [z for z in alpha if z!=a].index(b) for a,b in zip(c,c[1:])];assert v==x['decoded_rank_indices'];by[x['rotation'],x['direction']].append(v[1:])
for x in c1rows:
 ss=by[x['rotation'],x['direction']];v=sum(ss,[]);close(ent([v.count(i) for i in range(28)]),x['nonrepeat_entropy']);close(mi(ss),x['lag1_mutual_information'])
for name,ek,mk,ep,mp in [('ob-c1','min_entropy','max_lag1_mi','entropy_lower_tail_p','mi_upper_tail_p'),('ob-c2','nonrepeat_seen_rank_entropy','seen_rank_lag1_mi','entropy_p','mi_p')]:
 r=read(R/'worker-c'/name/'summary.json');n=read(R/'worker-c'/name/'nulls.json')
 for typ in ['generative','permutation']:
  close((1+sum(x[typ][ek]<=r['real'][ek] for x in n))/201,r['comparisons'][typ][ep]);close((1+sum(x[typ][mk]>=r['real'][mk] for x in n))/201,r['comparisons'][typ][mp])
 note(name,nulls=200,comparisons=r['comparisons'])
# Recurrent MTF rank equals number of distinct intervening symbols +1 (or0 on repetition).
c2=lines(R/'worker-c/ob-c2/full-output-maps.jsonl.gz');cnt=[0]*29;pairseq=[];pair=collections.Counter()
for row in c2:
 c=row['cipher'];seen={};valid=[]
 for i,x in enumerate(c):
  if x in seen:
   rank=len(set(c[seen[x]+1:i]));assert rank==row['source_rank'][i];valid.append(i)
  seen[x]=i
 assert valid==row['initial_independent_positions']
 if row['order']==[0,1]:
  valid=set(valid)
  for i in valid:
   z=row['source_rank'][i]
   if z:cnt[z]+=1
  for i in range(len(c)-1):
   if i in valid and i+1 in valid:pair[row['source_rank'][i],row['source_rank'][i+1]]+=1
r=read(R/'worker-c/ob-c2/summary.json');assert cnt==r['real']['counts'];close(ent(cnt),r['real']['nonrepeat_seen_rank_entropy']);note('C2-independent-MTF',maps=len(c2),counts_match=True)
r=read(R/'worker-c/ob-c3/summary.json');n=read(R/'worker-c/ob-c3/nulls.json');close(ent(r['newly_resolved']['counts']),r['newly_resolved']['nonrepeat_extra_entropy'])
for typ in ['generative','permutation']:
 close((1+sum(x[typ]['extra']['nonrepeat_extra_entropy']<=r['newly_resolved']['nonrepeat_extra_entropy'] for x in n))/201,r['comparisons'][typ]['extra_entropy_p'])
note('C3',new_runes=r['newly_resolved']['extra_runes'],held_null_saved=False)
def graph(ciphers):
 a=np.zeros((29,29))
 for c in ciphers:
  for x,y in zip(c,c[1:]):a[x,y]+=1;a[y,x]+=1
 deg=a.sum(axis=1);keep=deg>0;a=a[keep][:,keep];deg=deg[keep];eig=float(np.linalg.eigvalsh(a/np.sqrt(deg[:,None]*deg[None,:]))[0]);return max(0.,(1+eig)/2)
g=read(R/'worker-c/ob-c4/real-graph.json');bound=graph(list(cs.values()));close(bound,g['min_within_partition_fraction'])
rows=read(R/'worker-c/ob-c4/pagewise-boundary-checks.json')
for row in rows:
 c=cs[row['page']];close(graph([c]),row['min_within_bound'])
 for edge in row['nonself_triangle_witness']:
  assert sorted(c[edge['position']:edge['position']+2])==sorted(edge['runes'])
 for rr in row['within_pairs']:close(graph([c[i:i+2] for i in range(rr['phase'],len(c)-1,2)]),rr['min_within_bound'])
tiny=read(R/'worker-c/ob-c4/exhaustive-graph-controls.json')
for row in tiny:
 edges=row['edge_multiset'];v=min(sum(s[a]==s[b] for a,b in edges)/len(edges) for s in itertools.product([0,1],repeat=row['vertices']));close(v,row['exact_min_within']);assert row['spectral_lower_bound']<=v+1e-12
note('C4',pooled_bound=bound,pagewise=45,tiny_exact_graphs=100,triangle_witnesses=45)
# Extract only the finite decode function, avoiding owner imports and output mutations.
f=R/'worker-b/feasible.py';b=f.read_bytes();reads[str(f)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};node=next(x for x in ast.parse(b).body if isinstance(x,ast.FunctionDef) and x.name=='decode');scope={'heapq':heapq};exec(compile(ast.Module(body=[node],type_ignores=[]),str(f),'exec'),scope)
class Hostile:
 def add(self,t,s,n,r):return '',s+(r!=0)*100,n+1
n=0
for length in range(7):
 for c in itertools.product([0,1],repeat=length):
  for klen in range(length+1):
   for sign in [-1,1]:
    got=scope['decode'](c,list(range(klen)),sign,False,Hostile(),1);assert bool(got)==(klen>=sum(x!=0 for x in c));n+=1
note('B-finite-feasibility',width1_cases=n,claim='existence only, not score optimality')
(O/'checked-findings.json').write_text(json.dumps({'scope':'bounded independent arithmetic/evidence review','checks':checks,'inputs':reads},indent=2)+'\n');print(json.dumps(checks,indent=2))
