from pathlib import Path
import gzip,json,re,ast,collections,math,numpy as np,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parents[3]
module=ast.parse((ROOT/'liber-primus/src/lp/gematria.py').read_text());table=None
for st in module.body:
 if isinstance(st,(ast.Assign,ast.AnnAssign)):
  targets=st.targets if isinstance(st,ast.Assign) else [st.target]
  if any(isinstance(t,ast.Name) and t.id=='GEMATRIA' for t in targets):table=ast.literal_eval(st.value)
assert table
D={v[2]:v[0] for v in table};D.update(V=1,K=5,Q=5,Z=15)
def independent(s):
 s=s.upper();r=[];sp=[];i=0
 while i<len(s):
  n=2 if s[i:i+2] in D else 1
  assert s[i:i+n] in D
  r.append(D[s[i:i+n]]);sp.append([i,i+n]);i+=n
 return r,sp
train=json.load(gzip.open(O/'train-maps.json.gz','rt'));raw=(O/'pg218.txt').read_bytes().decode('utf-8-sig');held=json.load(gzip.open(O/'held-controls.json.gz','rt'));hr=(O/'pg227.txt').read_bytes().decode('utf-8-sig')
expected=[(m.start(),m.end()) for m in re.finditer('[A-Za-z]+',raw) if m.start()>=train['body'][0] and m.end()<=train['body'][1] and not any(m.start()>=a and m.end()<=b for a,b in train['excluded_headings'])]
assert expected==[(w['start'],w['end']) for w in train['words']]
count=0
for words,text in [(train['words'],raw)]+[(h['words'],hr) for h in held]:
 for w in words:
  a,b=w['start'],w['end'];assert text[a:b]==w['text'];r,sp=independent(text[a:b]);assert r==w['runes'];assert [[a+x,a+y] for x,y in sp]==w['rune_char_spans'];count+=1
for h in held:
 p=[];ends=[];sp=[]
 for w in h['words']:p+=w['runes'];ends.append(len(p)-1);sp+=w['rune_char_spans']
 assert p==h['indices'] and ends==h['ends'] and sp==h['rune_char_spans']
for i,h in enumerate(held):
 for g in held[i+1:]:assert h['words'][-1]['end']<g['words'][0]['start']
seq=[29,29]+[x for w in train['words'] for x in w['runes']+[29]]
a=np.zeros(30,dtype=np.int64);b=np.zeros((30,30),dtype=np.int64);c=np.zeros((30,30,30),dtype=np.int64)
for i in range(2,len(seq)):a[seq[i]]+=1;b[seq[i-1],seq[i]]+=1;c[seq[i-2],seq[i-1],seq[i]]+=1
base=(a+.5)/(sum(a)+15);big=(b+8*base[None,:])/(b.sum(1)[:,None]+8);tri=(c+5*big[None,:,:])/(c.sum(2)[:,:,None]+5)
actual=np.load(O/'model.npz')['logp'];err=float(np.max(np.abs(np.log(tri)-actual)));assert err<1e-12
stored=json.load(gzip.open(O/'counts.json.gz','rt'))
for ix,arr in enumerate([a,b,c]):
 for row in stored[ix]:assert int(arr[tuple(row['key'])])==row['count']
 assert len(stored[ix])==np.count_nonzero(arr)
meta=json.loads((O/'model.json').read_text())
for name,h in meta['hashes'].items():assert hashlib.sha256((O/name).read_bytes()).hexdigest()==h
out=dict(status='PASS',words_checked=count,train_tokens=len(seq)-2,logprob_cells=27000,max_logprob_error=err,held_sources=4,held_runes=[len(h['indices']) for h in held],limitations='Independent implementation shares declared GP table and downloaded sources; classical Latin training does not establish puzzle language or universal Latin power.')
(O/'independent-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
