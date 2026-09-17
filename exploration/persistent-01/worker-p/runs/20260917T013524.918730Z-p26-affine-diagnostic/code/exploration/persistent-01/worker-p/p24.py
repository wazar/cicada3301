from pathlib import Path
import json,gzip,random,itertools,time,datetime,sys,importlib.util,re,hashlib
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'exploration/persistent-01';P=B/'worker-p/P24'
spec=importlib.util.spec_from_file_location('gp',ROOT/'liber-primus/src/lp/gematria.py');gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)
FORBIDDEN=[tuple(x['pair']) for x in json.loads((B/'worker-p/P23/independent-certificate.json').read_text())['forbidden_pair_certificates']]
def guard():
 assert not (B/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):
 b=json.dumps(x,separators=(',',':')).encode()
 if n.endswith('.gz'):
  with gzip.open(P/n,'wb') as f:f.write(b)
 else:(P/n).write_bytes(b+b'\n')
def graph(units,n=29):
 obs=set();count={};witness={}
 for item in units:
  r=item['runes']
  for k,(a,b) in enumerate(zip(r,r[1:])):
   obs.add((a,b));count[(a,b)]=count.get((a,b),0)+1
   if (a,b) not in witness:witness[(a,b)]=dict(page=item['page'],unit=item['unit'],unit_positions=[k,k+1],source_rune_indices=item.get('source_rune_indices',[])[k:k+2],source_char_positions=item.get('source_char_positions',[])[k:k+2])
 absent={(a,b) for a in range(n) for b in range(n) if a!=b and (a,b) not in obs}
 return absent,dict(observed=[dict(pair=list(e),count=count[e],witness=witness[e]) for e in sorted(obs)],absent=[list(e) for e in sorted(absent)],absent_outdegree=[sum(a==i for a,b in absent) for i in range(n)],absent_indegree=[sum(b==i for a,b in absent) for i in range(n)])
def embed(edges,target,n):
 active=sorted({x for e in edges for x in e});out={x:sum(a==x for a,b in edges) for x in active};inc={x:sum(b==x for a,b in edges) for x in active}
 domains={x:[y for y in range(n) if sum(a==y for a,b in target)>=out[x] and sum(b==y for a,b in target)>=inc[x]] for x in active};start=time.monotonic();nodes=0
 def possible(x,y,m):
  if y in m.values():return False
  return all((y,m[b]) in target for a,b in edges if a==x and b in m) and all((m[a],y) in target for a,b in edges if b==x and a in m)
 def search(m):
  nonlocal nodes
  nodes+=1
  if nodes>1000000 or time.monotonic()-start>120:raise TimeoutError
  if len(m)==len(active):return dict(witness=m.copy()),m
  ds={x:[y for y in domains[x] if possible(x,y,m)] for x in active if x not in m};x=min(ds,key=lambda z:(len(ds[z]),-out[z]-inc[z],z));node=dict(variable=x,domain=ds[x],children=[])
  for y in ds[x]:
   child,w=search(m|{x:y});node['children'].append(dict(value=y,proof=child))
   if w is not None:return node,w
  return node,None
 try:
  tree,w=search({});status='SAT' if w is not None else 'UNSAT'
 except TimeoutError:tree=w=None;status='UNKNOWN'
 return dict(status=status,active=active,pattern_edges=[list(e) for e in edges],pattern_outdegree=out,pattern_indegree=inc,initial_domains=domains,witness=w,proof=tree,nodes=nodes,seconds=time.monotonic()-start)
def verify(edges,target,n,r):
 if r['status']!='SAT':return
 m={int(k):v for k,v in r['witness'].items()};assert len(set(m.values()))==len(m) and all(0<=v<n for v in m.values()) and all((m[a],m[b]) in target for a,b in edges)
def controls():
 guard();rng=random.Random(524900);tiny=[]
 for i in range(100):
  n=rng.randrange(2,7);k=rng.randrange(2,n+1);e=[(a,b) for a in range(k) for b in range(k) if a!=b and rng.random()<.3];t={(a,b) for a in range(n) for b in range(n) if a!=b and rng.random()<.5}
  r=embed(e,t,n);verify(e,t,n,r);active=sorted({x for p in e for x in p});truth=False
  for values in itertools.permutations(range(n),len(active)):
   m=dict(zip(active,values))
   if all((m[a],m[b]) in t for a,b in e):truth=True;break
  assert (r['status']=='SAT')==truth;tiny.append(dict(n=n,edges=e,target=sorted(t),result=r))
 save('tiny-controls.json.gz',tiny);rows=[]
 pages=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page'])
 for ix,name in enumerate(['0_welcome','jpg107-167','p56_an_end','p57_parable']):
  f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=f.read_text();words=[]
  for m in re.finditer('['+''.join(gp.RUNES)+']+',raw):words.append(gp.keyword_to_indices(''.join(gp.RUNE_TO_TRANS[x] for x in m.group())))
  perm=list(range(29));random.Random(524100+ix).shuffle(perm)
  units=[dict(page=page['page'],unit=j,runes=[perm[v] for v in w]) for page in pages for j,w in enumerate(words)]
  target,g=graph(units);r=embed(FORBIDDEN,target,29);verify(FORBIDDEN,target,29,r);assert r['status']=='SAT'
  mapping={int(k):v for k,v in r['witness'].items()};rest=iter(sorted(set(range(29))-set(mapping.values())))
  full=[mapping[i] if i in mapping else next(rest) for i in range(29)];inv={v:i for i,v in enumerate(full)}
  for w in words:
   decoded=[inv[perm[v]] for v in w];assert gp.keyword_to_indices(''.join(gp.IDX_TO_TRANS[v] for v in decoded))==decoded
  result=dict(name=name,source=str(f.relative_to(ROOT)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),words=words,planted_permutation=perm,full_found_permutation=full,units=units,graph=g,result=r)
  save('control-'+str(ix)+'.json.gz',result);rows.append(dict(name=name,nodes=r['nodes'],seconds=r['seconds'],active_mapping_errors=sum(mapping[i]!=perm[i] for i in mapping),absent_edges=len(target)))
 save('controls-summary.json',dict(tiny=100,rows=rows));print((P/'controls-summary.json').read_text())
def actual():
 assert (P/'controls-summary.json').exists();pages=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page'])
 assert len(pages)==45 and not set(p['page'] for p in pages)&{4,9,14,19,24,29,34,39,44,50,54}
 units=[]
 for page in pages:
  for j,w in enumerate(page['words']):
   start,end=w['start'],w['end'];units.append(dict(page=page['page'],unit=j,runes=page['indices'][start:end],source_rune_indices=list(range(start,end)),source_char_positions=page['source_char_positions'][start:end]))
 target,g=graph(units);r=embed(FORBIDDEN,target,29);verify(FORBIDDEN,target,29,r)
 save('actual.json.gz',dict(pages=[p['page'] for p in pages],units=units,graph=g,result=r));save('summary.json',dict(status=r['status'],nodes=r['nodes'],seconds=r['seconds'],pattern_active_vertices=len(r['active']),absent_edges=len(target),max_absent_outdegree=max(g['absent_outdegree']),max_absent_indegree=max(g['absent_indegree']),initial_domains=r['initial_domains']));print((P/'summary.json').read_text())
if __name__=='__main__':
 guard();t=time.monotonic();{'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
