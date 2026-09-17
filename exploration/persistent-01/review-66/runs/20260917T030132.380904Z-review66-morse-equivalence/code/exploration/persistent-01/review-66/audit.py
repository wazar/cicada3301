import os
for x in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[x]='1'
from pathlib import Path
import json,gzip,hashlib,itertools,random,re,collections
O=Path('exploration/persistent-01/review-66');B=O.parent;D=B/'worker-n/N16';P=B/'worker-p/P20';F=B/'worker-f/F06-maps.json'
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in D.iterdir() if p.is_file()]+[F];snap={str(p):sha(p) for p in files};(O/'inputs.json').write_text(json.dumps(snap,indent=2))
# Explicit per-character table, independently arranged alphabetically.
mc={'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.'}
codes=set(mc.values());assert len(codes)==36 and max(map(len,codes))==5 and all('.'*k in codes for k in range(1,6))
prefix={v[:i] for v in codes for i in range(1,len(v)+1)};states=prefix|{'G1','G2'};trans={}
for state in states:
 for ch in '.-g':
  dest=None
  if state in ['G1','G2']:
   if ch in '.-' and ch in prefix:dest=ch
   elif ch=='g' and state=='G1':dest='G2'
  else:
   if ch in '.-' and state+ch in prefix:dest=state+ch
   elif ch=='g' and state in codes:dest='G1'
  trans[state,ch]=dest
def valid(t):
 active=set(states)
 for c in t:active={trans[s,c] for s in active if trans[s,c] is not None}
 return bool(active)
assert all(valid(t) for t in ['...g---g...','.-gg-...','-----g.----'])
# Exhaustive finite trit strings: binary feasibility is not equal to validity for
# every assignment, but the all-dot extension of any feasible binary stream works.
finite=0
for n in range(1,11):
 for bits in itertools.product([False,True],repeat=n):
  text=''.join('g' if b else '.' for b in bits);binary='ggg' not in text and '......' not in text
  assert valid(text)==binary;finite+=1
proofnodes=0
def prove(clauses,tree,n=29):
 def walk(node,dom):
  nonlocal_count[0]+=1;dom=dom.copy()
  for ci,v,new in node['trail']:
   cl=clauses[ci];lookup=dict(cl);assert v in lookup
   for a,m in cl:
    assert dom[a]&m
    if a!=v:assert dom[a]&~m==0
   want=dom[v]&~lookup[v];assert want and want==new and want!=dom[v];dom[v]=want
  if 'conflict' in node:
   assert all(dom[v]&~m==0 for v,m in clauses[node['conflict']]);return None
  if 'sat' in node:
   a=node['sat'];assert len(a)==n and all(dom[v]&(1<<x) for v,x in enumerate(a));assert all(any(not(m&(1<<a[v])) for v,m in cl) for cl in clauses);return a
  v=node['var'];allowed=[i for i in range(3) if dom[v]&(1<<i)];children=node['children'];assert len({x for x,_ in children})==len(children)
  result=None
  for value,child in children:
   assert value in allowed;dd=dom.copy();dd[v]=1<<value;w=walk(child,dd)
   if w is not None:assert result is None;result=w
  if result is None:assert sorted(x for x,_ in children)==allowed
  return result
 nonlocal_count=[0];result=walk(tree,[7]*n);return result,nonlocal_count[0]
def clauses_valid(r):
 c=r['cipher'];assert len(r['clauses'])==len(r['clause_maps'])
 for cl,mp in zip(r['clauses'],r['clause_maps']):
  start=mp['start'];ids=mp['runes'];req=mp['required_masks'];assert c[start:start+len(ids)]==ids
  combined={}
  for v,m in zip(ids,req):combined[v]=combined.get(v,7)&m
  assert all(combined.values()) and sorted(combined.items())==[tuple(x) for x in cl]
  if mp['source_char_positions'] is not None:assert mp['source_char_positions']==r['source_char_positions'][start:start+len(ids)]
  kind=mp['kind']
  if kind=='three-gaps':assert req==[4]*3
  elif kind=='six-marks':assert req==[3]*6
  else:
   assert all(x in [1,2,4] for x in req);text=''.join({1:'.',2:'-',4:'g'}[x] for x in req);assert not valid(text)
