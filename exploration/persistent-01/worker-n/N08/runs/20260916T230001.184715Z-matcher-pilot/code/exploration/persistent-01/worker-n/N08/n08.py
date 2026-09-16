from pathlib import Path
import json,gzip,random,time,hashlib,sys,datetime,itertools
import numpy as np
O=Path(__file__).resolve().parent;B=O.parents[1];MAP=B/'worker-f/F06-maps.json';maps=json.loads(MAP.read_text());ids=[m['page'] for m in maps];seqs=[[w['end']-w['start'] for w in m['words']] for m in maps];pairs=[(i,ids.index(p+1)) for i,p in enumerate(ids) if p+1 in ids]
assert len(pairs)==33 and sum(map(len,seqs))==2355 and not set(ids)&{4,9,14,19,24,29,34,39,44,54}
def guard():
 assert not (B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def save(name,obj):
 with gzip.open(O/(name+'.json.gz'),'wt') as f:json.dump(obj,f)
def match(a,b,retain=False):
 bb=np.array(b,dtype=np.int16);dp=np.zeros(len(b)+1,dtype=np.int16);best=0;hits=[]
 for i,x in enumerate(a):
  dp[1:]=(dp[:-1]+1)*(bb==x);peak=int(dp.max())
  if peak>best:best=peak;hits=[]
  if retain and peak==best and best:
   for end in np.flatnonzero(dp[1:]==best):hits.append((i+1-best,int(end)+1-best,best))
 return best,hits
def scan(panel,retain=False):
 best=0;rows=[]
 for a,b in pairs:
  for reverse in [False,True]:
   n,hits=match(panel[a],panel[b][::-1] if reverse else panel[b],retain);best=max(best,n)
   if retain:
    spans=[]
    for i,j,k in hits:
     right=list(range(len(panel[b])-1-j,len(panel[b])-1-j-k,-1)) if reverse else list(range(j,j+k))
     spans.append(dict(left_units=list(range(i,i+k)),right_units=right,lengths=panel[a][i:i+k],left_rune_span=[sum(panel[a][:i]),sum(panel[a][:i+k])],right_rune_span=[sum(panel[b][:min(right)]),sum(panel[b][:max(right)+1])]))
    rows.append(dict(left_page=ids[a],right_page=ids[b],reverse=reverse,max_units=n,spans=spans))
 return best,rows
def permute(panel,rng,family):
 out=[];orders=[]
 for seq in panel:
  blocks=[[i] for i in range(len(seq))] if family==0 else [list(range(i,min(i+4,len(seq)))) for i in range(0,len(seq),4)]
  order=list(range(len(blocks)));rng.shuffle(order);indices=[i for k in order for i in blocks[k]];out.append([seq[i] for i in indices]);orders.append(dict(block_order=order,unit_order=indices))
 return out,orders
def nulls(panel,name,count,seed,family):
 rng=random.Random(seed);stats=[];path=O/(name+'.jsonl.gz')
 with gzip.open(path,'wt') as f:
  for rep in range(count):
   if rep%100==0:guard()
   sample,orders=permute(panel,rng,family);stat,_=scan(sample);stats.append(stat);f.write(json.dumps(dict(rep=rep,stat=stat,orders=orders))+'\n')
 return dict(seed=seed,family=family,stats=stats,count=count,path=path.name)
def pilot():
 rng=random.Random(1708000);tests=[]
 for rep in range(100):
  a=[rng.randrange(1,5) for _ in range(rng.randrange(2,14))];b=[rng.randrange(1,5) for _ in range(rng.randrange(2,14))];expected=0
  for i in range(len(a)):
   for j in range(len(b)):
    k=0
    while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]:k+=1
    expected=max(expected,k)
  actual,hits=match(a,b,True);assert actual==expected
  for i,j,k in hits:assert a[i:i+k]==b[j:j+k] and k==actual
  tests.append(dict(a=a,b=b,max=actual))
 start=time.monotonic();real,rows=scan(seqs,True);pilotnull=[]
 for family in [0,1]:
  rr=random.Random(1708001+family)
  for rep in range(10):sample,_=permute(seqs,rr,family);pilotnull.append(scan(sample)[0])
 elapsed=time.monotonic()-start;save('pilot-evidence',dict(tiny=tests,real_matches=rows,pilot_nulls=pilotnull));out=dict(real_max=real,pairs=33,orientations=2,offset_pairs=sum(2*len(seqs[a])*len(seqs[b]) for a,b in pairs),seconds_21_scans=elapsed,projected_total_seconds=elapsed/21*(1998+28*198+29),tiny_cases=100)
 (O/'pilot.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
def fresh_runes(panel,rng):
 out=[]
 for seq in panel:
  n=sum(seq);r=[rng.randrange(29)]
  for _ in range(n-1):v=rng.randrange(28);r.append(v+(v>=r[-1]))
  out.append(r)
 return out
def controls():
 with gzip.open(B/'worker-f/F08-evidence.json.gz','rt') as f:sources=json.load(f)['sources']
 lookup={Path(s['path']).stem.replace('solved_',''):s for s in sources};out=[]
 for index in range(28):
  rng=random.Random(1708100+index);panel,background=permute(seqs,rng,0);metadata={}
  if index<24:
   length=[6,10,16][index//8];reverse=index%8>=4;eligible=[(a,b) for a,b in pairs if min(len(panel[a]),len(panel[b]))>=length];a,b=rng.choice(eligible);i=rng.randrange(len(panel[a])-length+1);j=rng.randrange(len(panel[b])-length+1);copy=panel[a][i:i+length];before=panel[b][j:j+length];panel[b][j:j+length]=copy[::-1] if reverse else copy
   metadata=dict(kind='planted_copy',length=length,reverse=reverse,left_page=ids[a],right_page=ids[b],left_start=i,right_start=j,copied_lengths=copy,replaced_lengths=before)
  else:
   sourcepairs=[('0_koan_1','0_loss_of_divinity'),('0_welcome','jpg107-167'),('0_loss_of_divinity','0_welcome'),('jpg107-167','0_koan_1')];names=sourcepairs[index-24];used=[]
   for dest,name in zip([0,1],names):
    s=lookup[name];n=len(panel[dest]);assert len(s['words'])>=n;panel[dest]=[len(w) for w in s['words'][:n]];used.append(dict(name=name,path=s['path'],sha256=s['sha256'],units=[0,n]))
   metadata=dict(kind='disjoint_source',sources=used)
  assert list(map(len,panel))==list(map(len,seqs));runes=fresh_runes(panel,rng);best,rows=scan(panel,True);record=dict(index=index,seed=1708100+index,metadata=metadata,lengths=panel,runes=runes,background_permutations=background,rune_total_deltas=[sum(x)-sum(y) for x,y in zip(panel,seqs)],max_units=best,matches=rows)
  save('control-'+str(index),record);cal=[]
  for family in [0,1]:
   nn=nulls(panel,f'control-{index}-null-{family}',99,1709000+100*index+family,family);nn['tail']=(1+sum(v>=best for v in nn['stats']))/100;cal.append(nn)
  out.append(dict(index=index,metadata=metadata,max_units=best,nulls=cal,rune_total_deltas=record['rune_total_deltas']));print(json.dumps(dict(control=index,max=best,tails=[x['tail'] for x in cal])),flush=True)
 return out
def full():
 guard();real,rows=scan(seqs,True)
 for row in rows:
  a=ids.index(row['left_page']);b=ids.index(row['right_page'])
  for span in row['spans']:span['left_source_units']=[maps[a]['words'][i] for i in span['left_units']];span['right_source_units']=[maps[b]['words'][i] for i in span['right_units']]
 save('real-evidence',dict(map_sha256=hashlib.sha256(MAP.read_bytes()).hexdigest(),pages=ids,lengths=seqs,pairs=[[ids[a],ids[b]] for a,b in pairs],max_units=real,matches=rows));cal=[]
 for family in [0,1]:
  nn=nulls(seqs,'real-null-'+str(family),999,1708001+family,family);nn['tail']=(1+sum(v>=real for v in nn['stats']))/1000;cal.append(nn);print(json.dumps(dict(real=real,family=family,tail=nn['tail'])),flush=True)
 cc=controls();out=dict(real_max=real,real_nulls=cal,controls=cc,total_panels=1+1998+28*(1+198),pair_orientation_scans=(1+1998+28*(1+198))*66)
 (O/'result.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':pilot() if sys.argv[1]=='pilot' else full()
