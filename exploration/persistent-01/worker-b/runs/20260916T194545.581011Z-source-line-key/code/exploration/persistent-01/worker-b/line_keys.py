import pathlib,json,random,time,heapq,gzip,importlib.util,collections,zlib
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('baseline',OUT/'search.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
rs,_,_=b.setup();hold=set(b.load('exploration/persistent-01/config.json')['reserved_original_pages']);pages={p['original_page']:[l['indices'] for l in p['lines'] if l['indices']] for p in b.load('audit/parallel-01/inputs/dataset.json')['pages'] if p['original_page'] not in hold and p['original_page']<=55}

def decode(lines,k,sign,f,sc,width=256):
 states=[('',0.,0,0,[],[],[])];position=0
 for line in lines:
  states=[(t,s,n,0,p,path,useds) for t,s,n,j,p,path,useds in states]
  for c in line:
   ns=[]
   for t,s,n,j,p,path,useds in states:
    choices=[]
    if j<len(k):choices.append(((c+sign*k[j])%29,j+1,path))
    if f and c==0:choices.append((0,j,path+[position]))
    for r,jj,pp in choices:
     tt,ss,nn=sc.add(t,s,n,r);ns.append((tt,ss,nn,jj,p+[r],pp,useds))
   states=heapq.nlargest(width if f else 1,ns,key=lambda z:z[1]/z[2] if z[2] else -999);position+=1
  states=[(t,s,n,j,p,path,useds+[j]) for t,s,n,j,p,path,useds in states]
 return [dict(plain=p,path=path,line_used=useds,score=s/n if n else -999) for t,s,n,j,p,path,useds in states[:16]]
def verify(lines,k,sign,states):
 for x in states:
  pos=0
  for n,line in enumerate(lines):
   used=0
   for c in line:
    p=x['plain'][pos]
    if pos in x['path']:assert p==c==0
    else:assert (p-sign*k[used])%29==c;used+=1
    pos+=1
   assert used==x['line_used'][n]
def diagnostics(pp):
 n=len(pp);co=collections.Counter(pp)
 return dict(ioc_times_n=sum(v*(v-1) for v in co.values())/(n-1) if n>1 else None,min_distinct32=min((len(set(pp[t:t+32])) for t in range(n-31)),default=None),zlib_ratio=len(zlib.compress(bytes(pp)))/n if n else None,nonEnglishLM=None)
def controls(sc):
 plain=[b.old.ABC.index(r) for r in (ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt').read_text() if r in b.old.ABC];out=[]
 for ii,(r,sign,f) in enumerate([('row-r0c0-mod29',-1,False),('column-r1c0-reject232',1,True)]):
  lengths=[23,19,24,21,22,18];lines=[];truth=[];path=[];pos=offset=0;key=rs[r]['key']
  for n in lengths:
   pp=plain[offset:offset+n];offset+=n;truth+=pp;used=0;c=[]
   for p in pp:
    if f and p==0:c.append(0);path.append(pos)
    else:c.append((p-sign*key[used])%29);used+=1
    pos+=1
   lines.append(c)
  grid=[]
  for route,z in rs.items():
   for s in (-1,1):
    states=decode(lines,z['key'],s,f,sc);verify(lines,z['key'],s,states);grid.append(dict(route=route,sign=s,score=states[0]['score'],states=states))
  grid.sort(key=lambda x:x['score'],reverse=True);actual=next(x for x in grid if x['route']==r and x['sign']==sign)
  out.append(dict(truth_route=r,truth_sign=sign,F=f,cipher=lines,plain=truth,path=path,truth_key_rank=grid.index(actual)+1,truth_plain_rank=next((i+1 for i,z in enumerate(actual['states']) if z['plain']==truth),None),searched=32,top=grid[:3]))
 b.save('line-controls.json',out)
def main():
 sc=b.old.Score();controls(sc)
 for seed in (None,9200902):
  rng=random.Random(seed);tag='line-'+('real' if seed is None else 'null9200902');top=[];selected=[];start=time.monotonic();count=0
  with gzip.open(OUT/(tag+'-scores.jsonl.gz'),'wt') as output:
   for page,original in pages.items():
    lines=[l[:] for l in original]
    if seed is not None:
     for l in lines:rng.shuffle(l)
    half=max(1,len(lines)//2);train=lines[:half];test=lines[half:]
    if not test:continue
    records=[]
    for route,z in rs.items():
     for sign in (-1,1):
      for f in (False,True):
       tr=decode(train,z['key'],sign,f,sc);te=decode(test,z['key'],sign,f,sc);verify(test,z['key'],sign,te);count+=1
       row=dict(id=count-1,page=page,route=route,sign=sign,F=f,train_score=tr[0]['score'],test_score=te[0]['score'],**diagnostics(te[0]['plain']));output.write(json.dumps(row)+'\n');records.append(dict(**row,alternatives=te,train_alternatives=tr,key=z['key'],test_lines=test))
    records.sort(key=lambda x:x['train_score'],reverse=True);winner=records[0];selected.append({k:v for k,v in winner.items() if k not in ('alternatives','train_alternatives','key','test_lines')})
    top.append(winner);top.sort(key=lambda x:x['test_score'],reverse=True);top=top[:20]
  b.save(tag+'-results.json',dict(count=count,selected=selected,top=top,seconds=time.monotonic()-start));print(tag,count,time.monotonic()-start)
if __name__=='__main__':main()
