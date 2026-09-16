import argparse,datetime,gzip,hashlib,importlib.util,json,math,pathlib,time
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent/'p11';D.mkdir(exist_ok=True)
def loadmod(name,p):
 spec=importlib.util.spec_from_file_location(name,ROOT/p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
s=loadmod('checked_a','exploration/overnight-01/worker-a/search.py');cmod=loadmod('frozen_c','exploration/persistent-01/worker-c/p03_frozen.py')
def dump(p,x):p.write_text(json.dumps(x,indent=2,default=lambda z:z.item())+'\n')
def savegz(p,x):
 tmp=p.with_suffix(p.suffix+'.tmp')
 with gzip.open(tmp,'wt') as f:json.dump(x,f,default=lambda z:z.item())
 tmp.replace(p)
def stopped():return (ROOT/'exploration/persistent-01/STOP').exists() or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());fp=ROOT/'audit/parallel-01/inputs/dataset.json';assert hashlib.sha256(fp.read_bytes()).hexdigest()==cfg['dataset_sha256'];pages=[p for p in json.loads(fp.read_text())['pages'] if p['original_page']<=55 and p['original_page'] not in cfg['reserved_original_pages']];assert len(pages)==45
phi=np.arange(15001,dtype=np.int64)
for i in range(2,15001):
 if phi[i]==i:phi[i::i]-=phi[i::i]//i
assert all(phi[i]==sum(math.gcd(i,j)==1 for j in range(1,i+1)) for i in range(1,129));key=(phi[1:]%29);pin=json.loads((ROOT/'exploration/overnight-01/worker-b/r03/sequences.json').read_text())['integer_phi'];assert hashlib.sha256(key.tobytes()).hexdigest()==pin['sha256'];np.savez(D/'phi.npz',integer_phi=phi[1:],mod29=key)
manifest=json.loads((ROOT/'exploration/persistent-01/worker-c/p03-frozen-manifest.json').read_text())
for r in manifest:
 if r['path'].endswith('p03_frozen.py') or any(r['path'].endswith('solved_'+x+'.txt') for x in cmod.TRAIN):assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
q=s.Score();lm=cmod.LM();keys=[(off,sign) for off in range(128) for sign in [-1,1]];queue=[dict(offset=o,sign=g,page=p['original_page']) for o,g in keys for p in pages];dump(D/'queue.json',queue)
dump(D/'manifest.json',dict(strategy='outside-box-v1',phi_hash=pin['sha256'],integer_definition='phi(n+1)',dataset_hash=cfg['dataset_sha256'],frozen_lm_sources=lm.files,scorers={'english':'checked fbeam width256 normalized Latin quadgrams','rune':'frozen C width64 rune-boundary LM; same solved register, not non-English'},queue_sha256=hashlib.sha256(json.dumps(queue,sort_keys=True).encode()).hexdigest()))
lookup={p['original_page']:p for p in pages}
def decode(cipher,ends,off,sign,model):
 k=key[off:].tolist()
 if model=='english':alts,diag=s.fbeam(cipher,k,sign,q,width=256)
 else:alts,diag=cmod.beam(cipher,ends,k,sign,lm,width=64)
 for a in alts:
  p=a['plain'];path=set(a['literal_positions']);used=0;before=[];after=[]
  for i,v in enumerate(cipher):
   before.append(used)
   if i in path:assert p[i]==v==0
   else:assert (p[i]-sign*k[used])%29==v;used+=1
   after.append(used)
  assert used==a['used'];a.update(statistics=s.stats(p),english=q(p),rune_lm=lm.score(p,ends),key_index_before=before,key_index_after=after,boundary_consumption=[dict(site=i,before=before[i],after=after[i],absolute_after=off+after[i]) for i in sorted(ends)],reencryption=True)
 return dict(model=model,alternatives=alts,diagnostics=diag)
