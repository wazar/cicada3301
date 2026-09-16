"""Frozen full-selection negative panels and post-gate real slices; never called on failure."""
import random,json,hashlib

def finish(c,sk,keys,fixtures,spec,outdir):
 def select(cs):
  result={'ciphertext':cs,'choices':[],'hypotheses':[]}
  for label,K in keys.items():
   for sign in [-1,1]:
    scores=[];winners=[]
    for page,C in enumerate(cs):
     rows=[]
     for mode in ['rigid','beam']:
      out=sk.rigid_decode(C,K,sign=sign,o=0) if mode=='rigid' else c.traced_beam(sk,C,K,sign)
      if mode=='rigid':out['key_use']=list(range(120))
      out.update(recipe=label,sign=sign,page=page,mode=mode);rows.append(out);result['choices'].append(out)
     mx=max(x['score'] for x in rows);scores.append(mx);winners.append([x['mode'] for x in rows if x['score']==mx])
    result['hypotheses'].append({'recipe':label,'sign':sign,'page_scores':scores,'winning_decoders':winners,'joint':min(scores)})
  result['joint']=max(h['joint'] for h in result['hypotheses'])
  result['top_hypotheses']=[h for h in result['hypotheses'] if h['joint']==result['joint']]
  return result
 calibration=[];heldout=[]
 signed={tuple(sign*v%29 for v in K) for K in keys.values() for sign in [-1,1]}
 for i in range(200):
  phase='calibration' if i<100 else 'heldout';seed=920000+i;rng=random.Random(seed)
  while True:
   K=[rng.randrange(29) for _ in range(2048)]
   if tuple(K) not in signed and tuple(-v%29 for v in K) not in signed:break
  sign=-1 if i%4<2 else 1;supp=0 if i%2==0 else .83;P=fixtures[i%20]['plaintext'];cs=[];traces=[]
  for page,p in enumerate(P):
   C,tr=c.encrypt(p,K,sign,seed+1000000+page,supp);cs.append(C);traces.append(tr)
  result=select(cs);result.update(phase=phase,index=i,seed=seed,plaintext=P,source_text=fixtures[i%20]['texts'],plant_key=K,plant_sign=sign,suppression=supp,encryption_state_trace=traces)
  if phase=='calibration':calibration.append(result['joint']);result['decision']='CALIBRATION_ONLY'
  else:
   threshold=max(calibration)+.5;result['calibration_maximum']=max(calibration);result['threshold']=threshold
   result['flag']=result['joint']>=-5.5 and result['joint']>threshold;heldout.append(result['flag'])
  c.dump(outdir/f'{phase}-{i:03d}.json',result)
  if phase=='heldout' and result['flag']:
   return {'outcome':'BLOCKED_BY_CALIBRATION','calibration_count':len(calibration),'heldout_count':len(heldout),'heldout_flags':sum(heldout),'shuffle':'SKIPPED: heldout flag','real':'SKIPPED: heldout flag'}
 slices=c.load('slices.json');real=[p['indices'] for p in slices]
 # Histogram sensitivity is descriptive only: never used to tune the rule.
 for i in range(100):
  rng=random.Random(930000+i);cs=[v.copy() for v in real]
  for v in cs:rng.shuffle(v)
  result=select(cs);result.update(phase='shuffle',seed=930000+i,warning='Shuffling preserves histogram, destroys adjacency and repeat patterns; separate descriptive sensitivity, no threshold tuning')
  c.dump(outdir/f'shuffle-{i:03d}.json',result)
 result=select(real);threshold=max(calibration)+.5;result.update(phase='real',slice_hashes=[s['sha256_bytes_indices'] for s in slices],calibration_maximum=max(calibration),threshold=threshold,flag=result['joint']>=-5.5 and result['joint']>threshold)
 result['single_page_interest']=[{'recipe':v['recipe'],'sign':v['sign'],'page':v['page'],'mode':v['mode'],'score':v['score']} for v in result['choices'] if v['score']>=-5.5]
 c.dump(outdir/'real.json',result)
 return {'outcome':'COMPLETED_WITH_FLAG' if result['flag'] else 'COMPLETED_NO_FLAG','calibration_count':100,'heldout_count':100,'heldout_flags':0,'conditional_one_sided_95percent_upper_bound':1-.05**(1/100),'shuffle_count':100,'real_page_choices':32,'joint':result['joint'],'calibration_maximum':max(calibration),'threshold':threshold}
