import pathlib,json,hashlib,numpy as np,time,datetime,gzip
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];rng=np.random.default_rng(330824);PI=3/28
def gate():
 assert not(R.parent.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):(R/(name+'.json')).write_text(json.dumps(x,indent=2))
def collapse(c):
 starts=[0]+[i for i in range(1,len(c)) if c[i]!=c[i-1]];ends=starts[1:]+[len(c)];return [c[i] for i in starts],starts,[b-a for a,b in zip(starts,ends)]
def extract(v):
 a=list(range(29));seen=set();rank=[];valid=[]
 for x in v:
  r=a.index(x);rank.append(r);valid.append(x in seen);seen.add(x);a.pop(r);a.insert(0,x)
 counts=np.zeros((2,28),dtype=np.int64);eligible=[]
 for i in range(1,len(v)):
  if valid[i-1] and valid[i]:
   assert 1<=rank[i]<=28 and 1<=rank[i-1]<=28;s=int(rank[i-1]>3);counts[s,rank[i]-1]+=1;eligible.append(i)
 return counts,rank,valid,eligible

def fit_score(pages,detail=False):
 es=[extract(x) for x in pages];counts=np.array([x[0] for x in es]);tr=counts[::2].sum(0);held=counts[1::2].sum(0);base=(tr.sum(0)+1)/(tr.sum()+28);cond=(tr+28*base)/(tr.sum(1)[:,None]+28);log=np.log(cond/base);per=(counts*log).sum((1,2));n=counts.sum((1,2));out=dict(held_score=float((held*log).sum()/held.sum()),train_score=float((tr*log).sum()/tr.sum()),base=base.tolist(),conditional=cond.tolist(),train_counts=tr.tolist(),held_counts=held.tolist(),perpage_counts=counts.tolist(),perpage_gain=per.tolist(),perpage_eligible=n.tolist(),held_eligible=int(held.sum()))
 if detail:out['maps']=[dict(rank=e[1],seen=e[2],eligible=e[3],probabilities=[dict(index=i,context=int(e[1][i-1]>3),rank=e[1][i],conditional=float(cond[int(e[1][i-1]>3),e[1][i]-1]),baseline=float(base[e[1][i]-1])) for i in e[3]]) for e in es]
 return out

def generate(lengths,rho):
 vs=[];rs=[];starts=[]
 for n in lengths:
  a=rng.permutation(29).tolist();starts.append(a.copy());v=[a[0]];ranks=[255];previous_near=rng.random()<PI
  us=rng.random((n-1,2))
  for u,w in us:
   p=PI+rho*(1-PI) if previous_near else PI*(1-rho);near=u<p;r=1+int(w*3) if near else 4+int(w*25);previous_near=near;x=a.pop(r);a.insert(0,x);v.append(x);ranks.append(r)
  vs.append(v);rs.append(ranks)
 return vs,rs,starts

def main():
 gate();raw=ROOT/'exploration/persistent-01/worker-f/F06-maps.json';maps=json.load(open(raw));assert len(maps)==45;assert [m['page'] for m in maps]==sorted(m['page'] for m in maps);reserved={4,9,14,19,24,29,34,39,44,54};assert not reserved&{m['page'] for m in maps};cs=[m['indices'] for m in maps];collapsed=[collapse(c) for c in cs];lengths=[len(x[0]) for x in collapsed];stutters=sum(len(c)-n for c,n in zip(cs,lengths));manifest=dict(input_path=str(raw.relative_to(ROOT)),input_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),pages=[m['page'] for m in maps],train_pages=[m['page'] for m in maps[::2]],held_pages=[m['page'] for m in maps[1::2]],collapsed_lengths=lengths,stutters=stutters,original_lengths=list(map(len,cs)),collapsed_maps=[dict(original_positions=x[1],runlengths=x[2]) for x in collapsed],source_maps=maps,seed=330824);dump('input-manifest',manifest)
 records=[];outputs=[];genranks=[];inits=[];start=time.monotonic()
 # Null fit and predictive scores before real interpretation. Every fitted table retained.
 for kind,rho,count in [('null',0.,999),('control03',.3,100),('control06',.6,100)]:
  panel=[]
  for rep in range(count):
   if rep%20==0:gate()
   vs,rs,initial=generate(lengths,rho);r=fit_score(vs);r.update(kind=kind,rho=rho,replicate=rep);panel.append(r);records.append(r);outputs.append([x for v in vs for x in v]);genranks.append([x for v in rs for x in v]);inits.append(initial)
   # Source generatedrank recovers exactly whenever symbol seen; initial alphabet never leaks eligibility.
   for v,rr,ini,(orig,positions,lens) in zip(vs,rs,initial,collapsed):
    e=extract(v);assert all(e[1][i]==rr[i] for i in range(1,len(v)) if e[2][i]);a=ini.copy();replay=[a[0]]
    for rank in rr[1:]:x=a.pop(rank);a.insert(0,x);replay.append(x)
    assert replay==v
    expanded=np.repeat(v,lens);assert len(expanded)==sum(lens);assert np.array_equal(expanded[1:]==expanded[:-1],np.repeat(np.arange(len(v)),lens)[1:]==np.repeat(np.arange(len(v)),lens)[:-1])
  print(kind,'done',count,'seconds',time.monotonic()-start,flush=True)
 scores=np.array([r['held_score'] for r in records[:999]]);threshold=float(np.quantile(scores,.99,method='higher'));power={}
 for kind in ['control03','control06']:
  p=[r['held_score'] for r in records if r['kind']==kind];power[kind]=dict(n=len(p),above_null99=sum(x>threshold for x in p),minimum=min(p),maximum=max(p),mean=float(np.mean(p)))
 print('CONTROL_POWER',power,flush=True);real=fit_score([x[0] for x in collapsed],True);real['tail']=(1+sum(scores>=real['held_score']))/1000;dump('real',real);dump('summary',dict(real_score=real['held_score'],real_tail=real['tail'],real_train_score=real['train_score'],threshold99=threshold,power=power,nulls=999,controls=200,held_eligible=real['held_eligible'],seconds=time.monotonic()-start,rank_state='near1..3 versusfar4..28',rng_after=rng.bit_generator.state,scope='conditional recency-rank memory, not literal rune-order2'))
 with gzip.open(R/'replicates.json.gz','wt') as f:json.dump(records,f)
 np.savez_compressed(R/'generated-evidence.npz',collapsed=np.array(outputs,dtype=np.uint8),generated_ranks=np.array(genranks,dtype=np.uint8),initial_alphabets=np.array(inits,dtype=np.uint8),lengths=np.array(lengths),rhos=np.array([r['rho'] for r in records]));print('REAL',real['held_score'],real['tail'],flush=True)
if __name__=='__main__':main()
