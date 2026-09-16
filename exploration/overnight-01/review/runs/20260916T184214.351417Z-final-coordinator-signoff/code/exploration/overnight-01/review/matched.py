import pathlib,json,gzip,hashlib
R=pathlib.Path(__file__).resolve().parents[3];B=R/'exploration/overnight-01/worker-b';O=pathlib.Path(__file__).parent;out={};sources={}
for lane in ['r04','r04-wide','r06']:
 vals={False:[],True:[]};fits=0;pages=set()
 for f in (B/lane).glob('cell-*.json.gz'):
  sources[str(f.relative_to(R))]=hashlib.sha256(f.read_bytes()).hexdigest()
  with gzip.open(f,'rt') as h:rows=json.load(h)
  if lane=='r06':vals[rows['control']].extend(v for _,v in rows['scores']);pages.add(rows['page'])
  else:
   for z in rows:vals[z['control']].append(z['continuation_score']);pages.add(z['page']);fits+=1
 out[lane]={'pages':sorted(pages),'real_count':len(vals[False]),'random_count':len(vals[True]),'real_max':max(vals[False]),'random_max':max(vals[True]),'real_mean':sum(vals[False])/len(vals[False]),'random_mean':sum(vals[True])/len(vals[True])}
real=[];random=[];cr=[];cn=[]
for f in (B/'r05').glob('pair-*.json.gz'):
 sources[str(f.relative_to(R))]=hashlib.sha256(f.read_bytes()).hexdigest()
 with gzip.open(f,'rt') as h:rows=json.load(h)
 for z in rows:
  if z[0].endswith(':crib'):cr.append(z[3]);cn.append(z[4])
  else:real.append((z[2]-1/29)*z[1]**.5);random.append((z[5]-1/29)*z[1]**.5)
out['r05']={'relationships':len(real),'cribs':len(cr),'real_max':max(real),'random_max':max(random),'crib_real_max':max(cr),'crib_random_max':max(cn)}
(O/'matched.json').write_text(json.dumps({'results':out,'sources':sources},indent=2)+'\n');print(json.dumps(out,indent=2))
