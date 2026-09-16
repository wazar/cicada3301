from pathlib import Path
import json,gzip,hashlib,math,random
import numpy as np
O=Path(__file__).resolve().parent;inp=json.loads((O/'input.json').read_text());result=json.loads((O/'result.json').read_text());real=json.loads((O/'real.json').read_text());raw=Path(inp['map_path']);assert hashlib.sha256(raw.read_bytes()).hexdigest()==inp['map_sha256'];maps=json.loads(raw.read_text())
with gzip.open(O/'replicates.json.gz','rt') as f:rows=json.load(f)
archive=np.load(O/'generated.npz');C=archive['collapsed'].astype(np.int16);R=archive['latent_ranks'].astype(np.int16);E=archive['expanded'];assert len(C)==1199;offsets=inp['collapsed_offsets'];fullpos=0;counts=np.zeros((1200,45),dtype=int);ns=[];realflat=[];witnesses=[]
for page,(m,saved) in enumerate(zip(maps,inp['pages'])):
 original=np.array(m['indices']);starts=np.r_[0,np.flatnonzero(original[1:]!=original[:-1])+1];ends=np.r_[starts[1:],len(original)];base=original[starts];lengths=ends-starts;assert base.tolist()==saved['base'] and lengths.tolist()==saved['runlengths'];assert [list(range(int(a),int(b))) for a,b in zip(starts,ends)]==saved['runs'];realflat.extend(base.tolist());lo,hi=offsets[page:page+2]
 c=C[:,lo:hi];rank=R[:,lo:hi];assert np.array_equal(c[:,0],rank[:,0])
 if c.shape[1]>1:assert np.array_equal(c[:,1],rank[:,1]+(rank[:,1]>=c[:,0]))
 a,b=c[:,:-2],c[:,1:-1];f=(b+(b-a))%29;r=rank[:,2:];lower=np.minimum(b,f);higher=np.maximum(b,f);replayed=r+(r>=lower)+(r>=higher-1);replayed=np.where(r==27,f,replayed);assert np.array_equal(replayed,c[:,2:]);assert np.all(c[:,1:]!=c[:,:-1])
 expanded=np.repeat(c,lengths,axis=1);stored=E[:,fullpos:fullpos+len(original)];assert np.array_equal(expanded,stored);assert np.all((stored[:,1:]==stored[:,:-1])==(original[1:]==original[:-1]));fullpos+=len(original)
 # Independent expression: equality of successive modular increments.
 diffs=np.diff(c,axis=1)%29;events=diffs[:,1:]==diffs[:,:-1];counts[1:,page]=events.sum(1);actualdiff=np.diff(base)%29;actual=actualdiff[1:]==actualdiff[:-1];counts[0,page]=actual.sum();ns.append(len(actual))
 for index in np.flatnonzero(actual)+2:witnesses.append(dict(page=m['page'],collapsed_indices=[int(index-2),int(index-1),int(index)],runes=base[index-2:index+1].tolist(),original_run_starts=starts[index-2:index+1].tolist(),source_coordinates=[m['source_char_positions'][int(v)] for v in starts[index-2:index+1]]))
allstats=[real]+rows
for i,s in enumerate(allstats):
 train=sum(counts[i,::2]);held=sum(counts[i,1::2]);tn=sum(ns[::2]);hn=sum(ns[1::2]);eps=min(1/28,(train+.5)/(tn+1));score=(held*math.log(28*eps)+(hn-held)*math.log(28*(1-eps)/27))/hn
 assert int(train)==s['train_events'] and int(held)==s['held_events'] and tn==s['train_eligible'] and hn==s['held_eligible'];assert abs(eps-s['epsilon'])<1e-14 and abs(score-s['score'])<1e-12
 assert [r['events'] for r in s['perpage']]==counts[i].tolist()
null=[r['score'] for r in rows[:999]];tail=(1+sum(x>=real['score'] for x in null))/1000;assert tail==result['real']['tail']
for row in rows[999:]:assert row['tail']==(1+sum(x>=row['score'] for x in null))/1000
# Independent scalar generator replay for one null and each control strength, from saved seeds.
for idx in [0,998,999,1098,1099,1198]:
 row=rows[idx];rng=random.Random(row['seed']);built=[]
 for p in inp['pages']:
  base=[rng.randrange(29)]
  if len(p['base'])>1:
   rank=rng.randrange(28);allowed=[x for x in range(29) if x!=base[-1]];base.append(allowed[rank])
  for j in range(2,len(p['base'])):
   blocked=(2*base[-1]-base[-2])%29
   if rng.random()<row['generator_epsilon']:base.append(blocked)
   else:
    allowed=[x for x in range(29) if x not in [base[-1],blocked]];base.append(allowed[rng.randrange(27)])
  built.extend(base)
 assert built==C[idx].tolist()
(O/'exact-zero-witnesses.json').write_text(json.dumps(witnesses,indent=2));out=dict(status='PASS',panels_scored=1200,generated_panels_replayed=1199,latent_positions_replayed=int(R.size),exact_masks_checked=1199*45,scalar_rng_panels=6,exact_zero_witnesses=len(witnesses),real_tail=tail,null_event_mean=float(counts[1:1000].sum(1).mean()),null_event_expected=sum(ns)/28)
(O/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
