import pathlib,json,gzip,re,unicodedata,hashlib,ast,collections,math,random,datetime,time,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];R=pathlib.Path(__file__).parent/'P08'
S=.83
SOURCES={'caesar':'liber-primus/analysis/latin/latin_218.txt','newton':'liber-primus/analysis/latin/latin_28233.txt','virgil':'liber-primus/data/keys/armada19/virgil_aeneid_latin.txt'}
def gate():
 assert not(ROOT/'exploration/persistent-01/STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):
 (R/(n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def save(n,x):
 with gzip.open(R/(n+'.json.gz'),'wt') as f:json.dump(x,f)
def read(n):
 with gzip.open(R/(n+'.json.gz'),'rt') as f:return json.load(f)
TABLE=json.loads((ROOT/'KNOWLEDGE.json').read_text())['gematria_primus']['table'];TR={x['transliteration']:x['index'] for x in TABLE};TOK=sorted(TR,key=lambda x:(-len(x),TR[x]))
def maptext(s,offset):
 runes=[];ends=[];words=[];charmap=[];rmap=[]
 for m in re.finditer(r'A+', ''.join('A' if unicodedata.category(c).startswith('L') else ' ' for c in s)):
  chars=[];pos=[]
  for j,c in enumerate(s[m.start():m.end()]):
   v=c.upper().replace('Æ','AE').replace('Œ','OE');v=''.join(x for x in unicodedata.normalize('NFKD',v) if not unicodedata.combining(x));v=v.translate(str.maketrans({'J':'I','V':'U','K':'C','Q':'C','Z':'S'}));assert all('A'<=x<='Z' for x in v),(c,v)
   sourcepos=offset+m.start()+j;charmap.append(dict(position=sourcepos,character=c,normalized=v));chars.extend(v);pos.extend([sourcepos]*len(v))
  word=''.join(chars);i=0;start=len(runes)
  while i<len(word):
   t=next(t for t in TOK if word.startswith(t,i));runes.append(TR[t]);rmap.append(dict(index=len(runes)-1,rune=TR[t],latin=t,source_positions=pos[i:i+len(t)]));i+=len(t)
  ends.append(len(runes)-1);words.append(dict(source_span=[offset+m.start(),offset+m.end()],normalized=word,rune_span=[start,len(runes)]))
 letterpos={x['position'] for x in charmap};removed=[dict(position=offset+i,character=c) for i,c in enumerate(s) if offset+i not in letterpos]
 return dict(plain=runes,ends=ends,words=words,characters=charmap,rune_map=rmap,removed=removed)
def prepare():
 gate();out={};held=[]
 for name,path in SOURCES.items():
  p=ROOT/path;s=p.read_text();anchors={'caesar':('GALLIA est omnis','End of Project Gutenberg'), 'newton':('_Cum Veteres','_FINIS._'),'virgil':('ARMA virumque cano','Updated editions')}[name];a=s.index(anchors[0]);b=s.index(anchors[1],a);body=s[a:b];paragraphs=[]
  starts=[0]+[m.end() for m in re.finditer(r'\n[ \t]*\n',body)];stops=[m.start() for m in re.finditer(r'\n[ \t]*\n',body)]+[len(body)]
  for pi,(x,y) in enumerate(zip(starts,stops)):
   if not body[x:y].strip():continue
   mapped=maptext(body[x:y],a+x);paragraphs.append(dict(paragraph_index=pi,span=[a+x,a+y],text=body[x:y],**mapped))
   if name!='caesar' and sum(80<=len(q['plain'])<=400 for q in paragraphs)==2:break
  if name=='caesar':selected=paragraphs
  else:
   selected=[x for x in paragraphs if 80<=len(x['plain'])<=400][:2];assert len(selected)==2
   for v in selected:held.append(dict(source=name,**v))
  out[name]=dict(path=path,sha256=sha(p),raw_bytes=len(p.read_bytes()),normalized_chars=len(s),body_span=[a,b],anchors=anchors,selected=selected,paragraph_inventory=[dict(index=x['paragraph_index'],span=x['span'],n=len(x['plain']),selected=x in selected) for x in paragraphs])
 save('sources',out);save('held',held);dump('source-summary',{k:{x:v[x] for x in ['path','sha256','raw_bytes','normalized_chars','body_span']}|dict(paragraphs=len(v['selected']),runes=sum(len(x['plain']) for x in v['selected']),first_selected=[dict(index=x['paragraph_index'],span=x['span'],n=len(x['plain'])) for x in v['selected'][:2]]) for k,v in out.items()});print((R/'source-summary.json').read_text())
def setup():
 ns=dict(pathlib=pathlib,json=json,re=re,math=math,collections=collections,hashlib=hashlib,ROOT=ROOT,TRAIN=['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229'],ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ')
 src=ROOT/'exploration/persistent-01/worker-c/p03_frozen.py';tree=ast.parse(src.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['parse','LM']],type_ignores=[]),str(src),'exec'),ns)
 English=ns['LM'];eng=English();lat=English.__new__(English);lat.c=[collections.Counter() for _ in range(3)];lat.t=[collections.Counter() for _ in range(3)];lat.cache={};lat.files=[read('sources')['caesar']['path']]
 for q in read('sources')['caesar']['selected']:
  ctx=(29,29);ends=set(q['ends'])
  for i,r in enumerate(q['plain']):
   for x in ([r,29] if i in ends else [r]):
    for n in range(3):z=ctx[-n:] if n else ();lat.c[n][z+(x,)]+=1;lat.t[n][z]+=1
    ctx=(ctx[-1],x)
 models={'latin':lat,'english':eng};m=ROOT/'exploration/persistent-01/worker-m/M25/m25.py';env=dict(random=random,math=math,collections=collections,S=S);tree=ast.parse(m.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['encoder','transitions','decode','replay']],type_ignores=[]),str(m),'exec'),env)
 cells=json.loads((m.parent/'keys.json').read_text());assert len(cells)==4 and all(len(c['key'])==1024 for c in cells)
 return models,env,cells,ns['parse']
