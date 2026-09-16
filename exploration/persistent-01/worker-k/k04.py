import k01 as k,json,numpy as np
O=k.O;R=k.R;rng=np.random.default_rng(33010114)
NAMES=['global','initial','terminal','forward_cap3','reverse_cap3','forward_parity'];DIMS=[1,2,2,4,4,2]
def schedules(n,words):
 out=np.zeros((6,n),dtype=int);seen=np.zeros(n,dtype=int)
 for w in words:
  a,b=w['start'],w['end'];i=np.arange(b-a);out[1,a:b]=i==0;out[2,a:b]=i==b-a-1;out[3,a:b]=np.minimum(i,3);out[4,a:b]=np.minimum(b-a-1-i,3);out[5,a:b]=i%2;seen[a:b]+=1
 assert np.all(seen==1);return out

def score(cs,ss,detail=False):
 vs=np.zeros(6);ts=np.zeros(6);fits=[]
 for m,dim in enumerate(DIMS):
  ct=np.ones((dim,29))
  for c,s in zip(cs,ss):
   a=len(c)//2;ct+=np.bincount(s[m,:a]*29+c[:a],minlength=dim*29).reshape(dim,29)
  q=ct/ct.sum(axis=1)[:,None];pages=[]
  for c,s in zip(cs,ss):
   n=len(c);a=n//2;b=3*n//4;_,lam=k.fit0(c[:a]);lp=np.log(q[s[m,1:],c[1:]])+np.where(c[1:]==c[:-1],np.log(lam),0)-np.log(1+(lam-1)*q[s[m,1:],c[:-1]])
   v=float(lp[a-1:b-1].sum());t=float(lp[b-1:].sum());vs[m]+=v;ts[m]+=t
   if detail:pages.append({'train_stop':a,'validation_stop':b,'lambda':lam,'validation_logprob':v,'test_logprob':t})
  if detail:fits.append({'schedule':NAMES[m],'probabilities':q.tolist(),'pages':pages})
 best=int(np.argmax(vs));r={'selected':NAMES[best],'validation_gain':(vs-vs[0]).tolist(),'test_gain':(ts-ts[0]).tolist(),'statistic':float(ts[best]-ts[0])}
 if detail:r['fitted']=fits
 return r

def evaluate(cs,ss,B):
 r=score(cs,ss,True);ns=[]
 for i in range(B):
  if i%25==0:k.check()
  shifts=[int(rng.integers(len(c))) for c in cs];row=score(cs,[np.roll(s,t,axis=1) for s,t in zip(ss,shifts)]);row['shifts']=shifts;ns.append(row)
 r['null']=ns;r['p']=(1+sum(x['statistic']>=r['statistic'] for x in ns))/(B+1);return r

def parse(raw):
 positions=[i for i,x in enumerate(raw) if x in k.ABC];p=[k.ABC.index(raw[i]) for i in positions];starts=[0]
 for j,(a,b) in enumerate(zip(positions,positions[1:])):
  if raw[a+1:b].strip('\r\n'):starts.append(j+1)
 return p,[{'start':a,'end':b} for a,b in zip(starts,starts[1:]+[len(p)])]

k.check();prior=json.loads((O/'k02-results.json').read_text());sources=[]
for x in prior['sources']:
 f=R/'audit/parallel-01/reference/sources'/('solved_'+x['name']+'.txt');p,w=parse(f.read_text());assert p==x['indices'];sources.append({'name':x['name'],'sha256':k.sha(f),'indices':p,'words':w})
controls=[]
for panel,src in [('first5',sources[:5]),('last4',sources[5:])]:
 for register in ['natural','shuffled']:
  ps=[np.array(s['indices']) for s in src];ss=[schedules(len(p),s['words']) for p,s in zip(ps,src)]
  if register=='shuffled':ps=[rng.permutation(p) for p in ps]
  for model in [0,1,3,5]:
   keys=np.array([rng.permutation(29) for _ in range(DIMS[model])]);cs=[keys[s[model],p] for p,s in zip(ps,ss)];r=evaluate(cs,ss,99);row={'panel':panel,'register':register,'true_model':NAMES[model],'source_indices':[p.tolist() for p in ps],'schedules':[s.tolist() for s in ss],'keys':keys.tolist(),'ciphers':[c.tolist() for c in cs],'result':r};controls.append(row);print(panel,register,NAMES[model],r['selected'],r['statistic'],r['p'],flush=True)
f=R/'exploration/persistent-01/worker-f/F06-maps.json';maps=[m for m in json.loads(f.read_text()) if m['page'] in [0,1,3,7,17]];assert len(maps)==5
for m in maps:
 p=next(p for p in prior['real'] if p['original_page']==m['page']);assert p['indices']==m['indices'];assert p['source_char_positions']==m['source_char_positions']
cs=[np.array(m['indices']) for m in maps];ss=[schedules(len(c),m['words']) for c,m in zip(cs,maps)];r=evaluate(cs,ss,399)
stabilizers=[{name:[shift for shift in range(len(c)) if np.array_equal(np.roll(s[j],shift),s[j])] for j,name in enumerate(NAMES)} for c,s in zip(cs,ss)]
out={'seed':33010114,'source_map_sha256':k.sha(f),'input_hash':prior['input_hash'],'map_hash':prior['map_hash'],'sources':sources,'controls':controls,'real':[{'page':m['page'],'indices':m['indices'],'source_char_positions':m['source_char_positions'],'words':m['words'],'schedules':s.tolist(),'metrics':k.metrics(c)} for m,c,s in zip(maps,cs,ss)],'result':r,'stabilizers':stabilizers,'counts':{'control_fits':16*100*6,'real_fits':400*6,'decoded_candidates':0,'path_expansions':0}};(O/'k04-results.json').write_text(json.dumps(out));print('REAL',r['selected'],r['statistic'],r['p'])
