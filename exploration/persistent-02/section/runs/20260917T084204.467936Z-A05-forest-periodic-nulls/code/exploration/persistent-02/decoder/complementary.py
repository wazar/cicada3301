"""One frozen complementary English/rune trigram, independent source authors."""
import re,math,collections,json,hashlib,pathlib,sys,gzip,argparse
from compare import ROOT,O,run,references,section
sys.path.insert(0,str(ROOT/'liber-primus/src'));from lp.gematria import keyword_to_indices
SPEC=[('emerson_essays_first_series','There is a time'),('poe_tales_vol2','True!—nervous'),('plato_republic_jowett','I went down yesterday'),('melville_moby_dick','Call me Ishmael')]
def freeze():
 out=O/'complementary-model.json';assert not out.exists();records=[]
 for name,needle in SPEC:
  f=ROOT/'liber-primus/data/keys/armada18'/(name+'.txt');raw=f.read_text();start=raw.index(needle);matches=list(re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",raw[start:]))[:1000];assert len(matches)==1000
  spans=[[start+m.start(),start+m.end()] for m in matches];words=[m.group() for m in matches];runes=[];ends=[]
  for word in words:runes.extend(keyword_to_indices(re.sub("['’]",'',word)));ends.append(len(runes)-1)
  excerpt=raw[start:spans[-1][1]];assert 'Gutenberg' not in excerpt and '{Picture:' not in excerpt
  records.append(dict(path=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),span=[start,spans[-1][1]],word_spans=spans,raw_excerpt=excerpt,runes=runes,ends=ends,words=len(words)))
 obj=dict(id='P02-complementary-v1',sources=records,formula='same interpolated P03 orders/smoothing .5/8/5, but four external authors 1000 words each, GP greedy mapping and true lexical word ends; context resets per source',exclusions='Guest, Mill, Shelley, Blake and all LP texts excluded from training',frozen_before='complementary reference/fresh/section evaluation',limits='Corpus AND transliteration/boundary preprocessing differ from P03; joint change, not attribution solely to source diversity. First1000 body words avoid headings/furniture, exact spans retained. No hyperparameter search.')
 out.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(dict(model_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),sources=[dict(path=s['path'],runes=len(s['runes']),span=s['span']) for s in records])))
class LM:
 def __init__(self):
  data=json.loads((O/'complementary-model.json').read_text());self.c=[collections.Counter() for _ in range(3)];self.t=[collections.Counter() for _ in range(3)];self.cache={}
  for source in data['sources']:
   s=(29,29);ends=set(source['ends'])
   for i,r in enumerate(source['runes']):
    for x in ([r,29] if i in ends else [r]):
     for n in range(3):ctx=s[-n:] if n else ();self.c[n][ctx+(x,)]+=1;self.t[n][ctx]+=1
     s=(s[1],x)
 def step(self,s,x):
  key=s+(x,)
  if key not in self.cache:
   v=(self.c[0][(x,)]+.5)/(self.t[0][()]+15)
   for n,alpha in [(1,8),(2,5)]:ctx=s[-n:];v=(self.c[n][ctx+(x,)]+alpha*v)/(self.t[n][ctx]+alpha)
   self.cache[key]=math.log(v)
  return (s[1],x),self.cache[key]
 def extend(self,s,r,end):
  s,v=self.step(s,r)
  if end:s,w=self.step(s,29);v+=w
  return s,v
 def score(self,p,ends):
  s=(29,29);v=0.
  for i,r in enumerate(p):s,w=self.extend(s,r,i in ends);v+=w
  return v/(len(p)+len(ends))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','references','fresh','section']);a=ap.parse_args()
 if a.action=='freeze':return freeze()
 lm=LM();cases=references() if a.action=='references' else section() if a.action=='section' else json.loads((O/'fresh-controls.json').read_text())['cases'];out=O/('complementary-'+a.action);out.mkdir(exist_ok=True)
 for case in cases:
  result=run(case,lm,retain=16 if a.action=='section' else 256);(out/(case['id']+'.json.gz')).write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0));print(json.dumps(dict(id=case['id'],score=result['exact'][0]['score'],truth=result.get('truth_metrics'),beam_gaps={w:b['gap'] for w,b in result['beams'].items()},seconds=result['seconds'],maxrss_bytes=result['maxrss_bytes'])),flush=True)
if __name__=='__main__':main()
