from oracle import forward
from pathlib import Path
import json,gzip,random,hashlib
R=Path(__file__).parent;Q=R.parent/'worker-p/P15';load=lambda name:json.load(gzip.open(Q/(name+'.json.gz'),'rt'))
keys=load('keys');rng=random.Random(331519);results=[];inputs={};nsymbols=0
for pid in [0,17]:
 m=load('map-'+str(pid));real=load('real-'+str(pid));assert real['cipher']==m['indices'];c=real['cipher'];packets=[('real-'+str(pid),real)]
 for rep in range(19):
  expected=[rng.randrange(29)]
  for i in range(1,len(c)):
   if c[i]==c[i-1]:expected.append(expected[-1])
   else:
    u=rng.randrange(28);expected.append(u+(u>=expected[-1]))
  name=f'null-{pid}-{rep}';z=load(name);assert z['cipher']==expected and z['ends']==real['ends'];packets.append((name,z))
 for name,z in packets:
  p=Q/(name+'.json.gz');b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};(R/'snapshots'/p.name).write_bytes(b)
  for cell in keys:
   states={0};history=[];last=[];maxquery=-1
   for i,v in enumerate(z['cipher']):
    nextstates=set();last=[]
    for j in sorted(states):
     choices=[]
     for plain in range(29):
      ev=forward(plain,z['cipher'][i-1] if i else None,cell['key'],j)
      nsymbols+=1
      for e in ev:
       maxquery=max(maxquery,e['after']-1)
       if e['output']==v:nextstates.add(e['after']);choices.append([plain,e['after']])
     last.append({'start':j,'accepted_candidates':choices})
    history.append({'index':i,'before':sorted(states),'after':sorted(nextstates)});states=nextstates
    if not states:break
   prod=next(row for row in z['rows'] if row['id']==cell['id']);assert not states and not prod['decode']['feasible'] and prod['decode']['first_failed']==i
   assert prod['score'] is None and prod['decode']['eof_hypotheses']==0 and maxquery<2048
   results.append({'packet':name,'cell':cell['id'],'first_failed':i,'max_trial_index':maxquery,'reachable_sets':history,'failed_state_choices':last})
  assert z['top16'] is None
summary=load('summary');assert [s['page'] for s in summary]==[0,17]
assert all(row['score'] is None and row['tail'] is None and all(n['score'] is None for n in row['null']) for row in summary)
(R/'support-inputs.json').write_text(json.dumps(inputs,indent=2));(R/'support.json').write_text(json.dumps({'status':'PASS','cells':len(results),'forward_symbol_trees':nsymbols,'results':results},indent=2))
print('PASS',len(results),'cells;',nsymbols,'forward symbol trees')
print([(r['packet'],r['cell'],r['first_failed']) for r in results if r['packet'].startswith('real')])
