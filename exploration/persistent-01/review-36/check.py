from pathlib import Path
import json,hashlib,random,math,collections
import numpy as np
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;P=B/'worker-p/P22';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';D=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page']);assert len(D)==45 and not {4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in D};(R/'snapshots').mkdir(exist_ok=True);manifest={}
for path in list(P.glob('*.npz'))+list(P.glob('*.json'))+[P/'CARD.md',B/'worker-p/p22.py',B/'worker-f/F06-maps.json']:
 raw=path.read_bytes();manifest[str(path)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
 if path.suffix!='.npz':(R/'snapshots'/path.name).write_bytes(raw)
(R/'inputs.json').write_text(json.dumps(manifest,indent=2))

def read(name):
 z=json.loads((P/(name+'.json')).read_text());a=np.load(P/(name+'.npz'));lengths=list(map(int,a['lengths']));assert lengths==[len(p['indices']) for p in D];seqs=[];offset=0
 for n in lengths:seqs.append(list(map(int,a['cipher'][offset:offset+n])));offset+=n
 return z,a,seqs
maxscoreerr=0.;panelcount=0;seedcounts=collections.Counter();results={}
def verify(name,expected):
 global maxscoreerr,panelcount
 z,a,seqs=read(name);assert seqs==expected;train=[];held=[];scores=[];flatlength=sum(map(len,seqs));replay=np.full((32,flatlength),255,dtype=np.uint8)
 for lag in range(1,33):
  counts=[collections.Counter(),collections.Counter()];off=0
  for i,s in enumerate(seqs):
   suffix=[(value-s[j-lag])%29 for j,value in enumerate(s) if j>=lag];counts[int(i>=23)].update(suffix);replay[lag-1,off+lag:off+len(s)]=suffix;off+=len(s)
  c=[counts[0][j] for j in range(29)];h=[counts[1][j] for j in range(29)];q=[(v+1)/(sum(c)+29) for v in c];sc=sum(h[j]*math.log(29*q[j]) for j in range(29))/sum(h);train.append(c);held.append(h);scores.append(sc);assert np.max(abs(np.array(q)-z['q'][lag-1]))<1e-15
 assert np.array_equal(replay,a['decoded']);assert train==z['train_counts'] and held==z['held_counts'];maxscoreerr=max(maxscoreerr,float(np.max(abs(np.array(scores)-z['scores']))));assert maxscoreerr<1e-12;winner=max(range(32),key=lambda i:scores[i]);assert winner+1==z['selected_lag'];assert abs(scores[winner]-z['maximum'])<1e-12;panelcount+=1;return z,seqs

def weights(seqs):
 counts=collections.Counter(v for s in seqs[:23] for v in s);den=sum(counts.values())+29;return [(counts[i]+1)/den for i in range(29)]
def simulate(seqs,w,seed):
 rng=random.Random(seed);out=[]
 for s in seqs:
  result=[s[0]]
  for a,b in zip(s,s[1:]):
   if a==b:result.append(result[-1]);continue
   allowed=[i for i in range(29) if i!=result[-1]];draw=rng.random()*sum(w[i] for i in allowed);subtotal=0
   for i in allowed:
    subtotal+=w[i]
    if draw<subtotal:result.append(i);break
   else:raise AssertionError('CDF endpoint')
  assert [a==b for a,b in zip(result,result[1:])]==[a==b for a,b in zip(s,s[1:])];out.append(result)
 return out
for ix in range(4):
 name=f'control-{ix}';z,arr,seqs=read(name);source=ROOT/z['source'];raw=source.read_text();positions=[i for i,ch in enumerate(raw) if ch in ABC];plain=[ABC.index(raw[i]) for i in positions];assert positions==z['source_char_positions'] and plain==z['source_runes'];assert hashlib.sha256(source.read_bytes()).hexdigest()==z['source_sha256'];rng=random.Random(522100+ix);lag=[1,8,16,32][ix];cipher=[]
 for p,mp in zip(D,z['maps']):
  start=rng.randrange(len(plain));seeds=[rng.randrange(29) for _ in range(lag)];indices=[(start+i)%len(plain) for i in range(len(p['indices']))];pp=[plain[i] for i in indices];cc=[]
  for i,v in enumerate(pp):cc.append((v+(seeds[i] if i<lag else cc[i-lag]))%29)
  assert mp==dict(page=p['page'],source_start=start,source_indices=indices,source_chars=[positions[i] for i in indices],seed=seeds,plain=pp);cipher.append(cc)
 z,seqs=verify(name,cipher);w=weights(seqs);nullmax=[]
 for j in range(99):
  seed=522200+100*ix+j;seedcounts[seed]+=1;nz,_=verify(f'{name}-null-{j:03}',simulate(seqs,w,seed));assert nz['seed']==seed and np.max(abs(np.array(nz['weights'])-w))<1e-15;nullmax.append(nz['maximum'])
 saved=json.loads((P/(name+'-summary.json')).read_text());tail=(1+sum(v>=z['maximum'] for v in nullmax))/100;rank=1+sum(s>z['scores'][lag-1] for s in z['scores']);assert saved['tail']==tail and saved['rank']==rank;results[name]=saved
z,seqs=verify('actual',[p['indices'] for p in D]);assert z['source_maps']==[dict(page=p['page'],source_char_positions=p['source_char_positions']) for p in D];w=weights(seqs);nullmax=[]
for j in range(199):
 seed=522300+j;seedcounts[seed]+=1;nz,_=verify(f'actual-null-{j:03}',simulate(seqs,w,seed));assert nz['seed']==seed and np.max(abs(np.array(nz['weights'])-w))<1e-15;nullmax.append(nz['maximum'])
summary=json.loads((P/'summary.json').read_text());assert summary['null_maxima']==nullmax and summary['tail']==(1+sum(v>=z['maximum'] for v in nullmax))/200;assert panelcount==600
out={'status':'PASS','panels':panelcount,'lag_fits':panelcount*32,'max_score_error':maxscoreerr,'actual_selected_lag':z['selected_lag'],'actual_maximum':z['maximum'],'actual_tail':summary['tail'],'actual_train_counts_by_lag':[sum(x) for x in z['train_counts']],'actual_held_counts_by_lag':[sum(x) for x in z['held_counts']],'controls':results,'null_seed_draws':sum(seedcounts.values()),'distinct_null_seeds':len(seedcounts),'reused_null_seeds':[k for k,v in seedcounts.items() if v>1]};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='reused_null_seeds'},indent=2))
