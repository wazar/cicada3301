from pathlib import Path
import json,gzip,random
R=Path(__file__).parent;B=R.parents[1];pages={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text())};src=pages[0]['indices']+pages[1]['indices'];c=json.load(gzip.open(R/'controls-repaired.json.gz','rt'));rng=random.Random(c['seed']);labels=list(range(29));rng.shuffle(labels);assert labels==c['labels'];mapping=dict(zip(c['patterns'],labels));reverse={v:k for k,v in mapping.items()};attempts=0
for row in c['controls']:
 for proposal in row['proposals']:
  start=rng.randrange(len(src));salt=rng.getrandbits(max(1,row['L']-1));assert start==proposal['source_start'] and salt==proposal['salt'];v=0
  for j in range(max(1,row['L']//4+1)):v=29*v+src[(start+j)%len(src)]
  x=(1<<(row['L']-1))|((v^salt)&((1<<(row['L']-1))-1));assert x==proposal['integer'];s=format(row['L'],'b');bits='0'*(len(s)-1)+s+format(x,'b')[1:];chunks=[int(bits[i:i+5],2) for i in range(0,len(bits),5)];assert chunks==proposal['chunks'] and all(v in mapping for v in chunks)==proposal['accepted'];attempts+=1
 assert row['proposals'][-1]['accepted'] and not any(p['accepted'] for p in row['proposals'][:-1]);bits=''.join(format(reverse[r],'05b') for r in row['runes']);assert bits==row['bits'] and len(bits)==5*row['n'];it=iter(bits);zeros=0
 for digit in it:
  if digit=='1':break
  zeros+=1
 L=1
 for _ in range(zeros):L=(L<<1)|int(next(it))
 number=1
 for _ in range(L-1):number=(number<<1)|int(next(it))
 assert next(it,None) is None and number==row['proposals'][-1]['integer']
a=json.loads((R/'actual.json').read_text());witnesses=[]
for panel in a['pages']:
 p=pages[panel['page']]
 for row in panel['all_units']:
  w=p['words'][row['word']];seq=p['indices'][w['start']:w['end']];assert w==row['map'] and seq==row['runes'] and len(seq)==row['length'];possible=[L for L in range(1,row['bits']+1) if L+2*len(bin(L)[3:])==row['bits']];assert (possible[0] if possible else None)==row['integer_bitlength']
 for row in panel['violations']:
  assert row['length']==8 and row['bits']==40 and row['lower_L']==31 and row['upper_L']==32 and row['lower_T']==39 and row['upper_T']==42;witnesses.append(dict(page=panel['page'],word=row['word'],rune_start=row['map']['start'],rune_end=row['map']['end'],source_char_positions=row['map']['source_char_positions']))
assert len(witnesses)==6
(R/'check-result.json').write_text(json.dumps(dict(status='PASS',repaired_controls=len(c['controls']),proposals=attempts,violating_witnesses=witnesses,excluded_control_patterns=c['excluded']),indent=2));print(len(c['controls']),attempts,witnesses)
