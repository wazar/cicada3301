"""Independent forward decoding; never imports search implementations or writes their outputs."""
import pathlib,json,hashlib,math,gzip
R=pathlib.Path(__file__).resolve().parents[3]; O=pathlib.Path(__file__).parent
sources={}
def read(p):
 p=R/p if isinstance(p,str) else p;b=p.read_bytes();sources[str(p.relative_to(R))]=hashlib.sha256(b).hexdigest();return json.loads(b)
T='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
config=read('exploration/overnight-01/config.json');hold=set(config['reserved_original_pages'])
pages={p['original_page']:p for p in read('audit/parallel-01/inputs/dataset.json')['pages'] if p['original_page']<=55 and p['original_page'] not in hold};assert len(pages)==45
q=R/'liber-primus/data/english_quadgrams.txt';sources[str(q.relative_to(R))]=hashlib.sha256(q.read_bytes()).hexdigest();counts={a:int(b) for a,b in map(str.split,q.read_text().splitlines())};total=sum(counts.values());floor=math.log10(.01/total)
def score(p):
 s=''.join(T[x] for x in p);return sum(math.log10(counts[g]/total) if g in counts else floor for g in (s[i:i+4] for i in range(len(s)-3)))/max(1,len(s)-3)
def dec(c,k,sgn,literals=(),periodic=False):
 out=[];j=0;literals=set(literals)
 for i,x in enumerate(c):
  if i in literals:assert x==0;out.append(0)
  else:out.append((x+sgn*k[j%len(k) if periodic else j])%29);j+=1
 return out,j
checked=[]
def record(file,z,p,expected):
 assert p==expected,(str(file),z['id'],'runes');s=score(p);assert abs(s-z['score'])<1e-9,(str(file),z['id'],s,z['score']);checked.append(dict(file=str(file.relative_to(R)),id=z['id'],source_file=str(file.relative_to(R)),independently_reproduced=True,checktype='independent forward decode, key derivation and exact score',status='REPRODUCIBLE_CANDIDATE',score=s,raw=''.join(T[x] for x in p)))
# Byte interpretation reconstructed from token field and physical coordinates.
a='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx';blob=bytes(a.index(c['token'][0])*60+a.index(c['token'][1]) for c in read('audit/alphanumeric-01/v1/transcription.json')['cells']);assert hashlib.sha256(blob).hexdigest()=='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290'
cpath=R/'exploration/overnight-01/worker-c/top_candidates.json';cc=read(cpath)
for z in cc['R07']:
 axis,order,conv=z['route'].split('-');rr=order[1]=='1';cr=order[3]=='1';coords=sorted(((r,c) for r in range(32) for c in range(8)),key=lambda v:((-v[0] if rr else v[0]),(-v[1] if cr else v[1])) if axis=='row' else ((-v[1] if cr else v[1]),(-v[0] if rr else v[0])))
 key=[blob[r*8+c]%29 for r,c in coords if conv=='mod29' or blob[r*8+c]<232];off=z['offset'];key=key[off:]+(key[:off] if z['periodic'] else []);assert key==z['key'];c=pages[z['page']]['indices'];p,n=dec(c,key,z['sign'],z['path'],z['periodic']);assert n==z['used'];record(cpath,z,p,z['plain'])
 for alt in z['alternatives']:
  p,n=dec(c,key,z['sign'],alt['path'],z['periodic']);assert p==alt['plain'] and n==alt['used'] and abs(score(p)-alt['score'])<1e-9
# Independent sequence generation uses trial division and gcd totients, unlike worker sieve.
pr=[]
for n in range(2,180000):
 if all(n%d for d in pr if d*d<=n):pr.append(n)
 if len(pr)>=15001:break
phi=[sum(math.gcd(i,j)==1 for j in range(1,i+1)) for i in range(1,700)]
fib=[0,1]
for _ in range(15000):fib.append((fib[-2]+fib[-1])%29)
def seq(name,start,n):
 if name=='primes':v=pr[start:start+n]
 elif name=='prime_minus_one':v=[x-1 for x in pr[start:start+n]]
 elif name=='prime_gaps':v=[pr[i+1]-pr[i] for i in range(start,start+n)]
 elif name=='integers':v=list(range(start+1,start+n+1))
 elif name=='fibonacci':v=fib[start:start+n]
 elif name=='integer_phi':
  v=[]
  for i in range(start+1,start+n+1):
   t=i;result=i;d=2
   while d*d<=t:
    if t%d==0:
     result-=result//d
     while t%d==0:t//=d
    d+=1
   if t>1:result-=result//t
   v.append(result)
 else:raise ValueError(name)
 return [x%29 for x in v]
