import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,hashlib,random,time
R=Path(__file__).resolve().parents[3];B=R/'exploration/persistent-01';O=B/'worker-p/P29';s=json.loads(gzip.decompress((B/'worker-p/P17/source.json.gz').read_bytes()));runes=np.array([x for w in s['words'] for x in w['runes']],int);pairs=(29*runes[:-1]+runes[1:]).tolist();N=131;W=len(runes)-2*N+1;last=[{},{}];prev=[]
for i,p in enumerate(pairs):prev.append(last[i%2].get(p,-1));last[i%2][p]=i
prev=np.array(prev);starts=np.arange(W);PAT=np.empty((W,N),np.uint16)
for j in range(N):
 absolute=starts+2*j;back=prev[absolute];PAT[:,j]=np.where(back>=starts,(absolute-back)//2,0)
def pattern(seq):
 seen={};p=[]
 for i,x in enumerate(seq):p.append(i-seen[x] if x in seen else 0);seen[x]=i
 return np.array(p,dtype=np.uint16)
def expected(seq):
 cp=pattern(seq);bad=PAT!=cp;has=bad.any(1);first=bad.argmax(1);first[~has]=N;out=np.zeros((W,3),np.uint16);out[:,0]=first;out[:,2]=65535;ix=np.flatnonzero(has);j=first[ix];sp=PAT[ix,j];reason=np.where(sp>0,1,2);distance=np.where(sp>0,sp,cp[j]);out[ix,1]=reason;out[ix,2]=j-distance
 return out
rows=[];total=0;counts=0
for path in sorted(O.glob('*.npz')):
 name=path.stem;d=json.loads((O/(name+'.json')).read_text());a=np.load(path);c=a['cipher_pairs'].tolist();got=a['obstructions'];ex=expected(c);assert np.array_equal(got,ex);complete=np.flatnonzero(ex[:,0]==N).tolist();assert d['maximum_prefix']==int(ex[:,0].max()) and len(complete)==d['complete_matches'] and complete==[w['start'] for w in d['witnesses']]
 if 'null' in name:
  if name.startswith('control'):
   parts=name.split('-');i=int(parts[1]);j=int(parts[-1]);seed=529200+100*i+j;base=np.load(O/f'control-{i}.npz')['cipher_pairs'].tolist()
  else:j=int(name.split('-')[-1]);seed=530000+j;base=np.load(O/'actual.npz')['cipher_pairs'].tolist()
  perm=list(range(N));random.Random(seed).shuffle(perm);assert d['seed']==seed and d['permutation']==perm and c==[base[i] for i in perm]
 elif name.startswith('control'):
  i=int(name.split('-')[-1]);start=[0,4096,8192,12288][i];mapping=list(range(841));random.Random(529100+i).shuffle(mapping);assert d['truth']['source_start']==start and d['truth']['full_map']==mapping and d['truth']['plain']==runes[start:start+262].tolist();assert c==[mapping[pairs[start+2*j]] for j in range(N)] and start in complete
 else:
  page=next(x for x in json.loads((B/'worker-f/F06-maps.json').read_text()) if x['page']==0);assert c==[29*x+y for x,y in zip(page['indices'][::2],page['indices'][1::2])]
 for witness in d['witnesses']:
  start=witness['start'];mp=witness['full_map'];assert sorted(mp)==list(range(841));assert [mp[pairs[start+2*j]] for j in range(N)]==c and witness['plain']==runes[start:start+262].tolist();partial={pairs[start+2*j]:c[j] for j in range(N)};assert witness['partial_map']==[[x,y] for x,y in sorted(partial.items())];assert witness['unidentifiable_assignments']==841-len(partial)
 rows.append(dict(name=name,complete_matches=len(complete),maximum_prefix=d['maximum_prefix']));total+=W;counts+=1
for x in json.loads((O/'malformed-controls.json').read_text()):assert expected(x['cipher'])[x['source_start']].tolist()==x['result']
for prefix,n in [('control-'+str(i),99) for i in range(4)]+[('actual',199)]:
 file=O/(prefix+'-summary.json' if prefix!='actual' else 'summary.json')
 if not file.exists():continue
 d=json.loads(file.read_text());main=next(x for x in rows if x['name']==prefix);ns=[next(x for x in rows if x['name']==prefix+f'-null-{j:03}') for j in range(n)];assert d['null_maxima']==[x['maximum_prefix'] for x in ns] and d['prefix_tail']==(1+sum(x['maximum_prefix']>=main['maximum_prefix'] for x in ns))/(n+1) and d['null_full_acceptances']==sum(x['complete_matches']>0 for x in ns)
(O/'independent-check.json').write_text(json.dumps(dict(pass_all=True,panels=counts,windows=total,method='previous-occurrence distance patterns, independent of production bidirectional map',rows=rows),indent=2)+'\n');print('ALL PASS',counts,total)
