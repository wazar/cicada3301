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
