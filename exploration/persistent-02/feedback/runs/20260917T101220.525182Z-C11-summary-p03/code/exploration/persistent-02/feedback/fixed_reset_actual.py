import reset_actual as source
import reset_plants as rp
from fixed_reset import Engine,Refused
from reset_literal import encode
import extend as ex
import json,resource,time,sys,hashlib
O=ex.O/'C10-actual';O.mkdir(exist_ok=True);KP=ex.R/'exploration/persistent-02/section/key-grid.json';keys=json.loads(KP.read_text())['keys']
def run(panel,name):
 ex.guard();path=O/f'{name}-panel{panel:02}.json'
 if path.exists():return
 c=source.panels[panel];ends=source.ends;resets=source.resets;L=rp.model(name);rows=[];start=time.monotonic()
 for key in keys:
  seed=key['runes'];k=len(seed)
  try:
   full=Engine(seed,L).solve(c,ends,resets);prefix=Engine(seed,L).solve(c[:249],{i for i in ends if i<249},{i for i in resets if i<249});chosen=prefix['alternatives'][0];hist=[];a=b=29
   for i,p in enumerate(chosen['plain']):
    if i in resets:hist=[]
    if i not in chosen['literal_positions']:hist.append(p)
    a,b=b,p
    if i in ends:a,b=b,29
   tail=Engine(seed,L).solve(c[249:],{i-249 for i in ends if i>=249},{i-249 for i in resets if i>=249},initial_history=hist[-k:],initial_context=(a,b));continued=[]
   for x in tail['alternatives']:
    plain=chosen['plain']+x['plain'];literal=chosen['literal_positions']+[i+249 for i in x['literal_positions']];assert encode(plain,seed,literal,resets)==c;assert abs(rp.total(plain,ends,L)-chosen['total']-x['total'])<1e-8;continued.append(dict(seed=seed,plain=plain,literal_positions=literal,continuation_score=x['score'],continuation_total=x['total']))
   for x in full['alternatives']:assert encode(x['plain'],seed,x['literal_positions'],resets)==c;assert abs(rp.total(x['plain'],ends,L)-x['total'])<1e-8
   rows.append(dict(outcome='COMPLETE',key=key['id'],seed=seed,full=full,prefix=prefix,tail=tail,continuation=continued,maximum=full['alternatives'][0]['score'],continuation_score=continued[0]['continuation_score']))
  except Refused as e:rows.append(dict(outcome='UNRESOLVED_RESOURCE_REFUSAL',key=key['id'],seed=seed,error=str(e)))
 out=dict(panel=panel,model=name,cipher=c,ends=sorted(ends),resets=sorted(resets),rows=rows,seconds=time.monotonic()-start,peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_pins={str(p.relative_to(ex.R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source.SP,source.NP,source.AP,KP]});path.write_text(json.dumps(out,separators=(',',':'))+'\n');print(name,panel,[(r['key'],r['outcome'],r.get('maximum'),r.get('continuation_score')) for r in rows],flush=True)
def summary(name):
 rows=[json.loads((O/f'{name}-panel{i:02}.json').read_text()) for i in range(20)];assert all(r['outcome']=='COMPLETE' for p in rows for r in p['rows']),'unresolved panels prevent complete ranks';stats=[]
 for key in range(2):
  a=rows[0]['rows'][key];stats.append(dict(key=a['key'],actual_maximum=a['maximum'],score_rank=(1+sum(p['rows'][key]['maximum']>=a['maximum'] for p in rows[1:]))/20,actual_continuation=a['continuation_score'],continuation_rank=(1+sum(p['rows'][key]['continuation_score']>=a['continuation_score'] for p in rows[1:]))/20))
 mx=[max(r['maximum'] for r in p['rows']) for p in rows];ct=[max(r['continuation_score'] for r in p['rows']) for p in rows];out=dict(model=name,keys=stats,max_key_score_rank=sum(v>=mx[0] for v in mx)/20,max_key_continuation_rank=sum(v>=ct[0] for v in ct)/20,seconds=sum(p['seconds'] for p in rows),max_states=max(r[k]['peak_states'] for p in rows for r in p['rows'] for k in ['full','prefix','tail']),peak_rss=max(p['peak_process_rss_bytes'] for p in rows));(O/f'{name}-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':
 if sys.argv[1]=='summary':summary(sys.argv[2])
 else:
  for panel in map(int,sys.argv[2:]):run(panel,sys.argv[1])
