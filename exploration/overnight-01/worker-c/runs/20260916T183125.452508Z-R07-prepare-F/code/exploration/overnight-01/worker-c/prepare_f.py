from search import *
rs=routes();pages=load('audit/parallel-01/inputs/dataset.json')['pages'];hold=set(load('exploration/overnight-01/config.json')['reserved_original_pages']);pages=[p for p in pages if p['original_page'] not in hold and p['original_page']<=54]; jobs=[]
# Surrounding full valid offsets first, no key wrap. Key sufficiency permits all available F interruptions.
for p in pages:
 if p['original_page'] not in (49,51):continue
 for r,z in rs.items():
  for o in range(min(256,len(z['key'])-len(p['indices'])+p['indices'].count(0)+1)):
   for s in (-1,1):jobs.append(dict(page=p['original_page'],route=r,offset=o,sign=s,periodic=False))
# Independent fixed whole-page sample. All routes/signs at offset0, periodic and sufficient finite-key.
for p in pages:
 for r,z in rs.items():
  for per in (False,True):
   if not per and len(z['key'])<len(p['indices'])-p['indices'].count(0):continue
   for s in (-1,1):jobs.append(dict(page=p['original_page'],route=r,offset=0,sign=s,periodic=per))
# Rigid shortlisted finite/periodic cases are supplementary to the independent sample.
for f in OUT.glob('rigid-*-results.json'):
 for z in json.loads(f.read_text())['top']:jobs.append({k:z[k] for k in ('page','route','offset','sign','periodic')})
seen=set();out=[]
for j in jobs:
 sig=json.dumps(j,sort_keys=True)
 if sig not in seen:seen.add(sig);out.append(j)
save(OUT/'f-jobs.json',out);save(OUT/'f-definition.json',dict(jobs=len(out),selection='surrounding finite all valid offsets, then independent all-discovery route/sign offset0 finite or periodic, then rigid top20',width=256,top_alternatives=16));print(len(out))
