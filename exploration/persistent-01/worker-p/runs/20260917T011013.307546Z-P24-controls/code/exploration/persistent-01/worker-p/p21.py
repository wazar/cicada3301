from pathlib import Path
import sys,json,random,re,gzip,hashlib,datetime,time,importlib.util
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'exploration/persistent-01';OUT=BASE/'worker-p/P21'
spec=importlib.util.spec_from_file_location('p03',BASE/'worker-c/p03_frozen.py');p03=importlib.util.module_from_spec(spec);spec.loader.exec_module(p03)
ABC=p03.ABC;TRANS=[r['transliteration'] for r in json.loads((ROOT/'KNOWLEDGE.json').read_text())['gematria_primus']['table']]
def guard():
 assert not (BASE/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):
 b=json.dumps(x,separators=(',',':'),allow_nan=False).encode()
 if n.endswith('.gz'):
  with gzip.open(OUT/n,'wb') as f:f.write(b)
 else:(OUT/n).write_bytes(b+b'\n')
def extract(units,lm,origins=None):
 origins=[0]*len(units) if origins is None else origins
 plain=[];ends=set();kept=[];discarded=[];empty=[];outunits=[]
 for i,(unit,phase) in enumerate(zip(units,origins)):
  order=list(range(phase,len(unit)))+list(range(phase));keep=order[1:-1] if len(unit)>=3 else []
  kept.extend([dict(unit=i,position=j) for j in keep]);discarded.extend([dict(unit=i,position=j) for j in order if j not in keep])
  word=[unit[j] for j in keep]
  if word:plain.extend(word);ends.add(len(plain)-1);outunits.append(word)
  else:empty.append(i)
 return dict(origins=origins,plain=plain,ends=sorted(ends),kept=kept,discarded=discarded,empty_units=empty,units=outunits,score=lm.score(plain,ends) if plain else None,transliteration=' '.join(''.join(TRANS[r] for r in w) for w in outunits))
def nulls(units,lm,n,seed):
 rng=random.Random(seed);return [extract(units,lm,[rng.randrange(len(w)) for w in units]) for _ in range(n)]
def controls():
 guard();lm=p03.LM();rows=[]
 for ix,name in enumerate(p03.CHECK):
  f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=f.read_text();matches=list(re.finditer('['+ABC+']+',raw));words=[[ABC.index(x) for x in m.group()] for m in matches]
  rng=random.Random(521100+ix);carrier=[[rng.randrange(29)]+w+[rng.randrange(29)] for w in words]
  result=extract(carrier,lm);truth,ends=p03.parse(raw);assert result['plain']==truth and result['ends']==sorted(ends)
  ns=nulls(carrier,lm,199,521200+ix);tail=(1+sum(x['score']>=result['score'] for x in ns))/200
  r=dict(name=name,carrier=carrier,source=str(f.relative_to(ROOT)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_word_char_spans=[[m.start(),m.end()] for m in matches],seed=521100+ix,null_seed=521200+ix,result=result,nulls=ns,tail=tail,exact_recovery=True)
  save('control-'+str(ix)+'.json.gz',r);rows.append(dict(name=name,n=len(truth),carrier_length=sum(map(len,carrier)),units=len(carrier),score=result['score'],tail=tail))
 save('controls-summary.json',dict(rows=rows,lm_sources=lm.files));print(json.dumps(rows))
def actual():
 guard();assert (OUT/'controls-summary.json').exists();lm=p03.LM()
 pages=[p for p in json.loads((BASE/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,17]];pages.sort(key=lambda x:x['page'])
 inputs=[];outputs=[]
 for p in pages:
  units=[p['indices'][w['start']:w['end']] for w in p['words']]
  r=extract(units,lm);maps=[]
  for typ in ['kept','discarded']:
   for pos in r[typ]:
    w=p['words'][pos['unit']];index=w['start']+pos['position'];maps.append(dict(role=typ,**pos,source_rune_index=index,source_char_position=p['source_char_positions'][index],rune=p['indices'][index]))
  inputs.append(dict(page=p['page'],units=units,unit_bounds=[[w['start'],w['end']] for w in p['words']]))
  outputs.append(dict(page=p['page'],result=r,maps=maps))
 rng=random.Random(521300);panels=[]
 for i in range(999):
  if i%100==0:guard()
  rs=[extract(p['units'],lm,[rng.randrange(len(w)) for w in p['units']]) for p in inputs]
  panels.append(dict(rep=i,results=rs,maximum=max(x['score'] for x in rs)))
 maximum=max(x['result']['score'] for x in outputs);tail=(1+sum(x['maximum']>=maximum for x in panels))/1000
 save('actual.json.gz',dict(inputs=inputs,outputs=outputs,null_seed=521300,nulls=panels,maximum=maximum,tail=tail,lm_sources=lm.files))
 save('summary.json',dict(maximum=maximum,tail=tail,rows=[dict(page=x['page'],score=x['result']['score'],retained=len(x['result']['plain']),discarded=len(x['result']['discarded']),empty_units=len(x['result']['empty_units']),output=x['result']['transliteration']) for x in outputs]))
 print((OUT/'summary.json').read_text())
if __name__=='__main__':
 t=time.monotonic();{'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
