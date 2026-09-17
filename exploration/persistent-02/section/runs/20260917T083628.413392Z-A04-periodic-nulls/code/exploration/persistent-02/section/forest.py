"""Bounded prefix/middle/final alternative forest with exact conditional decodes."""
import pathlib,sys,json,gzip,argparse,time,hashlib
import numpy as np
O=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(O));import a02 as A
PERIODIC=A.A.module('original_kbest','exploration/persistent-01/worker-c/frozen_kbest.py')

def run(batch,label):
 t=time.monotonic();src=O/batch/(label+'.json.gz');d=json.load(gzip.open(src,'rt'));c=d['cipher'];ends=set(d['ends']);spans=d['spans'];cell=d['selected_cell'];lm=A.A.M.LM();decoder=PERIODIC if batch=='A01' else A.Finite;prefix=d['prefix_top'][0]['alternatives'];counts=[b-a+sum(a<=i<b for i in ends) for a,b in spans];results=[]
 for policy in ['continuous','page-reset']:
  cache={};plains=[];literals=[];scores=[];suffix=[];ranks=[]; maxerr=0.;replayed=0
  for pr,p in enumerate(prefix):
   history=next(x for x in d['continuations'] if x['policy']==policy and x['prefix_path_rank']==pr+1);middle=history['parts'][1]['alternatives'];pctx=A.A.ctxt(p['plain'],{i for i in ends if i<spans[0][1]})
   for mr,m in enumerate(middle):
    a,b=spans[1];me={i-a for i in ends if a<=i<b};context=A.A.ctxt(m['plain'],me,pctx);u=m['used'] if policy=='continuous' else 0;a,b=spans[2];fe={i-a for i in ends if a<=i<b};state=(u,context)
    if state not in cache:
     alts,diag=decoder.kbest(c[a:b],fe,cell['key'],cell['sign'],lm,retain=16,start_context=context,start_used=u)
     for alt in alts:assert A.A.forward(alt['plain'],cell['key'],cell['sign'],set(alt['literal_positions']),u)==(c[a:b],alt['used'])
     # The first cached state is recomputed independently as an explicit cache consistency check.
     if not cache:
      again,_=decoder.kbest(c[a:b],fe,cell['key'],cell['sign'],lm,retain=16,start_context=context,start_used=u);assert again==alts;replayed+=1
     cache[state]=(alts,diag)
    alts,_=cache[state]
    # Prefix and middle also re-encrypt; middle was frozen by the prior batch.
    assert A.A.forward(p['plain'],cell['key'],cell['sign'],set(p['literal_positions']),0)==(c[:spans[0][1]],p['used'])
    mu=p['used'] if policy=='continuous' else 0
    assert A.A.forward(m['plain'],cell['key'],cell['sign'],set(m['literal_positions']),mu)==(c[spans[1][0]:spans[1][1]],m['used'])
    for fr,f in enumerate(alts):
     plain=p['plain']+m['plain']+f['plain'];score=(p['score']*counts[0]+m['score']*counts[1]+f['score']*counts[2])/sum(counts);direct=lm.score(plain,ends);err=abs(score-direct);maxerr=max(maxerr,err);assert err<1e-11
     lit=np.zeros(len(c),dtype=np.uint8);lit[p['literal_positions']]=1;lit[[i+spans[1][0] for i in m['literal_positions']]]=1;lit[[i+spans[2][0] for i in f['literal_positions']]]=1
     plains.append(plain);literals.append(np.packbits(lit));scores.append(score);suffix.append((m['score']*counts[1]+f['score']*counts[2])/(counts[1]+counts[2]));ranks.append([pr+1,mr+1,fr+1])
  pp=np.asarray(plains,dtype=np.uint8);ss=np.asarray(suffix);best=int(ss.argmax()); rr=np.asarray(ranks,dtype=np.int16);stem=f'{batch}-{label}-{policy}';np.savez_compressed(O/'A04'/(stem+'.npz'),plain=pp,literal_bits=np.asarray(literals),full_score=np.asarray(scores),suffix_score=ss,stage_ranks=rr)
  row=dict(batch=batch,label=label,policy=policy,source=str(src.relative_to(O.parents[2])),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),selected_cell=cell,spans=spans,ends=sorted(ends),candidate_count=len(pp),distinct_plaintexts=len({bytes(x) for x in pp}),conditional_final_states=len(cache),cache_replay_checks=replayed,max_direct_score_error=maxerr,best_suffix_score=float(ss[best]),best_stage_ranks=rr[best].tolist(),best_transliteration=A.A.REF.render(pp[best]),array=stem+'.npz')
  if 'truth' in d:
   errors=np.count_nonzero(pp!=np.asarray(d['truth']),axis=1);ix=np.flatnonzero(errors==0);row.update(best_errors=int(errors[best]),minimum_errors=int(errors.min()),truth_members=len(ix),truth_stage_ranks=rr[ix].tolist(),truth_suffix_rank=(1+int(np.count_nonzero(ss>ss[ix[0]]))) if len(ix) else None,truth_suffix_ties=int(np.count_nonzero(ss==ss[ix[0]])) if len(ix) else None,planted_policy=d['plant']['policy'])
  (O/'A04'/(stem+'.json')).write_text(json.dumps(row,indent=2)+'\n');results.append(row)
 print(json.dumps(dict(batch=batch,label=label,seconds=time.monotonic()-t,rows=[{k:x[k] for k in ['policy','candidate_count','conditional_final_states','best_suffix_score','best_stage_ranks','best_errors','minimum_errors','truth_members','truth_suffix_rank'] if k in x} for x in results])),flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--batch',choices=['A01','A02'],required=True);ap.add_argument('--kind',choices=['controls','actual','nulls'],required=True);ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=19);a=ap.parse_args();(O/'A04').mkdir(exist_ok=True)
 if a.kind=='controls':names=['control-'+n for n in A.A.M.CHECK]
 elif a.kind=='actual':names=['actual-body','actual-whole']
 else:names=[f'null-{v}-{i:02}' for v in ['body','whole'] for i in range(a.start,a.start+a.count)]
 for name in names:run(a.batch,name)
if __name__=='__main__':main()
