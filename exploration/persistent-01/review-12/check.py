"""Independent scalar audit; does not import P's scripts or run optimizer."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import json,gzip,math,hashlib,statistics,itertools
D=Path('exploration/persistent-01/worker-p/P05');O=Path('exploration/persistent-01/review-12')
def read(p):
 return json.load(gzip.open(p,'rt') if str(p).endswith('.gz') else open(p))
inputs=[]
def load(p):
 inputs.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});return read(p)
def close(a,b):assert abs(a-b)<1e-8,(a,b)
model=load(D/'model.json'); manifest=load(D/'MANIFEST.json')
bad=[]
for r in manifest:
 p=Path(r['path'])
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:bad.append(r['path'])
assert not bad,bad
abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
latin='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
alphabet='BCDFGHJLMNPRSTWXY'; sources=[];rowcount=0
for s in model['sources']:
 p=Path(s['path']);raw=p.read_text();assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
 inputs.append({'path':str(p),'sha256':s['sha256']});seq=[];rows=[]
 for pos,c in enumerate(raw):
  if c not in abc:continue
  for off,ch in enumerate(latin[abc.index(c)]):
   keep=ch not in 'AEIOU';rows.append(dict(source_char=pos,rune=abc.index(c),offset=off,char=ch,keep=keep,index=len(seq) if keep else None))
   if keep:seq.append(alphabet.index(ch))
 assert rows==s['map'] and seq==s['seq'];sources.append(seq);rowcount+=len(rows)
un=Counter();bi=Counter();tri=Counter()
for s in sources[:5]:
 un.update(s);bi.update(zip(s,s[1:]));tri.update(zip(s,s[1:],s[2:]))
u=[(un[a]+.5)/(sum(un.values())+17*.5) for a in range(17)]
bp={(a,b):(bi[a,b]+4*u[b])/(sum(bi[a,c] for c in range(17))+4) for a in range(17) for b in range(17)}
t={(a,b,c):(tri[a,b,c]+4*bp[b,c])/(sum(tri[a,b,d] for d in range(17))+4) for a in range(17) for b in range(17) for c in range(17)}
for a in range(17):close(math.log(u[a]),model['u'][a])
for key,v in t.items():
 a,b,c=key;close(math.log(v),model['tri'][(a*17+b)*17+c])
for a,b in itertools.product(range(17),repeat=2):close(sum(t[a,b,c] for c in range(17)),1)
def lm(mapping,cipher):
 seq=[mapping[x] for x in cipher]
 return [math.log(u[v]) if i<2 else math.log(t[seq[i-2],seq[i-1],v]) for i,v in enumerate(seq)]
def branch(k,prev):
 out=[F(0)]*k
 for draw in range(k):
  if draw==prev and k>1:
   out[draw]+=F(1,k)*F(17,100)
   for other in range(k):
    if other!=draw:out[other]+=F(1,k)*F(83,100)*F(1,k-1)
  else:out[draw]+=F(1,k)
 assert sum(out)==1
 return out
finite=[]
for k in range(1,13):
 for prev in range(-1,k):
  probs=branch(k,prev)
  for r in range(k):
   formula=F(1,k) if prev<0 or k==1 else F(17,100*k) if r==prev else F(1,k)+F(83,100*k*(k-1))
   assert probs[r]==formula
  finite.append(dict(k=k,prev=prev,probs=list(map(str,probs))))
def em(mapping,cipher):
 bins={v:[i for i,x in enumerate(mapping) if x==v] for v in set(mapping)};terms=[]
 for i,r in enumerate(cipher):
  group=bins[mapping[r]];prev=cipher[i-1] if i else None
  probs=branch(len(group),group.index(prev) if prev in group else -1)
  terms.append(math.log(float(probs[group.index(r)])))
 return terms
evidence=load(D/'emission-evidence.json.gz');erows={r['label']:r for r in evidence['records']}
packets={};controls=[];valid=accepted=0;termschecked=0
for p in sorted(D.glob('*.json.gz')):
 if not p.name.startswith(('real-','null-','control-')):continue
 r=load(p);packets[r['label']]=r;c=r['cipher'];cut=r['cut'];assert cut==2*len(c)//3
 e=erows[r['label']];joint=[]
 assert len(r['alternatives'])==8
 for idx,a in enumerate(r['alternatives']):
  assert set(a['map'])==set(range(17));terms=lm(a['map'],c);ems=em(a['map'],c);ee=e['saved_candidates'][idx]
  for x,y in zip(terms,a['terms']):close(x,y)
  for x,y in zip(ems,ee['emission_terms']):close(x,y)
  close(sum(terms[:cut]),a['score']);close(sum(terms[:cut]),a['prefix_total'])
  close(sum(terms[cut:])/(len(c)-cut),a['suffix_conditional'])
  close(sum(terms[i]-math.log(u[a['map'][c[i]]]) for i in range(cut,len(c)))/(len(c)-cut),a['suffix_gain'])
  assert a['decoded']==[a['map'][v] for v in c]
  joint.append(sum(terms[:cut])+sum(ems[:cut]));close(joint[-1],ee['prefix_joint'])
  assert 0<=a['accepted']<=a['valid_proposals']<=5000
  accepted+=a['accepted'];valid+=a['valid_proposals'];termschecked+=len(c)
 assert r['selected']==max(range(8),key=lambda i:r['alternatives'][i]['prefix_total'])
 assert e['joint_selected']==max(range(8),key=joint.__getitem__)
 if 'control' in r:
  ct=r['control'];assert [ct['truth'][v] for v in c]==ct['plain'];assert Counter(ct['truth'])==dict(enumerate(ct['sizes']))
  tl=lm(ct['truth'],c);te=em(ct['truth'],c);truthjoint=sum(tl[:cut])+sum(te[:cut])
  close(sum(tl[:cut]),r['truth_score']['prefix_total']);close(truthjoint,e['truth_joint'])
  rank=1+sum(v>truthjoint+1e-9 for v in joint);assert rank==e['truth_joint_rank']
  assert r['truth_rank']==1+sum(a['prefix_total']>sum(tl[:cut])+1e-9 for a in r['alternatives'])
  best=r['alternatives'][r['selected']]['decoded'];acc=sum(x==y for x,y in zip(best,ct['plain']))/len(c)
  suffix=sum(best[i]==ct['plain'][i] for i in range(cut,len(c)))/(len(c)-cut)
  close(acc,r['accuracy']);close(suffix,r['suffix_accuracy'])
  controls.append(dict(label=r['label'],n=len(c),lm_rank=r['truth_rank'],joint_rank=rank,accuracy=acc,suffix_accuracy=suffix))
assert len(packets)==56 and len(controls)==16
samplers=load(D/'samplers.json.gz');swaps=0
for s in samplers:
 c=packets[f"real-{s['page']}"]['cipher'];z=c[:]
 for i,j in s['accepted_swaps']:
  assert z[i]!=z[j];edges=set(x for x in (i-1,i,j-1,j) if 0<=x<len(c)-1)
  before=sum(z[x]==z[x+1] for x in edges);z[i],z[j]=z[j],z[i]
  assert before==sum(z[x]==z[x+1] for x in edges);swaps+=1
 assert z==packets[f"null-{s['page']}-{s['rep']}"]['cipher'];assert len(s['accepted_swaps'])==100*len(c)
 assert Counter(c)==Counter(z);assert sum(a!=b for a,b in zip(c,z))==s['changed_positions']
tails={}
for page in (0,17):
 def selected(r):return r['alternatives'][r['selected']]['suffix_gain']
 rv=selected(packets[f'real-{page}']);tails[page]=(1+sum(selected(packets[f'null-{page}-{i}'])>=rv for i in range(19)))/20
result=dict(status='PASS',manifest_files=len(manifest),source_map_rows=rowcount,source_lengths=list(map(len,sources)),model_entries=17+17**3,finite_emission_cases=len(finite),packets=len(packets),restart_scores=56*8,terms_checked=termschecked,nominal_iterations=56*8*5000,valid_proposals=valid,accepted_proposals=accepted,accepted_swaps_replayed=swaps,tails=tails,controls=controls,median_accuracy=statistics.median(x['accuracy'] for x in controls),median_suffix_accuracy=statistics.median(x['suffix_accuracy'] for x in controls))
(O/'inputs.json').write_text(json.dumps(inputs,indent=2));(O/'results.json').write_text(json.dumps(result,indent=2));(O/'finite-emission.json').write_text(json.dumps(finite,indent=2));print(json.dumps(result,indent=2))
