import os
for v in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[v]='1'
from pathlib import Path
import numpy as np,json,gzip,hashlib,itertools,random,time,datetime,sys,re
B=Path('exploration/persistent-01');O=B/'worker-p/P31';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def guard():assert not (B/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def forward(s):return bytes(row[-1] for row in sorted(s[i:]+s[:i] for i in range(len(s))))
def canonical(s):return min(s[i:]+s[:i] for i in range(len(s)))
def test(last):
 n=len(last);counts=[last.count(c) for c in range(29)];starts=np.cumsum([0]+counts[:-1]).tolist();seen=[0]*29;lf=[]
 for c in last:lf.append(starts[c]+seen[c]);seen[c]+=1
 candidates=[];groups=[];which=[];lookup={};columns=[];valid=[]
 for primary in range(n):
  row=primary;s=[]
  for _ in range(n):s.append(last[row]);row=lf[row]
  s=bytes(reversed(s));candidates.append(s);key=canonical(s)
  if key not in lookup:
   lookup[key]=len(groups);groups.append(key);column=forward(key);columns.append(column);valid.append(column==last)
  which.append(lookup[key])
 return dict(lf=np.array(lf,dtype=np.uint16),candidates=np.array([list(s) for s in candidates],dtype=np.uint8),groups=np.array([list(s) for s in groups],dtype=np.uint8),group_for_primary=np.array(which,dtype=np.uint16),forward_columns=np.array([list(s) for s in columns],dtype=np.uint8),valid=np.array(valid,dtype=np.bool_))
def tiny():
 result=[]
 for alphabet,maxn in [(2,7),(3,5)]:
  for n in range(1,maxn+1):
   words=[bytes(x) for x in itertools.product(range(alphabet),repeat=n)];image={forward(s) for s in words};positive=0
   for last in words:
    r=test(last);got=bool(r['valid'].any());assert got==(last in image);positive+=got
    for g,v in zip(r['groups'],r['valid']):
     if v:assert forward(bytes(g))==last
   result.append(dict(alphabet=alphabet,n=n,inputs=len(words),valid=positive))
 (O/'tiny.json').write_text(json.dumps(result,indent=2))
def packet(i):
 if i<4:
  names=['0_welcome','jpg107-167','p56_an_end','p57_parable'];f=Path('audit/parallel-01/reference/sources')/('solved_'+names[i]+'.txt');raw=f.read_text();positions=[j for j,c in enumerate(raw) if c in ABC];plain=bytes(ABC.index(raw[j]) for j in positions)
  return dict(packet=i,name=names[i],indices=list(forward(plain)),truth=list(plain),source=dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),raw=raw,source_char_positions=positions))
 p=next(p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page']==[0,17,55][i-4]);return dict(packet=i,name='original'+str(p['page']),indices=p['indices'],source=p)
def run(i):
 guard();p=packet(i);(O/f'packet-{i}.json').write_text(json.dumps(p));summaries=[]
 for j in [None]+list(range(19)):
  guard();s=bytes(p['indices']);seed=None
  if j is not None:
   seed=531100+100*i+j;rng=random.Random(seed);s=list(s);rng.shuffle(s);s=bytes(s)
  name=f'packet-{i}-main' if j is None else f'packet-{i}-null-{j:02}';t=time.monotonic();r=test(s);validrows=[k for k,g in enumerate(r['group_for_primary']) if r['valid'][g]]
  np.savez_compressed(O/(name+'.npz'),input=np.frombuffer(s,dtype=np.uint8),**r)
  summary=dict(name=name,packet=i,null=j,seed=seed,n=len(s),candidate_groups=len(r['groups']),valid_primary_rows=validrows,valid_groups=np.flatnonzero(r['valid']).tolist(),compatible=bool(validrows),seconds=time.monotonic()-t)
  if i<4 and j is None:
   truth=canonical(bytes(p['truth']));assert validrows and any(bytes(g)==truth and valid for g,valid in zip(r['groups'],r['valid']));summary['truth_recovered_up_to_rotation']=True
  (O/(name+'.json')).write_text(json.dumps(summary));summaries.append(summary)
 out=dict(packet=i,name=p['name'],main=summaries[0],inventory_null_compatible=sum(x['compatible'] for x in summaries[1:]),nulls=19,seconds=sum(x['seconds'] for x in summaries));(O/f'packet-{i}-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':
 guard()
 if sys.argv[1]=='pilot':tiny();run(0)
 elif sys.argv[1]=='controls':
  for i in range(1,4):run(i)
 elif sys.argv[1]=='actual':
  for i in range(4,7):run(i)
