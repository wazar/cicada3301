"""Third/final rule: fixed major-mark key resets, frozen prefix and exact joint suffix."""
import pathlib,sys,json,gzip,hashlib,random,time,argparse
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];sys.path.insert(0,str(O));import a02 as A;import marked_exact as D
sys.path.insert(0,str(R/'exploration/persistent-02/decoder'));from complementary import LM
RESET_WHOLE=[13,154,275,297,350,394,434,531];RESET_BODY=[x-13 for x in RESET_WHOLE if x>13]

def cells(family):
 if family=='periodic':
  return [dict(id=f"{k['id']}:{p}:{s}",key_id=k['id'],phase=p,sign=s,key=k['runes'][p:]+k['runes'][:p]) for k in json.loads((O/'key-grid.json').read_text())['keys'] for p in range(len(k['runes'])) for s in [-1,1]]
 return [dict(id=f'{name}:{sign}',key_id=name,phase=0,sign=sign,key=[(p-delta)%29 for p in A.A.REF.primes(800)]) for name,delta in [('primes',0),('totients-of-primes',1)] for sign in [-1,1]]

def freeze():
 out=O/'A07-inputs.json';assert not out.exists();packet=json.loads((O/'section-packet.json').read_text());cs={f:cells(f) for f in ['periodic','finite']};sources=[]
 for name in A.A.M.CHECK:
  p,e=A.A.M.parse((R/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text());sources.append(dict(id='lp-'+name,truth=p,ends=sorted(e),source='audit/parallel-01/reference/sources/solved_'+name+'.txt'))
 fresh=json.loads((R/'exploration/persistent-02/decoder/fresh-controls.json').read_text())
 for x in fresh['cases']:
  if len(x['truth'])==716:sources.append(dict(id=x['id'],truth=x['truth'],ends=x['ends'],source=x['source'],source_rune_span=x['source_rune_span'],source_char_spans=x['source_char_spans']))
 rng=random.Random(260917307);controls=[]
 for family in ['periodic','finite']:
  for src in sources:
   p=src['truth'];n=len(p);candidates=[e+1 for e in src['ends'] if e+1<n];resets=sorted({min(candidates,key=lambda x:(abs(x-r*n/716),x)) for r in RESET_BODY});cell=cs[family][rng.randrange(len(cs[family]))];literal=[i for i,v in enumerate(p) if v==0 and i%3!=1];c,pos,used=D.encipher(p,cell['key'],cell['sign'],literal,periodic=family=='periodic',reset_before=resets)
   controls.append(dict(**src,id=family+'-'+src['id'],family=family,cipher=c,reset_before=resets,spans=[[0,n*249//716],[n*249//716,n*515//716],[n*515//716,n]],plant=cell,truth_literal_positions=literal,truth_final_position=pos,truth_used=used))
 layout=dict(whole_reset_before=RESET_WHOLE,body_reset_before=RESET_BODY,site_manifest='exploration/persistent-02/section/inspection/major-marks/manifest.json',ordinary_single_dots_reset=False,score_context_reset=False,physical_page_reset=False)
 obj=dict(layout=layout,controls=controls,grid=cs,control_selection_seed=260917307,inputs={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['exploration/persistent-02/section/section-packet.json','exploration/persistent-02/section/key-grid.json','exploration/persistent-02/decoder/fresh-controls.json']})
 out.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(dict(controls=len(controls),lengths=[len(x['cipher']) for x in controls],sha256=hashlib.sha256(out.read_bytes()).hexdigest())))

def score_parts(plain,ends,spans,lm):
 ctx=(29,29);totals=[0.,0.,0.];counts=[0,0,0];part=0
 for i,r in enumerate(plain):
  while i>=spans[part][1]:part+=1
  ctx,w=lm.extend(ctx,r,i in ends);totals[part]+=w;counts[part]+=1+int(i in ends)
 return [x/n for x,n in zip(totals,counts)]

def run(case,model,family,grid,lm):
 t=time.monotonic();out=O/'A07'/model/family;out.mkdir(parents=True,exist_ok=True);c=case['cipher'];ends=set(case['ends']);resets=set(case['reset_before']);spans=case['spans'];cut=spans[0][1];pe={e for e in ends if e<cut};se={e-cut for e in ends if e>=cut};pr={r for r in resets if r<cut};sr={r-cut for r in resets if r>=cut};periodic=family=='periodic';rows=[]
 for cell in grid:
  alts,diag=D.decode(c[:cut],cell['key'],lm.extend,sign=cell['sign'],periodic=periodic,ends=pe,reset_before=pr);rows.append(dict(cell=cell,score=alts[0]['score'],alternatives=alts,diagnostics=diag))
 rows.sort(key=lambda x:x['score'],reverse=True);selected=rows[0];cell=selected['cell'];pref=selected['alternatives'];full=[];bits=[];ranks=[];score=[];suffixscores=[];suffixcalls=[];directerr=0.
 for i,p in enumerate(pref):
  ctx=A.A.ctxt(p['plain'],pe);alts,diag=D.decode(c[cut:],cell['key'],lm.extend,sign=cell['sign'],periodic=periodic,start=p['position'],context=ctx,ends=se,reset_before=sr)
  assert D.encipher(p['plain'],cell['key'],cell['sign'],p['literal_positions'],periodic=periodic,reset_before=pr)==(c[:cut],p['position'],p['used'])
  for j,s in enumerate(alts):
   assert D.encipher(s['plain'],cell['key'],cell['sign'],s['literal_positions'],periodic=periodic,start=p['position'],reset_before=sr)==(c[cut:],s['position'],s['used'])
   plain=p['plain']+s['plain'];lit=p['literal_positions']+[cut+k for k in s['literal_positions']];assert D.encipher(plain,cell['key'],cell['sign'],lit,periodic=periodic,reset_before=resets)==(c,s['position'],p['used']+s['used']);v=(p['total']+s['total'])/(len(c)+len(ends));error=abs(v-lm.score(plain,ends));directerr=max(directerr,error);assert error<1e-11
   full.append(plain);b=np.zeros(len(c),dtype=np.uint8);b[lit]=1;bits.append(np.packbits(b));ranks.append([i+1,j+1]);score.append(v);suffixscores.append(s['score'])
  suffixcalls.append(dict(prefix_rank=i+1,start_position=p['position'],start_context=ctx,alternatives=alts,diagnostics=diag))
 pp=np.asarray(full,dtype=np.uint8);fs=np.asarray(score);ss=np.asarray(suffixscores);best=int(fs.argmax());sb=int(ss.argmax());np.savez_compressed(out/(case['id']+'.npz'),plain=pp,literal_bits=np.asarray(bits),stage_ranks=np.asarray(ranks,dtype=np.int16),full_score=fs,suffix_score=ss)
 result=dict(case=case,model=model,family=family,prefix_cells=[dict(cell=x['cell'],score=x['score']) for x in rows],prefix_top=rows[:5],selected_cell=cell,suffix_calls=suffixcalls,candidate_count=len(pp),distinct_plaintexts=len({bytes(x) for x in pp}),best_full_score=float(fs[best]),best_suffix_score=float(ss[sb]),full_winner=dict(stage_ranks=ranks[best],plain=pp[best].tolist(),transliteration=A.A.REF.render(pp[best]),part_scores=score_parts(pp[best],ends,spans,lm)),suffix_winner=dict(stage_ranks=ranks[sb],plain=pp[sb].tolist(),transliteration=A.A.REF.render(pp[sb]),part_scores=score_parts(pp[sb],ends,spans,lm)),max_direct_score_error=directerr,seconds=time.monotonic()-t)
 if 'truth' in case:
  truth=case['truth'];errs=np.count_nonzero(pp!=np.asarray(truth),axis=1);ix=np.flatnonzero(errs==0);tr=next(x for x in rows if x['cell']['id']==case['plant']['id']);oracle,od=D.decode(c,case['plant']['key'],lm.extend,sign=case['plant']['sign'],periodic=periodic,ends=ends,reset_before=resets)
  result['control']=dict(true_key_prefix_rank=1+sum(x['score']>tr['score']+1e-12 for x in rows),truth_in_fixed_prefix_candidate_set=bool(len(ix)),best_errors=int(errs[best]),minimum_errors=int(errs.min()),truth_full_rank=1+int(np.count_nonzero(fs>fs[ix[0]]+1e-12)) if len(ix) else None,truth_stage_ranks=np.asarray(ranks)[ix].tolist(),oracle_known_key_complete_errors=sum(a!=b for a,b in zip(oracle[0]['plain'],truth)),oracle_truth_top16_ranks=[i+1 for i,x in enumerate(oracle) if x['plain']==truth],oracle_alternatives=oracle,oracle_diagnostics=od)
 with gzip.open(out/(case['id']+'.json.gz'),'wt') as f:json.dump(result,f)
 print(json.dumps(dict(id=case['id'],model=model,family=family,key=cell['id'],full=result['best_full_score'],suffix=result['best_suffix_score'],seconds=result['seconds'],control={k:v for k,v in result.get('control',{}).items() if k not in ['oracle_alternatives','oracle_diagnostics']})),flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--action',choices=['freeze','controls','actual','nulls'],required=True);ap.add_argument('--model',choices=['p03','complementary'],default='p03');ap.add_argument('--family',choices=['periodic','finite'],default='periodic');a=ap.parse_args()
 if a.action=='freeze':freeze();return
 inp=json.loads((O/'A07-inputs.json').read_text());lm=A.A.M.LM() if a.model=='p03' else LM();grid=inp['grid'][a.family]
 if a.action=='controls':cases=[x for x in inp['controls'] if x['family']==a.family]
 else:
  packet=json.loads((O/'section-packet.json').read_text());cases=[];nulls=json.loads((R/'exploration/persistent-02/decoder/null-calibration-inputs.json').read_text())['packets']
  for variant in ['body','whole']:
   original=json.load(gzip.open(O/'A01'/('actual-'+variant+'.json.gz'),'rt'));sources=[('actual-'+variant,original['cipher'])] if a.action=='actual' else [(f'null-{variant}-{j:02}',x[13:] if variant=='body' else x) for j,x in enumerate(nulls)]
   for label,c in sources:cases.append(dict(id=label,cipher=c,ends=original['ends'],spans=original['spans'],reset_before=RESET_BODY if variant=='body' else RESET_WHOLE))
 for case in cases:run(case,a.model,a.family,grid,lm)
if __name__=='__main__':main()
