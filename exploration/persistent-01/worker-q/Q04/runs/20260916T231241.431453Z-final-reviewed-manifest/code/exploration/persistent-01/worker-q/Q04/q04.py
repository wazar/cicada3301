import pathlib,json,gzip,math,random,hashlib,subprocess,sys,time,datetime,collections,shutil
R=pathlib.Path(__file__).parent;P=R.parents[1]/'worker-p/P05';MODEL=json.loads((P/'model.json').read_text())
def gate():
 assert not (R.parents[1]/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(name,data):
 p=R/name
 if name.endswith('.gz'):
  with gzip.open(p,'wt') as f:json.dump(data,f)
 else:p.write_text(json.dumps(data,indent=2))
def terms(mapping,cipher,cut):
 assert len(mapping)==29 and set(mapping)==set(range(17));counts=collections.Counter(mapping);decoded=[mapping[r] for r in cipher];lm=[];em=[]
 for i,(r,a) in enumerate(zip(cipher,decoded)):
  lm.append(MODEL['u'][a] if i<2 else MODEL['tri'][(decoded[i-2]*17+decoded[i-1])*17+a]);k=counts[a]
  if not i or k==1 or decoded[i-1]!=a:prob=1/k
  elif cipher[i-1]==r:prob=.17/k
  else:prob=1/k+.83/(k*(k-1))
  em.append(math.log(prob))
 return {'decoded':decoded,'lm_terms':lm,'emission_terms':em,'prefix_lm':sum(lm[:cut]),'prefix_emission':sum(em[:cut]),'prefix_joint':sum(lm[:cut])+sum(em[:cut]),'suffix_lm':sum(lm[cut:]),'suffix_emission':sum(em[cut:]),'suffix_joint':sum(lm[cut:])+sum(em[cut:]),'full_joint':sum(lm)+sum(em)}
def generate(mapping,n,seed):
 src=random.Random(seed);emit=random.Random(seed+1);plain=[];cipher=[];draws=[];bins=[[r for r,a in enumerate(mapping) if a==i] for i in range(17)]
 for i in range(n):
  logp=MODEL['u'] if i<2 else MODEL['tri'][(plain[-2]*17+plain[-1])*17:(plain[-2]*17+plain[-1]+1)*17];u=src.random();cumul=0;a=None
  for j,p in enumerate(logp):
   cumul+=math.exp(p)
   if u<cumul:a=j;break
  assert a is not None;plain.append(a);v=emit.random();group=bins[a];initial=group[int(v*len(group))];r=initial;coin=redraw=None
  if cipher and r==cipher[-1] and len(group)>1:
   coin=emit.random()
   if coin<.83:rest=[v for v in group if v!=r];redraw=emit.random();r=rest[int(redraw*len(rest))]
  cipher.append(r);draws.append({'source_uniform':u,'initial_uniform':v,'initial_rune':initial,'rejection_uniform':coin,'redraw_uniform':redraw,'output':r})
 return {'plain':plain,'cipher':cipher,'draws':draws,'source_seed':seed,'emission_seed':seed+1}
def prepare():
 gate();inputs=[];packets=[];shutil.copyfile(P/'model.txt',R/'model.txt');shutil.copyfile(P/'model.json',R/'model.json')
 for group in range(4):
  path=P/f'control-{group}-0.json.gz';old=json.load(gzip.open(path,'rt'));truth=old['control']['truth'];n=len(old['cipher']);cut=old['cut'];inputs.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});save(f'snapshot-control-{group}-0.json.gz',old)
  held={'label':f'held-{group}','group':group,'type':'held_source','cipher':old['cipher'],'plain':old['control']['plain'],'truth':truth,'cut':cut,'optimizer_seed':old['seed'],'source_packet_sha256':inputs[-1]['sha256'],'old_alternatives':[x['map'] for x in old['alternatives']],'old_accuracy':old['accuracy'],'old_suffix_accuracy':old['suffix_accuracy'],'old_truth_rank':old['truth_rank']}
  gen=generate(truth,n,470400+2*group);model={'label':f'model-{group}','group':group,'type':'model_generated',**gen,'truth':truth,'cut':cut,'optimizer_seed':470800+group,'old_alternatives':held['old_alternatives']};packets.extend([held,model])
 for p in packets:
  assert [p['truth'][r] for r in p['cipher']]==p['plain'];(R/(p['label']+'-cipher.txt')).write_text(f"{len(p['cipher'])} {p['cut']}\n"+' '.join(map(str,p['cipher']))+'\n')
 inputs.extend({'path':str(P/name),'sha256':hashlib.sha256((P/name).read_bytes()).hexdigest()} for name in ['model.json','model.txt']);save('inputs.json',inputs);save('packets.json.gz',packets);print('prepared8frozenpackets')
