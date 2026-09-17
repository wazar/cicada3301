from pathlib import Path
import gzip,json,numpy as np
R=Path(__file__).parent;B=R.parent;Q=B/'coordinator/Q09-reciprocal';a=json.load(gzip.open(Q/'actual.json.gz','rt'));pages=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page']);rows=[]
for p,seq in zip(pages[23:],a['cipher'][23:]):
 n=0;score=0
 for x,y in zip(seq,seq[1:]):
  if x!=y:n+=1;score+=a['fits'][1]['log_probabilities'][x][y]-a['fits'][0]['log_probabilities'][x][y]
 rows.append(dict(page=p['page'],nonrepeat_events=n,gain=score))
total=sum(x['gain'] for x in rows);n=sum(x['nonrepeat_events'] for x in rows);assert abs(total-a['held_gain'])<1e-9
out=dict(gain=total,held_nonrepeat_events=n,nats_per_event=total/n,positive_pages=sum(x['gain']>0 for x in rows),held_pages=len(rows),perpage=rows,scope='Descriptive decomposition of frozen primary statistic, no page selection or separate tests');(R/'description.json').write_text(json.dumps(out,indent=2));print(out)
