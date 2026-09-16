"""Finite leading-F width1024 check plus rejection/ordinary/affine arithmetic and rank controls."""
import json,random,time
import search as s,clues,rejection

def main():
 start=time.monotonic();q=s.Score();keys=s.recipes();ps=s.pages();lookup={p['original_page']:p for p in ps};d=clues.freeze();defs={x['id']:x for x in d['keys']+d['texts']}
 # Freeze selected cases before widening; no new key or page search.
 plan=s.O/'widen-plan.json'
 if not plan.exists():
  selected=[]
  for lane,paths in [('R01',[s.O/x/'top20.json' for x in ['r01zero','r01f','r01zero-p55','r01f-p55']]),('R02',[s.O/'r02/literal_f/top20.json'])]:
   rows=[dict(r,lane=lane) for p in paths for r in json.loads(p.read_text()) if r['mode']=='literal_f'];rows.sort(key=lambda r:r['score'],reverse=True);seen=set();chosen=[]
   for row in rows:
    key=(row['original_page'],row.get('recipe',row.get('key_id')),row['offset'],row['sign'])
    if key not in seen:chosen.append(row);seen.add(key)
    if len(chosen)==10:break
   selected.extend(chosen)
  s.dump(plan,selected)
 selected=json.loads(plan.read_text());out=[]
 for old in selected:
  page=lookup[old['original_page']];c=page['indices'];key=keys[old['recipe']][old['offset']:] if old['lane']=='R01' else clues.key_for(old,defs,len(c));alts,diag=s.fbeam(c,key,old['sign'],q,1024,16);r={k:v for k,v in old.items() if k not in ['alternatives','diagnostics','key','plain','transliteration']};r.update(id='widen:'+old['id'],plain=alts[0]['plain'],transliteration=s.render(alts[0]['plain'],page),score=alts[0]['score'],alternatives=alts,diagnostics=diag,statistics=s.stats(alts[0]['plain']),word_view=s.wordstats(alts[0]['plain'],page),previous_score=old['score'],same_best=old['plain']==alts[0]['plain']);out.append(r)
 for lane,path in [('R01',s.O/'r01widen'),('R02',s.O/'r02/widen')]:
  path.mkdir(exist_ok=True);rows=[x for x in out if x['lane']==lane];s.dump(path/'checkpoint.json',dict(cursor=len(rows),total=len(rows),top=rows));s.dump(path/'top20.json',rows)
 raw=(s.ROOT/'audit/parallel-01/reference/sources/solved_p57_parable.txt').read_text();truth=[s.ABC.index(c) for c in raw if c in s.ABC];sk=rejection.module('legacy_skip','liber-primus/analysis/campaign18_skip/skipdecode.py');ctl=rejection.module('legacy_trace','audit/experiment-01/control.py');controls=[]
 for mode in ['ordinary','rejection']:
  cipher,trace=ctl.encrypt(truth,keys['DIVINITY'],-1,330103,.83 if mode=='rejection' else 0);rows=[]
  for name,k in keys.items():
   for sign in [-1,1]:
    result=ctl.traced_beam(sk,cipher,k,sign) if mode=='rejection' else sk.rigid_decode(cipher,k,sign=sign);p=result['plain_idx'];rows.append(dict(recipe=name,sign=sign,score=result['score'],errors=sum(a!=b for a,b in zip(p,truth)),plain=p))
  rows.sort(key=lambda x:x['score'],reverse=True);plant=next(x for x in rows if x['recipe']=='DIVINITY' and x['sign']==-1);bad=keys['DIVINITY'].copy();bad[0]=(bad[0]+1)%29;badresult=ctl.traced_beam(sk,cipher,bad,-1) if mode=='rejection' else sk.rigid_decode(cipher,bad,sign=-1)
  controls.append(dict(mode=mode,truth_rank=1+sum(x['score']>plant['score'] for x in rows),planted_errors=plant['errors'],best_errors=rows[0]['errors'],rows=rows,cipher=cipher,truth=truth,rejected_keys=sum(len(x['attempts'])-1 for x in trace),corrupted_first_key_errors=sum(a!=b for a,b in zip(badresult['plain_idx'],truth))))
 # Full affine selection: planted decoder a=17,b=9; inverse is modular inverse17.
 cipher=[((p-9)*pow(17,-1,29))%29 for p in truth];aff=[]
 for aa in range(1,29):
  for b in range(29):
   p=[(aa*v+b)%29 for v in cipher];aff.append(dict(a=aa,b=b,score=q(p),errors=sum(x!=y for x,y in zip(p,truth))))
 aff.sort(key=lambda x:x['score'],reverse=True);plant=next(x for x in aff if x['a']==17 and x['b']==9);s.dump(s.O/'additional-controls.json',dict(controls=controls,affine=dict(trials=len(aff),truth_rank=1+sum(x['score']>plant['score'] for x in aff),planted_errors=plant['errors'],top=aff[:20]),widened=len(out),widened_best_changed=sum(not x['same_best'] for x in out),seconds=time.monotonic()-start));print(json.dumps(dict(seconds=time.monotonic()-start,widened=len(out),changed=sum(not x['same_best'] for x in out),controls=[dict(mode=x['mode'],rank=x['truth_rank'],errors=x['planted_errors']) for x in controls])))
if __name__=='__main__':main()
