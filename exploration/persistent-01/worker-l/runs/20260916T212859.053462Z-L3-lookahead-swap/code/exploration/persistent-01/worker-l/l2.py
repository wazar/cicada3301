import pathlib,json,hashlib,gzip,collections,math,datetime,time
import numpy as np
O=pathlib.Path(__file__).resolve().parent;ROOT=O.parents[2];A='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';SEED=33012703

def guard():
 assert not (O.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def collapse(x):return [v for i,v in enumerate(x) if i==0 or v!=x[i-1]]
def pattern(x):
 seen={};p=[]
 for v in x:
  if v not in seen:seen[v]=len(seen)
  p.append(seen[v])
 return tuple(p)
def source_units(raw):
 chars=[(i,A.index(c)) for i,c in enumerate(raw) if c in A];words=[];start=0
 for j,((i,r),(ii,s)) in enumerate(zip(chars,chars[1:])):
  gap=raw[i+1:ii]
  if gap and not gap.isspace():words.append(collapse([r for i,r in chars[start:j+1]]));start=j+1
 if chars:words.append(collapse([r for i,r in chars[start:]]))
 return words
def fit(words):
 counts=collections.defaultdict(collections.Counter);pools=collections.defaultdict(list)
 for x in words:
  if len(x)>=3:counts[len(x)][pattern(x)]+=1;pools[len(x)].append(x)
 return counts,pools
def value(x,counts):
 n=len(x)
 if n not in counts:return None
 p=pattern(x);d=len(set(x));lnull=sum(math.log(29-j) for j in range(d))-math.log(29)-(n-1)*math.log(28);ps=counts[n][p]/sum(counts[n].values());return math.log(.9*ps+.1*math.exp(lnull))-lnull

def main():
 guard();t=time.monotonic();out=O/'l2';out.mkdir(exist_ok=True);rng=np.random.default_rng(SEED);cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());dataset=ROOT/'audit/parallel-01/inputs/dataset.json';assert hashlib.sha256(dataset.read_bytes()).hexdigest()==cfg['dataset_sha256'];allowed={p['original_page']:p['indices'] for p in json.loads(dataset.read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']};mapfile=ROOT/'exploration/persistent-01/worker-f/F06-maps.json';maps=sorted(json.loads(mapfile.read_text()),key=lambda p:p['page']);assert {p['page'] for p in maps}==set(allowed)
 sources=[]
 for f in sorted((ROOT/'audit/parallel-01/reference/sources').glob('solved_*.txt')):sources.append({'path':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'units':source_units(f.read_text())})
 counts,pools=fit([w for s in sources for w in s['units']]);rows=[]
 for pi,page in enumerate(maps):
  assert page['indices']==allowed[page['page']]
  for wi,w in enumerate(page['words']):
   raw=page['indices'][w['start']:w['end']];starts=[i for i in range(len(raw)) if i==0 or raw[i]!=raw[i-1]];runs=np.diff(starts+[len(raw)]).tolist();x=[raw[i] for i in starts];rows.append({'page':page['page'],'part':pi%2,'unit':wi,'source_start':w['start'],'source_end':w['end'],'raw':raw,'collapsed':x,'runs':runs,'eligible':len(x) in pools})
 dump(out/'inputs-and-maps.json',{'dataset_sha256':cfg['dataset_sha256'],'F06_maps_sha256':hashlib.sha256(mapfile.read_bytes()).hexdigest(),'seed':SEED,'sources':sources,'rows':rows})
 def score(xs,model=counts):
  sums=[0.,0.];ns=[0,0]
  for row,x in zip(rows,xs):
   v=value(x,model)
   if v is not None:sums[row['part']]+=v;ns[row['part']]+=1
  return sums,ns
 def nullword(n):
  x=[int(rng.integers(29))]
  for _ in range(n-1):
   z=int(rng.integers(28));x.append(z+(z>=x[-1]))
  return x
 controls=[];transfers=[];null=[]
 with gzip.open(out/'full-generated-output.jsonl.gz','wt') as f:
  for rep in range(20):
   guard();xs=[];meta=[]
   for row in rows:
    n=len(row['collapsed']);src=pools[n][int(rng.integers(len(pools[n])))] if n in pools else nullword(n);perm=rng.permutation(29);x=[int(perm[v]) for v in src];inv=np.argsort(perm);assert [int(inv[v]) for v in x]==list(src);assert pattern(x)==pattern(src);xs.append(x);meta.append({'source':src,'permutation':perm.tolist(),'expanded_output':np.repeat(x,row['runs']).tolist()})
   sc,ns=score(xs);controls.append(sc);f.write(json.dumps({'kind':'source-control','replicate':rep,'scores':sc,'metadata':meta})+'\n')
  for held,s in enumerate(sources):
   model,_=fit([w for j,other in enumerate(sources) if j!=held for w in other['units']]);_,pool=fit(s['units']);xs=[];used=[]
   for i,row in enumerate(rows):
    n=len(row['collapsed'])
    if n in pool and n in model:src=pool[n][int(rng.integers(len(pool[n])))];perm=rng.permutation(29);xs.append([int(perm[v]) for v in src]);used.append(i)
    else:xs.append([])
   sc,ns=score(xs,model);transfers.append({'source_held':held,'scores':sc,'eligible_counts':ns});f.write(json.dumps({'kind':'leave-source-out-transfer','source_held':held,'scores':sc,'eligible_counts':ns,'outputs':xs})+'\n')
  for rep in range(400):
   if rep%20==0:guard()
   xs=[nullword(len(r['collapsed'])) for r in rows];sc,ns=score(xs);null.append(sc);f.write(json.dumps({'kind':'conditional-null','replicate':rep,'scores':sc,'collapsed_outputs':xs})+'\n')
  real,ns=score([r['collapsed'] for r in rows]);arr=np.array(null);crit=float(np.quantile(arr[:,1],.99));p=(1+int(np.sum(arr[:,1]>=real[1])))/401;power=int(sum(c[1]>crit for c in controls));assert power==20,'source-control discrimination gate failed; no negative conclusion'
  result={'real_scores_train_held':real,'eligible_units_train_held':ns,'held_p':p,'null_99percentile':crit,'source_controls_detected':power,'source_control_n':20,'source_control_held_range':[min(c[1] for c in controls),max(c[1] for c in controls)],'null_held_range':[float(arr[:,1].min()),float(arr[:,1].max())],'leave_source_out_transfers':transfers,'excluded_collapsed_length_counts':dict(collections.Counter(len(r['collapsed']) for r in rows if not r['eligible'])),'hypotheses':1,'seconds':time.monotonic()-t};dump(out/'null-and-controls.json',{'null':null,'controls':controls});dump(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