def inputs(page,mode):
 cipher,ends=cmod.parse('/'.join(x['raw'] for x in page['lines']));assert cipher==page['indices'];cipher=list(cipher)
 if mode=='null':
  nz=[i for i,x in enumerate(cipher) if x!=0]; vals=np.array(cipher)[nz];np.random.default_rng(190020+page['original_page']).shuffle(vals)
  for i,v in zip(nz,vals):cipher[i]=int(v)
 return cipher,ends
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['controls','search']);ap.add_argument('--limit',type=int,default=16);ap.add_argument('--seconds',type=int,default=780);a=ap.parse_args();start=time.monotonic()
 if a.mode=='controls':
  out=D/'controls';out.mkdir(exist_ok=True)
  for name,off,sign in [('0_welcome',37,-1),('p56_an_end',91,1)]:
   plain,ends=cmod.parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text());u=0;cipher=[];path=[]
   for i,v in enumerate(plain):
    if v==0:cipher.append(0);path.append(i)
    else:cipher.append(int((v-sign*key[off+u])%29));u+=1
   fixture=dict(name=name,plain=plain,ends=sorted(ends),cipher=cipher,offset=off,sign=sign,literal_positions=path,used=u);dump(out/(name+'-fixture.json'),fixture)
   for model in ['english','rune']:
    target=out/(name+'-'+model);target.mkdir(exist_ok=True);scores=[];truthrow=None
    for ix,(o,g) in enumerate(keys):
     pth=target/f'{ix:03}.json.gz'
     if pth.exists():
      with gzip.open(pth,'rt') as f:r=json.load(f)
     else:
      if stopped() or time.monotonic()-start>a.seconds:print('CONTROL_PARTIAL',flush=True);return
      r=decode(cipher,ends,o,g,model);r.update(offset=o,sign=g);savegz(pth,r)
     scores.append(dict(offset=o,sign=g,score=r['alternatives'][0]['score']))
     if (o,g)==(off,sign):truthrow=r
    scores.sort(key=lambda x:x['score'],reverse=True);truthrank=next(i+1 for i,r in enumerate(scores) if (r['offset'],r['sign'])==(off,sign));alts=truthrow['alternatives'];summary=dict(name=name,model=model,truth_key_rank=truthrank,planted_top_rune_errors=sum(x!=y for x,y in zip(alts[0]['plain'],plain)),truth_in_top16=any(x['plain']==plain for x in alts),n=len(plain),literal_count=len(path),ranked_keys=scores)
    dump(out/(name+'-'+model+'-summary.json'),summary);print(json.dumps({k:v for k,v in summary.items() if k!='ranked_keys'}),flush=True)
 else:
  out=D/'search';out.mkdir(exist_ok=True);cp=out/'checkpoint.json';state=json.loads(cp.read_text()) if cp.exists() else dict(cursor=0);begin=state['cursor'];summarypath=out/f'batch-{begin:05}.jsonl';n=0
  with summarypath.open('w') as f:
   for ix in range(begin,min(len(queue),a.limit)):
    if stopped() or time.monotonic()-start>a.seconds:break
    cell=queue[ix];page=lookup[cell['page']];result=dict(cell=cell,ordinal=ix,output={})
    for mode in ['real','null']:
     cipher,ends=inputs(page,mode);r=dict(cipher=cipher,ends=sorted(ends),models=[])
     for model in ['english','rune']:r['models'].append(decode(cipher,ends,cell['offset'],cell['sign'],model))
     result['output'][mode]=r
    savegz(out/f'cell-{ix:05}.json.gz',result)
    summ=dict(ordinal=ix,**cell,scores={mode:{r['model']:r['alternatives'][0]['score'] for r in result['output'][mode]['models']} for mode in ['real','null']})
    f.write(json.dumps(summ)+'\n');f.flush();state=dict(cursor=ix+1,total=len(queue),last_cell=cell,last_batch_seconds=time.monotonic()-start);dump(cp,state);n+=1
    if n%16==0:print(json.dumps(state),flush=True)
  print(json.dumps(dict(**state,batch_cells=n,seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
