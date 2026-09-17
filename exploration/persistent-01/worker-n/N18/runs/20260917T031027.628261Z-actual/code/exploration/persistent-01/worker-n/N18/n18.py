import json,hashlib,random,itertools,time,sys,datetime
from pathlib import Path
import numpy as np
D=Path(__file__).parent;O=Path('exploration/persistent-01/worker-p/P31')
def guard():assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc) and not Path('exploration/persistent-01/STOP').exists()
def forward(s):return bytes(row[-1] for row in sorted(s[i:]+s[:i] for i in range(len(s))))
def fit(runes):
 vals=[x+1 for x in runes];n=len(vals);candidates=[];columns=[];lfs=[];cycles=[];valid=[]
 for ins in range(n+1):
  last=vals[:ins]+[0]+vals[ins:];pairs=sorted((v,j) for j,v in enumerate(last));lf=[0]*(n+1)
  for dest,(_,src) in enumerate(pairs):lf[src]=dest
  row=ins;out=[];seen=set()
  for _ in range(n+1):out.append(last[row]);seen.add(row);row=lf[row]
  candidate=bytes(out[::-1]);col=forward(candidate);good=col==bytes(last);assert good==(len(seen)==n+1)
  if good:assert candidate[-1]==0 and candidate.count(0)==1
  candidates.append(list(candidate));columns.append(list(col));lfs.append(lf);cycles.append(len(seen));valid.append(good)
 return {'candidates':np.array(candidates,np.uint8),'forward_columns':np.array(columns,np.uint8),'lf':np.array(lfs,np.uint16),'sentinel_cycle_length':np.array(cycles,np.uint16),'valid':np.array(valid,bool)}
def tiny():
 rows=[];count=0
 for a,limit in [(2,6),(3,4)]:
  for n in range(1,limit+1):
   words=[bytes(w) for w in itertools.product(range(1,a+1),repeat=n)];image={forward(w+b'\0') for w in words}
   for runes in words:
    z=fit([v-1 for v in runes])
    for ins in range(n+1):assert bool(z['valid'][ins])==(runes[:ins]+b'\0'+runes[ins:] in image);count+=1
   rows.append({'alphabet':a,'n':n,'source_words':len(words),'image_size':len(image)})
 (D/'tiny.json').write_text(json.dumps({'rows':rows,'columns_checked':count},indent=2))
def packet(i):
 old=json.loads((O/f'packet-{i}.json').read_text())
 if i<4:
  s=bytes(v+1 for v in old['truth'])+b'\0';column=forward(s);pos=column.index(0);indices=[v-1 for v in column if v];return {'packet':i,'name':old['name'],'indices':indices,'truth':old['truth'],'truth_sentinel_position':pos,'source':old['source']}
 return old

def run(i):
 guard();p=packet(i);(D/f'packet-{i}.json').write_text(json.dumps(p));rows=[]
 for j in [None]+list(range(19)):
  guard();c=p['indices'].copy();seed=None
  if j is not None:seed=531100+100*i+j;random.Random(seed).shuffle(c)
  name=f'packet-{i}-main' if j is None else f'packet-{i}-null-{j:02}';start=time.monotonic();z=fit(c);np.savez_compressed(D/(name+'.npz'),input=np.array(c,np.uint8),**z);positions=np.flatnonzero(z['valid']).tolist();outputs=[{'sentinel_position':q,'runes':(z['candidates'][q][:-1]-1).tolist()} for q in positions]
  if i<4 and j is None:assert any(o['runes']==p['truth'] and o['sentinel_position']==p['truth_sentinel_position'] for o in outputs)
  meta={'name':name,'packet':i,'null':j,'seed':seed,'n':len(c),'valid_positions':positions,'outputs':outputs,'compatible':bool(positions),'seconds':time.monotonic()-start};(D/(name+'.json')).write_text(json.dumps(meta));rows.append(meta)
 out={'packet':i,'name':p['name'],'main':rows[0],'null_compatible':sum(r['compatible'] for r in rows[1:]),'null_valid_positions':[len(r['valid_positions']) for r in rows[1:]],'seconds':sum(r['seconds'] for r in rows)};(D/f'packet-{i}-summary.json').write_text(json.dumps(out,indent=2));print(i,len(rows[0]['valid_positions']),out['null_compatible'],out['seconds'],flush=True);return out
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='pilot':tiny();r=run(0);(D/'pilot.json').write_text(json.dumps({'seconds':r['seconds'],'forecast140':7*r['seconds'],'bytes20':sum(f.stat().st_size for f in D.glob('packet-0-*.npz'))},indent=2))
 elif mode=='controls':
  for i in range(1,4):run(i)
 elif mode=='actual':
  for i in range(4):assert json.loads((D/f'packet-{i}-summary.json').read_text())['main']['compatible']
  for i in range(4,7):run(i)
