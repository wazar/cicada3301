import pathlib,json,gzip,sys,hashlib
R=pathlib.Path(__file__).resolve().parent;O=R/'P18'
load=lambda n:json.load(gzip.open(O/(n+'.json.gz'),'rt'))
key=load('key-map')['key'];keybytes=bytes(key)
def check(name):
 agg=load(name+'-aggregate');f=agg['packet'];n=len(f['cipher']);count=0;errors=0;maxend=0;best=-float('inf');scores=[];sha=hashlib.sha256()
 paths=sorted(O.glob(name+'-*.jsonl.gz'),key=lambda p:int(p.name.split('-')[-2]))
 for file in paths:
  with gzip.open(file,'rt') as g:
   for line in g:
    row=json.loads(line);assert row['id']==count;count+=1;job=row['job'];assert job==dict(offset=(count-1)//2,sign=[-1,1][(count-1)%2]);scores.append(row['score'])
    for a in row['alternatives']:
     lit=set(a['literal_positions']);u=0;out=[]
     for i,v in enumerate(f['cipher']):
      if i in lit:assert v==0;out.append(0)
      else:
       assert job['offset']+u<len(key);out.append((v+job['sign']*key[job['offset']+u])%29);u+=1
     assert a['plain']==out and a['used']==u and len(out)==n;maxend=max(maxend,job['offset']+u);sha.update(bytes(out));best=max(best,a['score'])
 assert count==agg['cells']==2*(len(key)-sum(x!=0 for x in f['cipher'])+1)
 assert best==agg['best_score']
 for a in agg['top16']:
  aliases=[];lit=set(a['literal_positions'])
  for sign in [-1,1]:
   required=[((p-v)*sign)%29 for i,(p,v) in enumerate(zip(a['plain'],f['cipher'])) if i not in lit]
   for o in range(len(key)-len(required)+1):
    if key[o:o+len(required)]==required:aliases.append(dict(offset=o,sign=sign))
  assert aliases==a['aliases']
 result=dict(name=name,status='PASS',cell_outputs=count,max_source_after=maxend,stream_plain_sha256=sha.hexdigest(),global_alternatives=len(agg['top16']),complete_aliases=[len(a['aliases']) for a in agg['top16']])
 if 'truth' in f:
  truth=f['truth'];pos=2*truth['offset']+(truth['sign']==1);assert 1+sum(s is not None and s>scores[pos] for s in scores)==agg['truth_job_score_rank'];result['truth_rank']=agg['truth_job_score_rank']
 (O/(name+'-check.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':
 for name in sys.argv[1:]:check(name)
