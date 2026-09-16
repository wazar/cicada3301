"""Frozen delimiter-rune scorer, independently sampled beyond prior32-key coverage."""
import argparse,importlib.util,json,random,time,gzip,datetime,hashlib
import p01
s=p01.s;O=p01.O;ROOT=p01.ROOT
PATH=ROOT/'exploration/persistent-01/worker-c/p03_frozen.py'
assert hashlib.sha256(PATH.read_bytes()).hexdigest()=='c67395df4b002059f39c243ca977a8c565977daa47881a6c156876e5ccadbf05'
spec=importlib.util.spec_from_file_location('p03frozen',PATH);lm_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(lm_module)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['control','real','null'],default='control');ap.add_argument('--seconds',type=int,default=780);a=ap.parse_args();t=time.monotonic();data,pages,_,_=p01.setup();lm=lm_module.LM();pool=[dict(key_id=k['id'],phase=phase,sign=sign,key=k['key'][phase:]+k['key'][:phase]) for k in data['keys'][32:] for phase in range(len(k['key'])) for sign in [-1,1]];cs=random.Random(330112).sample(pool,128);stage=O/('p12-'+a.mode);stage.mkdir(exist_ok=True);s.dump(stage/'keys.json',cs)
 if a.mode=='control':
  output=[]
  for j,name in enumerate(lm_module.CHECK):
   f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');plain,ends=lm_module.parse(f.read_text());target=cs[j*31];key=target['key'];cipher=[];path=[];u=0
   for i,v in enumerate(plain):
    if v==0 and i%3!=1:cipher.append(0);path.append(i)
    else:cipher.append((v-target['sign']*key[u%len(key)])%29);u+=1
   for mode in ['plant','null']:
    c=cipher.copy()
    if mode=='null':random.Random(330112+j).shuffle(c)
    rows=[]
    for ix,cell in enumerate(cs):
     alts,diag=lm_module.beam(c,ends,cell['key'],cell['sign'],lm,width=64,truth=path if cell==target and mode=='plant' else None);rows.append(dict(index=ix,cell=cell,score=alts[0]['score'],alternatives=alts,diagnostics=diag))
    rows.sort(key=lambda r:r['score'],reverse=True);tr=next(r for r in rows if r['cell']==target);record=dict(source=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),mode=mode,n=len(c),count=len(rows),truth_key_rank=rows.index(tr)+1,top_errors=sum(x!=y for x,y in zip(rows[0]['alternatives'][0]['plain'],plain)),planted_truth_top16=any(x['plain']==plain for x in tr['alternatives']),planted_alternatives=tr['alternatives'],top20=rows[:20],all_scores=[dict(index=r['index'],score=r['score']) for r in rows]);output.append(record);s.dump(stage/'results.json',output);print(name,mode,record['truth_key_rank'],record['top_errors'],flush=True)
  return
 assert (O/'p12-control/results.json').exists()
 queue=[(p,ix,c) for p in pages for ix,c in enumerate(cs)];cp=stage/'checkpoint.json';state=json.loads(cp.read_text()) if cp.exists() else dict(cursor=0,top=[]);start=state['cursor'];top=state['top']
 with gzip.open(stage/f'scores-{start:07d}.jsonl.gz','wt') as f:
  for i in range(start,len(queue)):
   if (ROOT/'exploration/persistent-01/STOP').exists() or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc):break
   page,ix,cell=queue[i];c,ends=lm_module.parse('/'.join(l['raw'] for l in page['lines']));assert c==page['indices']
   if a.mode=='null':random.Random(330113+page['original_page']).shuffle(c)
   alts,diag=lm_module.beam(c,ends,cell['key'],cell['sign'],lm,width=64);p=alts[0]['plain'];r=dict(id=f'p12:{a.mode}:{i}',original_page=page['original_page'],key_cell_index=ix,**cell,score=alts[0]['score'],statistics=s.stats(p),diagnostics=diag);f.write(json.dumps(r)+'\n')
   if len(top)<20 or r['score']>top[-1]['score']:top.append(dict(r,plain=p,transliteration=s.render(p,page),alternatives=alts));top.sort(key=lambda r:r['score'],reverse=True);top=top[:20]
   state=dict(cursor=i+1,total=len(queue),top=top,seconds_this_batch=time.monotonic()-t)
   if (i+1)%32==0:s.dump(cp,state);f.flush();print(i+1,time.monotonic()-t,flush=True)
   if time.monotonic()-t>a.seconds:break
 s.dump(cp,state);s.dump(stage/'top20.json',top)
if __name__=='__main__':main()
