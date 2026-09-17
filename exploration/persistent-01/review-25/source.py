from pathlib import Path
import json,gzip,re,hashlib
R=Path(__file__).parent;P=R.parent/'worker-p/P17';b=(P/'pg45315.txt').read_bytes();assert hashlib.sha256(b).hexdigest()=='fc9a76619fcb76c58273d7fc9e034108b0d7fffed3780ad5b8226954a12b289a';raw=b.decode('utf-8-sig');a=raw.index('THE ARGUMENT');z=raw.index('For everything that lives is holy.',a)+len('For everything that lives is holy.')
trans='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split();idx={x:i for i,x in enumerate(trans)};alias={'V':1,'K':5,'Z':15,'Q':5};digraph={x:i for x,i in idx.items() if len(x)==2};saved=json.load(gzip.open(P/'source.json.gz','rt'));words=[];runes=[];rune_maps=[]
for wi,m in enumerate(re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",raw[a:z])):
 text=m.group();letters=[(ch.upper(),a+m.start()+i) for i,ch in enumerate(text) if ch not in "'’"];r=[];j=0
 while j<len(letters):
  token=''.join(x[0] for x in letters[j:j+2]);take=2 if token in digraph else 1;token=''.join(x[0] for x in letters[j:j+take]);v=idx[token] if token in idx else alias[token];r.append(v);rune_maps.append({'word':wi,'word_rune':len(r)-1,'rune_id':v,'source_character_positions':[x[1] for x in letters[j:j+take]]});j+=take
 words.append({'span':[a+m.start(),a+m.end()],'text':text,'runes':r});runes.extend(r)
assert words==saved['words'] and raw==saved['raw'] and [len(w['runes']) for w in words]==saved['lengths'];assert [words[0]['span'][0],words[-1]['span'][1]]==saved['body_span']
out={'status':'PASS','raw_sha256':hashlib.sha256(b).hexdigest(),'rune_bytes_sha256':hashlib.sha256(bytes(runes)).hexdigest(),'rune_count':len(runes),'word_count':len(words),'body_span':saved['body_span'],'words':words,'runes':runes,'rune_maps':rune_maps};
with gzip.open(R/'source-replay.json.gz','wt') as f:json.dump(out,f)
print({k:v for k,v in out.items() if k not in ['words','runes','rune_maps']})
