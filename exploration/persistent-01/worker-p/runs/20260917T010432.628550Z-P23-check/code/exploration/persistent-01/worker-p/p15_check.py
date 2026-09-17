import gzip,json,math,random,sys
import p15 as p
load=lambda n:json.load(gzip.open(p.O/(n+'.json.gz'),'rt'))
def check_path(c,ends,a,key):
 score=0.;ctx=(29,29);j=0;iv=0;soft=0
 for i,(plain,accept) in enumerate(zip(a['plain'],a['accepted'])):
  for q in range(j,accept):
   z=plain^key[q]
   if z in (29,30,31):iv+=1
   else:assert i>0 and z==c[i-1];soft+=1;score+=math.log(.83)
  assert plain^key[accept]==c[i] and c[i]<29
  if i and c[i]==c[i-1]:score+=math.log(.17)
  ctx,w=p.lm.extend(ctx,plain,i in ends);score+=w;j=accept+1
 assert j==a['used'];return score,iv,soft
rows=[]
for i in range(4):
 f=load('fixture-'+str(i));key=next(c['key'] for c in p.CELLS if c['id']==f['cell_id']);truth=dict(plain=f['plain'],accepted=[e[-1]['draw'] for e in f['encoder']['events']],used=f['encoder']['used']);score,iv,soft=check_path(f['encoder']['cipher'],set(f['ends']),truth,key)
 raw=(p.ROOT/f['source']['path']).read_text();assert [p.parse(raw[j])[0][0] for j in f['source']['character_offsets']]==f['plain']
 r=load('control-'+str(i));trace=[]
 for row in r['rows']:
  k=next(c['key'] for c in p.CELLS if c['id']==row['id'])
  for a in row['decode']['alternatives']:
   sc,*_=check_path(r['cipher'],set(r['ends']),a,k);assert abs(sc-a['total'])<1e-10
 for a in r['top16']['alternatives']:
  k=next(c['key'] for c in p.CELLS if c['id']==r['rows'][0]['id']);sc,*_=check_path(r['cipher'],set(r['ends']),a,k);assert abs(sc-a['total'])<1e-10
 rows.append(dict(control=i,truth_total=score,invalid=iv,soft=soft,truth_probability_log=iv*0+soft*math.log(.83)+sum(x==y for x,y in zip(r['cipher'],r['cipher'][1:]))*math.log(.17)))
if sys.argv[1]=='actual':
 # Independent support-only inverse; does not call production transition helper or LM.
 checks=[];rng=random.Random(331519)
 for pid in [0,17]:
  r=load('real-'+str(pid));real=r['cipher']
  for rep in [-1]+list(range(19)):
   name='real-'+str(pid) if rep==-1 else 'null-'+str(pid)+'-'+str(rep);r=load(name)
   if rep!=-1:
    sh=[rng.randrange(29)]
    for i in range(1,len(real)):
     if real[i]==real[i-1]:sh.append(sh[-1])
     else:v=rng.randrange(28);sh.append(v+(v>=sh[-1]))
    assert sh==r['cipher']
   for row in r['rows']:
    key=next(c['key'] for c in p.CELLS if c['id']==row['id']);states={0};history=[]
    for i,v in enumerate(r['cipher']):
     nxt=set()
     for start in states:
      # Scan all plaintext symbols independently, stopping at first compulsory acceptance.
      for plain in range(29):
       q=start
       while q<len(key):
        z=plain^key[q]
        if z<29:
         if z==v:nxt.add(q+1)
         if i==0 or z!=r['cipher'][i-1]:break
        q+=1
     states=nxt;history.append(len(states))
     if not states:break
    assert bool(states)==row['decode']['feasible']
    if not states:assert len(history)-1==row['decode']['first_failed']
    for a in row['decode']['alternatives']:
     sc,*_=check_path(r['cipher'],set(r['ends']),a,key);assert abs(sc-a['total'])<1e-10
    checks.append(dict(name=name,cell=row['id'],feasible=bool(states),first_failed=None if states else len(history)-1,states=history))
   if r['top16']:
    key=next(c['key'] for c in p.CELLS if c['id']==r['rows'][0]['id'])
    for a in r['top16']['alternatives']:
     sc,*_=check_path(r['cipher'],set(r['ends']),a,key);assert abs(sc-a['total'])<1e-10
  print('verified',pid,flush=True)
 p.dump('actual-check',checks)
p.dump('control-check',rows);print(json.dumps(dict(status='PASS',controls=rows)),flush=True)
