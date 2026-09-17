from pathlib import Path
import json,gzip,hashlib,collections,math,re,ast
import numpy as np
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;P=B/'coordinator/Q05-latin';meta=json.loads((P/'model.json').read_text());raws={n:(P/n).read_bytes().decode('utf-8-sig') for n in ['pg218.txt','pg227.txt']};maps=json.load(gzip.open(P/'train-maps.json.gz','rt'));held=json.load(gzip.open(P/'held-controls.json.gz','rt'));(R/'snapshots').mkdir(exist_ok=True);inputs={}
for path in P.iterdir():
 if path.is_file():
  b=path.read_bytes();inputs[str(path)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
  if path.suffix not in ['.npz','.gz']:(R/'snapshots'/path.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
for n,h in meta['hashes'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h
for entry in json.loads((P/'retrieval.json').read_text()):
 path=P/entry['url'].rsplit('/',1)[1];assert len(path.read_bytes())==entry['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'];assert entry['status']==200
# Independent table extraction + trie maximal munch, preserving decoded-string coordinates.
tree=ast.parse((ROOT/'liber-primus/src/lp/gematria.py').read_text());table=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GEMATRIA' for t in n.targets));lex={t:i for i,r,t,p in table}|{'V':1,'K':5,'Q':5,'Z':15};trie={}
for s,v in lex.items():
 node=trie
 for c in s:node=node.setdefault(c,{})
 node['value']=v

def tokens(raw,start,end,exclude):
 words=[];i=start
 while i<end:
  if not ('A'<=raw[i]<='Z' or 'a'<=raw[i]<='z'):i+=1;continue
  j=i+1
  while j<end and ('A'<=raw[j]<='Z' or 'a'<=raw[j]<='z'):j+=1
  if not any(a<=i and j<=b for a,b in exclude):
   text=raw[i:j];upper=text.upper();ids=[];spans=[];pos=0
   while pos<len(upper):
    node=trie;at=pos;last=None
    while at<len(upper) and upper[at] in node:
     node=node[upper[at]];at+=1
     if 'value' in node:last=(at,node['value'])
    stop,v=last;ids.append(v);spans.append([i+pos,i+stop]);pos=stop
   words.append(dict(text=text,start=i,end=j,runes=ids,rune_char_spans=spans))
  i=j
 return words
raw=raws['pg218.txt'];start=raw.index('GALLIA est omnis');end=raw.index('*** END OF THE PROJECT GUTENBERG');assert [start,end]==meta['train_body']==maps['body'];offset=0;headingranges=[];headinglines=[]
for line in raw.splitlines(keepends=True):
 if start<=offset<end and line.strip().startswith('C. IULI CAESARIS DE BELLO GALLICO COMMENTARIUS '):headingranges.append([offset,offset+len(line)]);headinglines.append(line.strip())
 offset+=len(line)
assert len(headingranges)==3;words=tokens(raw,start,end,headingranges);assert words==maps['words'];assert len(words)==meta['train_words'] and sum(len(w['runes']) for w in words)==meta['train_runes']
raw2=raws['pg227.txt'];headers=[];offset=0
for line in raw2.splitlines(keepends=True):
 text=line.strip()
 if text.startswith('LIBER ') and set(text[6:])<=set('IVX'):headers.append((text[6:],offset,offset+len(line)))
 offset+=len(line)
assert len(headers)==12
for book,control in zip(['I','IV','VII','X'],held):
 ii=next(i for i,row in enumerate(headers) if row[0]==book);_,a,b=headers[ii];stop=headers[ii+1][1] if ii+1<len(headers) else raw2.index('*** END OF THE PROJECT GUTENBERG');ws=tokens(raw2,b,stop,[])[:60];assert ws==control['words'] and len(ws)==60;flat=[v for w in ws for v in w['runes']];ends=[];n=0
 for w in ws:n+=len(w['runes']);ends.append(n-1)
 assert flat==control['indices'] and ends==control['ends'] and [s for w in ws for s in w['rune_char_spans']]==control['rune_char_spans']
spans=[(c['words'][0]['start'],c['words'][-1]['end']) for c in held];assert all(b<=c or d<=a for i,(a,b) in enumerate(spans) for c,d in spans[i+1:])

def counts(ws):
 C=[collections.Counter() for _ in range(3)];history=[29,29];n=0
 for word in ws:
  for value in word['runes']+[29]:
   for order in [0,1,2]:C[order][tuple(history[-order:])+(value,) if order else (value,)]+=1
   history.append(value);n+=1
 return C,n
C,n=counts(words);savedcounts=json.load(gzip.open(P/'counts.json.gz','rt'))
for order in range(3):assert [{'key':list(k),'count':v} for k,v in sorted(C[order].items())]==savedcounts[order]
assert n==meta['train_tokens'];lp=np.load(P/'model.npz')['logp'];maxerr=0.;normalization=0.
def makeprobs(C,n):
 result=np.empty((30,30,30))
 for a in range(30):
  for b in range(30):
   bigtotal=sum(C[1][b,x] for x in range(30));tritotal=sum(C[2][a,b,x] for x in range(30))
   for x in range(30):
    p0=(C[0][x,]+.5)/(n+15);p1=(C[1][b,x]+8*p0)/(bigtotal+8);p2=(C[2][a,b,x]+5*p1)/(tritotal+5);result[a,b,x]=math.log(p2)
 return result
expected=makeprobs(C,n);maxerr=float(np.max(abs(expected-lp)));assert maxerr<1e-14;normalization=float(np.max(abs(np.exp(lp).sum(axis=2)-1)));assert normalization<1e-12
legacy=raw.index("End of Project Gutenberg's",start);footer=[w for w in words if w['start']>=legacy];assert legacy==150887 and len(footer)==16 and sum(len(w['runes']) for w in footer)==59;cleanwords=[w for w in words if w['start']<legacy];cleanC,cleann=counts(cleanwords);cleanlp=makeprobs(cleanC,cleann)
# Targeted metadata/English-marker scan, not a proof of language identity for every token.
pattern=re.compile(r'\b(?:Project|Gutenberg|Produced|Copyright|License|English|Translation|Contents|Commentaries|Books|End|of|the|with|from|and|by|this|that)\b',re.I);markers=[dict(text=m.group(),start=m.start(),end=m.end(),inside_legacy_footer=m.start()>=legacy) for m in pattern.finditer(raw,start,end)];nonascii=[dict(character=c,position=i,inside_legacy_footer=i>=legacy) for i,c in enumerate(raw) if start<=i<end and c.isalpha() and ord(c)>127];assert all(x['inside_legacy_footer'] for x in nonascii)
np.savez_compressed(R/'independent-clean-expected.npz',logp=cleanlp)
out={'status':'MODEL_REPLAY_PASS_SOURCE_BOUNDARY_DEFECT','train_words':len(words),'train_runes':sum(len(w['runes']) for w in words),'train_tokens':n,'held_words':sum(len(c['words']) for c in held),'held_runes':[len(c['indices']) for c in held],'probabilities_checked':27000,'max_logp_error':maxerr,'max_row_normalization_error':normalization,'headings':headinglines,'legacy_footer_start':legacy,'legacy_footer_text':raw[legacy:end],'included_footer_words':footer,'footer_tokens':n-cleann,'expected_clean_words':len(cleanwords),'expected_clean_runes':sum(len(w['runes']) for w in cleanwords),'expected_clean_tokens':cleann,'max_abs_logp_change_on_cleaning':float(np.max(abs(cleanlp-lp))),'targeted_English_marker_scan':markers,'nonASCII_alphabetic_body':nonascii,'interpretation':'Targeted source scan, not exhaustive linguistic proof. Original model unchanged; expected cleaned model only under own review directory.'};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['included_footer_words','targeted_English_marker_scan','nonASCII_alphabetic_body']},indent=2))
