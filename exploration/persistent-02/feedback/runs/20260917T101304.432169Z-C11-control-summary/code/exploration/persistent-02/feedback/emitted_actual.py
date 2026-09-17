import reset_actual as source
import reset_plants as rp
from emitted_feedback import Engine,encode,Refused
import extend as ex
import json,resource,time,sys,hashlib
O=ex.O/'C11-actual';O.mkdir(exist_ok=True)
def run(panel,name):
 ex.guard();path=O/f'{name}-panel{panel:02}.json'
 if path.exists():return
 c=source.panels[panel];ends=source.ends;L=rp.model(name);rows=[];start=time.monotonic()
 for k in [2,3]:
  try:
   full=Engine(k,L).solve(c,ends);prefix=Engine(k,L).solve(c[:249],{i for i in ends if i<249});chosen=prefix['alternatives'][0];assert all(v is not None for v in chosen['seed']);a=b=29
   for i,p in enumerate(chosen['plain']):
    a,b=b,p
    if i in ends:a,b=b,29
   phase=min(k,249-len(chosen['literal_positions']));tail=Engine(k,L,seed=chosen['seed']).solve(c[249:],{i-249 for i in ends if i>=249},initial_history=chosen['plain'][-k:],initial_phase=phase,initial_context=(a,b));continued=[]
   for x in tail['alternatives']:
    plain=chosen['plain']+x['plain'];literal=chosen['literal_positions']+[i+249 for i in x['literal_positions']];assert encode(plain,chosen['seed'],literal)==c;assert abs(rp.total(plain,ends,L)-chosen['total']-x['total'])<1e-8;continued.append(dict(seed=chosen['seed'],plain=plain,literal_positions=literal,continuation_score=x['score'],continuation_total=x['total']))
   for x in full['alternatives']:assert encode(x['plain'],x['seed'],x['literal_positions'])==c;assert abs(rp.total(x['plain'],ends,L)-x['total'])<1e-8
   rows.append(dict(outcome='COMPLETE',k=k,full=full,prefix=prefix,tail=tail,continuation=continued,maximum=full['alternatives'][0]['score'],prefix_maximum=chosen['score'],continuation_score=continued[0]['continuation_score']))
  except Refused as e:rows.append(dict(outcome='UNRESOLVED_RESOURCE_REFUSAL',k=k,error=str(e)))
 out=dict(panel=panel,model=name,cipher=c,ends=sorted(ends),rows=rows,seconds=time.monotonic()-start,peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_pins={str(p.relative_to(ex.R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source.SP,source.NP]});path.write_text(json.dumps(out,separators=(',',':'))+'\n');print(name,panel,[(r['k'],r['outcome'],r.get('maximum'),r.get('continuation_score')) for r in rows],flush=True)
def summary(name):
 rows=[json.loads((O/f'{name}-panel{i:02}.json').read_text()) for i in range(20)];assert all(r['outcome']=='COMPLETE' for p in rows for r in p['rows']),'unresolved panels prevent complete ranks';stats=[]
 for ix in range(2):
  a=rows[0]['rows'][ix];stats.append(dict(k=a['k'],actual_maximum=a['maximum'],score_rank=(1+sum(p['rows'][ix]['maximum']>=a['maximum'] for p in rows[1:]))/20,actual_continuation=a['continuation_score'],continuation_rank=(1+sum(p['rows'][ix]['continuation_score']>=a['continuation_score'] for p in rows[1:]))/20))
 mx=[max(r['maximum'] for r in p['rows']) for p in rows];chosen=[max(p['rows'],key=lambda r:(r['prefix_maximum'],-r['k'])) for p in rows];ct=[r['continuation_score'] for r in chosen];out=dict(model=name,k_results=stats,family_full_rank=sum(v>=mx[0] for v in mx)/20,prefix_selected_k=chosen[0]['k'],prefix_selected_continuation=ct[0],prefix_selected_continuation_rank=sum(v>=ct[0] for v in ct)/20,seconds=sum(p['seconds'] for p in rows),max_states=max(r[k]['peak_states'] for p in rows for r in p['rows'] for k in ['full','prefix','tail']),peak_rss=max(p['peak_process_rss_bytes'] for p in rows));(O/f'{name}-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':
 if sys.argv[1]=='summary':summary(sys.argv[2])
 else:
  for panel in map(int,sys.argv[2:]):run(panel,sys.argv[1])
