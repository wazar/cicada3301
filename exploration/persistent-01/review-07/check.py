import pathlib,json,hashlib,gzip,collections,math,itertools,datetime
from fractions import Fraction
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];L=O.parent/'worker-l'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(a):
 return tuple(next(i for i,z in enumerate(a) if z==v) for v in a)
def collapse(a):return [v for i,v in enumerate(a) if not i or a[i-1]!=v]
def counts_metric(cs):
 out=[[0,0,0,0],[0,0,0,0]]
 for j,c in enumerate(cs):
  o=out[j%2];o[2]+=sum(a==b for a,b in zip(c,c[1:]));o[3]+=len(c)-1
  for a,b,d in zip(c,c[1:],c[2:]):
   if a!=b and b!=d:o[1]+=1;o[0]+=a==d
 return out

def main():
 assert not(O.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
 cfg=load(O.parent/'config.json');dataset=R/'audit/parallel-01/inputs/dataset.json';mp=R/'audit/parallel-01/inputs/page-map.json';assert sha(dataset)==cfg['dataset_sha256'];assert sha(mp)==cfg['map_sha256']
 manifest=load(L/'evidence-manifest.json');bad=[]
 for v in manifest['files']:
  p=R/v['path']
  if sha(p)!=v['sha256'] or p.stat().st_size!=v['bytes']:bad.append(v['path'])
 assert not bad
 ids=load(L/'l1-conditional/input-manifest.json')['pages'];assert not set(ids)&set(cfg['reserved_original_pages']);orig={p['original_page']:p['indices'] for p in load(dataset)['pages'] if p['original_page'] in ids};assert len(orig)==45
 maps=load(L/'l1-conditional/maps-full-phases.json');wits=load(L/'l1-conditional/phase-witnesses.json');wit={(v['original_page'],v['m'],v['phase']):v for v in wits};phases=0;tot=np.zeros((2,3,2));elig={}
 for row,pid in zip(maps,ids):
  c=orig[pid];ix=[i for i in range(len(c)) if not i or c[i]!=c[i-1]];x=np.array([c[i] for i in ix]);assert row['compressed']==x.tolist() and row['source_indices']==ix
  prefix=np.vstack([np.zeros(29,int),np.cumsum(np.eye(29,dtype=int)[x],axis=0)])
  for k,model in enumerate(row['models']):
   m=model['m'];B=29*m;expected_eligible=len(x)>=2*B-1;assert bool(model['phases'])==expected_eligible
   if not expected_eligible:continue
   assert [v[0] for v in model['phases']]==list(range(B));scores=[]
   for phase,expected,den in model['phases']:
    starts=np.arange(phase,len(x)-B+1,B);h=prefix[starts+B]-prefix[starts];v=int(np.maximum(h-m,0).sum());assert v==expected and den==len(starts)*B and v>0
    w=wit[pid,m,phase];st=w['compressed_block_start'];assert st in starts;positions=[ix[z] for z in range(st,st+B) if x[z]==w['rune_index']];assert positions==w['source_occurrences'] and len(positions)==w['count']>m
    assert w['block_source_start']==ix[st] and w['block_source_end_inclusive']==ix[st+B-1]
    scores.append([phase,v,den]);phases+=1
   best=min(scores,key=lambda z:(z[1]/z[2],z[0]));assert best==model['best'];tot[row['page_index']%2,k]+=best[1:]
 assert phases==7105==len(wits);assert np.allclose(tot[:,:,0]/tot[:,:,1],load(L/'l1-conditional/summary.json')['real_scores'])
 boundary=[]
 for B in [29,58,116]:
  assert all((2*B-1-r)//B>=1 for r in range(B));assert (2*B-2-(B-1))//B==0;boundary.append(B)
 failed=[]
 for p in (L/'runs').glob('*/command.json'):
  cmd=load(p)
  if cmd['outcome']=='NONZERO':failed.append({'path':str(p.relative_to(R)),'outcome':cmd['outcome'],'started_utc':cmd['started_utc']})
 assert failed and (L/'l1-failed-control/generated-full-outputs.jsonl.gz').is_file();failedlines=sum(1 for _ in gzip.open(L/'l1-failed-control/generated-full-outputs.jsonl.gz','rt'))
 # Independent source parsing, preserving only whitespace gaps as within-unit.
 data=load(L/'l2/inputs-and-maps.json');ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';sources=[];spacegaps=[]
 for s in data['sources']:
  p=R/s['path'];assert sha(p)==s['sha256'];raw=p.read_text();units=[];cur=[];gap=''
  for ch in raw:
   if ch in ABC:
    if cur and gap and not gap.isspace():units.append(collapse(cur));cur=[]
    if gap and gap.isspace() and ' ' in gap:spacegaps.append(gap)
    cur.append(ABC.index(ch));gap=''
   elif cur:gap+=ch
  if cur:units.append(collapse(cur))
  assert units==s['units'];sources.append(units)
 def fit(ss):
  d={}
  for w in itertools.chain.from_iterable(ss):
   if len(w)>=3:d.setdefault(len(w),collections.Counter())[canon(w)]+=1
  return d
 model=fit(sources)
 def score(w,mod):
  N=len(w)
  if N not in mod:return None
  assert all(a!=b for a,b in zip(w,w[1:]));d=len(set(w));p0=math.prod(range(29-d+1,30))/(29*28**(N-1));ps=mod[N][canon(w)]/sum(mod[N].values());return math.log(.9*ps/p0+.1)
 rows=data['rows'];real=[0.,0.];eligible=[0,0]
 for row in rows:
  c=orig[row['page']][row['source_start']:row['source_end']];assert c==row['raw'] and collapse(c)==row['collapsed'];re=[]
  for v,nn in zip(row['collapsed'],row['runs']):re.extend([v]*nn)
  assert re==c;v=score(row['collapsed'],model)
  if v is not None:real[row['part']]+=v;eligible[row['part']]+=1
 assert np.allclose(real,load(L/'l2/summary.json')['real_scores_train_held']);assert eligible==[922,959]
 norm=[];dist={1:1}
 for N in range(1,15):
  mass=sum(Fraction(num*math.prod(range(29-d+1,30)),29*28**(N-1)) for d,num in dist.items());assert mass==1;norm.append({'length':N,'canonical_patterns':sum(dist.values()),'mass':str(mass)})
  nxt=collections.Counter()
  for d,num in dist.items():nxt[d]+=num*(d-1);nxt[d+1]+=num
  dist=nxt
 checked=collections.Counter();trans=0
 for line in gzip.open(L/'l2/full-generated-output.jsonl.gz','rt'):
  r=json.loads(line);kind=r['kind']
  if kind=='source-control' and checked[kind]<3:
   xs=[]
   for row,meta in zip(rows,r['metadata']):
    perm=meta['permutation'];assert sorted(perm)==list(range(29));w=[perm[v] for v in meta['source']];expanded=list(itertools.chain.from_iterable([v]*nn for v,nn in zip(w,row['runs'])));assert expanded==meta['expanded_output'];assert canon(w)==canon(meta['source']);xs.append(w)
  elif kind=='conditional-null' and checked[kind]<3:xs=r['collapsed_outputs']
  elif kind=='leave-source-out-transfer':
   mod=fit([s for j,s in enumerate(sources) if j!=r['source_held']]);vals=[0.,0.]
   for row,w in zip(rows,r['outputs']):
    v=score(w,mod)
    if v is not None:vals[row['part']]+=v
   assert np.allclose(vals,r['scores']);trans+=1;continue
  else:continue
  vals=[0.,0.]
  for row,w in zip(rows,xs):
   assert len(w)==len(row['collapsed']);v=score(w,model)
   if v is not None:vals[row['part']]+=v
  assert np.allclose(vals,r['scores']);checked[kind]+=1
 # Exact equality-class Markov chain over (previousprevious, previous, queued).
 states=[(0,0,0),(0,0,1),(0,1,0),(0,1,1),(0,1,2)]
 def canonical3(t):
  d={};return tuple(d.setdefault(v,len(d)) for v in t)
 s=load(L/'l3/input-manifest.json')['s_fitted'];P=np.zeros((5,5));num=np.zeros(5);den=np.zeros(5);q=np.zeros(5)
 for k,(a,b,c) in enumerate(states):
  for z in range(29):
   cases=[(c,z,1.)] if c!=b or z==c else [(z,c,s),(c,z,1-s)]
   for emitted,buffer,weight in cases:
    w=weight/29;P[k,states.index(canonical3((b,emitted,buffer)))]+=w;q[k]+=w*(b==emitted);den[k]+=w*(a!=b and b!=emitted);num[k]+=w*(a==emitted and a!=b and b!=emitted)
 assert np.allclose(P.sum(1),1);A=P.T-np.eye(5);A[-1]=1;rhs=np.array([0.,0.,0.,0.,1.]);stationary=np.linalg.solve(A,rhs);stationaryq=float(stationary@q);assert abs(stationaryq-(1-s*28/29)/29)<1e-14
 # Exact expected finite-page totals, initialized iid first output/current queue; initial dummy previousprevious same as first output.
 ex=np.zeros((2,4))
 for j,pid in enumerate(ids):
  state=np.array([1/29,28/29,0.,0.,0.]);N=len(orig[pid])
  for step in range(1,N):
   ex[j%2,2]+=state@q;ex[j%2,3]+=1
   if step>=2:ex[j%2,0]+=state@num;ex[j%2,1]+=state@den
   state=state@P
 l3summary=load(L/'l3/summary.json');actual=counts_metric([orig[p] for p in ids]);assert actual==l3summary['real_totals'];savedrows=0;queues=0
 for line in gzip.open(L/'l3/full-generated-output.jsonl.gz','rt'):
  r=json.loads(line)
  if r['kind']!='swap-control' or r['replicate']>=5:continue
  emitted=[]
  for meta in r['pages']:
   raw=meta['iid_queue'];buffer=collections.deque(raw[1:]);out=[raw[0]];sites=set(meta['swap_positions'])
   for i in range(1,len(raw)-1):
    current=buffer.popleft()
    if i in sites:
     nxt=buffer.popleft();assert current==out[-1] and nxt!=current;buffer.appendleft(current);current=nxt
    out.append(current)
   assert out==meta['emitted'] and list(buffer)==[meta['terminal_buffer']];assert collections.Counter(out+list(buffer))==collections.Counter(raw);queues+=1;emitted.append(out)
  assert counts_metric(emitted)==r['totals'];savedrows+=1
 result={'manifest_files_verified':len(manifest['files']),'L1':{'phase_scores_and_witnesses':phases,'eligibility_boundary_blocks':boundary,'failed_logs':failed,'failed_generated_rows_preserved':failedlines},'L2':{'real_scores':real,'eligible':eligible,'source_files':len(sources),'normalization':norm,'saved_control_null_rows_checked':dict(checked),'transfer_fixtures_rescored':trans,'source_whitespace_space_gaps':len(spacegaps)},'L3':{'states':states,'transition_matrix':P.tolist(),'stationary':stationary.tolist(),'analytic_q':stationaryq,'stationary_ABA_ratio':float((stationary@num)/(stationary@den)),'finite_expected_totals':ex.tolist(),'finite_expected_ABA_ratio':(ex[:,0]/ex[:,1]).tolist(),'control_reported_mean_ABA':l3summary['swap_rate_mean'],'saved_control_rows_verified':savedrows,'queues_replayed':queues,'actual_totals':actual}}
 (O/'findings.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
