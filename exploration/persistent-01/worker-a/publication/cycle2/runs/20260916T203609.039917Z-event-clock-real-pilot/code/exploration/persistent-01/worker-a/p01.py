"""Independent literal-F clue coverage; imports read-only helpers, no historical writes."""
import sys,pathlib,json,random,time,argparse,gzip,hashlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3]; O=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'exploration/overnight-01/worker-a'))
import search as s
import clues

def setup():
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text()); data=json.loads((ROOT/'exploration/overnight-01/worker-a/r02/keys.json').read_text());ps=s.pages(); assert len(ps)==45 and all(p['original_page'] not in cfg['reserved_original_pages']+[50] for p in ps)
 old=clues.cells(data,ps); exclude=set(json.loads((ROOT/'exploration/overnight-01/worker-a/r02/f-plan.json').read_text())['queue']); queue=[dict(old_ordinal=i,**x) for i,x in enumerate(old) if x['periodic'] and i not in exclude];random.Random(330103).shuffle(queue)
 return data,ps,queue, len([i for i in exclude if old[i]['periodic']])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['real','plant','null'],default='real');ap.add_argument('--limit',type=int,default=256);ap.add_argument('--seconds',type=int,default=780);a=ap.parse_args();t=time.monotonic(); data,ps,queue,excluded=setup(); defs={x['id']:x for x in data['keys']}; lookup={p['original_page']:p for p in ps}; q=s.Score();stage=O/a.mode;stage.mkdir(exist_ok=True); cp=stage/'checkpoint.json';state=json.loads(cp.read_text()) if cp.exists() else dict(cursor=0,top=[]);start=state['cursor'];top=state['top']; truths={}
 if a.mode=='plant':
  raw=(ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt').read_text(); base=[s.ABC.index(x) for x in raw if x in s.ABC]
  for pid,page in lookup.items():
   chosen=next(cell for cell in queue[:256] if cell['original_page']==pid); plain=(base*((len(page['indices'])+len(base)-1)//len(base)))[:len(page['indices'])];k=clues.key_for(chosen,defs,len(plain));cipher=[];used=0
   for v in plain:
    if v==0:cipher.append(0)
    else:cipher.append((v-chosen['sign']*k[used])%29);used+=1
   truths[pid]=dict(plain=plain,cell=chosen); lookup[pid]=dict(page,indices=cipher)
  s.dump(stage/'truth.json',truths)
 if a.mode=='null':
  for pid,page in lookup.items():
   c=page['indices'].copy(); random.Random(330104+pid).shuffle(c);lookup[pid]=dict(page,indices=c)
 limit=min(a.limit,len(queue));stop=ROOT/'exploration/persistent-01/STOP'
 with gzip.open(stage/f'scores-{start:07d}.jsonl.gz','wt') as f:
  for j in range(start,limit):
   if stop.exists() or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc):break
   cell=queue[j];page=lookup[cell['original_page']];c=page['indices'];key=clues.key_for(cell,defs,len(c));alts,diag=s.fbeam(c,key,cell['sign'],q); p=alts[0]['plain'];r=dict(id=f'p01:{a.mode}:{j}',**cell,n=len(c),score=alts[0]['score'],statistics=s.stats(p),diagnostics=diag)
   if a.mode=='plant':
    truth=truths[cell['original_page']];r.update(plant_cell=cell==truth['cell'],rune_errors=sum(x!=y for x,y in zip(p,truth['plain'])),truth_top16=any(z['plain']==truth['plain'] for z in alts))
   f.write(json.dumps(r)+'\n')
   if len(top)<20 or r['score']>top[-1]['score']:
    top.append(dict(r,plain=p,transliteration=s.render(p,page),alternatives=alts));top.sort(key=lambda z:z['score'],reverse=True);top=top[:20]
   state=dict(cursor=j+1,total=len(queue),excluded_old_periodic=excluded,top=top,seconds_this_batch=time.monotonic()-t,mode=a.mode)
   if (j+1)%16==0:s.dump(cp,state);f.flush();print(json.dumps({k:v for k,v in state.items() if k!='top'}),flush=True)
   if time.monotonic()-t>=a.seconds:break
 s.dump(cp,state);s.dump(stage/'top20.json',top);print(json.dumps({k:v for k,v in state.items() if k!='top'}),flush=True)
if __name__=='__main__':main()
