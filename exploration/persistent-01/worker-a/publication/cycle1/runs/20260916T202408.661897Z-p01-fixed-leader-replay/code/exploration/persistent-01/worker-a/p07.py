"""Source-line permutation/literal-F composition; fixed phasezero clue-key crossover."""
import argparse,json,random,time,gzip,datetime
import p01
s=p01.s;O=p01.O

def routes(page):
 n=len(page['indices']);lines=[list(range(l['rune_start'],l['rune_end'])) for l in page['lines']];assert sum(lines,[])==list(range(n))
 out={'reverse':list(range(n-1,-1,-1)),'reverse_lines':sum(lines[::-1],[]),'reverse_within_lines':sum([l[::-1] for l in lines],[]),'boustrophedon':sum([l[::-1] if i%2 else l for i,l in enumerate(lines)],[])}
 for perm in out.values():assert sorted(perm)==list(range(n))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['control','real','null'],default='control');ap.add_argument('--seconds',type=int,default=780);ap.add_argument('--limit',type=int,default=92160);a=ap.parse_args();t=time.monotonic();data,pages,_,_=p01.setup();q=s.Score();defs={x['id']:x for x in data['keys']};stage=O/('p07-'+a.mode);stage.mkdir(exist_ok=True);ps={p['original_page']:p for p in pages};truth=json.loads((O/'plant/truth.json').read_text())
 if a.mode=='control':
  rows=[]
  for page in pages:
   target=truth[str(page['original_page'])];cell=target['cell'];plain=target['plain'];k=p01.clues.key_for(cell,defs,len(plain));c=[];u=0
   for v in plain:c.append(0 if v==0 else (v-cell['sign']*k[u])%29);u+=v!=0
   for name,perm in routes(page).items():
    original=[None]*len(c)
    for i,j in enumerate(perm):original[j]=c[i]
    routed=[original[j] for j in perm];assert routed==c
    alts,diag=s.fbeam(routed,k,cell['sign'],q);rows.append(dict(page=page['original_page'],route=name,route_to_original=perm,cell=cell,errors=sum(x!=y for x,y in zip(plain,alts[0]['plain'])),truth_top16=any(x['plain']==plain for x in alts),alternatives=alts,diagnostics=diag))
  s.dump(stage/'controls.json',rows);print('controls',len(rows),'truth_survives',sum(x['truth_top16'] for x in rows),'exact_top',sum(x['errors']==0 for x in rows));return
 assert (O/'p07-control/controls.json').exists(),'run composition controls first'
 queue=[dict(key_id=k['id'],offset=0,sign=sign,original_page=p['original_page'],periodic=True,route=route) for k in data['keys'] for sign in [-1,1] for p in pages for route in routes(p)];random.Random(330107).shuffle(queue)
 if a.mode=='null':
  for page in pages:random.Random(330108+page['original_page']).shuffle(page['indices'])
 cp=stage/'checkpoint.json';state=json.loads(cp.read_text()) if cp.exists() else dict(cursor=0,top=[]);start=state['cursor'];top=state['top']
 with gzip.open(stage/f'scores-{start:07d}.jsonl.gz','wt') as f:
  for i in range(start,min(a.limit,len(queue))):
   if (p01.ROOT/'exploration/persistent-01/STOP').exists() or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc):break
   cell=queue[i];page=ps[cell['original_page']];perm=routes(page)[cell['route']];c=[page['indices'][j] for j in perm];key=p01.clues.key_for(cell,defs,len(c));alts,diag=s.fbeam(c,key,cell['sign'],q);p=alts[0]['plain'];r=dict(id=f'p07:{a.mode}:{i}',**cell,score=alts[0]['score'],statistics=s.stats(p),diagnostics=diag);f.write(json.dumps(r)+'\n')
   if len(top)<20 or r['score']>top[-1]['score']:top.append(dict(r,plain=p,transliteration=''.join(s.TOK[x] for x in p),alternatives=alts,route_to_original=perm));top.sort(key=lambda x:x['score'],reverse=True);top=top[:20]
   state=dict(cursor=i+1,total=len(queue),top=top,seconds_this_batch=time.monotonic()-t)
   if (i+1)%16==0:s.dump(cp,state);f.flush();print('cursor',i+1,'elapsed',time.monotonic()-t,flush=True)
   if time.monotonic()-t>a.seconds:break
 s.dump(cp,state);s.dump(stage/'top20.json',top)
if __name__=='__main__':main()
