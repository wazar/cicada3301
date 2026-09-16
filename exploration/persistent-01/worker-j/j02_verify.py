import pathlib,json,gzip,collections,math
import numpy as np
O=pathlib.Path(__file__).resolve().parent
D=json.loads((O/'j02-results.json').read_text());W=json.load(gzip.open(O/'j02-windows.json.gz','rt'))
def solve(ns):
 ns=[int(x) for x in ns if x];table={(0,0):(0,[])}
 for i,n in enumerate(ns):
  for used in range(i+1,30):
   opts=[]
   for k in range(1,used-i+1):
    if (i,used-k) not in table:continue
    q,r=divmod(n,k);cost=(k-r)*q*(q-1)//2+r*(q+1)*q//2;base,path=table[i,used-k];opts.append((base+cost,path+[k]))
   if opts:table[i+1,used]=min(opts)
 return table[len(ns),29]
controls=[]
for profile in D['profiles']:
 for a in D['actual']:
  n=a['n'];v=np.array(profile['probabilities'])*n;cts=np.floor(v).astype(int)
  for j in np.argsort(-(v-cts))[:n-int(cts.sum())]:cts[j]+=1
  value,alloc=solve(cts);cipher=[];truth=[];book={};offset=0
  for rune,(cnt,k) in enumerate(zip([int(x)for x in cts if x],alloc)):
   book.update({offset+j:rune for j in range(k)});cipher.extend(offset+j%k for j in range(cnt));truth.extend([rune]*cnt);offset+=k
  got=sum(c*(c-1)//2 for c in collections.Counter(cipher).values());assert value==got and [book[x]for x in cipher]==truth
  controls.append({'profile':profile['name'],'n':n,'counts':cts.tolist(),'allocation':alloc,'bound':value,'cipher':cipher,'truth':truth})
convolution=np.array([1.]);offset=0;stats=[]
for ws,act in zip(W['windows'],D['actual']):
 for w in ws:assert solve(w['counts'])[0]==w['bound']
 vals=[w['bound'] for w in ws];lo=min(vals);hist=np.bincount(np.array(vals)-lo)/len(vals);convolution=np.convolve(convolution,hist);offset+=lo
 stats.append({'page':act['page'],'minimum':lo,'actual':act['pairs'],'total_windows':len(ws),'compatible_windows':sum(v<=act['pairs'] for v in vals)})
actual=sum(a['pairs']for a in D['actual']);prob=float(convolution[:max(0,actual-offset+1)].sum())
ws=W['windows'][-1];w=min(ws,key=lambda v:v['bound']);edits=[]
for i,c in enumerate(w['counts']):
 if not c:continue
 for j in range(29):
  if i==j:continue
  counts=w['counts'].copy();counts[i]-=1;counts[j]+=1;v,_=solve(counts);edits.append({'from':i,'to':j,'bound':v})
result={'controls':controls,'window_stats':stats,'exact_window_sum_compatibility':prob,'convolution_offset':offset,'convolution_probabilities':convolution.tolist(),'p17_min_window':w,'one_edit_results':edits,'one_edit_minimum':min(x['bound']for x in edits),'one_edit_compatible':sum(x['bound']<=D['actual'][-1]['pairs'] for x in edits)}
(O/'j02-verify-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['controls','convolution_probabilities','one_edit_results','p17_min_window']}))