for lane in ['r03','r03-f','r04','r04-wide']:
 for file in sorted((R/'exploration/overnight-01/worker-b'/lane).glob('top*candidates.json')):
  for z in read(file):
   c=pages[z['page']]['indices'];k=z.get('key') or seq(z['family'],z.get('key_start',z.get('offset',0)),len(c));alts=z.get('choices',[z])
   for alt in alts:
    p,n=dec(c,k,z.get('sign',-1),alt.get('literal_positions',()),lane.startswith('r04'));assert p==alt['rune_indices'];assert abs(score(p)-alt['score'])<1e-9
   p=alts[0]['rune_indices'];record(file,z,p,z['rune_indices'])
   if lane.startswith('r04'):assert abs(score(p[:z['split']])-z['train_score'])<1e-9 and abs(score(p[z['split']:])-z['continuation_score'])<1e-9
# A retained keys independently tied to frozen recipes, not arbitrary re-encryption.
keys=read('audit/experiment-01/keys.json')
for file in sorted((R/'exploration/overnight-01/worker-a').glob('r01*/top20.json')):
 for z in read(file):
  c=pages[z['original_page']]['indices']
  if z['mode']=='rejection':
   key=keys[z['recipe']];use=z['key_use'];assert len(use)==len(c) and use[0]==0;p=[(v+z['sign']*key[j])%29 for v,j in zip(c,use)]
   for i in range(1,len(c)):
    assert 1<=use[i]-use[i-1]<=4
    for j in range(use[i-1]+1,use[i]):assert (p[i]-z['sign']*key[j])%29==c[i-1]
  elif z['mode']=='affine':p=[(int(z['recipe'])*v+z['sign'])%29 for v in c]
  else:
   key=keys[z['recipe']][z['offset']:];assert key[:len(c)]==z['key'];alt=z['alternatives'][0] if z['alternatives'] else {};p,n=dec(c,key,z['sign'],alt.get('literal_positions',()));
   for alt in z['alternatives']:
    ap,an=dec(c,key,z['sign'],alt['literal_positions']);assert ap==alt['plain'] and an==alt['used'] and abs(score(ap)-alt['score'])<1e-9
  record(file,z,p,z['plain'])
# Final normalized A exports; reconstruct clue arrays directly from cited rune source spans.
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
clues=read('exploration/overnight-01/worker-a/r02/keys.json');defs={x['id']:x for x in clues['keys']+clues['texts']}
for definition in defs.values():
 source=definition['aliases'][0]['source'] if 'aliases' in definition else definition['source'];fp=R/source;raw=fp.read_text();sources[source]=hashlib.sha256(fp.read_bytes()).hexdigest()
 if 'aliases' in definition:
  a=definition['aliases'][0];raw=raw[a['character_start']:a['character_end']]
 assert [ABC.index(c) for c in raw if c in ABC]==definition['key']
for lane in ['R01','R02']:
 file=R/'exploration/overnight-01/worker-a'/lane/'top_candidates.json'
 for z in read(file):
  c=pages[z['original_page']]['indices'];m=z['method'];off=m['offset'];mode=m['mode']
  if lane=='R02':
   k=defs[m['key_id']]['key'];key=[k[(i+off)%len(k)] for i in range(len(c))] if m['periodic'] else k[off:off+len(c)]
  elif mode!='affine':key=keys[m['recipe']][off:]
  if mode=='affine':p=[(int(m['recipe'])*v+m['sign'])%29 for v in c]
  elif mode=='rejection':
   use=z['key_use'];p=[(v+m['sign']*key[j])%29 for v,j in zip(c,use)]
   for i in range(1,len(c)):
    assert 1<=use[i]-use[i-1]<=4
    for j in range(use[i-1]+1,use[i]):assert (p[i]-m['sign']*key[j])%29==c[i-1]
  else:
   p,n=dec(c,key,m['sign'],z['literal_positions'])
   for a in z['alternatives']:
    ap,an=dec(c,key,m['sign'],a['literal_positions']);assert ap==a['plain'] and an==a['used'] and abs(score(ap)-a['score'])<1e-9
  record(file,dict(z,score=z['scores']['english_quadgram']),p,z['plain_idx'])
result=dict(checked=checked,count=len(checked),sources=sources,discovery_pages=sorted(pages),reserved_decoded=[],limitation='Independent forward transforms and score checks; no search optimizer reruns, no heldout reveal, no claimed semantic validity.')
(O/'checked.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checked':len(checked),'source_count':len(sources),'discovery_pages':len(pages),'reserved_decoded':[]}))
for z in checked:print(z['file'],z['id'],round(z['score'],6),z['raw'])
