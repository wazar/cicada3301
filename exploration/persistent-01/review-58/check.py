import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,gzip,hashlib,re,random,collections,datetime
import numpy as np
B=Path('exploration/persistent-01');P=B/'worker-p/P29';O=B/'review-58';source=B/'worker-p/P17/pg45315.txt';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();manifest=[]
def register(p):manifest.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
for p in [P/'CARD.md',P/'REPORT.md',B/'worker-p/p29.py',B/'worker-p/p29_check.py',source,B/'worker-p/P17/source.json.gz',P/'source-maps.json.gz',B/'worker-f/F06-maps.json']:register(p)
raw=source.read_bytes().decode('utf-8-sig');start=raw.index('THE ARGUMENT');end=raw.index('For everything that lives is holy.',start)+len('For everything that lives is holy.');table='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split();lookup={s:i for i,s in enumerate(table)};lookup.update(V=1,K=5,Z=15,Q=5);runes=[];maps=[];words=[]
for wi,match in enumerate(re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",raw[start:end])):
 text=match.group();characters=[(v.upper(),start+match.start()+i) for i,v in enumerate(text) if v not in "'’"];word=[];i=0
 while i<len(characters):
  candidates=[s for s in lookup if ''.join(c[0] for c in characters[i:i+len(s)])==s];token=max(candidates,key=len);v=lookup[token];word.append(v);maps.append({'word':wi,'word_rune':len(word)-1,'rune_id':v,'source_character_positions':[c[1] for c in characters[i:i+len(token)]]});runes.append(v);i+=len(token)
 words.append({'span':[start+match.start(),start+match.end()],'text':text,'runes':word})
stored=json.loads(gzip.decompress((P/'source-maps.json.gz').read_bytes()));assert stored['runes']==runes and stored['rune_maps']==maps and stored['source']['words']==words and stored['source']['raw']==raw;assert stored['source_raw_sha256']==sha(source);assert stored['source_json_sha256']==sha(B/'worker-p/P17/source.json.gz')
page=next(p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page']==0);assert page==stored['cipher_page'];cipher=[29*page['indices'][i]+page['indices'][i+1] for i in range(0,262,2)];pairs=np.array([29*a+b for a,b in zip(runes,runes[1:])]);W=len(runes)-262+1;N=131;assert W==18323
# Canonical first-occurrence labels, rather than production pair maps or distance signatures.
canonical=np.empty((W,N),dtype=np.uint16);previous=np.empty((W,N),dtype=np.int16)
for s in range(W):
 first={};last={}
 for i,a in enumerate(pairs[s:s+262:2]):
  if a not in first:first[a]=len(first)
  canonical[s,i]=first[a];previous[s,i]=last.get(a,-1);last[a]=i

def expected(c):
 first={};last={};pattern=[];prev=[]
 for i,v in enumerate(c):
  if v not in first:first[v]=len(first)
  pattern.append(first[v]);prev.append(last.get(v,-1));last[v]=i
 bad=canonical!=np.array(pattern,dtype=np.uint16);conflict=bad.argmax(axis=1);conflict[~bad.any(axis=1)]=N;out=np.zeros((W,3),np.uint16);out[:,0]=conflict;out[:,2]=65535;ix=np.flatnonzero(conflict<N);j=conflict[ix];sp=previous[ix,j];cp=np.array(prev,dtype=np.int16)[j];carr=np.array(c)
 source_failure=(sp>=0)&(carr[np.maximum(sp,0)]!=carr[j]);reason=np.where(source_failure,1,2);witness=np.where(source_failure,sp,cp);assert np.all(witness>=0);out[ix,1]=reason;out[ix,2]=witness
 return out
rows=[];maxima={};seeds=[];controls=[];arraybytes=0;reasoncounts=None;examples=[]
for path in sorted(P.glob('*.npz')):
 assert not (B/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 register(path);jp=path.with_suffix('.json');register(jp);data=json.loads(jp.read_text());arrays=np.load(path);c=arrays['cipher_pairs'].tolist();got=arrays['obstructions'];ex=expected(c);assert np.array_equal(got,ex),path.name
 complete=np.flatnonzero(ex[:,0]==131).tolist();assert complete==[w['start'] for w in data['witnesses']];assert len(complete)==data['complete_matches'];mx=int(ex[:,0].max());assert mx==data['maximum_prefix'];maxima[path.stem]=(mx,len(complete));arraybytes+=path.stat().st_size
 name=path.stem
 if '-null-' in name:
  j=int(name.split('-')[-1]);iscontrol=name.startswith('control');i=int(name.split('-')[1]) if iscontrol else None;seed=529200+100*i+j if iscontrol else 530000+j;base=np.load(P/(f'control-{i}.npz' if iscontrol else 'actual.npz'))['cipher_pairs'].tolist();perm=list(range(N));random.Random(seed).shuffle(perm);assert data['seed']==seed and data['permutation']==perm and c==[base[k] for k in perm];assert sorted(c)==sorted(base);seeds.append(seed)
 elif name.startswith('control-'):
  i=int(name[-1]);offset=[0,4096,8192,12288][i];perm=list(range(841));random.Random(529100+i).shuffle(perm);assert data['truth']['full_map']==perm and data['truth']['source_start']==offset;assert c==[perm[int(pairs[offset+2*j])] for j in range(N)];assert complete==[offset];controls.append({'id':i,'source_start':offset,'observed_assignments':len(set(pairs[offset:offset+262:2].tolist()))})
 else:
  assert name=='actual' and c==cipher and data['source_positions']==page['source_char_positions'] and data['ignored_words']==page['words'];reasoncounts=collections.Counter(map(int,ex[:,1]));assert not complete
  for s in np.flatnonzero(ex[:,0]==mx):
   j,k=int(ex[s,0]),int(ex[s,2]);examples.append({'source_start':int(s),'conflict_pair':j,'earlier_pair':k,'reason':int(ex[s,1]),'source_pair_values':[[runes[s+2*v],runes[s+2*v+1]] for v in [k,j]],'source_char_positions':[[maps[s+2*v+q]['source_character_positions'] for q in range(2)] for v in [k,j]],'cipher_pair_values':[[page['indices'][2*v],page['indices'][2*v+1]] for v in [k,j]],'cipher_source_positions':[[page['source_char_positions'][2*v],page['source_char_positions'][2*v+1]] for v in [k,j]]})
 for witness in data['witnesses']:
  s=witness['start'];mp=witness['full_map'];assert sorted(mp)==list(range(841));assert witness['plain']==runes[s:s+262];assert [mp[int(pairs[s+2*j])] for j in range(N)]==c;partial={int(pairs[s+2*j]):c[j] for j in range(N)};assert witness['partial_map']==[[a,b] for a,b in sorted(partial.items())];assert witness['unidentifiable_assignments']==841-len(partial);missingin=sorted(set(range(841))-partial.keys());missingout=sorted(set(range(841))-set(partial.values()));assert all(mp[a]==b for a,b in zip(missingin,missingout))
 rows.append({'name':name,'max_prefix':mx,'complete':len(complete)})
assert len(rows)==600 and len(seeds)==595 and len(set(seeds))==595
malformed=json.loads((P/'malformed-controls.json').read_text());register(P/'malformed-controls.json')
for r in malformed:assert expected(r['cipher'])[r['source_start']].tolist()==r['result']
tails=[]
for prefix,n in [('control-'+str(i),99) for i in range(4)]+[('actual',199)]:
 path=P/(prefix+'-summary.json' if prefix!='actual' else 'summary.json');register(path);saved=json.loads(path.read_text());nulls=[maxima[prefix+f'-null-{j:03}'] for j in range(n)];main=maxima[prefix];tail=(1+sum(x[0]>=main[0] for x in nulls))/(n+1);assert saved['prefix_tail']==tail and saved['null_maxima']==[x[0] for x in nulls] and saved['null_full_acceptances']==sum(x[1]>0 for x in nulls);tails.append({'panel':prefix,'tail':tail,'range':[min(x[0] for x in nulls),max(x[0] for x in nulls)]})
report={'status':'PASS','source_runes':len(runes),'source_words':len(words),'source_sha256':sha(source),'panels':len(rows),'windows':len(rows)*W,'all_first_conflicts_verified':True,'method':'first-occurrence canonical labels for compatibility; direct parity-independent source/cipher prior-index checks for first conflict witnesses','control_codes':controls,'malformed_cases':len(malformed),'unique_null_seeds':len(set(seeds)),'actual_reason_counts':dict(reasoncounts),'tails':tails,'actual_maximal_examples':examples,'array_bytes':arraybytes,'rows':rows};(O/'result.json').write_text(json.dumps(report,indent=2));(O/'MANIFEST.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
