"""Local path reconvergence and suffix-invariant dominance, frozen model/key only."""
import json,gzip,math,random,hashlib,time
from compare import O,LM
from complementary import LM as OtherLM
from exact import decode

def trace(cipher,key,sign,periodic,ends,literals,lm,initial=(29,29),start=0):
 ctx=initial;u=start;score=0.;rows=[];ends=set(ends);literal=set(literals)
 for i,c in enumerate(cipher):
  before=(u%len(key) if periodic else u,*ctx);lit=i in literal
  assert not lit or c==0
  assert periodic or lit or u<len(key)
  r=0 if lit else (c+sign*key[u%len(key)])%29;ct=ctx;ctx,w1=lm.step(ctx,r);tokens=[dict(context=list(ct),emitted=r,weight=w1)];w=w1
  if i in ends:
   ct=ctx;ctx,w2=lm.step(ctx,29);tokens.append(dict(context=list(ct),emitted=29,weight=w2));w+=w2
  score+=w;u+=not lit;after=(u%len(key) if periodic else u,*ctx);rows.append(dict(i=i,cipher=c,literal=lit,emitted=r,before=list(before),after=list(after),consumed=u-start,local_weight=w,total=score,contributions=tokens))
 return rows

def main():
 tick=time.monotonic();cases={c['id']:c for c in json.loads((O/'continuation-inputs.json').read_text())['cases']};out=[];rng=random.Random(260917208);suffix_checks=[]
 for model,lm in [('p03',LM()),('complementary',OtherLM())]:
  folder='fresh' if model=='p03' else 'complementary-fresh'
  for name in ['fresh-shelley-2','fresh-mill-1']:
   case=cases[name];prior=json.loads(gzip.decompress((O/folder/(name+'.json.gz')).read_bytes()));base=prior['case'];n=len(base['cipher']);wrong=prior['exact'][0];true=trace(base['cipher'],case['key'],base['sign'],base['periodic'],base['ends'],base['truth_literal_positions'],lm);bad=trace(base['cipher'],case['key'],base['sign'],base['periodic'],base['ends'],wrong['literal_positions'],lm)
   assert [r['emitted'] for r in true]==base['truth'];assert [r['emitted'] for r in bad]==wrong['plain'];segments=[];start=None
   for i,(a,b) in enumerate(zip(true,bad)):
    if start is None and (a['literal']!=b['literal'] or a['after']!=b['after']):start=i
    if start is not None and a['after']==b['after']:
     previous_true=0. if start==0 else true[start-1]['total'];previous_bad=0. if start==0 else bad[start-1]['total'];gap=sum(bad[j]['local_weight']-true[j]['local_weight'] for j in range(start,i+1));segments.append(dict(start=start,reconverged_after=i,state=a['after'],true_segment_weight=sum(r['local_weight'] for r in true[start:i+1]),wrong_segment_weight=sum(r['local_weight'] for r in bad[start:i+1]),wrong_minus_true=gap,true_rows=true[start:i+1],wrong_rows=bad[start:i+1],source_spans=case['source_char_spans'][start:i+1],qualifier='Real-sum gap invariant under identical legal suffix; float additions monotone so truth cannot overtake, although scores may round to ties.'))
     if gap>0:
      # Shared random cipher suffixes. Position/context identical, same exact path chosen for both.
      pos,aa,bb=a['after'];startabs=a['consumed'];remaining=len(case['key'])-startabs if not base['periodic'] else 200
      for trial in range(50):
       length=rng.randrange(0,min(200,remaining)+1);cipher=[0 if rng.random()<.1 else rng.randrange(1,29) for _ in range(length)];ends={j for j in range(length) if rng.random()<.2};alts,d=decode(cipher,case['key'],lm.extend,sign=base['sign'],periodic=base['periodic'],start=startabs,context=(aa,bb),ends=ends,retain=1)
       prefix_a=a['total'];prefix_b=b['total'];tail=trace(cipher,case['key'],base['sign'],base['periodic'],ends,alts[0]['literal_positions'],lm,initial=(aa,bb),start=startabs)
       for row in tail:prefix_a+=row['local_weight'];prefix_b+=row['local_weight'];assert prefix_b>=prefix_a
       suffix_checks.append(dict(model=model,id=name,segment_start=start,trial=trial,cipher=cipher,ends=sorted(ends),literal_positions=alts[0]['literal_positions'],true_final=prefix_a,wrong_final=prefix_b,gap=prefix_b-prefix_a))
     start=None
   unresolved=None if start is None else dict(start=start,true_final_state=true[-1]['after'],wrong_final_state=bad[-1]['after'],true_score=true[-1]['total'],wrong_score=bad[-1]['total'])
   out.append(dict(model=model,id=name,segments=segments,unreconverged=unresolved,prefix_length=n,true_literal_positions=base['truth_literal_positions'],wrong_literal_positions=wrong['literal_positions'],total_wrong_minus_true=bad[-1]['total']-true[-1]['total']))
 result=dict(cases=out,random_suffix_checks=len(suffix_checks),seed=260917208,seconds=time.monotonic()-tick,claim='At a common state, identical future legal decisions and weights are available. If a wrong history has greater score, every completion of the true history has a no-lower-scoring wrong counterpart. Extra unchanged suffix cannot make the true history uniquely optimal; floating arithmetic may tie. Applies only to current local score/state/key, not richer scorers or corrected source assumptions.')
 (O/'dominance.json').write_text(json.dumps(result,indent=2)+'\n');(O/'dominance-suffix-checks.json.gz').write_bytes(gzip.compress(json.dumps(suffix_checks).encode(),mtime=0));print(json.dumps({k:v for k,v in result.items() if k!='cases'}));print(json.dumps([dict(model=r['model'],id=r['id'],segments=[{k:s[k] for k in ['start','reconverged_after','state','wrong_minus_true']} for s in r['segments']],unreconverged=r['unreconverged']) for r in out],indent=2))
if __name__=='__main__':main()
