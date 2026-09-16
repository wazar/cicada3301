import sys,pathlib,json,math,random,collections,hashlib,subprocess,time,datetime,gzip
D=pathlib.Path('exploration/persistent-01/worker-p/P05');B=D.parents[1];ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';T=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA'];AL='BCDFGHJLMNPRSTWXY';NAMES=['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229','0_welcome','jpg107-167','p56_an_end','p57_parable']
def guard():
 assert not (B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def prepare():
 sources=[]
 for name in NAMES:
  p=pathlib.Path('audit/parallel-01/reference/sources')/('solved_'+name+'.txt');raw=p.read_text();seq=[];rows=[]
  for pos,c in enumerate(raw):
   if c not in ABC:continue
   r=ABC.index(c)
   for off,ch in enumerate(T[r]):
    row=dict(source_char=pos,rune=r,offset=off,char=ch,keep=ch in AL,index=len(seq) if ch in AL else None);rows.append(row)
    if ch in AL:seq.append(AL.index(ch))
  sources.append(dict(name=name,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),seq=seq,map=rows,split='train' if len(sources)<5 else 'held'))
 un=collections.Counter(v for s in sources[:5] for v in s['seq']);bi=collections.Counter(z for s in sources[:5] for z in zip(s['seq'],s['seq'][1:]));tr=collections.Counter(z for s in sources[:5] for z in zip(s['seq'],s['seq'][1:],s['seq'][2:]));bl=collections.Counter(a for a,b in bi for _ in range(bi[a,b]));tl=collections.Counter()
 for (a,b,c),n in tr.items():tl[a,b]+=n
 u=[(un[i]+.5)/(sum(un.values())+8.5) for i in range(17)];bb=[[(bi[a,b]+4*u[b])/(bl[a]+4) for b in range(17)] for a in range(17)];tt=[math.log((tr[a,b,c]+4*bb[b][c])/(tl[a,b]+4)) for a in range(17) for b in range(17) for c in range(17)];model=dict(u=[math.log(v) for v in u],tri=tt,sources=sources,alphabet=AL,train_total=sum(un.values()))
 (D/'model.json').write_text(json.dumps(model));(D/'model.txt').write_text(' '.join(map(str,model['u']+tt)));return model
def score(m,c,cut):
 p=[m[v] for v in c];tr=MODEL['tri'];u=MODEL['u'];terms=[u[p[i]] if i<2 else tr[(p[i-2]*17+p[i-1])*17+p[i]] for i in range(len(p))];return dict(decoded=p,prefix_total=sum(terms[:cut]),suffix_conditional=sum(terms[cut:])/(len(p)-cut),suffix_gain=sum(terms[i]-u[p[i]] for i in range(cut,len(p)))/(len(p)-cut),terms=terms)
def encode(plain,seed):
 rng=random.Random(seed);sizes=[1]*17;freq=[math.exp(x) for x in MODEL['u']]
 for i in range(12):k=max(range(17),key=lambda j:freq[j]/sizes[j]);sizes[k]+=1
 outputs=list(range(29));rng.shuffle(outputs);bins=[];book=[None]*29;off=0
 for letter,size in enumerate(sizes):
  group=outputs[off:off+size];bins.append(group);off+=size
  for r in group:book[r]=letter
 cipher=[];rejected=0;blocked=0
 for letter in plain:
  group=bins[letter];v=rng.choice(group)
  if cipher and v==cipher[-1]:
   if len(group)>1 and rng.random()<.83:v=rng.choice([x for x in group if x!=cipher[-1]]);rejected+=1
   elif len(group)==1:blocked+=1
  cipher.append(v)
 assert [book[v] for v in cipher]==plain
 return dict(cipher=cipher,truth=book,plain=plain,sizes=sizes,rejected=rejected,unary_repeat_events=blocked,seed=seed)
