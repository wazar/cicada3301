import extend as ex
from literal_feedback import Engine,encode
import json,numpy as np,resource,time,sys,hashlib
O=ex.O/'C05-actual';O.mkdir(exist_ok=True)
section_path=ex.R/'exploration/persistent-02/section/section-packet.json';section=json.loads(section_path.read_text());C=section['body']['runes'];ENDS=set(section['body']['explicit_ends'])
null_path=ex.R/'exploration/persistent-02/decoder/null-calibration-inputs.json';null=json.loads(null_path.read_text());PANELS=[C]+[c[13:] for c in null['packets']]
assert len(PANELS)==20 and len(C)==716
for c in PANELS:
 assert len(c)==716 and [x==0 for x in c]==[x==0 for x in C]
 assert [a==b for a,b in zip(c,c[1:])]==[a==b for a,b in zip(C,C[1:])]
def run(panel):
 ex.guard();path=O/f'panel{panel:02}.json'
 if path.exists():return json.loads(path.read_text())
 c=PANELS[panel];norm=len(c)+len(ENDS);rows=[];arrays={};t=time.monotonic()
 for k in [2,3]:
  ex.guard();result=Engine(k,ex.q.L).solve(c,ENDS,retain=16,block=32)
  for a in result['alternatives']:
   assert all(x is not None for x in a['seed']);assert encode(a['plain'],a['seed'],a['literal_positions'])==c
   assert abs(ex.q.lm.score(a['plain'],ENDS)*norm-a['total'])<2e-9
  base=ex.q.decode(c,[0]*k);W=ex.q.table(base,ENDS,k);v=ex.q.scores(W,k)/norm;idx=int(np.argmax(v));offset=ex.q.OFF[k][idx];seed=((-offset[:k])%29).tolist();uninterrupted=dict(maximum=float(v[idx]),seed=seed,plain=ex.q.decode(c,seed),seed_count=len(v));assert result['maximum']/norm>=uninterrupted['maximum']-1e-10
  arrays[f'k{k}_uninterrupted_scores']=v;arrays[f'k{k}_uninterrupted_factors']=W;rows.append(dict(k=k,result=result,uninterrupted=uninterrupted));print(panel,k,result['seconds'],result['peak_states'],result['maximum']/norm,uninterrupted['maximum'],flush=True)
 maximum=max(r['result']['maximum']/norm for r in rows);unmax=max(r['uninterrupted']['maximum'] for r in rows);out=dict(panel=panel,cipher=c,ends=sorted(ENDS),rows=rows,maximum=maximum,uninterrupted_maximum=unmax,gain=maximum-unmax,seconds=time.monotonic()-t,peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_pins={str(p.relative_to(ex.R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [section_path,null_path]})
 np.savez_compressed(O/f'panel{panel:02}.npz',**arrays);path.write_text(json.dumps(out,separators=(',',':'))+'\n');return out
def summary():
 rows=[json.loads(p.read_text()) for p in sorted(O.glob('panel??.json'))];assert len(rows)==20;a=rows[0];s=dict(actual_maximum=a['maximum'],actual_uninterrupted_maximum=a['uninterrupted_maximum'],actual_gain=a['gain'],score_rank=(1+sum(r['maximum']>=a['maximum'] for r in rows[1:]))/20,gain_rank=(1+sum(r['gain']>=a['gain'] for r in rows[1:]))/20,panels=20,solves=40,total_seconds=sum(r['seconds'] for r in rows),max_process_rss_bytes=max(r['peak_process_rss_bytes'] for r in rows),max_states=max(r0['result']['peak_states'] for r in rows for r0 in r['rows']))
 (O/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s))
if __name__=='__main__':
 if sys.argv[1]=='summary':summary()
 else:
  for panel in map(int,sys.argv[1:]):run(panel)
