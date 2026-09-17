"""Reviewed structured seed search on full section and prefix-continuation."""
import extend as ex,structured as st
import json,numpy as np,pathlib,hashlib,sys,resource,time
O=ex.O/'C02-actual';O.mkdir(exist_ok=True)
F=ex.R/'exploration/persistent-02/section/section-packet.json';packet=json.loads(F.read_text());C=packet['body']['runes'];ENDS=set(packet['body']['explicit_ends']);N=249
assert len(C)==716 and packet['body']['page_spans']==[[0,249],[249,515],[515,716]]
def run(panel):
 ex.guard();path=O/f'panel{panel:02}.json'
 if path.exists():return json.loads(path.read_text())
 begin=time.monotonic();seed=None if panel==0 else 2026091900+panel-1;c=C if panel==0 else ex.q.null(C,seed);arrays={};groups={}
 for mode in ['full','prefix']:
  cc=c if mode=='full' else c[:N];ends=ENDS if mode=='full' else {e for e in ENDS if e<N};norm=len(cc)+len(ends);rows=[]
  for k in [5,6,7,8]:
   ex.guard();base=ex.q.decode(cc,[0]*k);W=ex.q.table(base,ends,k);result=st.solve(W,max_nodes=100000,max_seconds=30);alts=[]
   for alt in result['alternatives']:
    seedkey=[(-x)%29 for x in alt['offset'][:k]];p=ex.q.decode(c,seedkey);score=ex.q.lm.score(p[:len(cc)],ends);assert abs(score*norm-alt['score'])<2e-9
    prefix_norm=N+sum(e<N for e in ENDS);full_norm=len(c)+len(ENDS);prefix=ex.q.lm.score(p[:N],{e for e in ENDS if e<N})*prefix_norm;full=ex.q.lm.score(p,ENDS)*full_norm
    alts.append(dict(k=k,seed=seedkey,offset=alt['offset'],selection_score=score,full_score=full/full_norm,continuation_score=(full-prefix)/(full_norm-prefix_norm),plain=p))
   arrays[f'{mode}_k{k}_factors']=W;arrays[f'{mode}_k{k}_baseline']=np.array(base,dtype=np.uint8)
   rows.append(dict(k=k,result=result,lower=result['maximum']/norm,upper=result['upper_bound']/norm,alternatives=alts));print(panel,mode,k,result['seconds'],result['nodes_popped'],result['gap'],flush=True)
  candidates=[a for r in rows for a in r['alternatives']];candidates.sort(key=lambda x:(-x['selection_score'],x['k'],x['offset']));top=[];seen=set()
  for alt in candidates:
   key=tuple(alt['plain'])
   if key not in seen:top.append(alt);seen.add(key)
   if len(top)==16:break
  groups[mode]=dict(rows=rows,global16=top,lower=max(r['lower'] for r in rows),upper=max(r['upper'] for r in rows),all_certified=all(r['result']['certified_within_1e_10'] for r in rows))
 out=dict(panel=panel,null_seed=seed,cipher=c,ends=sorted(ENDS),prefix_runes=N,source=dict(path=str(F.relative_to(ex.R)),sha256=hashlib.sha256(F.read_bytes()).hexdigest()),groups=groups,seconds=time.monotonic()-begin,peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,platform_rss_units='macOS bytes')
 np.savez_compressed(O/f'panel{panel:02}.npz',**arrays);path.write_text(json.dumps(out,separators=(',',':'))+'\n');return out
def summary():
 rows=[json.loads(p.read_text()) for p in sorted(O.glob('panel??.json'))]
 assert len(rows)==20
 a=rows[0];nulls=rows[1:];lo=a['groups']['full']['lower'];hi=a['groups']['full']['upper'];selected=a['groups']['prefix']['global16'][0];all_exact=all(r['groups'][g]['all_certified'] for r in rows for g in ['full','prefix'])
 res=dict(panels=20,solves=160,actual_full_lower=lo,actual_full_upper=hi,full_rank_interval=[(1+sum(r['groups']['full']['lower']>=hi+1e-12 for r in nulls))/20,(1+sum(r['groups']['full']['upper']>=lo-1e-12 for r in nulls))/20],full_procedure_rank=(1+sum(r['groups']['full']['lower']>=lo for r in nulls))/20,actual_prefix_selected_seed=selected['seed'],actual_prefix_selected_k=selected['k'],actual_continuation_score=selected['continuation_score'],continuation_procedure_rank=(1+sum(r['groups']['prefix']['global16'][0]['continuation_score']>=selected['continuation_score'] for r in nulls))/20,all_numerically_certified=all_exact,total_solver_seconds=sum(r0['result']['seconds'] for r in rows for g in r['groups'].values() for r0 in g['rows']),max_peak_rss_bytes=max(r['peak_process_rss_bytes'] for r in rows))
 (O/'summary.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
if __name__=='__main__':
 if sys.argv[1]=='summary':summary()
 else:
  for panel in map(int,sys.argv[1:]):run(panel)
