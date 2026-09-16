import kernel as k
import pathlib,json,gzip,collections,random,math,itertools,hashlib
O=k.O;M=k.M
load=lambda p:json.loads(p.read_text())
def read(p):
 with gzip.open(p,'rt') as f:return json.load(f)
def enc(plain,key,sign,seed):
 rng=random.Random(seed);j=0;out=[];events=[]
 for p in plain:
  rejected=[];burned=[];coins=[]
  while True:
   if j>=len(key):raise ValueError('finite key exhausted')
   candidate=(p-sign*key[j])%29
   if out and candidate==out[-1]:
    u=rng.random();coins.append(u)
    if u<.83:rejected.append(j);burned.append(j+1);j+=2;continue
   out.append(candidate);events.append({'rejected':rejected,'burned':burned,'accepted':j,'random_decisions':coins});j+=1;break
 return out,events,j

def reach(c,plain,key,sign,stride):
 states={0};counts=[]
 for i,(cipher,p) in enumerate(zip(c,plain)):
  nxt=set()
  for start in states:
   allowed=True
   for a in range(start,len(key),stride):
    if not allowed:break
    proposed=(p-sign*key[a])%29
    if proposed==cipher:nxt.add(a+1)
    allowed=i>0 and proposed==c[i-1]
  states=nxt;counts.append(len(states))
  if not states:return {'reachable':False,'first_failed_position':i,'state_counts':counts,'terminal_used':[]}
 return {'reachable':True,'first_failed_position':None,'state_counts':counts,'terminal_used':sorted(states)}
def replay(c,a,cell,ends,stride=2):
 j=0;totalreject=0
 for i,(cipher,p,t) in enumerate(zip(c,a['plain'],a['reject_counts'])):
  assert i>0 or t==0;accepted=j+stride*t;assert accepted<len(cell['key']);tested=list(range(j,accepted,stride));burned=[v for v in range(j,accepted) if v not in tested]
  assert all((p-cell['sign']*cell['key'][v])%29==c[i-1] for v in tested);assert (p-cell['sign']*cell['key'][accepted])%29==cipher
  if 'key_walk' in a:
   w=a['key_walk'][i];assert w=={'input_index':i,'key_start':j,'rejected':tested,'burned':burned,'accepted':accepted,'key_after':accepted+1}
  j=accepted+1;totalreject+=t
 assert j==a['used'] and j<=len(cell['key']);assert j-len(c)==stride*totalreject
 rep=sum(x==y for x,y in zip(c,c[1:]));score=k.lm.score(a['plain'],ends)+(totalreject*math.log(.83)+rep*math.log(.17))/(len(c)+len(ends));assert abs(score-a['score'])<1e-12
 return rep*math.log(.17)
