import pathlib,json,math,random,hashlib,zlib,collections,datetime
O=pathlib.Path(__file__).resolve().parent; R=O.parents[2]; rng=random.Random(33010101)
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def check():
 assert not (O.parent/'STOP').exists(),'STOP'
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00'),'deadline'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(p,a):
 a=a.copy();c=[]
 for x in p:c.append(a[x]);a[x],a[0]=a[0],a[x]
 return c
 defnever=0
def dec(c,a):
 a=a.copy();p=[]
 for x in c:
  k=a.index(x);p.append(k);a[k],a[0]=a[0],a[k]
 return p
def canon(c):return [0]+dec(c[1:],[c[0]]+[x for x in range(29) if x!=c[0]])
def metric(c,detail=False):
 p=canon(c);n=len(p);cut=2*n//3;ct=collections.Counter(x for x in p[1:cut] if x);den=sum(ct.values())+28
 pred=[(ct[x]+1)/den for x in range(1,29)]
 score=sum(math.log(28*pred[x-1]) for x in p[cut:] if x)
 out={'score':score,'cut':cut,'prefix_counts':[ct[x] for x in range(29)],'suffix_nonanchor':sum(x!=0 for x in p[cut:]),'prediction_nonanchor':pred}
 if detail:
  counts=collections.Counter(p);probs=[v/n for v in counts.values()];pairs=collections.Counter(zip(p,p[1:]));left=collections.Counter(p[:-1]);right=collections.Counter(p[1:]);m=n-1
  out.update(decoded=p,reencryption_exact=enc(p[1:],[c[0]]+[x for x in range(29) if x!=c[0]])==c[1:],entropy=-sum(v*math.log2(v) for v in probs),ioc_times_n=sum(v*(v-1) for v in counts.values())/(n-1),min_distinct32=min(len(set(p[i:i+32])) for i in range(n-31)),zlib_bytes_per_rune=len(zlib.compress(bytes(p)))/n,lag_mi=sum(v/m*math.log2(v*m/(left[a]*right[b])) for (a,b),v in pairs.items()),nonenglish_lm=None,nonenglish_lm_reason='No language-model instrument; exact rune outputs retained')
 return out
def null(c):
 out=[rng.randrange(29)]
 for i in range(1,len(c)):
  if c[i]==c[i-1]:out.append(out[-1])
  else:
   v=rng.randrange(28);out.append(v+(v>=out[-1]))
 return out
def tail(x,ns):return (1+sum(v>=x for v in ns))/(len(ns)+1)
check();controls=[];files=[]
for name in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229','0_welcome','jpg107-167','p56_an_end','p57_parable']:
 f=R/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');p=[(ABC.index(x)+1)%29 for x in f.read_text() if x in ABC];files.append({'path':str(f.relative_to(R)),'sha256':sha(f)})
 for mode in ['original','shuffled']:
  q=p.copy()
  if mode=='shuffled':rng.shuffle(q)
  a=list(range(29));rng.shuffle(a);c=enc(q,a);assert dec(c,a)==q;assert all((c[i]==c[i-1])==(q[i]==0) for i in range(1,len(c)))
  d=canon(c);mapping={};rev={}
  for x,y in zip(q[1:],d[1:]):
   assert mapping.setdefault(x,y)==y and rev.setdefault(y,x)==x
  assert mapping.get(0,0)==0
  m=metric(c,True);assert m['reencryption_exact'];ns=[metric(null(c))['score'] for _ in range(199)]
  controls.append({'name':name,'mode':mode,'source':q,'cipher':c,'initial_alphabet':a,'relabel_map':mapping,'result':m,'null_scores':ns,'p':tail(m['score'],ns)})
check();f=R/'audit/parallel-01/inputs/dataset.json';D=json.loads(f.read_text());pages=[p for p in D['pages'] if p['original_page'] in [0,1,3,7,17]];assert len(pages)==5
real=[]
for p in pages:
 c=p['indices'];m=metric(c,True);assert m['reencryption_exact'];real.append({'page':p['original_page'],'cipher':c,'source_char_positions':p['source_char_positions'],'result':m})
nulls=[]
for i in range(999):
 if i%50==0:check()
 nulls.append([metric(null(p['indices']))['score'] for p in pages])
score=sum(x['result']['score'] for x in real);p=tail(score,[sum(x) for x in nulls])
for j,x in enumerate(real):x['p']=tail(x['result']['score'],[y[j] for y in nulls])
out={'strategy':'outside-box-v1','seed':33010101,'input':{'path':str(f.relative_to(R)),'sha256':sha(f)},'source_files':files,'controls':controls,'real':real,'null_scores':nulls,'aggregate_score':score,'aggregate_p':p,'counts':{'real_pages':5,'real_recipe_representatives':5,'real_null_pages':999*5,'controls':len(controls),'control_null_pages':199*len(controls)},'control_detected_001':sum(x['p']<=.01 for x in controls)}
(O/'j01-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['controls','real','null_scores','source_files']}));print(json.dumps({'real':[{'page':x['page'],'score':x['result']['score'],'p':x['p']} for x in real],'controls':[{'name':x['name'],'mode':x['mode'],'p':x['p']} for x in controls]}))
