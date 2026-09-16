"""Exploratory unknown periodic key + latent literalF using frozen rune LM."""
import argparse,random,json,time,collections
from p03 import O,ROOT,ABC,LM,parse,dump,beam

def fit(c,ends,period,lm,seed,width=32,restarts=2,sweeps=3):
 rng=random.Random(seed);initial=[]
 for j in range(period):
  vals=[]
  for k in range(29):
   vals.append(sum(lm.step((29,29),(v-k)%29)[1] for i,v in enumerate(c) if i%period==j))
  initial.append(max(range(29),key=vals.__getitem__))
 best=None;starts=[];evals=0;expanded=0
 for restart in range(restarts):
  key=initial.copy() if restart==0 else [rng.randrange(29) for _ in range(period)]
  alts,d=beam(c,ends,key,-1,lm,width);evals+=1;expanded+=d['expanded'];value=alts[0]['score']
  for _ in range(sweeps):
   change=False;order=list(range(period));rng.shuffle(order)
   for j in order:
    variants=[]
    for k in range(29):
     trial=key.copy();trial[j]=k;a,d=beam(c,ends,trial,-1,lm,width);evals+=1;expanded+=d['expanded'];variants.append((a[0]['score'],trial,a))
    sc,trial,a=max(variants,key=lambda x:x[0])
    if sc>value+1e-12:key=trial;value=sc;alts=a;change=True
   if not change:break
  starts.append(dict(restart=restart,key=key,score=value,alternatives=alts))
  if best is None or value>best['score']:best=dict(key=key,score=value,alternatives=alts)
 return best,starts,evals,expanded

def continuation(c,ends,split,key,train,lm,width):
 s=(29,29)
 for i,r in enumerate(train['plain']):s,_=lm.extend(s,r,i in ends)
 return beam(c[split:],{i-split for i in ends if i>=split},key,-1,lm,width,start_context=s,start_used=train['used'])[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--label',default='p08');ap.add_argument('--width',type=int,default=32);ap.add_argument('--real-all',action='store_true');a=ap.parse_args();out=O/a.label;out.mkdir(exist_ok=True);lm=LM();rng=random.Random(330108);cases=[]
 for name in ([] if a.real_all else ['0_welcome','jpg107-167']):
  truth,ends=parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text())
  for period in [1,3,8]:
   key=[rng.randrange(29) for _ in range(period)];c=[];u=0;path=[]
   for i,p in enumerate(truth):
    if p==0 and i%3!=1:c.append(0);path.append(i)
    else:c.append((p+key[u%period])%29);u+=1
   cases.append(dict(id=f'control-{name}-{period}',cipher=c,ends=sorted(ends),period=period,truth=truth,truth_key=key,truth_path=path))
   sh=c.copy();rng.shuffle(sh);cases.append(dict(id=f'control-null-{name}-{period}',cipher=sh,ends=sorted(ends),period=period))
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());pages=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages']
 for page in pages:
  if (page['original_page']>55 or page['original_page']==50 or page['original_page'] in cfg['reserved_original_pages']) if a.real_all else page['original_page'] not in [0,17,55]:continue
  assert page['original_page'] not in cfg['reserved_original_pages'];c,ends=parse('/'.join(l['raw'] for l in page['lines']));assert c==page['indices']
  for period in [1,3,8]:
   cases.append(dict(id=f'real-{page["original_page"]}-{period}',cipher=c,ends=sorted(ends),period=period));sh=c.copy();rng.shuffle(sh);cases.append(dict(id=f'real-null-{page["original_page"]}-{period}',cipher=sh,ends=sorted(ends),period=period))
 dump(out/'frozen-cases.json',cases);results=[];t=time.monotonic()
 for ix,case in enumerate(cases):
  c=case['cipher'];ends=set(case['ends']);split=len(c)//2;trainends={i for i in ends if i<split};best,starts,evals,expanded=fit(c[:split],trainends,case['period'],lm,330108+ix,a.width);cont=continuation(c,ends,split,best['key'],best['alternatives'][0],lm,a.width);row=dict(**case,split=split,best=best,starts=starts,evaluations=evals,path_expansions=expanded,continuation=cont)
  if 'truth' in case:
   truth=case['truth'];oracle,diag=beam(c[:split],trainends,case['truth_key'],-1,lm,a.width,truth=[i for i in case['truth_path'] if i<split]);row.update(key_errors=sum(x!=y for x,y in zip(best['key'],case['truth_key'])),train_errors=sum(x!=y for x,y in zip(best['alternatives'][0]['plain'],truth[:split])),continuation_errors=sum(x!=y for x,y in zip(cont[0]['plain'],truth[split:])),oracle_errors=sum(x!=y for x,y in zip(oracle[0]['plain'],truth[:split])),oracle=oracle,oracle_diagnostics=diag)
  results.append(row);dump(out/'results.json',results);summary=dict(id=case['id'],train_score=best['score'],continuation_score=cont[0]['score'],evaluations=evals,elapsed=time.monotonic()-t,**{k:row[k] for k in ['key_errors','train_errors','continuation_errors','oracle_errors'] if k in row});print(json.dumps(summary),flush=True)
 dump(out/'summary.json',dict(cases=len(cases),seconds=time.monotonic()-t,evaluations=sum(r['evaluations'] for r in results)))
if __name__=='__main__':main()