def runpacket(c,label,seed,truth=None):
 guard();cut=2*len(c)//3;f=D/(label+'-cipher.txt');f.write_text(f'{len(c)} {cut}\n'+' '.join(map(str,c)));ts=time.monotonic();p=subprocess.run([str(D/'search'),str(D/'model.txt'),str(f),str(seed)],capture_output=True,text=True);(D/(label+'-stdout.txt')).write_text(p.stdout);(D/(label+'-stderr.txt')).write_text(p.stderr);assert p.returncode==0;rows=json.loads(p.stdout)
 for r in rows:
  assert set(r['map'])==set(range(17));ss=score(r['map'],c,cut);assert abs(ss['prefix_total']-r['score'])<1e-7;r.update(ss);r['text']=''.join(AL[v] for v in ss['decoded'])
 best=max(range(8),key=lambda i:rows[i]['prefix_total']);out=dict(label=label,seed=seed,cipher=c,cut=cut,seconds=time.monotonic()-ts,exit_code=p.returncode,selected=best,alternatives=rows,repeats=sum(a==b for a,b in zip(c,c[1:])),distinct=len(set(c)))
 if truth is not None:
  s=score(truth['truth'],c,cut);plain=truth['plain'];pred=rows[best]['decoded'];used=sorted(set(c));out.update(control=truth,truth_score=s,accuracy=sum(a==b for a,b in zip(plain,pred))/len(c),suffix_accuracy=sum(a==b for a,b in zip(plain[cut:],pred[cut:]))/(len(c)-cut),observable_mapping_accuracy=sum(truth['truth'][r]==rows[best]['map'][r] for r in used)/len(used),unused_runes=sorted(set(range(29))-set(used)),wrong_positions=[i for i,(a,b) in enumerate(zip(plain,pred)) if a!=b],truth_rank=1+sum(r['prefix_total']>s['prefix_total']+1e-9 for r in rows))
 with gzip.open(D/(label+'.json.gz'),'wt') as f:json.dump(out,f)
 print(json.dumps(dict(label=label,seconds=out['seconds'],accuracy=out.get('accuracy'),suffix_accuracy=out.get('suffix_accuracy'),truth_rank=out.get('truth_rank'),held_gain=rows[best]['suffix_gain'])),flush=True);return out
MODE=sys.argv[1];guard()
if MODE=='pilot':
 ver=subprocess.check_output(['c++','--version'],text=True);(D/'compiler-version.txt').write_text(ver);p=subprocess.run(['c++','-O3','-std=c++17',str(D/'search.cpp'),'-o',str(D/'search')],capture_output=True,text=True);(D/'compile.json').write_text(json.dumps(dict(command=p.args,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)));assert p.returncode==0;MODEL=prepare();out=[]
 for i,s in enumerate(MODEL['sources'][5:]):
  t=encode(s['seq'],130105+i*100);out.append(runpacket(t['cipher'],f'control-{i}-0',130205+i*100,t))
 (D/'pilot.json').write_text(json.dumps(dict(controls=[{k:v for k,v in r.items() if k not in ['alternatives','truth_score','control','cipher']} for r in out],binary_sha256=hashlib.sha256((D/'search').read_bytes()).hexdigest()),indent=2))
