"""Fixed 200-rune source continuations; horizon and endpoint artifacts separated."""
import json,pathlib,sys,re,gzip,random,hashlib,argparse,time
from compare import ROOT,O,LM
from complementary import LM as OtherLM
from exact import decode
sys.path.insert(0,str(ROOT/'liber-primus/src'));from lp.gematria import keyword_to_indices

def freeze():
 f=O/'continuation-inputs.json';assert not f.exists();original=json.loads((O/'fresh-controls.json').read_text());rng=random.Random(260917206);cases=[]
 for case in original['cases']:
  src=next(s for s in original['sources'] if s['id']==case['source']);path=ROOT/src['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==src['sha256'];raw=path.read_text();start,stop=src['body_char_span'];body=raw[start:stop];exclusions=list(re.finditer(r'\{[^}]*\}',body));matches=[m for m in re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",body) if not any(a.start()<=m.start()<a.end() for a in exclusions)]
  p=[];ee=[];spans=[]
  for m in matches:
   w=keyword_to_indices(re.sub("['’]",'',m.group()));p.extend(w);ee.append(len(p)-1);spans.extend([[start+m.start(),start+m.end()]]*len(w))
  offset,end=case['source_rune_span'];n=end-offset;truth=p[offset:end+200];assert truth[:n]==case['truth'] and len(truth)==n+200
  genuine={i-offset for i in ee if offset<=i<end+200};original_prefix=set(case['ends']);assert original_prefix-{n-1}=={i for i in genuine if i<n-1}
  primary=original_prefix|{i for i in genuine if i>=n};key=case['key'][:]
  if not case['periodic']:key.extend(rng.randrange(29) for _ in range(200))
  c=case['cipher'][:];u=n-len(case['truth_literal_positions']);literals=case['truth_literal_positions'][:]
  for i,v in enumerate(truth[n:],n):
   lit=v==0 and rng.random()<.65
   if lit:c.append(0);literals.append(i)
   else:c.append((v-case['sign']*key[u%len(key)])%29);u+=1
  cases.append(dict(id=case['id'],source=case['source'],cipher=c,key=key,sign=case['sign'],periodic=case['periodic'],truth=truth,truth_literal_positions=literals,prefix_length=n,ends_primary=sorted(primary),ends_genuine=sorted(genuine),prefix_end_is_genuine=n-1 in genuine,source_char_spans=spans[offset:end+200]))
 obj=dict(seed=260917206,added_runes=200,cases=cases,method='Same original prefix ciphertext and keys; finite keys retain original full prefix and append200 independent fixed RNG values. New plaintext from next200source runes, independently planted literal F suffix. Primary retains original artificial prefix endpoint; genuine-end diagnostic removes it where absent in source. No artificial new final endpoint at suffix cut. Search never receives truth literal positions.',selection='Motivated by Mill1 terminal error; not blind new power estimate. Models unchanged. Compare committed bestprefix, retained16prefix alternatives, joint horizon; report irreversible prefixerrors separately.')
 f.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(dict(sha256=hashlib.sha256(f.read_bytes()).hexdigest(),cases=len(cases),artificial_prefix_ends=sum(not c['prefix_end_is_genuine'] for c in cases))))
def context(plain,ends):
 ctx=(29,29)
 for i,r in enumerate(plain):
  ctx=(ctx[1],r)
  if i in ends:ctx=(ctx[1],29)
 return ctx

def process(case,lm,model):
 n=case['prefix_length'];c=case['cipher'];key=case['key'];periodic=case['periodic'];sign=case['sign'];ends=set(case['ends_primary']);suffixends={e-n for e in ends if e>=n};original_name='fresh' if model=='p03' else 'complementary-fresh';base=json.loads(gzip.decompress((O/original_name/(case['id']+'.json.gz')).read_bytes()));prefixends=set(base['case']['ends']);assert c[:n]==base['case']['cipher'];rows=[];t=time.monotonic()
 # Search inputs contain no planted interruption positions or plaintext.
 for rank,prefix in enumerate(base['exact'][:16],1):
  alts,diag=decode(c[n:],key,lm.extend,sign=sign,periodic=periodic,start=prefix['used'],context=context(prefix['plain'],prefixends),ends=suffixends,retain=16)
  best=alts[0];plain=prefix['plain']+best['plain'];total=prefix['total']+best['total'];rows.append(dict(prefix_rank=rank,score=total/(len(c)+len(ends)),plain=plain,literal_positions=prefix['literal_positions']+[n+i for i in best['literal_positions']],prefix_errors=sum(a!=b for a,b in zip(prefix['plain'],case['truth'][:n])),suffix_errors=sum(a!=b for a,b in zip(best['plain'],case['truth'][n:])),suffix_alternatives=alts,diagnostics=diag))
 joint,jd=decode(c,key,lm.extend,sign=sign,periodic=periodic,ends=ends,retain=256);genuine,gd=decode(c,key,lm.extend,sign=sign,periodic=periodic,ends=case['ends_genuine'],retain=256)
 def metrics(alts,ee):
  truthscore=lm.score(case['truth'],set(ee));higher=sum(a['score']>truthscore+1e-12 for a in alts);complete=len(alts)<256 or alts[-1]['score']<truthscore-1e-12
  return dict(best_errors=sum(a!=b for a,b in zip(alts[0]['plain'],case['truth'])),truth_score=truthscore,truth_rank=1+higher if complete else None,truth_rank_lower_bound=1+higher,truth_retained_plain_matches=[i+1 for i,a in enumerate(alts) if a['plain']==case['truth']])
 return dict(id=case['id'],model=model,prefix_length=n,primary_ends=sorted(ends),genuine_ends=case['ends_genuine'],prefix_end_is_genuine=case['prefix_end_is_genuine'],committed_top=rows[0],retained_prefix_continuations=rows,best_retained_prefix=min(rows,key=lambda r:-r['score']),joint=joint,joint_diagnostics=jd,joint_metrics=metrics(joint,ends),genuine=genuine,genuine_diagnostics=gd,genuine_metrics=metrics(genuine,case['ends_genuine']),seconds=time.monotonic()-t)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','run']);a=ap.parse_args()
 if a.action=='freeze':return freeze()
 cases=json.loads((O/'continuation-inputs.json').read_text())['cases'];out=O/'continuation';out.mkdir(exist_ok=True)
 for model,lm in [('p03',LM()),('complementary',OtherLM())]:
  for case in cases:
   r=process(case,lm,model);(out/(model+'-'+case['id']+'.json.gz')).write_bytes(gzip.compress(json.dumps(r).encode(),mtime=0));print(json.dumps(dict(model=model,id=case['id'],committed_errors=r['committed_top']['prefix_errors']+r['committed_top']['suffix_errors'],retained16_errors=r['best_retained_prefix']['prefix_errors']+r['best_retained_prefix']['suffix_errors'],joint=r['joint_metrics'],genuine=r['genuine_metrics'],seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