# Control source fixtures and masks, independent scalar RNG.
abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';latin=[v['transliteration'] for v in json.loads(Path('KNOWLEDGE.json').read_text())['gematria_primus']['table']];sources={};controlstats=[]
for i in range(4):
 f=load(P/f'control-{i}.json.gz');src=Path(f['source']);assert sha(src)==f['source_sha256'];raw=src.read_text();words=[''.join(latin[abc.index(v)] for v in m.group()) for m in re.finditer('['+abc+']+',raw)];assert words==f['words'];text='gg'.join('g'.join(mc[c] for c in word) for word in words);assert text==f['trits'] and valid(text)
 rng=random.Random(520100+i);ids=list(range(29));rng.shuffle(ids);bins={'.':ids[:10],'-':ids[10:20],'g':ids[20:]};assert bins==f['bins'];out=[]
 for t in text:out.append(rng.choice([v for v in bins[t] if not out or v!=out[-1]]))
 assert out==sum([p['indices'] for p in f['pages']],[]);sources[f'control-{i}']=out
pages={p['page']:p for p in json.loads(F.read_text()) if p['page'] in [0,1]}
for k in range(19):
 f=load(P/f'null-{k}.json.gz');rng=random.Random(520300+k)
 for ix in [0,1]:
  p=pages[ix];seq=[p['indices'][0]]
  for a,b in zip(p['indices'],p['indices'][1:]):seq.append(seq[-1] if a==b else rng.choice([v for v in range(29) if v!=seq[-1]]))
  assert seq==f['pages'][ix]['indices'];sources[f'null-{k}-{ix}']=seq
counts=collections.Counter();sat_extensions=0
for path in sorted(D.glob('*.json.gz')):
 if path.name=='tiny-exhaustive.json.gz':continue
 r=load(path);name=path.name[:-8];clauses_valid(r)
 if 'source_fixture' in r:assert sha(Path(r['source_fixture']))==r['source_sha256'] and r['cipher']==sources[name]
 else:
  p=pages[r['page']];assert r['cipher']==p['indices'] and r['source_char_positions']==p['source_char_positions']
 assert r['status'] in ['SAT','UNSAT'];w,n=prove(r['clauses'],r['proof']);proofnodes+=n;assert n==r['nodes'];assert (w is not None)==(r['status']=='SAT')
 if w is not None:
  assert w==r['map'];text=''.join('.-g'[w[v]] for v in r['cipher']);assert text==r['trits'] and valid(text)
  extension=''.join('g' if w[v]==2 else '.' for v in r['cipher']);assert valid(extension);sat_extensions+=1
  if name.startswith('control'):
   i=int(name.split('-')[1]);f=load(P/f'control-{i}.json.gz');assert r['planted_trits']==f['trits'];true={v:'.-g'.index(t) for t,vs in f['bins'].items() for v in vs};roleerrors=sum(w[v]!=true[v] for v in range(29));triterrors=sum(a!=b for a,b in zip(text,f['trits']));controlstats.append(dict(control=i,role_errors=roleerrors,trit_errors=triterrors))
 if 'second_map_result' in r:
  sr=r['second_map_result'];block=[(v,1<<r['map'][v]) for v in sorted(set(r['cipher']))];ww,n=prove(r['clauses']+[block],sr['proof']);proofnodes+=n;assert n==sr['nodes'] and ww==sr['map'];text=''.join('.-g'[ww[v]] for v in r['cipher']);assert valid(text) and text==sr['trits'] and text!=r['trits']
 if name.startswith('null'):counts[r['status']]+=1
# Tiny complete assignment truth table and proofs.
tinyassign=0
for t in load(D/'tiny-exhaustive.json.gz'):
 c=t['cipher'];n=max(c)+1;validcount=0
 for a in itertools.product(range(3),repeat=n):validcount+=valid(''.join('.-g'[a[v]] for v in c));tinyassign+=1
 assert validcount==t['valid'] and t['assignments']==3**n
 # Saved proof references clauses derived by the independent stream instances above;
 # tiny finite existence is checked exhaustively, no duplicated solver needed.
 assert (t['result']['status']=='SAT')==bool(validcount)
# Original binary witnesses extend directly, independent of N16 solutions.
for i in [0,1]:
 p=load(P/f'actual-page-{i}.json.gz');a=p['witness'];text=''.join('g' if a[v] else '.' for v in p['pages'][0]['indices']);assert valid(text)
assert all(sha(Path(p))==h for p,h in snap.items())
result=dict(pass_all=True,proof_nodes=proofnodes,tiny_assignments=tinyassign,binary_all_dot_strings=finite,SAT_extensions=sat_extensions,null_statuses=dict(counts),control_recovery=controlstats,lemma='Full feasibility iff binary gap relaxation because dot runs1..5 are E/I/S/H/5 and every code has<=5 marks; partial-edge framing preserved.',limits='No requirement both mark classes occur; no new feasibility coverage or plaintext recovery; tiny existence exhaustive, tiny proof trees not replayed.')
(O/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
