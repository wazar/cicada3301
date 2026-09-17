"""Frozen H3 plants and one complete prefix/joint-suffix adapter panel."""
import pathlib,sys,json,gzip,random,hashlib,numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];S=R/'exploration/persistent-02/section';sys.path.insert(0,str(R/'exploration/persistent-02/decoder'))
from compare import LM,parse
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
def forward(p,lit,key,sign,resets,periodic,start=0):
 pos=start;used=0;c=[]
 for i,v in enumerate(p):
  if i in resets:pos=0
  if i in lit:assert v==0;c.append(0)
  else:
   assert periodic or pos<len(key);c.append((v-sign*key[pos])%29);used+=1;pos=(pos+1)%len(key) if periodic else pos+1
 return c,pos,used
def context(p,ends):
 tokens=[29,29]
 for i,v in enumerate(p):tokens.append(v);tokens.extend([29] if i in ends else [])
 return tuple(tokens[-2:])
def main():
 d=json.loads((S/'A07-inputs.json').read_text());fresh=json.loads((R/'exploration/persistent-02/decoder/fresh-controls.json').read_text());rng=random.Random(260917307);controls=d['controls'];assert len(controls)==16;inputs=[]
 for path,digest in d['inputs'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest
 for c in controls:
  if c['source'].startswith('audit/'):
   truth,ends=parse((R/c['source']).read_text());assert truth==c['truth'] and sorted(ends)==c['ends']
  else:
   src=next(x for x in fresh['cases'] if x['source']==c['source'] and len(x['truth'])==716);assert c['truth']==src['truth'] and c['ends']==src['ends'] and c['source_char_spans']==src['source_char_spans']
  n=len(c['truth']);ends=[x+1 for x in c['ends'] if x+1<n];resets=sorted({min(ends,key=lambda e:(abs(e-r*n/716),e)) for r in d['layout']['body_reset_before']});assert resets==c['reset_before'];grid=d['grid'][c['family']];plant=grid[rng.randrange(len(grid))];assert plant==c['plant'];literal=[i for i,x in enumerate(c['truth']) if x==0 and i%3!=1];assert literal==c['truth_literal_positions'];assert c['spans']==[[0,n*249//716],[n*249//716,n*515//716],[n*515//716,n]]
  assert forward(c['truth'],set(literal),plant['key'],plant['sign'],set(resets),c['family']=='periodic')==(c['cipher'],c['truth_final_position'],c['truth_used']);inputs.append(dict(id=c['id'],length=n,resets=resets))
 name='periodic-fresh-guest-2';path=S/'A07/p03/periodic'/(name+'.json.gz');rec=json.loads(gzip.decompress(path.read_bytes()));case=next(x for x in controls if x['id']==name);assert rec['case']==case;cell=rec['selected_cell'];assert cell==rec['prefix_cells'][0]['cell'];assert all(x['score']<=rec['prefix_cells'][0]['score'] for x in rec['prefix_cells'])
 with np.load(path.with_suffix('').with_suffix('.npz')) as raw:a={k:raw[k] for k in raw.files}
 n=len(case['cipher']);cut=case['spans'][0][1];ends=set(case['ends']);pe={x for x in ends if x<cut};se={x-cut for x in ends if x>=cut};resets=set(case['reset_before']);pr={x for x in resets if x<cut};sr={x-cut for x in resets if x>=cut};lm=LM();prefix=rec['prefix_top'][0]['alternatives'];maxerror=0.;different_clock=0
 for j,(pi,si) in enumerate(a['stage_ranks']):
  p=prefix[int(pi)-1];call=rec['suffix_calls'][int(pi)-1];s=call['alternatives'][int(si)-1];ctx=context(p['plain'],pe);assert call['start_position']==p['position'] and tuple(call['start_context'])==ctx
  assert forward(p['plain'],set(p['literal_positions']),cell['key'],cell['sign'],pr,True)==(case['cipher'][:cut],p['position'],p['used'])
  assert forward(s['plain'],set(s['literal_positions']),cell['key'],cell['sign'],sr,True,start=p['position'])==(case['cipher'][cut:],s['position'],s['used']);different_clock+=p['position']!=p['used']%len(cell['key'])
  plain=p['plain']+s['plain'];assert plain==a['plain'][j].tolist();lit=set(np.flatnonzero(np.unpackbits(a['literal_bits'][j])[:n]).tolist());assert lit==set(p['literal_positions']+[cut+x for x in s['literal_positions']]);assert forward(plain,lit,cell['key'],cell['sign'],resets,True)==(case['cipher'],s['position'],p['used']+s['used'])
  direct=lm.score(plain,ends);maxerror=max(maxerror,abs(direct-float(a['full_score'][j])));assert abs(direct-float(a['full_score'][j]))<1e-11;total=0.
  for i,x in enumerate(s['plain']):ctx,w=lm.extend(ctx,x,i in se);total+=w
  assert abs(total/(len(s['plain'])+len(se))-float(a['suffix_score'][j]))<1e-11
 assert rec['candidate_count']==len(a['plain'])<=256;assert rec['distinct_plaintexts']==len({bytes(x) for x in a['plain']})
 bi=int(a['full_score'].argmax());bs=int(a['suffix_score'].argmax());assert rec['full_winner']['plain']==a['plain'][bi].tolist() and rec['suffix_winner']['plain']==a['plain'][bs].tolist();assert rec['best_full_score']==float(a['full_score'][bi]) and rec['best_suffix_score']==float(a['suffix_score'][bs])
 errors=np.count_nonzero(a['plain']!=np.array(case['truth']),axis=1);assert int(errors.min())==rec['control']['minimum_errors'];assert int(errors[bi])==rec['control']['best_errors'];assert bool(np.any(errors==0))==rec['control']['truth_in_fixed_prefix_candidate_set']
 dump('h3-plant-checks.json',dict(passed=True,frozen_controls=inputs,panel=name,retained_paths=len(a['plain']),max_direct_score_error=maxerror,paths_where_position_differs_from_used_mod_key=different_clock,control_metrics=rec['control'],scope='All16frozeninputsource/RNG/scaledmark/re-encryption checks; one716rune completeadapterpanel allretainedpaths. No actualsearch.'))
 print('H3 plant PASS',len(controls),len(a['plain']),maxerror,different_clock)
if __name__=='__main__':main()