def main():
 keys=load(M/'keys.json');assert len(keys)==4;primes=[];v=2
 while len(primes)<1024:
  if all(v%p for p in primes if p*p<=v):primes.append(v)
  v+=1
 phi=[sum(math.gcd(j,n)==1 for j in range(1,n+1))%29 for n in range(1,1025)]
 for cell in keys:assert len(cell['key'])==1024 and cell['key']==([((p-1)%29) for p in primes] if cell['family']=='prime_minus_one' else phi)
 cells={c['id']:c for c in keys};ctls=load(M/'controls.json');up=load(M/'upstream-controls.json');upchecks=0
 assert hashlib.sha256((k.R/up['path']).read_bytes()).hexdigest()==up['sha256']
 for f in up['controls']:
  c,e,u=enc(f['plain'],f['key'],-1,f['seed']);assert c==f['cipher'] and e==f['events'] and u==f['used'];upchecks+=1
 stress=k.brute([0]*4,{1,3},[0]*16,1,2);got=k.ns['decode']([0]*4,{1,3},{'key':[0]*16,'sign':1},2,16);assert len(stress)>16 and len(got['alternatives'])==16;assert all(abs(a['joint_total']-b['score'])<1e-12 for a,b in zip(got['alternatives'],stress))
 ctlout=[];burnviolations=0;paths=0
 for row in ctls:
  f=row['fixture'];cell=f['cell'];assert cell==cells[cell['id']];c,e,u=enc(f['plain'],cell['key'],cell['sign'],f['seed']);assert c==f['cipher'] and e==f['events'] and u==f['used']
  usedevents=sum(len(v['rejected']) for v in e);assert u==len(c)+2*usedevents
  for i,event in enumerate(e):
   for j in event['burned']:burnviolations+=(f['plain'][i]-cell['sign']*cell['key'][j])%29!=c[i-1]
  r2=reach(c,f['plain'],cell['key'],cell['sign'],2);r1=reach(c,f['plain'],cell['key'],cell['sign'],1);assert r2==row['reachability_stride2'] and r1==row['reachability_stride1']
  for a in row['truth_correctkey_top16']['alternatives']:replay(c,a,cell,set(f['ends']));paths+=1
  a=row['truth_correctkey_top16']['alternatives'][0];assert a['plain']==f['plain'] and a['reject_counts']==[len(x['rejected']) for x in e] and a['used']==u
  ctlout.append({'name':f['name'],'length':len(c),'rejections':usedevents,'used':u,'stride1':r1,'stride2':r2})
 cal=load(M/'calibration.json');real=load(M/'real.json');byname={f['fixture']['name']:f['fixture'] for f in ctls};rows=[];nullcounts=0
 for row in cal['results']:
  original=read(M/'evidence'/(row['name']+'.json.gz'));c=original['cipher'];ends=set(original['ends']);reps=sum(x==y for x,y in zip(c,c[1:]));term=reps*math.log(.17);assert row['score']==original['score']
  for candidate in original['rows']:
   a=candidate['decode']['alternatives'][0];assert abs(replay(c,a,cells[candidate['id']],ends)-term)<1e-12;paths+=1
  for a in original['top16']['alternatives']:replay(c,a,cells[original['rows'][0]['id']],ends);paths+=1
  for null in row['null']:
   r=read(M/'evidence'/(null['name']+'.json.gz'));cc=r['cipher'];assert r['ends']==original['ends'] and len(cc)==len(c);assert [a==b for a,b in zip(cc,cc[1:])]==[a==b for a,b in zip(c,c[1:])];assert null['score']==r['score'];assert null['repeat_count']==reps;nullcounts+=1
  tail=(1+sum(v['score']>=original['score'] for v in row['null']))/(len(row['null'])+1);assert tail==row['tail'];out={'name':row['name'],'conditional_tail':tail,'original_score':original['score'],'repeat_count':reps,'repeat_likelihood_total':term}
  if row['name'].startswith('real-'):
   pid=int(row['name'].split('-')[1]);old=next(z for z in real if z['page']==pid);assert old['score']==original['score'] and old['best_id']==original['rows'][0]['id'];assert pid in [0,17]
   oldrep=[z['repeats'] for z in old['null']];out.update(original_shuffle_tail=old['tail'],shuffle_repeat_range=[min(oldrep),max(oldrep)],shuffle_repeat_mean=sum(oldrep)/len(oldrep),same_real_output_sha256=hashlib.sha256((M/'evidence'/(row['name']+'.json.gz')).read_bytes()).hexdigest())
  rows.append(out)
 assert [r['conditional_tail'] for r in rows if r['name'].startswith('real-')]==[.26,.61]
 out={'upstream_saved_encoder_fixtures_reproduced':upchecks,'key_buffers_independently_verified':4,'constant_key_top16_stress_paths':len(stress),'controls':ctlout,'burned_draws_failing_skip1_test':burnviolations,'retained_paths_replayed':paths,'conditional_null_masks_checked':nullcounts,'calibration':rows,'all_search_files_counted_only':len(list((M/'evidence').glob('*.json.gz')))};(O/'evidence-findings.json').write_text(json.dumps(out,indent=2));print(json.dumps({kk:vv for kk,vv in out.items() if kk!='controls'}))
if __name__=='__main__':main()
