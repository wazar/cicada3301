"""Targeted B06 Mill1 consequence review, source alignment and complete replay."""
from integration_checks import R,O,dump
import continuation as C
import json,gzip,re,hashlib
def main():
 base=R/'exploration/persistent-02/decoder';cases=json.loads((base/'continuation-inputs.json').read_text())['cases'];case=next(x for x in cases if x['id']=='fresh-mill-1')
 initial=json.loads((base/'fresh-controls.json').read_text());old=next(x for x in initial['cases'] if x['id']==case['id']);src=next(x for x in initial['sources'] if x['id']=='mill');raw=(R/src['path']).read_text();assert hashlib.sha256((R/src['path']).read_bytes()).hexdigest()==src['sha256']
 lo,hi=src['body_char_span'];body=raw[lo:hi];excluded=[(m.start(),m.end()) for m in re.finditer(r'\{[^}]*\}',body)];flat=[];spans=[];ends=[]
 for m in re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",body):
  if any(a<=m.start()<b for a,b in excluded):continue
  rr=C.keyword_to_indices(re.sub("['’]",'',m.group()));flat+=rr;spans.extend([[lo+m.start(),lo+m.end()]]*len(rr));ends.append(len(flat)-1)
 a,b=old['source_rune_span'];truth=flat[a:b+200];assert truth==case['truth'];assert spans[a:b+200]==case['source_char_spans'];assert case['cipher'][:b-a]==old['cipher']
 assert case['ends_genuine']==[x-a for x in ends if a<=x<b+200]
 assert not case['prefix_end_is_genuine'];assert case['ends_primary']==sorted(set(old['ends'])|{x-a for x in ends if b<=x<b+200})
 u=0;cipher=[];literal=set(case['truth_literal_positions'])
 for i,p in enumerate(truth):
  if i in literal:assert p==0;cipher.append(0)
  else:cipher.append((p-case['sign']*case['key'][u%len(case['key'])])%29);u+=1
 assert cipher==case['cipher']
 results=[]
 for name,lm in [('p03',C.LM()),('complementary',C.OtherLM())]:
  got=C.process(case,lm,name);expected=json.loads(gzip.decompress((base/'continuation'/(name+'-'+case['id']+'.json.gz')).read_bytes()))
  for field in ['joint','genuine','joint_metrics','genuine_metrics']:assert got[field]==expected[field]
  for lhs,rhs in zip(got['retained_prefix_continuations'],expected['retained_prefix_continuations']):
   for field in ['prefix_rank','score','plain','literal_positions','prefix_errors','suffix_errors','suffix_alternatives']:assert lhs[field]==rhs[field]
   assert abs(lm.score(lhs['plain'],set(case['ends_primary']))-lhs['score'])<1e-12
  assert (got['committed_top']['prefix_errors'],got['committed_top']['suffix_errors'])==(1,89)
  assert got['best_retained_prefix']['prefix_rank']==2 and got['best_retained_prefix']['prefix_errors']==got['best_retained_prefix']['suffix_errors']==0
  assert got['joint_metrics']['best_errors']==0 and got['joint_metrics']['truth_rank']==1
  results.append(got)
 dump('continuation-check.json',dict(passed=True,id=case['id'],source_hash=src['sha256'],truth=truth,case=case,results=results,scope='Targeted review of previously observed Mill1 horizon example, not independent selection/power estimate'))
 print('Mill1 both models: source alignment/re-encryption/replay passed; committed1+89 errors, alternative2 and joint zero errors')
if __name__=='__main__':main()
