from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import json,math,hashlib,random
O=Path(__file__).resolve().parent;MP=O.parents[0]/'worker-p/P05/model.json';M=json.loads(MP.read_text())
def branch(mapping,prev,current):
 group=[i for i,v in enumerate(mapping) if v==mapping[current]];prob=F(0)
 for initial in group:
  if initial==prev and len(group)>1:
   if current==initial:prob+=F(1,len(group))*F(17,100)
   if current!=initial:prob+=F(1,len(group))*F(83,100)*F(1,len(group)-1)
  elif initial==current:prob+=F(1,len(group))
 return prob
def score(mapping,cipher,cut):
 plain=[mapping[x] for x in cipher];lm=[];em=[]
 for i,c in enumerate(cipher):
  a=plain[i];lm.append(M['u'][a] if i<2 else M['tri'][(plain[i-2]*17+plain[i-1])*17+a]);em.append(math.log(float(branch(mapping,cipher[i-1] if i else None,c))))
 return dict(plain=plain,lm_terms=lm,emission_terms=em,prefix_lm=sum(lm[:cut]),prefix_emission=sum(em[:cut]),prefix_joint=sum(lm[:cut])+sum(em[:cut]),suffix_joint=sum(lm[cut:])+sum(em[cut:]))
rows=[]
for size in range(1,14):
 mapping=list(range(17))+[0]*(size-1)+[1]*(13-size);assert len(mapping)==29;group=[i for i,v in enumerate(mapping) if v==0]
 for prev in group+[1]:
  for current in group:
   cipher=[2,prev,current,3,3,1];cut=3;rows.append(dict(id=len(rows),mapping=mapping,cipher=cipher,cut=cut,expected=score(mapping,cipher,cut),kind='all-bin-branches',binsize=size))
rng=random.Random(1717001)
for rep in range(64):
 mapping=list(range(17))+[rng.randrange(17) for _ in range(12)];rng.shuffle(mapping);cipher=[rng.randrange(29) for _ in range(15)];cut=10;rows.append(dict(id=len(rows),mapping=mapping,cipher=cipher,cut=cut,expected=score(mapping,cipher,cut),kind='random-complete-map'))
mapping=list(range(17))+[0]*12;changed=mapping[:];changed[28]=2;c=[0,1,2,0,1,2];before=score(mapping,c,6);after=score(changed,c,6);assert before['plain']==after['plain'] and before['prefix_lm']==after['prefix_lm'] and before['prefix_emission']!=after['prefix_emission']
out=dict(model_path=str(MP),model_sha256=hashlib.sha256(MP.read_bytes()).hexdigest(),fixtures=rows,unused_rune_witness=dict(cipher=c,moved_rune=28,map_before=mapping,map_after=changed,before=before,after=after))
(O/'fixtures.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(fixtures=len(rows),unused_emission_delta=after['prefix_emission']-before['prefix_emission'])))
