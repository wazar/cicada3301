"""Existing rejection decoder isolated from literal-F, width400 maxskip3, startzero all known recipes."""
import gzip,importlib.util,json,time
import search as s

def module(name,path):
 sp=importlib.util.spec_from_file_location(name,s.ROOT/path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def main():
 t=time.monotonic();sk=module('existing_skip','liber-primus/analysis/campaign18_skip/skipdecode.py');ctl=module('existing_trace','audit/experiment-01/control.py');keys=s.recipes();ps=s.pages();o=s.O/'r01rejection';o.mkdir(exist_ok=True);cp=o/'checkpoint.json';state=json.loads(cp.read_text()) if cp.exists() else dict(cursor=0,top=[]);top=state['top'];start=state['cursor'];queue=[(name,sign,p) for name in keys for sign in [-1,1] for p in ps]
 with gzip.open(o/f'scores-{start:05}.jsonl.gz','wt') as f:
  for ix in range(start,len(queue)):
   name,sign,page=queue[ix];c=page['indices'];k=keys[name];out=ctl.traced_beam(sk,c,k,sign);p=out['plain_idx'];assert len(p)==len(c)
   for i,(v,j) in enumerate(zip(p,out['key_use'])):
    assert (v-sign*k[j])%29==c[i]
    if i:
     assert all((v-sign*k[rej])%29==c[i-1] for rej in range(out['key_use'][i-1]+1,j))
   r=dict(id=f'r01rejection:{ix}',mode='rejection',recipe=name,sign=sign,offset=0,original_page=page['original_page'],n=len(c),score=out['score'],statistics=s.stats(p),word_view=s.wordstats(p,page));f.write(json.dumps(r)+'\n')
   if len(top)<20 or r['score']>top[-1]['score']:
    r.update(plain=p,transliteration=s.render(p,page),key_use=out['key_use'],diagnostics={'beam_width':400,'max_skip':3,'cumulative_prefix_score':out['beam_score']},status='UNREVIEWED');top.append(r);top.sort(key=lambda x:x['score'],reverse=True);top=top[:20]
   state=dict(cursor=ix+1,total=len(queue),top=top,seconds_this_batch=time.monotonic()-t);s.dump(cp,state);f.flush()
   if (ix+1)%10==0:print(json.dumps(dict(cursor=ix+1,total=len(queue),seconds=time.monotonic()-t,best=top[0]['score'])),flush=True)
   if time.monotonic()-t>780:break
 s.dump(o/'top20.json',top);print(json.dumps(dict(cursor=state['cursor'],total=len(queue),seconds=time.monotonic()-t)),flush=True)
if __name__=='__main__':main()
