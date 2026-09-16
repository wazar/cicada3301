import pathlib,json,hashlib,datetime
from PIL import Image,ImageDraw
O=pathlib.Path(__file__).parent; R=O.parents[2]; G=O.parent/'worker-g'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
assert not (O.parent/'STOP').exists()
D=json.loads((R/'audit/parallel-01/inputs/dataset.json').read_text()); alphabet=set(D['alphabet'])
P={p['original_page']:p for p in D['pages'] if p['original_page'] in [3,7,17]}
for p in P.values():
 count=0
 for row in p['lines']:
  assert row['rune_start']==count
  count+=sum(c in alphabet for c in row['raw'])
  assert row['rune_end']==count
 assert count==len(p['indices'])
source=(R/D['source']).read_text(); M=json.loads((G/'g06-source-gap-map.json').read_text())
checks=[]; sheet=Image.new('RGB',(1000,7*190),'white'); draw=ImageDraw.Draw(sheet)
for i,m in enumerate(M):
 p=P[m['page']]; gap=m['rune_gap']; im=Image.open(R/f"liber-primus/data/relikd/p{m['page']}.jpg"); x,y=m['image']['center']; box=(int(x)-105,int(y)-70,int(x)+105,int(y)+70)
 crop=im.crop(box); cx=(i%2)*500;cy=(i//2)*190; sheet.paste(crop,(cx,cy+35)); draw.text((cx+5,cy+5),f"p{m['page']} gap {gap} dots {m['image']['count']} row {m['image']['line']}",fill='black')
 if m['source_marker']=='.':
  row=p['lines'][m['line']]; before=0; rowgaps=[]
  for c in row['raw']:
   if c in alphabet: before+=1
   elif c=='.': rowgaps.append(row['rune_start']+before)
  assert gap in rowgaps
  assert p['source_char_positions'][gap-1]==m['preceding_source_char']
  assert source[m['preceding_source_char']+1]=='.'
 else:
  assert gap==194 and m['page']==7
  a=p['source_char_positions'][193]+1;b=p['source_char_positions'][194]
  assert '&' in source[a:b]; assert source[a:b].count('.')==1
 checks.append({'page':m['page'],'gap':gap,'dots':m['image']['count'],'line':m['image']['line'],'source_ok':True})
sheet.save(O/'fourteen-signs.png')
for page,p in P.items():
 print('PAGE',page)
 for row in p['lines']: print(row['source_line'],row['rune_start'],row['rune_end'],row['raw'])
print('P7 GAP194 RAW',repr(source[P[7]['source_char_positions'][193]+1:P[7]['source_char_positions'][194]]))
# Independent modular Gaussian elimination for a fixed-degree recurrence.
def fit(s,d):
 a=[[s[i-j-1]%29 for j in range(d)]+[s[i]%29] for i in range(d,len(s))]; piv=[];r=0
 for col in range(d):
  k=next((k for k in range(r,len(a)) if a[k][col]),None)
  if k is None: continue
  a[r],a[k]=a[k],a[r]; inv=pow(a[r][col],-1,29);a[r]=[x*inv%29 for x in a[r]]
  for k in range(len(a)):
   if k!=r:
    fac=a[k][col];a[k]=[(x-fac*y)%29 for x,y in zip(a[k],a[r])]
  piv.append(col);r+=1
 if any(all(x==0 for x in row[:-1]) and row[-1] for row in a):return None
 c=[0]*d
 for k,col in enumerate(piv):c[col]=a[k][-1]
 return c
def hits(s):
 n=0
 for start in range(len(s)-23):
  t=s[start:start+16]; c=fit(t,8)
  if c is None:continue
  out=t.copy()
  for _ in range(8):out.append(sum(c[j]*out[-j-1] for j in range(8))%29)
  n+=out[16:]==s[start+16:start+24]
 return n
g10=json.loads((G/'g10-results.json').read_text()); unique=set(); nominal=0
for u in g10['units']:
 s=u['indices']; assert hits(s)==u['result']['exact_windows']==0
 for k in range(len(s)-23):unique.add((u['page'],u['range'][0]+k))
 nominal+=len(s)-23
control_counts=[]
for c in g10['controls']:
 raw=c['raw']; coef=c['coefficients']; degree=c['degree']
 assert all(raw[i]==sum(coef[j]*raw[i-j-1]for j in range(degree))%29 for i in range(degree,len(raw)))
 accepted=[]; rejected=set(c['rejected_offsets'])
 for i,v in enumerate(raw):
  if i in rejected: assert accepted and v==accepted[-1]
  else: accepted.append(v)
  if len(accepted)==c['length']:break
 assert accepted==c['accepted']
 h=hits(c['accepted']); assert h==c['result']['exact_windows'];control_counts.append(h)
g09=json.loads((G/'g09-results.json').read_text())
for c in g09['controls']:
 s=c['truth'];cut=c['result']['cut'];coef=fit(s[:cut],8);assert coef is not None
 out=s[:cut].copy()
 for _ in range(len(s)-cut):out.append(sum(coef[j]*out[-j-1]for j in range(8))%29)
 assert out==s
for c in g09['filter_controls']:
 assert fit(c['accepted'][:c['result']['cut']],8) is None
assert all(sum(sum(x)for x in v)==0 for v in g10['null'].values())
result={'g06':checks,'g10':{'nominal':nominal,'unique':len(unique),'real_hits':0,'controls_checked':len(control_counts),'detected':sum(x>0 for x in control_counts),'minimum_hits':min(control_counts)},'g09_raw_controls_checked':len(g09['controls'])}
(O/'checked-findings.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
