from pathlib import Path
import json,gzip,math,collections,hashlib
B=Path('exploration/persistent-01/worker-s');O=B/'S17';M=Path('exploration/persistent-01/coordinator/Q05-latin-clean');packets=json.loads((O/'packets.json').read_text());c=[{tuple(r['key']):r['count'] for r in a} for a in json.loads(gzip.decompress((M/'counts.json.gz').read_bytes()))];tot=[]
for cc in c:
 t=collections.Counter()
 for key,count in cc.items():t[key[:-1]]+=count
 tot.append(t)
def score(plain,ends):
 s=(29,29);out=0;es=set(ends)
 for i,p in enumerate(plain):
  for x in ([p,29] if i in es else [p]):
   v=(c[0].get((x,),0)+.5)/(tot[0][()]+15)
   for n,alpha in [(1,8),(2,5)]:ctx=s[-n:];v=(c[n].get(ctx+(x,),0)+alpha*v)/(tot[n][ctx]+alpha)
   out+=math.log(v);s=(s[-1],x)
 return out
trans=[r['transliteration'] for r in json.loads(Path('KNOWLEDGE.json').read_text())['gematria_primus']['table']]
controls=[];actual=[];outputs=[];maxerr=0;evals=0;accepted=0;seconds=0;nulltimes=0;attempts=[];nsearch=0
for i,p in enumerate(packets):
 files=[O/f'packet{i}-main.json']+([O/f'packet{i}-null{j:02}.json' for j in range(19)] if i>=4 else []);nullmax=[]
 for fi,f in enumerate(files):
  r=json.loads(f.read_text());assert r['complete'] and r['exit']==0;assert len(r['restarts'])==24;assert r['cipher']==p['cipher'] if fi==0 else True;nsearch+=1;seconds+=r['seconds']
  for row in r['restarts']:
   assert sorted(row['map'])==list(range(29));inv=[row['map'].index(x) for x in range(29)];assert [inv[x] for x in row['plain']]==r['cipher'];s=score(row['plain'],r['ends']);err=abs(s-row['score']);maxerr=max(maxerr,err);assert err<1e-8;evals+=row['evaluations'];accepted+=row['accepted_sa']
  best=max(r['restarts'],key=lambda v:v['score']);assert r['best_restart']==best['restart'] and r['maximum']==best['score']
  if fi:
   q=json.loads((O/f'packet{i}-null{fi-1:02}.input.json').read_text());x=q['cipher'];assert q['complete'] and x==r['cipher'];assert sorted(x)==sorted(p['cipher']);assert sum(a==b for a,b in zip(x,x[1:]))==sum(a==b for a,b in zip(p['cipher'],p['cipher'][1:]));nulltimes+=q['seconds'];attempts.append(q['attempts']);nullmax.append(r['maximum'])
  else:
   main=r
   if i<4:controls.append({'name':p['name'],'n':len(r['cipher']),**r['control']})
   else:
    for row in sorted(r['restarts'],key=lambda r:r['score'],reverse=True):
     strings=[];word='';es=set(r['ends'])
     for k,x in enumerate(row['plain']):
      word+=trans[x]
      if k in es:strings.append(word);word=''
     if word:strings.append(word)
     outputs.append({'page':p['name'],'restart':row['restart'],'map':row['map'],'canonical_runes':row['plain'],'score':row['score'],'transliteration':' '.join(strings)})
 if i>=4:
  count=sum(s>=main['maximum'] for s in nullmax);actual.append({'page':p['name'],'runes':len(p['cipher']),'tokens':len(main['tokens']),'maximum':main['maximum'],'mean_token_score':main['mean_token_score'],'null_maxima':nullmax,'exceedances':count,'tail':(1+count)/20,'selected_restart':main['best_restart']})
summary={'controls':controls,'actual':actual,'searches':nsearch,'restarts':nsearch*24,'nominal_sa_proposals':nsearch*24*30000,'total_swap_evaluations_including_hill':evals,'accepted_sa':accepted,'independent_full_score_max_absolute_error':maxerr,'search_seconds':seconds,'null_generation_seconds':nulltimes,'null_attempts':attempts,'null_cap_failures':0,'outputs':len(outputs)}
(O/'summary.json').write_text(json.dumps(summary,indent=2));(O/'actual-full-alternatives.json').write_text(json.dumps(outputs,indent=2));print(json.dumps(summary,indent=2))
