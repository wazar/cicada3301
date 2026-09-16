import pathlib,json,gzip,numpy as np,math,hashlib
R=pathlib.Path(__file__).parent;manifest=json.load(open(R/'input-manifest.json'));real=json.load(open(R/'real.json'));summary=json.load(open(R/'summary.json'));zfile=np.load(R/'generated-evidence.npz');z={name:zfile[name] for name in zfile.files};lens=z['lengths'];cuts=np.r_[0,np.cumsum(lens)];
with gzip.open(R/'replicates.json.gz','rt') as f:records=json.load(f)
assert len(records)==1199 and len(z['collapsed'])==1199;assert summary['real_tail']==(1+sum(r['held_score']>=real['held_score'] for r in records[:999]))/1000
# Scalar formula replay for every fitted prediction table/counts, independent of worker functions.
for r in records+[real]:
 counts=np.array(r['perpage_counts']);tr=counts[::2].sum(0);he=counts[1::2].sum(0);base=(tr.sum(0)+1)/(tr.sum()+28);cond=(tr+28*base)/(tr.sum(1)[:,None]+28);assert np.allclose(base,r['base'],rtol=0,atol=1e-15);assert np.allclose(cond,r['conditional'],rtol=0,atol=1e-15);score=sum(int(he[s,j])*math.log(cond[s,j]/base[j]) for s in range(2) for j in range(28))/int(he.sum());assert abs(score-r['held_score'])<1e-14
# Reconstruct ranks using number of distinct intervening symbols, independent of MTF implementation.
realeligible=[]
for pi,m in enumerate(manifest['source_maps']):
 runs=manifest['collapsed_maps'][pi];v=[m['indices'][i] for i in runs['original_positions']];last={};ranks=[];valid=[]
 for i,x in enumerate(v):
  valid.append(x in last);ranks.append(len(set(v[last[x]+1:i])) if x in last else None);last[x]=i
 # distinctintervening symbols equals MTF rank, as current symbol absent in interval.
 emap=real['maps'][pi];assert valid==emap['seen'];assert all(ranks[i]==emap['rank'][i] for i in range(len(v)) if valid[i]);eligible=[i for i in range(1,len(v)) if valid[i] and valid[i-1]];assert eligible==emap['eligible'];realeligible.append(len(eligible))
 # Repeating run counts reconstructs exact data and stutter mask.
 assert np.repeat(v,runs['runlengths']).tolist()==m['indices']
latent=[]
for ix,r in enumerate(records):
 near=0;den=0;group=np.zeros((2,2),dtype=int)
 for pi in range(45):
  v=z['collapsed'][ix,cuts[pi]:cuts[pi+1]].tolist();rr=z['generated_ranks'][ix,cuts[pi]:cuts[pi+1]].tolist();a=z['initial_alphabets'][ix,pi].tolist();re=[a[0]]
  for rank in rr[1:]:x=a.pop(rank);a.insert(0,x);re.append(x)
  assert re==v and all(x!=y for x,y in zip(v,v[1:]));runmap=manifest['collapsed_maps'][pi];expanded=np.repeat(v,runmap['runlengths']);orig=np.array(manifest['source_maps'][pi]['indices']);assert np.array_equal(expanded[1:]==expanded[:-1],orig[1:]==orig[:-1]);flags=[x<=3 for x in rr[1:]];near+=sum(flags);den+=len(flags)
  for a,b in zip(flags,flags[1:]):group[int(a),int(b)]+=1
 latent.append(dict(kind=r['kind'],replicate=r['replicate'],near_fraction=near/den,group_counts=group.tolist()))
cal={}
for kind in ['null','control03','control06']:
 vals=[x['near_fraction'] for x in latent if x['kind']==kind];cal[kind]=dict(replicates=len(vals),near_fraction_mean=float(np.mean(vals)),near_fraction_min=min(vals),near_fraction_max=max(vals),target=3/28)
out=dict(replicates_replayed=1199,predictive_tables_replayed=1200,latent_generation_exact=True,all_exact_observed_stutter_masks=True,independent_real_distinctsymbol_rank_replay=True,real_eligible_by_page=realeligible,latent_marginal_calibration=cal,real_null_exceedances=sum(r['held_score']>=real['held_score'] for r in records[:999]))
(R/'check-result.json').write_text(json.dumps(out,indent=2));(R/'latent-calibration.json').write_text(json.dumps(latent));print(json.dumps(out,indent=2))
