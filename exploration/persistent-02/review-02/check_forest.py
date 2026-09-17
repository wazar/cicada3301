"""Independent bounded-forest provenance/state/score reconstruction."""
import pathlib,sys,json,gzip,hashlib,math
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];S=R/'exploration/persistent-02/section';sys.path.insert(0,str(R/'exploration/persistent-02/decoder'))
from compare import LM
from complementary import LM as OtherLM
from exact import decode
def dump(name,x):(O/name).write_text(json.dumps(x,indent=2)+'\n')
def context(p,ends,start=(29,29)):
 tokens=list(start)
 for i,v in enumerate(p):tokens.append(v);tokens.extend([29] if i in ends else [])
 return tuple(tokens[-2:])
def forward(p,lit,key,sign,start,periodic):
 u=start;out=[]
 for i,r in enumerate(p):
  if i in lit:assert r==0;out.append(0)
  else:
   assert periodic or u<len(key);out.append((r-sign*key[u%len(key)])%29);u+=1
 return out,u
def main():
 panels=[('A01','control-jpg107-167','page-reset'),('A02','control-0_welcome','continuous'),('A02','control-p56_an_end','continuous'),('A05-finite','control-p57_parable','page-reset'),('A02','actual-body','continuous'),('A05-periodic','actual-whole','page-reset')];results=[]
 for batch,label,policy in panels:
  stem=f'{batch}-{label}-{policy}';meta=json.loads((S/'A04'/(stem+'.json')).read_text());source=R/meta['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==meta['source_sha256'];d=json.loads(gzip.decompress(source.read_bytes()));lm=OtherLM() if batch.startswith('A05') else LM();periodic=batch in ['A01','A05-periodic'];key=d['selected_cell']['key'];sign=d['selected_cell']['sign'];assert d['selected_cell']==meta['selected_cell']
  assert d['selected_cell']==d['prefix_cells'][0]['cell'];assert all(x['score']<=d['prefix_cells'][0]['score'] for x in d['prefix_cells'])
  with np.load(S/'A04'/meta['array']) as arr:arr={k:arr[k] for k in arr.files}
  assert arr['plain'].shape==(meta['candidate_count'],len(d['cipher']));assert len(arr['plain'])<=4096;assert len({bytes(x) for x in arr['plain']})==meta['distinct_plaintexts']
  ends=set(d['ends']);spans=d['spans'];assert spans[0][0]==0 and spans[-1][1]==len(d['cipher']) and spans[0][1]==spans[1][0] and spans[1][1]==spans[2][0];prefix=d['prefix_top'][0]['alternatives'];cache={};maxerr=0.;triples=[]
  for row,(pr,mr,fr) in enumerate(arr['stage_ranks']):
   p=prefix[int(pr)-1];middle=next(x for x in d['continuations'] if x['policy']==policy and x['prefix_path_rank']==int(pr))['parts'][1]['alternatives'];m=middle[int(mr)-1]
   a,b=spans[0];pc=context(p['plain'],{i for i in ends if i<b});a,b=spans[1];me={i-a for i in ends if a<=i<b};mc=context(m['plain'],me,pc);u=int(m['used']) if policy=='continuous' else 0;state=(u,mc);a,b=spans[2];fe={i-a for i in ends if a<=i<b}
   if state not in cache:cache[state]=decode(d['cipher'][a:b],key,lm.extend,sign=sign,periodic=periodic,start=u,context=mc,ends=fe,retain=16)[0]
   final=cache[state];plain=arr['plain'][row].tolist();literal=np.unpackbits(arr['literal_bits'][row])[:len(plain)];assert plain[:spans[0][1]]==p['plain'] and plain[spans[1][0]:spans[1][1]]==m['plain']
   # Independent cut-state scoring; final tied representatives may differ.
   ctx=mc;sc=0.
   for i,v in enumerate(plain[a:b]):ctx,w=lm.extend(ctx,v,i in fe);sc+=w
   assert abs(sc-final[int(fr)-1]['total'])<1e-10
   used=0
   for lo,hi in spans:
    if policy=='page-reset':used=0
    got,used=forward(plain[lo:hi],set(np.flatnonzero(literal[lo:hi]).tolist()),key,sign,used,periodic);assert got==d['cipher'][lo:hi]
   score=lm.score(plain,ends);maxerr=max(maxerr,abs(score-float(arr['full_score'][row])));assert abs(score-float(arr['full_score'][row]))<1e-11
   ctx=pc;ss=0.;lo=spans[1][0]
   for i,v in enumerate(plain[lo:],lo):ctx,w=lm.extend(ctx,v,i in ends);ss+=w
   suffix=ss/(len(plain)-lo+sum(e>=lo for e in ends));assert abs(suffix-float(arr['suffix_score'][row]))<1e-11
   triples.append((int(pr),int(mr),int(fr)))
  assert len(triples)==len(set(triples));assert len(cache)==meta['conditional_final_states'];winner=int(arr['suffix_score'].argmax());assert float(arr['suffix_score'][winner])==meta['best_suffix_score'];assert arr['stage_ranks'][winner].tolist()==meta['best_stage_ranks']
  if 'truth' in d:
   errors=np.count_nonzero(arr['plain']!=np.array(d['truth']),axis=1);assert int(errors.min())==meta['minimum_errors']==0;assert int((errors==0).sum())==meta['truth_members'];assert int(errors[winner])==meta['best_errors']
  results.append(dict(batch=batch,label=label,policy=policy,candidates=len(triples),conditional_final_states=len(cache),max_direct_score_error=maxerr,best_suffix_ranks=meta['best_stage_ranks'],best_full_ranks=arr['stage_ranks'][arr['full_score'].argmax()].tolist(),source_sha256=meta['source_sha256']))
  print('forest passed',stem,len(triples),flush=True)
 dump('forest-checks.json',dict(passed=True,panels=results,scope='Four consequential control panels and two actual metadata panels; bounded16cubed forest, not full global plaintext search. No negative comparator rerun.'))
if __name__=='__main__':main()