elif MODE=='full':
 MODEL=json.loads((D/'model.json').read_text());controls=[]
 for i,s in enumerate(MODEL['sources'][5:]):
  with gzip.open(D/f'control-{i}-0.json.gz','rt') as f:controls.append(json.load(f))
  for rep in range(1,4):
   t=encode(s['seq'],130105+i*100+rep);controls.append(runpacket(t['cipher'],f'control-{i}-{rep}',130205+i*100+rep,t))
 dataset=json.loads((B/'worker-f/F06-maps.json').read_text());real=[];null=[];samplers=[]
 def repeats(c):return sum(a==b for a,b in zip(c,c[1:]))
 def shuffled(c,seed):
  rng=random.Random(seed);z=c[:];n=len(z);target=100*n;accepted=[];attempts=0
  while len(accepted)<target and attempts<2000*n:
   attempts+=1;i=rng.randrange(n);j=rng.randrange(n-1);j+=j>=i
   if z[i]==z[j]:continue
   edges={x for x in [i-1,i,j-1,j] if 0<=x<n-1};before=sum(z[x]==z[x+1] for x in edges);z[i],z[j]=z[j],z[i];after=sum(z[x]==z[x+1] for x in edges)
   if before==after:accepted.append([i,j])
   else:z[i],z[j]=z[j],z[i]
  assert collections.Counter(z)==collections.Counter(c) and repeats(z)==repeats(c)
  return z,dict(seed=seed,attempts=attempts,accepted_swaps=accepted,accepted_target=target,reached_target=len(accepted)==target,changed_positions=sum(a!=b for a,b in zip(c,z)))
 for page in [0,17]:
  c=next(m['indices'] for m in dataset if m['page']==page);r=runpacket(c,f'real-{page}',140000+page*1000);real.append(r);nn=[]
  for rep in range(19):
   guard();z,samp=shuffled(c,150000+page*1000+rep);samp.update(page=page,rep=rep);samplers.append(samp);nn.append(runpacket(z,f'null-{page}-{rep}',140001+page*1000+rep))
  null.append(nn)
 sys.path.insert(0,str(pathlib.Path('liber-primus/src').resolve()));from lp.score import Quadgram
 q=Quadgram();cs=[]
 for c in controls:
  true=c['truth_score'];chosen=c['alternatives'][c['selected']];truthtext=''.join(AL[v] for v in c['control']['plain']);cs.append(dict(label=c['label'],n=len(c['cipher']),cut=c['cut'],accuracy=c['accuracy'],suffix_accuracy=c['suffix_accuracy'],observable_mapping_accuracy=c['observable_mapping_accuracy'],unused_runes=c['unused_runes'],truth_rank=c['truth_rank'],truth_prefix=true['prefix_total'],found_prefix=chosen['prefix_total'],truth_held_gain=true['suffix_gain'],found_held_gain=chosen['suffix_gain'],repeats=c['repeats'],repeat_rate=c['repeats']/(len(c['cipher'])-1),plaintext_repeats=repeats(c['control']['plain']),unary_repeat_events=c['control']['unary_repeat_events'],suppressed_events=c['control']['rejected'],legacy_correct_plain_score=q.score_norm(truthtext)))
 rs=[]
 for page,r,nn in zip([0,17],real,null):
  chosen=r['alternatives'][r['selected']];ns=[x['alternatives'][x['selected']]['suffix_gain'] for x in nn];rs.append(dict(page=page,n=len(r['cipher']),cut=r['cut'],repeats=r['repeats'],selected=r['selected'],held_gain=chosen['suffix_gain'],held_conditional=chosen['suffix_conditional'],null_held_gains=ns,descriptive_tail=(1+sum(v>=chosen['suffix_gain'] for v in ns))/20,decoded_text=chosen['text'],mapping=chosen['map']))
 with gzip.open(D/'samplers.json.gz','wt') as f:json.dump(samplers,f)
 summary=dict(controls=cs,real=rs,optimizer=dict(restarts=8,proposals_per_restart=5000,packet_count=56,total_nominal_proposals=56*40000),sampler_summary=[{k:v for k,v in s.items() if k!='accepted_swaps'}|dict(accepted=len(s['accepted_swaps'])) for s in samplers],tail_interpretation='Exploratory MCMC comparisons, uniform conditional mixing not proved. Not calibrated p values. Search controls constrain all real conclusions.');(D/'results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(dict(control_suffix_accuracy=[c['suffix_accuracy'] for c in cs],truth_ranks=[c['truth_rank'] for c in cs],real=[{k:v for k,v in r.items() if k not in ['decoded_text','mapping','null_held_gains']} for r in rs]),indent=2))
else:raise ValueError(MODE)
