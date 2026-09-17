import json,gzip,hashlib,time,sys
from pathlib import Path
import numpy as np
D=Path(__file__).parent
F=Path('exploration/persistent-01/worker-f/F06-maps.json')
GP='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
P=json.loads(F.read_text())
def route(rows):
 rows=[list(x) for x in rows if len(x)]; out=[]
 while rows:
  out+=rows.pop(0)
  for row in rows:
   if row:out.append(row.pop())
  rows=[r for r in rows if r]
  if rows:out+=rows.pop()[::-1]
  for row in rows[::-1]:
   if row:out.append(row.pop(0))
  rows=[r for r in rows if r]
 return out
R=[];E=[]
for p in P:
 rows=[[i for i,l in enumerate(p['line_of_rune']) if l==j] for j in sorted(set(p['line_of_rune']))]
 r=route(rows);assert sorted(r)==list(range(len(p['indices'])))
 e=[(a,b) for a,b in zip(r,r[1:]) if abs(a-b)>1]
 R.append(r);E.append(np.array(e,dtype=int).reshape(-1,2))
assert route([[0,1,2],[3,4,5],[6,7,8]])==[0,1,2,5,8,7,6,3,4]
N=sum(len(p['indices']) for p in P)
def count(cs):return sum(int(np.sum(c[e[:,0]]==c[e[:,1]])) for c,e in zip(cs,E))
def evaluate(cs,seed,B,name):
 rng=np.random.default_rng(seed); actual=count(cs); stats=np.zeros(B,dtype=int); generated=[]
 for c,e in zip(cs,E):
  w=np.bincount(c,minlength=29)+.5; w=w/w.sum(); q=np.tile(w,(29,1));np.fill_diagonal(q,0);q/=q.sum(axis=1)[:,None];cdf=np.cumsum(q,axis=1);cdf[:,-1]=1
  z=np.empty((B,len(c)),dtype=np.uint8);z[:,0]=c[0]
  for i in range(1,len(c)):
   if c[i]==c[i-1]:z[:,i]=z[:,i-1]
   else:z[:,i]=(rng.random(B)[:,None]>cdf[z[:,i-1]]).sum(axis=1)
  stats+=(z[:,e[:,0]]==z[:,e[:,1]]).sum(axis=1);generated.append(z)
 np.savez_compressed(D/(name+'.npz'),cipher=np.concatenate(cs),nulls=np.concatenate(generated,axis=1),null_stats=stats)
 out={'name':name,'seed':seed,'B':B,'actual':actual,'tail':(1+int(sum(stats<=actual)))/(B+1),'null_mean':float(stats.mean()),'null_min':int(min(stats)),'edges':sum(map(len,E))}
 (D/(name+'.json')).write_text(json.dumps(out,indent=2));return out
sources=['solved_0_warning.txt','solved_0_wisdom.txt','solved_0_koan_1.txt','solved_p57_parable.txt']
def control(k):
 path=Path('audit/parallel-01/reference/sources')/sources[k//3];raw=path.read_text();s=[GP.index(x) for x in raw if x in GP];rng=np.random.default_rng(614100+k);cs=[];trace=[]
 for p,r in zip(P,R):
  j=int(rng.integers(len(s)));start=j; seq=[];events=[]
  while len(seq)<len(r):
   v=s[j%len(s)];u=float(rng.random()) if seq and v==seq[-1] else None;accept=u is None or u>=.83;events.append([j%len(s),u,accept]);j+=1
   if accept:seq.append(v)
  c=np.empty(len(r),dtype=np.uint8);c[r]=seq;cs.append(c);trace.append({'page':p['page'],'start':start,'events':events})
 with gzip.open(D/f'control-{k}-source.json.gz','wt') as f:json.dump({'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seed':614100+k,'traces':trace},f)
 return evaluate(cs,615000+k,199,f'control-{k}')
if __name__=='__main__':
 start=time.time()
 if sys.argv[1]=='pilot':
  maps=[{'page':p['page'],'route':r,'source_char_positions':[p['source_char_positions'][i] for i in r],'source_lines':[p['line_of_rune'][i] for i in r],'novel_edges':e.tolist()} for p,r,e in zip(P,R,E)]
  (D/'maps.json').write_text(json.dumps(maps));print(control(0))
 else:
  results=[json.loads((D/'control-0.json').read_text())]+[control(k) for k in range(1,12)]
  actual=evaluate([np.array(p['indices'],dtype=np.uint8) for p in P],614001,999,'actual');(D/'result.json').write_text(json.dumps({'actual':actual,'controls':results,'power_05':sum(x['tail']<=.05 for x in results),'seconds':time.time()-start},indent=2));print((D/'result.json').read_text())
 print('seconds',time.time()-start)
