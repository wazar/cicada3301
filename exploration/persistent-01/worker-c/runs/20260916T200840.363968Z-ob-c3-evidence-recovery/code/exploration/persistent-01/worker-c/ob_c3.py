"""Adjacentpage continuity resolves MTF first-occurrence ambiguity."""
import json,time
import numpy as np
from p03_frozen import O,ROOT,parse,CHECK,dump
from ob_c2 import enc,dec,metric
from ob_c1 import nullpages

def grouping(pages):
 groups=[]
 for p in pages:
  if groups and p['original_page']==groups[-1][-1]['original_page']+1:groups[-1].append(p)
  else:groups.append([p])
 return groups

def extra_metric(groups):
 counts=np.zeros(29,dtype=int);maps=[];total=0
 for group in groups:
  cs=[np.array(p['indices']) for p in group];c=np.concatenate(cs);rank,valid=dec(c);start=0
  for page,part in zip(group,cs):
   _,localvalid=dec(part);gvalid=valid[start:start+len(part)];extra=gvalid&(~localvalid);rr=rank[start:start+len(part)];counts+=np.bincount(rr[extra&(rr!=0)],minlength=29);total+=int(extra.sum());maps.append(dict(page=page['original_page'],global_source_rank=rr.tolist(),newly_resolved_positions=np.flatnonzero(extra).tolist()));start+=len(part)
 prob=counts/counts.sum();nz=prob>0;return dict(nonrepeat_extra_entropy=float(-np.sum(prob[nz]*np.log2(prob[nz]))),extra_runes=total,counts=counts.tolist()),maps

def repartition(groups,cs):
 out=[]
 for group,c in zip(groups,cs):
  part=[];start=0
  for p in group:part.append(dict(original_page=p['original_page'],indices=c[start:start+len(p['indices'])].tolist()));start+=len(p['indices'])
  out.append(part)
 return out

def main():
 out=O/'ob-c3';out.mkdir(exist_ok=True);t=time.monotonic();rng=np.random.default_rng(330119);cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());ps=sorted([p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']],key=lambda p:p['original_page']);groups=grouping(ps);group_cs=[np.concatenate([np.array(p['indices']) for p in group]) for group in groups];real=metric(group_cs);extra,maps=extra_metric(groups);dump(out/'maps.json',maps);q=sum(np.sum(c[1:]==c[:-1]) for c in group_cs)/sum(len(c)-1 for c in group_cs);lengths=list(map(len,group_cs));nulls=[]
 for ix in range(200):
  generated=nullpages(lengths,q,rng);permuted=[np.concatenate([rng.permutation(p['indices']) for p in group]) for group in groups];nulls.append(dict(id=ix,generative=dict(pooled=metric(generated),extra=extra_metric(repartition(groups,generated))[0]),permutation=dict(pooled=metric(permuted),extra=extra_metric(repartition(groups,permuted))[0])))
 dump(out/'nulls.json',nulls)
 heldgroups=[]
 for gi,name in enumerate(CHECK):
  p=np.array(parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text())[0]);c=enc(p,7,-1);heldgroups.append([dict(original_page=1000+gi*100+j//64,indices=c[j:j+64].tolist()) for j in range(0,len(c),64)])
 hc,hmap=extra_metric(heldgroups);hcs=[np.concatenate([p['indices'] for p in g]) for g in heldgroups];hq=sum(np.sum(c[1:]==c[:-1]) for c in hcs)/sum(len(c)-1 for c in hcs);hlens=list(map(len,hcs));hnull=[]
 for ix in range(200):hnull.append(extra_metric(repartition(heldgroups,nullpages(hlens,hq,rng)))[0]['nonrepeat_extra_entropy'])
 dump(out/'held-null-entropies.json',hnull)
 comparisons={}
 for typ in ['generative','permutation']:
  ent=[x[typ]['pooled']['nonrepeat_seen_rank_entropy'] for x in nulls];extraen=[x[typ]['extra']['nonrepeat_extra_entropy'] for x in nulls];comparisons[typ]=dict(pooled_entropy_p=(1+sum(x<=real['nonrepeat_seen_rank_entropy'] for x in ent))/201,extra_entropy_p=(1+sum(x<=extra['nonrepeat_extra_entropy'] for x in extraen))/201,extra_entropy_range=[min(extraen),max(extraen)])
 result=dict(strategy='outside-box-v1',groups=[[p['original_page'] for p in g] for g in groups],real=real,newly_resolved=extra,held_extra=hc,held_extra_entropy_p=(1+sum(x<=hc['nonrepeat_extra_entropy'] for x in hnull))/201,comparisons=comparisons,seconds=time.monotonic()-t,limits='Continuity only where physicalpageIDs adjacent. No reserve/gap bridged. Lowentropy rank-source class only.')
 dump(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
