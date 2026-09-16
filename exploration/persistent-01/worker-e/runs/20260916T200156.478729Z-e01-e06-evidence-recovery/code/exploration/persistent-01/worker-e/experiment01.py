import json,re,random,time,hashlib,pathlib
ROOT=pathlib.Path(__file__).parent
D=json.load(open('audit/parallel-01/inputs/dataset.json')); A=D['alphabet']
primes=[x for x in range(2,110) if all(x%d for d in range(2,int(x**.5)+1))]; assert len(primes)==29
V=dict(zip(A,primes)); pat=re.compile('['+A+']+|[0-9]+')
def val(s):return int(s) if s.isdecimal() else sum(V[c] for c in s)
def linesums(a):return [sum(a[i*5:i*5+5]) for i in range(5)]+[sum(a[i::5]) for i in range(5)]+[sum(a[::6]),sum(a[4:21:4])]
def magic(a):
 s=sum(a[:5])
 if any(sum(a[i*5:i*5+5])!=s for i in range(1,5)):return False
 return len(set(linesums(a)))==1 and len(set(a))>1
def rank(a,p=29):
 m=[list(x%p for x in a[i*5:i*5+5]) for i in range(5)]; r=0
 for j in range(5):
  z=next((i for i in range(r,5) if m[i][j]),None)
  if z is None:continue
  m[r],m[z]=m[z],m[r]; iv=pow(m[r][j],-1,p);m[r]=[(x*iv)%p for x in m[r]]
  for i in range(5):
   if i!=r:
    q=m[i][j];m[i]=[(x-q*y)%p for x,y in zip(m[i],m[r])]
  r+=1
 return r
src=[]
for name in ['solved_0_wisdom.txt','solved_jpg229.txt']:
 f=pathlib.Path('audit/parallel-01/reference/sources')/name
 rows=[pat.findall(l) for l in f.read_text().splitlines()[-5:]];assert all(len(r)==5 for r in rows)
 cells=[val(t) for row in rows for t in row];src.append({'source':str(f),'tokens':rows,'values':cells,'line_sums':linesums(cells),'magic':magic(cells),'rank_mod29':rank(cells)})
# classic normal5x5 magic square fixture, independent fixed values
control=[17,24,1,8,15,23,5,7,14,16,4,6,13,20,22,10,12,19,21,3,11,18,25,2,9]
assert magic(control);bad=control[:];bad[0]+=1;assert not magic(bad)
reserved={4,9,14,19,24,29,34,39,44,54};pages=[]
for p in D['pages']:
 n=p['original_page']
 if not isinstance(n,int) or n not in range(56) or n==50 or n in reserved:continue
 cells=[]
 for line in p['lines']:
  for mt in pat.finditer(line['raw']):
   cells.append({'value':val(mt[0]),'token':mt[0],'source_line':line['source_line'],'raw_char_start':mt.start(),'raw_char_end':mt.end()})
 pages.append({'page':n,'cells':cells})
assert len(pages)==45
hits=[];nwindows=0
for p in pages:
 vs=[c['value'] for c in p['cells']]
 for j in range(len(vs)-24):
  nwindows+=1
  if magic(vs[j:j+25]):hits.append({'page':p['page'],'cell_start':j,'cells':p['cells'][j:j+25]})
rng=random.Random(20260917);null=[];t=time.monotonic()
for rep in range(1000):
 count=0
 for p in pages:
  vs=[c['value'] for c in p['cells']];rng.shuffle(vs)
  count+=sum(magic(vs[j:j+25]) for j in range(len(vs)-24))
 null.append(count)
out={'sources':src,'controls':{'known_magic':True,'corrupted_rejected':True},'pages':[p['page'] for p in pages],'cell_counts':{p['page']:len(p['cells']) for p in pages},'windows':nwindows,'hits':hits,'null_reps':1000,'null_total_hits':sum(null),'null_max_hits':max(null),'elapsed_null_seconds':time.monotonic()-t,'input_sha256':hashlib.sha256(pathlib.Path('audit/parallel-01/inputs/dataset.json').read_bytes()).hexdigest()}
(ROOT/'experiment01-result.json').write_text(json.dumps(out,indent=2)+'\n');(ROOT/'experiment01-discovery-cells.json').write_text(json.dumps(pages,ensure_ascii=False)+'\n');print(json.dumps(out,indent=2))

import gzip
with gzip.open(ROOT/'experiment01-null.json.gz','wt') as f:json.dump({'null_hit_counts':null,'rng_seed':20260917,'ordering':'1000replicates, pages in saved order, shuffle sequentially'},f)
