"""Frozen positive-gate executor; inherited code is read-only, trace copy is checked."""
import pathlib,json,random,hashlib,importlib.util,time,datetime,argparse
O=pathlib.Path(__file__).resolve().parent;R=O.parents[1]
def load(n):return json.loads((O/n).read_text())
def sha(n):return hashlib.sha256((O/n).read_bytes()).hexdigest()
def dump(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def traced_beam(sk,C,K,sign):
 # Same enumeration, scoring, stable sorting, and tie selection as inherited beam.
 # Extra tuple slot records accepted-key history only; first five slots unchanged.
 d,floor=sk.Q.d,sk.Q.floor;p0=(C[0]+sign*K[0])%29;t0=sk.gp.IDX_TO_TRANS[p0]
 beams=[(0.,0,t0,[p0],C[0],[0])];widths=[]
 for i in range(1,len(C)):
  ci=C[i];nxt=[]
  for sc,pa,tl,pidx,cprev,trace in beams:
   for dsk in range(4):
    acc=pa+1+dsk
    if acc>=len(K):break
    p=(ci+sign*K[acc])%29
    if any((p-sign*K[m])%29!=cprev for m in range(pa+1,acc)):continue
    add=sk.gp.IDX_TO_TRANS[p];nsc=sc+sk._quad_delta(tl,add,floor,d)
    nxt.append((nsc,acc,tl+add,pidx+[p],ci,trace+[acc]))
  if not nxt:break
  nxt.sort(key=lambda x:x[0],reverse=True);beams=nxt[:400]
  widths.append({'rune':i,'expanded':len(nxt),'retained':len(beams)})
 best=max(beams,key=lambda x:x[0]);out={'score':sk.Q.score_norm(best[2]),'beam_score':best[0],'plain_idx':best[3],'ptr_end':best[1],'translit':best[2]}
 # Exact dictionary check includes every production field and floating-point score.
 production=sk.beam_decode(C,K,sign=sign,o=0,beam_w=400,max_skip=3)
 assert out==production,{'instrumentation_mismatch':out,'production':production}
 return dict(production,key_use=best[5],beam_widths=widths,instrumentation_equals_production=True,top_cumulative_beam_ties=[{'plain_idx':b[3],'key_use':b[5],'beam_score':b[0],'score':sk.Q.score_norm(b[2])} for b in beams if b[0]==best[0]])
def encrypt(P,K,sign,seed,supp):
 rng=random.Random(seed);j=0;C=[];trace=[]
 for i,p in enumerate(P):
  attempts=[]
  while True:
   c=(p-sign*K[j])%29;repeat=bool(C and c==C[-1]);u=rng.random() if repeat and supp else None;reject=bool(repeat and supp and u<supp)
   attempts.append({'key_index':j,'key_value':K[j],'candidate_cipher':c,'repeats_previous':repeat,'random_uniform':u,'rejected':reject})
   j+=1
   if not reject:break
  C.append(c);trace.append({'rune':i,'plain':p,'previous_cipher':C[-2] if i else None,'attempts':attempts,'accepted_key_index':j-1,'cipher':c,'next_key_index':j})
 return C,trace

def main():
 a=argparse.ArgumentParser();a.add_argument('--limit',type=int,default=1);a.add_argument('--start',type=int,default=0);args=a.parse_args()
 start=time.monotonic();spec=load('preregistration.json');fr=load('FREEZE.json')
 for n in ['preregistration','keys','fixtures','slices']:
  assert sha(n+'.json')==fr[n+'_sha256']
 keys=load('keys.json');fixtures=load('fixtures.json');plan=spec['positive_cells']
 outdir=O/'outputs'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');outdir.mkdir(parents=True)
 module=importlib.util.spec_from_file_location('next01_sk',R/'liber-primus/analysis/campaign18_skip/skipdecode.py');sk=importlib.util.module_from_spec(module);module.loader.exec_module(sk)
 # Independent encryptor arithmetic tests, including both inverse signs.
 assert encrypt([2,3,4],[1,0,2,5,8,9],-1,1,1)[0]==[3,5,9]
 assert encrypt([28,1],[2,28],-1,1,0)[0]==[1,0]
 assert encrypt([28,1],[2,28],1,1,0)[0]==[26,2]
 assert all(len(p)==120 for f in fixtures for p in f['plaintext'])
 assert list(sk.gp.IDX_TO_TRANS.values())==spec['alphabet_tokens'] if isinstance(sk.gp.IDX_TO_TRANS,dict) else sk.gp.IDX_TO_TRANS==spec['alphabet_tokens']
 groups={}
 for label,K in keys.items():
  for sign in [-1,1]:groups.setdefault(tuple(sign*v%29 for v in K),[]).append({'recipe':label,'sign':sign})
 dump(outdir/'candidate-dedup.json',{'distinct_signed_arrays':len(groups),'groups':list(groups.values()),'key_hashes':{k:hashlib.sha256(bytes(v)).hexdigest() for k,v in keys.items()}})
 summary={'preregistration_sha256':fr['preregistration_sha256'],'planned_cells':plan,'planned_cases':320,'executed':[],'calibration':'SKIPPED: positives not fully passed','heldout':'SKIPPED: positives not fully passed','shuffle':'SKIPPED: synthetic gates not fully passed','real':'SKIPPED: synthetic gates not fully passed','outcome':'PILOT_COMPLETE'}
 for ordinal in range(args.start,min(320,args.start+args.limit)):
  cellindex,case=divmod(ordinal,20);cell=plan[cellindex];K=keys[cell['recipe']];ps=fixtures[case]['plaintext'];cs=[];traces=[]
  for page,P in enumerate(ps):
   ct,tr=encrypt(P,K,cell['sign'],910000+cellindex*1000+case*2+page,.83 if cell['model']=='rejection_beam' else 0);cs.append(ct);traces.append(tr)
  result={'ordinal':ordinal,'cell_index':cellindex,'cell':cell,'case':case,'seed_per_page':[910000+cellindex*1000+case*2+p for p in [0,1]],'plaintext':ps,'source_text':fixtures[case]['texts'],'ciphertext':cs,'plant_key':K,'encryption_state_trace':traces,'choices':[],'hypotheses':[]}
  for label,key in keys.items():
   for sign in [-1,1]:
    page_best=[];winning=[]
    for page,C in enumerate(cs):
     choices=[]
     for mode in ['rigid','beam']:
      out=sk.rigid_decode(C,key,sign=sign,o=0) if mode=='rigid' else traced_beam(sk,C,key,sign)
      if mode=='rigid':out['key_use']=list(range(120))
      out.update(recipe=label,sign=sign,mode=mode,page=page,exact=out['plain_idx']==ps[page],rune_matches=sum(a==b for a,b in zip(out['plain_idx'],ps[page])))
      choices.append(out);result['choices'].append(out)
     mx=max(v['score'] for v in choices);page_best.append(mx);winning.append([v['mode'] for v in choices if v['score']==mx])
    result['hypotheses'].append({'recipe':label,'sign':sign,'page_scores':page_best,'winning_decoders':winning,'joint':min(page_best)})
  maximum=max(h['joint'] for h in result['hypotheses']);top=[h for h in result['hypotheses'] if h['joint']==maximum]
  planted=next(h for h in result['hypotheses'] if h['recipe']==cell['recipe'] and h['sign']==cell['sign'])
  required_mode='rigid' if cell['model']=='unfiltered_rigid' else 'beam'
  required=[v for v in result['choices'] if v['recipe']==cell['recipe'] and v['sign']==cell['sign'] and v['mode']==required_mode]
  required_exact=all(v['exact'] for v in required)
  selected_exact=all(any(v['exact'] and v['mode'] in planted['winning_decoders'][page] for v in result['choices'] if v['recipe']==cell['recipe'] and v['sign']==cell['sign'] and v['page']==page) for page in [0,1])
  result.update(top_hypotheses=top,planted_is_tied_top=planted in top,required_mode=required_mode,required_exact=required_exact,selected_exact=selected_exact,passed=required_exact and selected_exact and planted in top,truth_scores=[sk.Q.score_norm(''.join(spec['alphabet_tokens'][x] for x in p)) for p in ps])
  name=f'case-{ordinal:03d}.json';dump(outdir/name,result)
  summary['executed'].append({'ordinal':ordinal,'cell_index':cellindex,'case':case,'passed':result['passed'],'path':name,'required_exact':required_exact,'selected_exact':selected_exact,'planted_is_tied_top':planted in top})
  print(json.dumps(summary['executed'][-1]),flush=True)
  if not result['passed']:
   summary['outcome']='BLOCKED_BY_POSITIVE_CONTROL';break
 summary['elapsed_seconds']=time.monotonic()-start
 done={x['ordinal'] for x in summary['executed']}
 summary['not_executed_this_run']=[{'ordinal':i,'cell_index':i//20,'case':i%20,'reason':'stopped after first required failure' if summary['outcome']=='BLOCKED_BY_POSITIVE_CONTROL' else 'outside bounded pilot'} for i in range(320) if i not in done]
 dump(outdir/'summary.json',summary);print(json.dumps({'output':str(outdir.relative_to(R)),'outcome':summary['outcome'],'seconds':summary['elapsed_seconds']}))
if __name__=='__main__':main()