def kernelcheck():
 gate();packets=json.load(gzip.open(R/'packets.json.gz','rt'));checks=[]
 for p in packets:
  maps=[p['truth']]+p['old_alternatives'];mf=R/(p['label']+'-arithmetic-maps.txt');mf.write_text('\n'.join(' '.join(map(str,m)) for m in maps)+'\n');cmd=[str(R/'search'),str(R/'model.txt'),str(R/(p['label']+'-cipher.txt')),'0',str(mf)];result=subprocess.run(cmd,text=True,capture_output=True,timeout=60,check=True);values=json.loads(result.stdout)
  for mapping,cvalue in zip(maps,values):
   v=terms(mapping,p['cipher'],p['cut']);assert abs(v['prefix_lm']-cvalue['lm'])<1e-8 and abs(v['prefix_emission']-cvalue['emission'])<1e-8 and abs(v['prefix_joint']-cvalue['joint'])<1e-8
  checks.append({'label':p['label'],'maps':maps,'kernel_scores':values,'command':cmd})
 save('kernel-check.json',{'status':'PASS','cases':72,'records':checks});print('72kernel arithmetic cases passed')
def search(stage):
 gate();assert json.loads((R/'kernel-check.json').read_text())['status']=='PASS';packets=json.load(gzip.open(R/'packets.json.gz','rt'));chosen=packets[:2] if stage=='pilot' else packets[2:];summ=[]
 for p in chosen:
  gate();path=R/(p['label']+'-result.json.gz');assert not path.exists(),'do not rerun completed finite budget';cmd=[str(R/'search'),str(R/'model.txt'),str(R/(p['label']+'-cipher.txt')),str(p['optimizer_seed'])];started=time.monotonic();run=subprocess.run(cmd,capture_output=True,text=True,timeout=120);elapsed=time.monotonic()-started;(R/(p['label']+'-stdout.json')).write_text(run.stdout);(R/(p['label']+'-stderr.txt')).write_text(run.stderr);assert run.returncode==0;alts=json.loads(run.stdout);assert len(alts)==8
  for a in alts:
   value=terms(a['map'],p['cipher'],p['cut']);assert abs(value['prefix_joint']-a['score'])<1e-8;assert abs(value['prefix_lm']-a['lm'])<1e-8 and abs(value['prefix_emission']-a['emission'])<1e-8;a.update(value)
  selected=max(range(8),key=lambda i:alts[i]['prefix_joint']);best=alts[selected];truth=terms(p['truth'],p['cipher'],p['cut']);plain=p['plain'];n=len(plain);cut=p['cut'];used=sorted(set(p['cipher']));unused=sorted(set(range(29))-set(used));acc=lambda lo,hi:sum(best['decoded'][i]==plain[i] for i in range(lo,hi))/(hi-lo)
  summary={'label':p['label'],'type':p['type'],'n':n,'cut':cut,'selected':selected,'truth_rank':1+sum(a['prefix_joint']>truth['prefix_joint']+1e-9 for a in alts),'truth_ties':[i for i,a in enumerate(alts) if abs(a['prefix_joint']-truth['prefix_joint'])<=1e-9],'truth_minus_best_prefix':truth['prefix_joint']-best['prefix_joint'],'plaintext_accuracy':acc(0,n),'prefix_accuracy':acc(0,cut),'suffix_accuracy':acc(cut,n),'observable_map_accuracy':sum(best['map'][r]==p['truth'][r] for r in used)/len(used),'full_map_accuracy':sum(a==b for a,b in zip(best['map'],p['truth']))/29,'exact_observed_map':all(best['map'][r]==p['truth'][r] for r in used),'exact_full_map':best['map']==p['truth'],'unused_runes':unused,'nominal_proposals':sum(a['nominal_proposals'] for a in alts),'valid_proposals':sum(a['valid_proposals'] for a in alts),'accepted_proposals':sum(a['accepted'] for a in alts),'seconds':elapsed}
  result={'packet':p,'alternatives':alts,'truth_score':truth,'summary':summary,'command':cmd,'exit_code':run.returncode,'selected_wrong_positions':[i for i,x in enumerate(best['decoded']) if x!=plain[i]]};save(path.name,result);summ.append(summary);print(json.dumps(summary),flush=True)
 save(stage+'-summary.json',summ)
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='prepare':prepare()
 elif mode=='kernelcheck':kernelcheck()
 else:search(mode)
