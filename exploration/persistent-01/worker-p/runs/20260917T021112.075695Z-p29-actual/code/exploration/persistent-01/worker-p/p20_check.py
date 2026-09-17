from pathlib import Path
import json,gzip,itertools,random,hashlib,re
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'exploration/persistent-01/worker-p/P20'
assert not (P.parents[1]/'STOP').exists()
def read(f):
 with gzip.open(f,'rt') as x:return json.load(x)
def clause_sat(c,a):return any(a.get(abs(v)-1)==(v>0) for v in c)
def checkproof(cs,r):
 used=set();leafs=0;branches=0
 def visit(node,assignment):
  nonlocal leafs,branches
  a=dict(assignment)
  for ci,lit in node['trail']:
   used.add(ci);c=cs[ci]
   assert not clause_sat(c,a)
   free={v for v in c if abs(v)-1 not in a}
   assert free=={lit};a[abs(lit)-1]=lit>0
  if 'conflict' in node:
   used.add(node['conflict']);c=cs[node['conflict']]
   assert all(abs(v)-1 in a and a[abs(v)-1]!=(v>0) for v in c);leafs+=1;return False
  if node.get('sat'):
   assert r['status']=='SAT' and all(clause_sat(c,a) for c in cs);return True
  v=node['variable'];assert v not in a and 0<=v<29;branches+=1
  zero=visit(node['zero'],a|{v:False})
  if r['status']=='UNSAT':assert 'one' in node
  one=visit(node['one'],a|{v:True}) if 'one' in node else False
  return zero or one
 if r['status']=='UNKNOWN':return dict(status='UNKNOWN')
 found=visit(r['proof'],{});assert found==(r['status']=='SAT')
 if found:
  a=dict(enumerate(map(bool,r['witness'])));assert all(clause_sat(c,a) for c in cs)
 return dict(status=r['status'],branches=branches,conflict_leaves=leafs,used_clause_ids=sorted(used))
original={p['page']:p for p in json.loads((ROOT/'exploration/persistent-01/worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]}
small=read(P/'small-exhaustive.json.gz')
for x in small:
 checkproof(x['clauses'],x['result'])
 truth=any(all(clause_sat(c,dict(enumerate(a))) for c in x['clauses']) for a in itertools.product([False,True],repeat=8))
 assert truth==(x['result']['status']=='SAT')
rows=[]
for f in sorted(P.glob('*.json.gz')):
 if f.name=='small-exhaustive.json.gz':continue
 r=read(f);cs=[];maps=[]
 for page in r['pages']:
  s=page['indices']
  for length in (3,6):
   for offset in range(len(s)-length+1):
    sign=-1 if length==3 else 1
    cs.append(sorted({sign*(v+1) for v in s[offset:offset+length]}))
    maps.append((page['page'],offset,length,s[offset:offset+length]))
 assert cs==r['clauses']
 assert maps==[(m['page'],m['start'],m['length'],m['indices']) for m in r['clause_maps']]
 info=checkproof(cs,r);info['name']=f.name
 if f.name.startswith('actual'):
  for page in r['pages']:assert page['indices']==original[page['page']]['indices']
  for m in r['clause_maps']:assert m['source_char_positions']==original[m['page']]['source_char_positions'][m['start']:m['start']+m['length']]
 if f.name.startswith('null'):
  rng=random.Random(r['seed'])
  for page in r['pages']:
   o=original[page['page']]['indices'];s=[o[0]]
   for i in range(1,len(o)):
    s.append(s[-1] if o[i]==o[i-1] else [k for k in range(29) if k!=s[-1]][rng.randrange(28)])
   assert s==page['indices']
 if 'bins' in r:
  roles={v:k for k,vs in r['bins'].items() for v in vs}
  s=sum([p['indices'] for p in r['pages']],[])
  assert ''.join(roles[v] for v in s)==r['trits']
  truth=[int(roles[v]=='g') for v in range(29)]
  assert all(any(bool(truth[abs(v)-1])==(v>0) for v in c) for c in cs)
  info['separator_assignment_errors_vs_truth']=sum(x!=y for x,y in zip(truth,r['witness']))
  info['planted_gap_ids']=r['bins']['g'];info['found_gap_ids']=[i for i,v in enumerate(r['witness']) if v]
  assert all(a!=b for a,b in zip(s,s[1:]))
 rows.append(info)
 if f.name=='actual-joint.json.gz':
  core=[cs[i] for i in info['used_clause_ids']]
  # Whole refutation used only these original clauses; map core to coordinates without minimizing.
  (P/'refutation-used-core.json').write_text(json.dumps([dict(id=i,clause=cs[i],source=r['clause_maps'][i]) for i in info['used_clause_ids']],indent=2)+'\n')
(P/'independent-check.json').write_text(json.dumps(dict(pass_all=True,small_cases=200,rows=rows),indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k!='used_clause_ids'} for x in rows]))
