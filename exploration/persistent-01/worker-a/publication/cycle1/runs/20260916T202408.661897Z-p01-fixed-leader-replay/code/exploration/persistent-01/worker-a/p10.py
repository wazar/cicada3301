"""Finite solved-source running keys with literal-F viability before pruning."""
import importlib.util,json,hashlib,random,time,gzip,datetime
import p01
s=p01.s;O=p01.O;ROOT=p01.ROOT;PATH=ROOT/'exploration/persistent-01/worker-b/feasible.py'
assert hashlib.sha256(PATH.read_bytes()).hexdigest()=='e5c9cc1444716ca2a3ab4f71e7c58cf041db2809fe0e3788d27e3beacc2af17b'
sp=importlib.util.spec_from_file_location('finite_feasible',PATH);decoder=importlib.util.module_from_spec(sp);sp.loader.exec_module(decoder)
def main():
 data,pages,_,_=p01.setup();defs={x['id']:x for x in data['texts']};q=decoder.b.old.Score();start=time.monotonic();old=p01.clues.cells(data,pages);excluded={tuple(old[i][k] for k in ['key_id','offset','sign','original_page']) for i in json.loads((ROOT/'exploration/overnight-01/worker-a/r02/f-plan.json').read_text())['queue'] if not old[i]['periodic']};queue=[dict(key_id=k['id'],offset=o,sign=sign,original_page=p['original_page']) for k in data['texts'] for o in k['offsets'] for sign in [-1,1] for p in pages if len(k['key'])-o>=len(p['indices'])-p['indices'].count(0) and (k['id'],o,sign,p['original_page']) not in excluded];assert len(queue)==3961;lookup={p['original_page']:p for p in pages};stage=O/'p10';stage.mkdir(exist_ok=True)
 raw=(ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt').read_text();plain=[s.ABC.index(c) for c in raw if c in s.ABC][:80];used=len(plain)-plain.count(0);controlkeys=[dict(key_id=k['id'],key=k['key'][:used],sign=sign) for k in data['texts'] if len(k['key'])>=used for sign in [-1,1]];target=controlkeys[4];cipher=[];u=0
 for v in plain:cipher.append(0 if v==0 else (v-target['sign']*target['key'][u])%29);u+=v!=0
 controls=[]
 for mode in ['plant','null']:
  c=cipher.copy()
  if mode=='null':random.Random(330110).shuffle(c)
  rows=[]
  for cell in controlkeys:
   alts=decoder.decode(c,cell['key'],cell['sign'],False,q,256);assert alts;rows.append(dict(cell=cell,score=alts[0]['score'],alternatives=alts))
  rows.sort(key=lambda x:x['score'],reverse=True);tr=next(x for x in rows if x['cell']==target);controls.append(dict(mode=mode,cipher=c,truth=plain,count=len(rows),truth_key_rank=rows.index(tr)+1,truth_top16=any(x['plain']==plain for x in tr['alternatives']),top_errors=sum(x!=y for x,y in zip(rows[0]['alternatives'][0]['plain'],plain)),rows=rows))
 s.dump(stage/'controls.json',controls)
 for mode in ['real','null']:
  top=[]
  with gzip.open(stage/(mode+'-scores.jsonl.gz'),'wt') as f:
   for ix,cell in enumerate(queue):
    if (ROOT/'exploration/persistent-01/STOP').exists() or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc):return
    page=lookup[cell['original_page']];c=page['indices'].copy()
    if mode=='null':random.Random(330111+cell['original_page']).shuffle(c)
    key=defs[cell['key_id']]['key'][cell['offset']:];alts=decoder.decode(c,key,cell['sign'],False,q,256);assert alts
    for alt in alts:
     u=0;literal=set(alt['path'])
     for j,v in enumerate(alt['plain']):
      if j in literal:assert v==c[j]==0
      else:assert (v-cell['sign']*key[u])%29==c[j];u+=1
     assert u==alt['used']<=len(key)
    p=alts[0]['plain'];r=dict(id=f'p10:{mode}:{ix}',**cell,score=alts[0]['score'],minimum_consumption=len(c)-c.count(0),available_key=len(key),new_length_gap=len(key)<len(c),statistics=s.stats(p));f.write(json.dumps(r)+'\n')
    if len(top)<20 or r['score']>top[-1]['score']:top.append(dict(r,plain=p,transliteration=s.render(p,page),alternatives=alts));top.sort(key=lambda r:r['score'],reverse=True);top=top[:20]
    if (ix+1)%100==0:f.flush();print(mode,ix+1,time.monotonic()-start,flush=True)
  s.dump(stage/(mode+'-results.json'),dict(count=len(queue),old_cells_excluded=len(excluded),new_length_gap_cells=sum(len(defs[x['key_id']]['key'])-x['offset']<len(lookup[x['original_page']]['indices']) for x in queue),top20=top,elapsed=time.monotonic()-start))
if __name__=='__main__':main()
