from pathlib import Path
import json,gzip,hashlib,random,re,math,collections
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;P=B/'worker-p/P21';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';TR=[r['transliteration'] for r in json.loads((ROOT/'KNOWLEDGE.json').read_text())['gematria_primus']['table']];TRAIN=['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229'];(R/'snapshots').mkdir(exist_ok=True);inputs={};sources=[ROOT/'audit/parallel-01/reference/sources'/f'solved_{n}.txt' for n in TRAIN]
for path in list(P.iterdir())+[B/'worker-p/p21.py',B/'worker-c/p03_frozen.py',B/'worker-f/F06-maps.json']+sources:
 if path.is_file():
  raw=path.read_bytes();inputs[str(path)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
  if path.suffix!='.gz':(R/'snapshots'/path.name).write_bytes(raw)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
def words(raw):return [[ABC.index(ch) for ch in m.group()] for m in re.finditer('['+ABC+']+',raw)]
counts=[collections.Counter() for _ in range(3)];totals=[collections.Counter() for _ in range(3)]
for source in sources:
 tokens=[t for w in words(source.read_text()) for t in w+[29]];history=[29,29]
 for token in tokens:
  for order in [0,1,2]:
   context=tuple(history[-order:]) if order else ();counts[order][(context,token)]+=1;totals[order][context]+=1
  history.append(token)
def score(units):
 history=[29,29];total=0.;n=0
 for word in units:
  for t in word+[29]:
   p=(counts[0][((),t)]+.5)/(totals[0][()]+30*.5)
   for order,alpha in [(1,8),(2,5)]:
    context=tuple(history[-order:]);p=(counts[order][(context,t)]+alpha*p)/(totals[order][context]+alpha)
   total+=math.log(p);n+=1;history.append(t)
 return total/n if n else None
maxerr=0.;outputs=0

def check(units,phases,saved):
 global maxerr,outputs
 kept=[];discard=[];empty=[];out=[]
 for wi,(w,phase) in enumerate(zip(units,phases)):
  rotated=[(phase+j)%len(w) for j in range(len(w))];inside=rotated[1:len(w)-1] if len(w)>2 else [];kept.extend(dict(unit=wi,position=j) for j in inside);discard.extend(dict(unit=wi,position=j) for j in rotated if j not in inside)
  if inside:out.append([w[j] for j in inside])
  else:empty.append(wi)
 plain=[v for w in out for v in w];ends=[];n=0
 for w in out:n+=len(w);ends.append(n-1)
 assert saved['plain']==plain and saved['ends']==ends and saved['kept']==kept and saved['discarded']==discard and saved['empty_units']==empty and saved['units']==out and saved['origins']==phases;assert saved['transliteration']==' '.join(''.join(TR[v] for v in w) for w in out);sc=score(out);maxerr=max(maxerr,abs(sc-saved['score']));assert maxerr<1e-12;outputs+=1;return sc
controltails=[]
for i in range(4):
 z=json.load(gzip.open(P/f'control-{i}.json.gz','rt'));source=ROOT/z['source'];raw=source.read_text();assert hashlib.sha256(source.read_bytes()).hexdigest()==z['source_sha256'];ws=words(raw);spans=[[m.start(),m.end()] for m in re.finditer('['+ABC+']+',raw)];assert spans==z['source_word_char_spans'];rng=random.Random(521100+i);carrier=[[rng.randrange(29)]+w+[rng.randrange(29)] for w in ws];assert carrier==z['carrier'];actual=check(carrier,[0]*len(carrier),z['result']);assert z['result']['units']==ws;rng=random.Random(521200+i);ns=[]
 for saved in z['nulls']:
  phases=[rng.randrange(len(w)) for w in carrier];ns.append(check(carrier,phases,saved))
 tail=(1+sum(s>=actual for s in ns))/200;assert tail==z['tail'];controltails.append(tail)
a=json.load(gzip.open(P/'actual.json.gz','rt'));D=[p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,17]];units=[];actualscores=[];rows=[]
for p,inp,out in zip(D,a['inputs'],a['outputs']):
 u=[p['indices'][w['start']:w['end']] for w in p['words']];assert inp['units']==u and inp['unit_bounds']==[[w['start'],w['end']] for w in p['words']];units.append(u);actualscores.append(check(u,[0]*len(u),out['result']));maps=[]
 for role in ['kept','discarded']:
  for pos in out['result'][role]:
   index=p['words'][pos['unit']]['start']+pos['position'];maps.append(dict(role=role,**pos,source_rune_index=index,source_char_position=p['source_char_positions'][index],rune=p['indices'][index]))
 assert maps==out['maps'];assert sorted(m['source_rune_index'] for m in maps)==list(range(len(p['indices'])));rows.append(dict(page=p['page'],retained=len(out['result']['plain']),discarded=len(out['result']['discarded']),empty=len(out['result']['empty_units']),boundary_tokens=len(out['result']['ends']),score=actualscores[-1],denominator=len(out['result']['plain'])+len(out['result']['ends'])))
rng=random.Random(521300);maximum=max(actualscores);exceed=0
for i,panel in enumerate(a['nulls']):
 scores=[]
 for u,saved in zip(units,panel['results']):scores.append(check(u,[rng.randrange(len(w)) for w in u],saved))
 assert panel['rep']==i and abs(panel['maximum']-max(scores))<1e-12;exceed+=max(scores)>=maximum
assert len(a['nulls'])==999 and abs(a['maximum']-maximum)<1e-12 and (1+exceed)/1000==a['tail'];assert outputs==2800
out={'status':'PASS','complete_outputs':outputs,'max_score_error':maxerr,'control_tails':controltails,'actual':rows,'null_panel_exceedances':exceed,'tail':a['tail'],'training_sources':[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources]};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
