"""Fixed body-first seed fit, unmodified sum recurrence continued across pages1/2."""
import extend as ex
import pathlib,json,hashlib,numpy as np,sys
O=ex.O/'C03';O.mkdir(exist_ok=True)
ex.q.O=O
packet_path=ex.R/'exploration/persistent-02/section/section-packet.json'
s=json.loads(packet_path.read_text());body=s['body'];C=body['runes'];ENDS=set(body['explicit_ends']);N=249
assert len(C)==716 and len(s['pages'][0]['runes'])-s['heading']['body_start']==N

def run():
 meta=dict(source=str(packet_path.relative_to(ex.R)),sha256=hashlib.sha256(packet_path.read_bytes()).hexdigest(),cipher=C,ends=sorted(ENDS),fit_runes=N,continuation_runes=len(C)-N,policy='body starts original0 index13; no page-join boundary token or recurrence reset; fit seed only on first249 body runes')
 (O/'input.json').write_text(json.dumps(meta,indent=2)+'\n');rows=[]
 for panel in range(20):
  ex.guard();seed=None if panel==0 else 2026091800+panel-1
  c=C if panel==0 else ex.q.null(C,seed)
  name='actual-prefix' if panel==0 else f'null{panel-1:02}-prefix'
  data=dict(name=name,cipher=c[:N],ends=sorted(e for e in ENDS if e<N),source={k:meta[k] for k in ['source','sha256','policy']})
  result=ex.q.search(data);alts=[]
  for row in result['global16']:
   p=ex.q.decode(c,row['seed']);assert p[:N]==row['plain']
   prefix_norm=N+len(data['ends']);full_norm=len(c)+len(ENDS);full=ex.q.lm.score(p,ENDS)*full_norm;prefix=ex.q.lm.score(p[:N],set(data['ends']))*prefix_norm
   # Subtraction leaves continuation increments with the true carried context.
   suffix=(full-prefix)/(full_norm-prefix_norm)
   alts.append(dict(k=row['k'],seed=row['seed'],prefix_score=row['score'],continuation_score=suffix,full_score=full/full_norm,plain=p))
  out=dict(panel=panel,null_seed=seed,fit_search_seeds=732511,selected_by='highest prefix P03 score only, tie order k then offset index',alternatives=alts)
  (O/f'panel{panel:02}.json').write_text(json.dumps(out,separators=(',',':'))+'\n');rows.append(out)
  if panel>0:ex.compact_null(name)
  print(panel,alts[0]['prefix_score'],alts[0]['continuation_score'],flush=True)
 stats=dict(actual_prefix=rows[0]['alternatives'][0]['prefix_score'],actual_continuation=rows[0]['alternatives'][0]['continuation_score'],tail=(1+sum(r['alternatives'][0]['continuation_score']>=rows[0]['alternatives'][0]['continuation_score'] for r in rows[1:]))/20,comparators=19,fit_seeds_per_panel=732511,panels=20,note='one frozen prefix-best seed per panel; continuation is model-specific and discovery previously observed; no refit by continuation')
 (O/'summary.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats))
if __name__=='__main__':run()
