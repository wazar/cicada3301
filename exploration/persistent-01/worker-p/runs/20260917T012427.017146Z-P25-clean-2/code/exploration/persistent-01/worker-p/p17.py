import pathlib,json,gzip,hashlib,re,random,sys,datetime,subprocess,os
R=pathlib.Path(__file__).resolve().parent;ROOT=R.parents[2];O=R/'P17';sys.path.insert(0,str(ROOT/'liber-primus/src'))
from lp.gematria import keyword_to_indices
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):
 with gzip.open(O/(name+'.json.gz'),'wt') as f:json.dump(x,f)
def provenance():
 from PIL import Image
 import numpy as np
 p=ROOT/'corpus/A-primary-artifacts/pgp/messages/2012-01-second-chance.asc';key=ROOT/'corpus/A-primary-artifacts/pgp/keys/cicada-3301-pubkey.keyserver.ubuntu.com.asc';home=O/'gpg-local';home.mkdir(exist_ok=True);os.chmod(home,0o700)
 args=['/opt/homebrew/bin/gpg','--no-options','--homedir',str(home),'--batch'];i=subprocess.run(args+['--import',str(key)],capture_output=True,text=True);v=subprocess.run(args+['--status-fd','1','--verify',str(p)],capture_output=True,text=True);assert v.returncode==0 and 'VALIDSIG 6D854CD7933322A601C3286D181F01E57A35090F' in v.stdout
 a=np.array(Image.open(O/'hkdgl.png').convert('RGB'));b=np.array(Image.open(O/'mhh4.jpg').convert('RGB'))[360:496,5:368];delta=a.astype(int)-b.astype(int);assert a.shape==b.shape
 dump('provenance',dict(signature=dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),import_exit=i.returncode,verify_exit=v.returncode,status=v.stdout,stderr=v.stderr),image_crop=[5,360,368,496],pixel_exact_fraction=float(np.mean(np.all(a==b,axis=2))),max_channel_difference=int(abs(delta).max()),mean_abs_difference=float(abs(delta).mean()),sources=[dict(path=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in O.iterdir() if f.is_file() and f.suffix in ['.txt','.html','.jpg','.png']],limitations='URL signed; archived image bytes not independently cryptographically signed; museum/Gutenberg corroborate work, not historical code edition'))
 print('provenance PASS',flush=True)
def setup():
 raw=(O/'pg45315.txt').read_bytes().decode('utf-8-sig');assert hashlib.sha256((O/'pg45315.txt').read_bytes()).hexdigest()=='fc9a76619fcb76c58273d7fc9e034108b0d7fffed3780ad5b8226954a12b289a'
 start=raw.index('THE ARGUMENT');end=raw.index('For everything that lives is holy.',start)+len('For everything that lives is holy.');matches=list(re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",raw[start:end]));words=[]
 for m in matches:
  word=m.group();runes=keyword_to_indices(re.sub("['’]",'',word).upper());words.append(dict(span=[start+m.start(),start+m.end()],text=word,runes=runes))
 maps=json.loads((ROOT/'exploration/persistent-01/worker-f/F06-maps.json').read_text());seqs=[[w['end']-w['start'] for w in m['words']] for m in maps];return raw,words,maps,seqs,[len(w['runes']) for w in words]
def automaton(source):
 states=[dict(length=0,link=-1,next={},pos=-1)];last=0
 for pos,x in enumerate(source):
  cur=len(states);states.append(dict(length=states[last]['length']+1,link=0,next={},pos=pos));p=last
  while p!=-1 and x not in states[p]['next']:states[p]['next'][x]=cur;p=states[p]['link']
  if p!=-1:
   q=states[p]['next'][x]
   if states[p]['length']+1==states[q]['length']:states[cur]['link']=q
   else:
    clone=len(states);states.append(dict(length=states[p]['length']+1,link=states[q]['link'],next=states[q]['next'].copy(),pos=states[q]['pos']))
    while p!=-1 and states[p]['next'].get(x)==q:states[p]['next'][x]=clone;p=states[p]['link']
    states[q]['link']=states[cur]['link']=clone
  last=cur
 return states
def scan(seqs,sam):
 best=0
 for seq in seqs:
  s=0;n=0
  for x in seq:
   while s and x not in sam[s]['next']:s=sam[s]['link'];n=sam[s]['length']
   if x in sam[s]['next']:s=sam[s]['next'][x];n+=1
   else:s=0;n=0
   best=max(best,n)
 return best
def matches(seqs,source,n):
 idx={}
 for j in range(len(source)-n+1):idx.setdefault(tuple(source[j:j+n]),[]).append(j)
 return [dict(page_index=pi,page_start=i,source_start=j,length=n) for pi,seq in enumerate(seqs) for i in range(len(seq)-n+1) for j in idx.get(tuple(seq[i:i+n]),[])]
def shuffled(seqs,rng):
 pp=[rng.sample(range(len(x)),len(x)) for x in seqs];return [[x[i] for i in p] for x,p in zip(seqs,pp)],pp
def controls():
 raw,words,maps,seqs,lengths=setup();sam=automaton(lengths);records=[];pi=next(i for i,x in enumerate(seqs) if len(x)>=50)
 for ix,j in enumerate([1000,2000]):
  rng=random.Random(331700+ix);plant=[x[:] for x in seqs];plant[pi][5:45]=lengths[j:j+40];best=scan(plant,sam);hits=matches(plant,lengths,40);assert dict(page_index=pi,page_start=5,source_start=j,length=40) in hits
  plain=[r for w in words[j:j+40] for r in w['runes']];cipher=[(2*r+3)%29 for r in plain];assert [15*(c-3)%29 for c in cipher]==plain
  null=[];perms=[]
  for _ in range(99):sh,pp=shuffled(plant,rng);null.append(scan(sh,sam));perms.append(pp)
  records.append(dict(source_start=j,page_index=pi,page=maps[pi]['page'],best=best,hits40=hits,plain=plain,cipher=cipher,sequences=plant,null=null,permutations=perms,tail=(1+sum(n>=best for n in null))/100))
 dump('source',dict(raw=raw,words=words,lengths=lengths,body_span=[words[0]['span'][0],words[-1]['span'][1]],mapping='H01variant0'));dump('controls',records);print('controls PASS',[(x['best'],x['tail']) for x in records],flush=True)
def actual():
 raw,words,maps,seqs,lengths=setup();sam=automaton(lengths);best=scan(seqs,sam);hits=matches(seqs,lengths,best);rng=random.Random(331719);null=[];perms=[]
 for rep in range(999):
  if rep%50==0:gate()
  sh,pp=shuffled(seqs,rng);null.append(scan(sh,sam));perms.append(pp)
 tail=(1+sum(n>=best for n in null))/1000
 for h in hits:
  j=h['source_start'];n=h['length'];span=[words[j]['span'][0],words[j+n-1]['span'][1]];h.update(page=maps[h['page_index']]['page'],source_span=span,source_text=raw[span[0]:span[1]],page_rune_span=[maps[h['page_index']]['words'][h['page_start']]['start'],maps[h['page_index']]['words'][h['page_start']+n-1]['end']])
 result=dict(source_words=len(words),mapping_count=1,pages=len(maps),max_exact_units=best,tail=tail,admitted=best>=12 and tail<=.01,hits=hits,null=null,permutations=perms,real_sequences=seqs,seed=331719)
 dump('actual',result);print(json.dumps({k:v for k,v in result.items() if k not in ['null','permutations','real_sequences']}),flush=True)
if __name__=='__main__':
 gate();{'provenance':provenance,'controls':controls,'actual':actual}[sys.argv[1]]()
