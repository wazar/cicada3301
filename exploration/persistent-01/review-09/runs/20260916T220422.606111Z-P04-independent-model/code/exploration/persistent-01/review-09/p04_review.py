import pathlib,json,gzip,itertools,collections,hashlib,datetime,time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csr_matrix,load_npz,save_npz
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];S=O/'snapshots/exploration/persistent-01/worker-p';P=O.parent/'worker-p/P04'
def load(p):return json.loads(p.read_text())
def readgz(p):
 with gzip.open(p,'rt') as f:return json.load(f)
def main():
 assert not(O.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
 e=readgz(S/'P03/evidence.json.gz');support=readgz(S/'P04/support-evidence.json.gz');common=support['common_supports'];assert len(common)==1;letters=[ord(c)-65 for c in common[0]];ids=[p['page'] for p in e['real']];hist=[dict(p['output_counts_by_rune']) for p in e['real']]
 # Rebuild unsorted source vectors directly from source files once again, never sorted target profiles.
 T=[z['transliteration'] for z in load(R/'KNOWLEDGE.json')['gematria_primus']['table']];ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';seqs={}
 for name in ['0_koan_1','0_loss_of_divinity','0_welcome','jpg107-167']:
  raw=(R/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text();seqs[name]=[ord(c)-65 for ch in raw if ch in ABC for c in T[ABC.index(ch)] if c not in 'AEIOU']
 choices=[]
 for page,stored in zip(e['real'],support['pages']):
  feasible={(v['group'],v['start']) for case in page['cases'] if case['result']['status']=='FEASIBLE' for v in case['provenance']};vectors=set()
  for name,seq in seqs.items():
   for start in range(len(seq)-page['n']+1):
    counts=collections.Counter(seq[start:start+page['n']])
    if set(counts)==set(letters) and (name,start) in feasible:vectors.add(tuple(counts.get(j,0) for j in range(26)))
  opts=sorted(vectors);assert opts==[tuple(z['counts']) for z in stored['groups'][common[0]]];choices.append(opts)
 def build(L,opts):
  variables=[('assignment',letter,rune) for letter in L for rune in range(29)];index={v:i for i,v in enumerate(variables)}
  for pi,vecs in enumerate(opts):
   for j,v in enumerate(vecs):index['window',pi,j]=len(variables);variables.append(('window',pi,j))
  rows=[];rhs=[];desc=[]
  for rune in range(29):
   row={index['assignment',letter,rune]:1 for letter in L};rows.append(row);rhs.append(1);desc.append(('one_letter',rune))
  for pi,vecs in enumerate(opts):
   rows.append({index['window',pi,j]:1 for j in range(len(vecs))});rhs.append(1);desc.append(('one_window',ids[pi]))
   for letter in L:
    row={index['assignment',letter,rune]:hist[pi][rune] for rune in range(29)}
    for j,v in enumerate(vecs):row[index['window',pi,j]]=-v[letter]
    rows.append(row);rhs.append(0);desc.append(('count',ids[pi],letter))
  mat=np.zeros((len(rows),len(variables)),int)
  for j,row in enumerate(rows):
   for k,v in row.items():mat[j,k]=v
  return mat,np.array(rhs),variables,desc
 A,b,variables,desc=build(letters,choices);oldmodel=load(S/'P04/real-0-model.json');oldA=load_npz(S/'P04/real-0-matrix.npz').toarray();oldb=np.load(S/'P04/real-0-rhs.npy');colperm=[]
 for v in oldmodel['variables']:
  key=('assignment',v['letter'],v['rune']) if v['kind']=='assign' else ('window',ids.index(v['page']),choices[ids.index(v['page'])].index(tuple(v['counts'])))
  colperm.append(variables.index(key))
 rowperm=[]
 for d in oldmodel['rows']:
  k=('one_letter',d['rune']) if d['kind']=='one_letter' else ('one_window',d['page']) if d['kind']=='one_window' else ('count',d['page'],d['letter']);rowperm.append(desc.index(k))
 assert np.array_equal(A[np.ix_(rowperm,colperm)],oldA) and np.array_equal(b[rowperm],oldb);save_npz(O/'independent-matrix.npz',csr_matrix(A));np.save(O/'independent-rhs.npy',b)
 def solve(mat,rhs,integral,label):
  start=time.monotonic();r=milp(c=np.zeros(mat.shape[1]),integrality=np.full(mat.shape[1],int(integral)),bounds=Bounds(0,1),constraints=LinearConstraint(csr_matrix(mat),rhs,rhs),options={'time_limit':30.,'presolve':True,'threads':1,'mip_rel_gap':0.,'disp':True});out={'label':label,'status':int(r.status),'message':r.message,'seconds':time.monotonic()-start,'x':None if r.x is None else r.x.tolist()}
  if integral and r.x is not None:xx=np.rint(r.x);assert np.max(abs(xx-r.x))<1e-7 and np.array_equal(mat@xx,rhs) and np.all((xx==0)|(xx==1))
  return out
 lp=solve(A,b,False,'real_LP_relaxation');integer=solve(A,b,True,'real_integral');assert integer['status']==2
 pos=[]
 for h in hist:
  v=[0]*26
  for rune,n in h.items():v[[1,2,3][rune%3]]+=n
  pos.append([tuple(v)])
 ap,bp,_,_=build([1,2,3],pos);positive=solve(ap,bp,True,'positive');assert positive['status']==0
 neg=[[list(v) for v in group] for group in pos];old=neg[0][0][1];neg[0][0][1]=1;neg[0][0][2]+=old-1;an,bn,_,_=build([1,2,3],neg);negative=solve(an,bn,True,'negative');assert negative['status']==2
 # Cheap exact per-letter relaxed profile obstruction. Ignore coupling between letters/windowchoices.
 profiles={r:tuple(h[r] for h in hist) for r in range(29)};checks=[]
 for letter in letters:
  allowed=[{v[letter] for v in opts} for opts in choices];upper=tuple(max(a) for a in allowed);candidates=[r for r,p in profiles.items() if all(v<=u for v,u in zip(p,upper))];rows=[]
  if len(candidates)<=18:
   for bits in itertools.product([0,1],repeat=len(candidates)):
    chosen=[r for r,on in zip(candidates,bits) if on];profile=tuple(sum(profiles[r][j] for r in chosen) for j in range(5))
    if all(v in aa for v,aa in zip(profile,allowed)):rows.append({'runes':chosen,'profile':profile})
   checks.append({'letter':chr(letter+65),'allowed_counts_by_page':[sorted(a) for a in allowed],'eligible_runes':candidates,'eligible_profiles':{str(r):profiles[r] for r in candidates},'enumerated_subsets':2**len(candidates),'matching_subsets':rows,'empty_is_exact_obstruction':not rows})
  else:checks.append({'letter':chr(letter+65),'eligible_runes':candidates,'skipped':'more than18 eligible runes; bounded review only'})
 out={'shape':list(A.shape),'nonzeros':int(np.count_nonzero(A)),'matrix_exactly_matches_saved_after_permutation':True,'common_support':common[0],'window_vectors':[len(z) for z in choices],'LP':lp,'integral':integer,'positive':positive,'negative':negative,'per_letter_profile_checks':checks};(O/'P04-findings.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['positive','per_letter_profile_checks','LP']}));print('ELEMENTARY',[c['letter'] for c in checks if c.get('empty_is_exact_obstruction')])
if __name__=='__main__':main()
