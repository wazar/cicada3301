import p08 as p
import random,math,json,unicodedata,re
p.gate();models,env,cells,parse=p.setup();brute=[]
for name,model in models.items():
 env['lm']=model
 for ix in range(40):
  rng=random.Random(334108+ix);key=[rng.randrange(4) for _ in range(14)];c=[rng.randrange(4) for _ in range(4)];ends={1,3};sign=[-1,1][ix%2];paths=[]
  def rec(i,j,plain,ts):
   if i==len(c):
    sc=model.score(plain,ends)*6+sum(ts)*math.log(.83)+sum(c[z]==c[z-1] for z in range(1,4))*math.log(.17);paths.append((sc,plain,ts,j));return
   for accept in range(j,len(key),2):
    if i==0 and accept!=j:continue
    x=(c[i]+sign*key[accept])%29;reject=list(range(j,accept,2))
    if reject and any((x-sign*key[z])%29!=c[i-1] for z in reject):continue
    rec(i+1,accept+1,plain+[x],ts+[len(reject)])
  rec(0,0,[],[]);paths.sort(reverse=True,key=lambda x:x[0]);d=env['decode'](c,ends,dict(key=key,sign=sign),retain=16);assert len(d['alternatives'])==min(16,len(paths));assert all(abs(a['joint_total']-b[0])<1e-10 for a,b in zip(d['alternatives'],paths));brute.append(dict(model=name,case=ix,paths=len(paths),max=paths[0][0]))
# Rebuild mapped rune strings directly from raw source positions, independent of maptext.
scount=0;rcount=0
for name,src in p.read('sources').items():
 f=p.ROOT/src['path'];assert p.sha(f)==src['sha256'];s=f.read_text()
 for q in src['selected']:
  a,b=q['span'];assert s[a:b]==q['text'];seen=[]
  for cm in q['characters']:
   assert s[cm['position']]==cm['character'];v=s[cm['position']].upper().replace('Æ','AE').replace('Œ','OE');v=''.join(x for x in unicodedata.normalize('NFKD',v) if not unicodedata.combining(x));v=v.translate(str.maketrans({'J':'I','V':'U','K':'C','Q':'C','Z':'S'}));assert v==cm['normalized'];seen.append(cm['position']);scount+=1
  assert set(seen)|{x['position'] for x in q['removed']}==set(range(a,b))
  assert not(set(seen)&{x['position'] for x in q['removed']})
  for w in q['words']:
   x,y=w['rune_span'];assert ''.join(p.TABLE[r]['transliteration'] for r in q['plain'][x:y])==w['normalized']
   # Direct left-to-right maximal token lengths reproduce entire word's rune IDs.
   text=w['normalized'];rr=[]
   while text:
    token=text[:2] if text[:2] in p.TR else text[:1];rr.append(p.TR[token]);text=text[len(token):]
   assert rr==q['plain'][x:y]
  assert q['ends']==[w['rune_span'][1]-1 for w in q['words']];rcount+=len(q['plain'])
# Replay all completed search outputs directly, without transition helper.
rowschecked=0;nullchecked=0
for label in ['control-'+str(i) for i in range(4)]+['real-0','real-17']:
 d=p.read(label+'-batch');pack=d['packet'];c=pack['cipher'];ends=set(pack['ends']);rng=random.Random(d['seed'])
 for n in d['nulls']:
  gen=[rng.randrange(29)]
  for i in range(1,len(c)):
   if c[i]==c[i-1]:gen.append(gen[-1])
   else:
    v=rng.randrange(28);gen.append(v+(v>=gen[-1]))
  assert gen==n['cipher'];nullchecked+=1
 for cipher,rows in [(c,d['observed'])]+[(n['cipher'],n['models']) for n in d['nulls']]:
  for modelname,result in rows.items():
   model=models[modelname]
   for row in result:
    cell=next(k for k in cells if k['id']==row['id']);a=row['decode']['alternatives'][0];j=0
    for i,(x,r,t) in enumerate(zip(cipher,a['plain'],a['reject_counts'])):
     for z in range(t):assert i and (r-cell['sign']*cell['key'][j+2*z])%29==cipher[i-1]
     j+=2*t;assert (r-cell['sign']*cell['key'][j])%29==x;j+=1
    assert j==a['used'];total=model.score(a['plain'],ends)*(len(c)+len(ends))+sum(a['reject_counts'])*math.log(.83)+sum(cipher[i]==cipher[i-1] for i in range(1,len(c)))*math.log(.17);assert abs(total-a['joint_total'])<1e-8;rowschecked+=1
p.dump('check',dict(status='PASS',brute=brute,source_characters=scount,mapped_runes=rcount,search_rows_replayed=rowschecked,null_rng_replayed=nullchecked));print('PASS',scount,rcount,rowschecked,nullchecked)
