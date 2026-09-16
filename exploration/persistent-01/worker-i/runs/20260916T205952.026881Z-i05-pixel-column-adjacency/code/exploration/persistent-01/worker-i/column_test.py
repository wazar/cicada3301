import json,pathlib,hashlib
import numpy as np
from scipy.cluster.hierarchy import linkage,fcluster
from scipy.spatial.distance import pdist
D=pathlib.Path('exploration/persistent-01/worker-i');assert not pathlib.Path('exploration/persistent-01/STOP').exists();rng=np.random.default_rng(190019)
r=json.loads((D/'coordinates.json').read_text());cl=np.load(D/'width-arrays.npz')['classes'];dataset=json.load(open('audit/parallel-01/inputs/dataset.json'));pages={p['original_page']:p for p in dataset['pages'] if p['original_page'] in [0,1]};records=[];skipped=[]
for p in [0,1]:
 for row in range(12):
  ix=[i for i,x in enumerate(r) if x['page']==p and x['row']==row];line=pages[p]['lines'][row]
  if len(ix)!=len(line['indices']):skipped.append(dict(page=p,row=row,components=len(ix),expected=len(line['indices'])));continue
  for i,label,src in zip(ix,line['indices'],line['source_char_positions']):records.append(dict(**r[i],component_id=i,shape_class=int(cl[i]),rune=int(label),source_char_position=src))
classmap={}
for x in records:classmap.setdefault(x['shape_class'],set()).add(x['rune'])
conflicts={k:sorted(v) for k,v in classmap.items() if len(v)>1}
(D/'route-mapping.json').write_text(json.dumps(dict(records=records,skipped=skipped,class_to_runes={k:sorted(v) for k,v in classmap.items()},conflicts=conflicts),indent=2))
if conflicts:raise RuntimeError(f'identity mapping conflicts: {conflicts}')
xs=np.array([(x['x']+x['right'])/2 for x in records]);sp=[]
for p in [0,1]:
 for row in range(12):
  xx=[xs[i] for i,x in enumerate(records) if x['page']==p and x['row']==row];sp.extend(np.diff(xx))
bound=float(np.median(sp)/2);bands=fcluster(linkage(pdist(xs[:,None]),method='complete'),bound,criterion='distance');N=len(records);lab=np.array([x['rune'] for x in records]);groups=[];all_edges=[];wrap_breaks=[]
for p in [0,1]:
 rows=sorted(set(x['row'] for x in records if x['page']==p));profs=[]
 for row in rows:
  ix=np.array([i for i,x in enumerate(records) if x['page']==p and x['row']==row]);profs.append({b:int(ii[0]) for b in set(bands[ix]) if len(ii:=ix[bands[ix]==b])==1})
 links=[(j,j+1) for j in range(len(rows)-1) if rows[j+1]==rows[j]+1];pair_edges={}
 for a in range(len(rows)):
  for b in range(len(rows)):
   pair_edges[a,b]=[(profs[a][k],profs[b][k]) for k in set(profs[a])&set(profs[b])]
 for a,b in links:all_edges.extend(pair_edges[a,b])
 groups.append(dict(page=p,rows=rows,profiles=profs,links=links,pair_edges=pair_edges))
def counts(labels,draws):
 counts=np.zeros(draws.shape[0],int);edges=np.zeros_like(counts)
 off=0
 for g in groups:
  n=len(g['rows']);mat=np.zeros((n,n),int);em=np.zeros_like(mat)
  for (a,b),es in g['pair_edges'].items():em[a,b]=len(es);mat[a,b]=sum(labels[i]==labels[j] for i,j in es)
  perm=draws[:,off:off+n];off+=n
  for a,b in g['links']:counts+=mat[perm[:,a],perm[:,b]];edges+=em[perm[:,a],perm[:,b]]
 return counts,edges
sizes=[len(g['rows']) for g in groups]
def permutations(n):return np.concatenate([np.array([rng.permutation(s) for _ in range(n)]) for s in sizes],axis=1)
identity=np.concatenate([np.arange(s) for s in sizes])[None,:];draw=permutations(10000);actual_c,actual_e=counts(lab,identity);null_c,null_e=counts(lab,draw);rate=actual_c[0]/actual_e[0];pval=(1+sum(null_c/np.maximum(null_e,1)<=rate))/(len(draw)+1)
perpage=[]
for g in groups:
 es=[e for a,b in g['links'] for e in g['pair_edges'][a,b]];perpage.append(dict(page=g['page'],rows=g['rows'],edges=len(es),repeats=sum(lab[i]==lab[j] for i,j in es),rate=sum(lab[i]==lab[j] for i,j in es)/max(len(es),1)))
# Same row-profile randomizations for every controlled field; no parameter selection.
cdraw=permutations(1000);plants=[];uniforms=[];plant_null=[];uniform_null=[];cp=[];cn=[]
for trial in range(100):
 u=rng.integers(0,29,N);v=u.copy()
 # edges descend by consecutive row, each node has at most one predecessor
 for i,j in sorted(all_edges,key=lambda e:(records[e[1]]['page'],records[e[1]]['row'])):
  if v[j]==v[i] and rng.random()<.85:v[j]=(v[j]+rng.integers(1,29))%29
 for vals,outs,nullouts,pouts in [(v,plants,plant_null,cp),(u,uniforms,uniform_null,cn)]:
  c,e=counts(vals,identity);nc,ne=counts(vals,cdraw);rr=c[0]/max(e[0],1);nr=nc/np.maximum(ne,1);pp=(1+sum(nr<=rr))/(len(nr)+1);outs.append(vals);nullouts.append(nr);pouts.append(pp)
# readable exact graph and sorted route nodes; no missing nodes or wraps silently concatenated
(D/'column-graph.json').write_text(json.dumps(dict(band_diameter_px=bound,bands=bands.tolist(),edges=all_edges,complete_rows=[dict(page=g['page'],rows=g['rows'],links=g['links']) for g in groups]),indent=2))
np.savez(D/'column-arrays.npz',labels=lab,x=xs,bands=bands,edges=np.array(all_edges),null_counts=null_c,null_edges=null_e,permutations=draw,control_permutations=cdraw,planted=plants,uniform=uniforms,planted_null=plant_null,uniform_null=uniform_null,planted_p=cp,uniform_p=cn)
horizontal=[]
for p in [0,1]:
 es=[]
 for row in range(12):
  ix=[i for i,x in enumerate(records) if x['page']==p and x['row']==row];es.extend(zip(ix[:-1],ix[1:]))
 horizontal.append(dict(page=p,edges=len(es),repeats=sum(lab[i]==lab[j] for i,j in es)))
out=dict(mapped_instances=N,skipped=skipped,shape_identity_conflicts=conflicts,band_diameter_px=bound,bands=len(set(bands)),column_edges=int(actual_e[0]),column_repeats=int(actual_c[0]),column_rate=float(rate),null_rate_mean=float(np.mean(null_c/np.maximum(null_e,1))),p_lower=float(pval),perpage=perpage,horizontal=horizontal,control_power=float(np.mean(np.array(cp)<=.01)),control_false_positive=float(np.mean(np.array(cn)<=.01)),scope='complete source rows only; missing rows/bands and all wraps break edges; row-profile permutation preserves typography; geometry-only route frozen before label scores')
(D/'column-results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
