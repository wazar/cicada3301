import pathlib,sys,re,json,hashlib,random,gzip,argparse
from compare import ROOT,O,LM,run
sys.path.insert(0,str(ROOT/'liber-primus/src'));from lp.gematria import keyword_to_indices
SOURCES=[('guest','exploration/persistent-01/worker-h/sources/mabinogion_vol1_guest_edwards_ed.txt','King Arthur {15} was at Caerlleon','PEREDUR THE SON OF EVRAWC.'),('mill','liber-primus/data/keys/armada19/mill_on_liberty.txt','The subject of this Essay','CHAPTER II.'),('shelley','liber-primus/data/keys/armada19/shelley_frankenstein.txt','I am by birth a Genevese','Chapter 2'),('blake','exploration/persistent-01/worker-p/P17/pg45315.txt','Rintrah roars','*** END OF THE PROJECT GUTENBERG')]
def build():
 rng=random.Random(260917203);cases=[];sources=[]
 for si,(name,path,left,right) in enumerate(SOURCES):
  f=ROOT/path;raw=f.read_text();start=raw.index(left);stop=raw.index(right,start+len(left));body=raw[start:stop]
  # Remove brace-contained footnote and image furniture; body spans frozen before results.
  matches=[m for m in re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",body) if not any(a.start()<=m.start()<a.end() for a in re.finditer(r'\{[^}]*\}',body))]
  words=[keyword_to_indices(re.sub("['’]",'',m.group())) for m in matches];positions=[];flat=[];ends=[]
  for m,w in zip(matches,words):
   flat.extend(w);positions.extend([[start+m.start(),start+m.end()]]*len(w));ends.append(len(flat)-1)
  sources.append(dict(id=name,path=path,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),body_char_span=[start,stop],body_runes=len(flat),excluded='brace footnote/image spans; no headings selected in fixed excerpt windows'))
  for j,n in enumerate([249,515,716]):
   # Three predetermined non-overlapping source offsets, rounded to word starts.
   offset=next((e+1 for e in ends if e+1>=j*900),0) if j else 0;truth=flat[offset:offset+n];assert len(truth)==n
   ee={e-offset for e in ends if offset<=e<offset+n};ee.add(n-1);key=[rng.randrange(29) for _ in range([7,11,23][j])];sign=[-1,1,-1][j];periodic=j!=2
   if not periodic:key=[rng.randrange(29) for _ in range(n)]
   cipher=[];literal=[];u=0
   for i,p in enumerate(truth):
    lit=p==0 and rng.random()<.65
    if lit:cipher.append(0);literal.append(i)
    else:cipher.append((p-sign*key[u%len(key)])%29);u+=1
   cases.append(dict(id=f'fresh-{name}-{j}',cipher=cipher,ends=sorted(ee),key=key,sign=sign,periodic=periodic,truth=truth,truth_literal_positions=literal,source=name,source_rune_span=[offset,offset+n],source_char_spans=positions[offset:offset+n],seed=260917203))
 return dict(sources=sources,cases=cases,scope='12 deterministic excerpts from four authors; independent planted keys; not a random-language population power estimate; sources never used by P03 training. Physical source line wraps are not word boundaries.',preprocessing='GP greedy multi-letter rune aliases from pinned gematria; apostrophes removed; lexical word ends + final boundary. This differs from natural LP spelling and bounds recovery.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','run']);a=ap.parse_args();f=O/'fresh-controls.json'
 if a.action=='freeze':
  assert not f.exists();f.write_text(json.dumps(build(),indent=2)+'\n');print(f.relative_to(ROOT));return
 cases=json.loads(f.read_text())['cases'];out=O/'fresh';out.mkdir(exist_ok=True);lm=LM()
 for case in cases:
  result=run(case,lm,retain=256);(out/(case['id']+'.json.gz')).write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0));print(json.dumps(dict(id=case['id'],truth=result['truth_metrics'],gaps={w:b['gap'] for w,b in result['beams'].items()},seconds=result['seconds'],maxrss=result['maxrss_bytes'])),flush=True)
if __name__=='__main__':main()