def search(c,ends,model,env,cells):
 env['lm']=model;rows=[]
 for cell in cells:
  d=env['decode'](c,set(ends),cell);assert d['feasible'];a=d['alternatives'][0];u,walk=env['replay'](c,a['plain'],a['reject_counts'],cell['key'],cell['sign'],2);assert u==a['used'];a['walk']=walk;rows.append(dict(id=cell['id'],score=a['score'],decode=d))
 rows.sort(key=lambda x:x['score'],reverse=True);return rows

def controls(which):
 models,env,cells,parse=setup();hs=read('held');summary=[]
 for ix in which:
  gate();h=hs[ix];cell=cells[ix];seed=330108+ix;c,events,used=env['encoder'](h['plain'],cell['key'],cell['sign'],seed);rejects=[len(x['rejected']) for x in events];f=dict(held_index=ix,cell=cell['id'],cipher=c,events=events,used=used,seed=seed,plain=h['plain'],ends=h['ends']);results={};t=time.monotonic()
  for name,model in models.items():
   rows=search(c,h['ends'],model,env,cells);best=rows[0]['decode']['alternatives'][0];tr=next(x for x in rows if x['id']==cell['id']);ta=tr['decode']['alternatives'][0]
   results[name]=dict(rows=rows,key_correct=rows[0]['id']==cell['id'],key_rank=1+sum(x['score']>tr['score'] for x in rows),best_errors=sum(a!=b for a,b in zip(best['plain'],h['plain'])),correctkey_errors=sum(a!=b for a,b in zip(ta['plain'],h['plain'])),path_correct=best['reject_counts']==rejects,used_correct=best['used']==used,truth_lm=model.score(h['plain'],set(h['ends'])),truth_joint=(model.score(h['plain'],set(h['ends']))*(len(c)+len(h['ends']))+sum(rejects)*math.log(S)+sum(c[i]==c[i-1] for i in range(1,len(c)))*math.log(1-S))/(len(c)+len(h['ends'])))
  save('control-'+str(ix),dict(fixture=f,results=results));row=dict(index=ix,source=h['source'],n=len(c),rejections=sum(rejects),seconds=time.monotonic()-t,models={k:{a:b for a,b in v.items() if a!='rows'} for k,v in results.items()});summary.append(row);dump('control-summary-'+str(ix),row);print(json.dumps(row),flush=True)
if __name__=='__main__':
 {'prepare':prepare,'pilot':lambda:controls([0]),'controls':lambda:controls([1,2,3])}[sys.argv[1]]()
