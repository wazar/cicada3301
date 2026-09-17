"""Paired fixed-objective complete-reference and section diagnostic."""
import pathlib,sys,json,time,resource,gzip,hashlib,argparse
ROOT=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'))
from p03_frozen import LM,parse,beam
from frozen_kbest import kbest
from exact import decode
sys.path.insert(0,str(ROOT/'audit/parallel-01/reference'))
from fixtures import CASES
from reference import decode as reference_decode,primes

def timed(fn):
 t=time.monotonic();x=fn();return x,time.monotonic()-t

def finite_beam(c,ends,key,sign,lm,width):
 states=[(0.,(29,29),0,b'',())]
 for i,v in enumerate(c):
  nxt=[]
  for sc,ctx,u,p,lp in states:
   for lit in ([False,True] if v==0 else [False]):
    if not lit and u>=len(key):continue
    r=0 if lit else (v+sign*key[u])%29;ss,w=lm.extend(ctx,r,i in ends)
    nxt.append((sc+w,ss,u+int(not lit),p+bytes([r]),lp+(i,) if lit else lp))
  states=sorted(nxt,key=lambda x:x[0],reverse=True)[:width]
 return [dict(score=sc/(len(c)+len(ends)),plain=list(p),literal_positions=list(lp),used=u) for sc,ctx,u,p,lp in states[:16]],{}

def run(case,lm,retain=16):
 c=case['cipher'];ends=set(case['ends']);key=case['key'];sign=case.get('sign',-1);periodic=case.get('periodic',True)
 (alts,diag),secs=timed(lambda:decode(c,key,lm.extend,sign=sign,periodic=periodic,ends=ends,retain=retain))
 beams={}
 for width in [64,256,1024]:
  (ba,bd),bs=timed(lambda:beam(c,ends,key,sign,lm,width) if periodic else finite_beam(c,ends,key,sign,lm,width))
  delta=alts[0]['score']-ba[0]['score'];assert delta>=-1e-12
  beams[str(width)]=dict(seconds=bs,gap=delta,alternatives=ba,diagnostics=bd)
 old=None
 if periodic:
  (oa,od),os=timed(lambda:kbest(c,ends,key,sign,lm,retain=retain));assert max(abs(x['score']-y['score']) for x,y in zip(oa,alts))<1e-12;old=dict(seconds=os,diagnostics=od)
 ordinary=[(v+sign*key[i%len(key)])%29 for i,v in enumerate(c)] if periodic else [(v+sign*key[i])%29 for i,v in enumerate(c)] if len(key)>=len(c) else None
 result=dict(case=case,exact=alts,diagnostics=diag,seconds=secs,beams=beams,old_exact=old,ordinary=dict(plain=ordinary,score=lm.score(ordinary,ends)) if ordinary else None,maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 if 'truth' in case:
  truth=case['truth'];score=lm.score(truth,ends);matching=[i+1 for i,x in enumerate(alts) if x['plain']==truth];higher=sum(x['score']>score+1e-12 for x in alts);complete=len(alts)<retain or alts[-1]['score']<score-1e-12
  result['truth_metrics']=dict(score=score,best_errors=sum(a!=b for a,b in zip(truth,alts[0]['plain'])),top_path_plaintext_matches=matching,strictly_higher_path_count=higher,rank_is_exact=complete,competition_rank=1+higher if complete else None,rank_lower_bound=1+higher,best_gap=alts[0]['score']-score,beam_errors={w:sum(a!=b for a,b in zip(truth,b['alternatives'][0]['plain'])) for w,b in beams.items()},note='Rank counts decision paths, not distinct plaintexts; tolerance1e-12 used for truth rank comparisons.')
 return result

def references():
 cases=[]
 for name,method,key,interrupts,_ in CASES:
  if method not in ['keyed','totient']:continue
  f=ROOT/'audit/parallel-01/reference/sources'/(name+'.txt');c,ends=parse(''.join(f.read_text().splitlines()));solved=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');truth,te=parse(''.join(solved.read_text().splitlines()));assert te==ends
  assert reference_decode(c,method,key,interrupts)==truth
  cases.append(dict(id='reference-'+name,cipher=c,ends=sorted(ends),key=key if method=='keyed' else [(p-1)%29 for p in primes(len(c))],periodic=method=='keyed',truth=truth,input_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),truth_sha256=hashlib.sha256(solved.read_bytes()).hexdigest(),boundary_policy='physical newlines removed; explicit separators retained; final boundary',oracle_interruptions_supplied_to_search=False))
 return cases

def section():
 packet=json.loads((ROOT/'exploration/persistent-02/section/section-packet.json').read_text());grid=json.loads((ROOT/'exploration/persistent-02/section/key-grid.json').read_text());cases=[]
 for policy,part in [('body',packet['body']),('whole',packet)]:
  for k in grid['keys']:
   key=k['runes']
   for phase in range(len(key)):
    for sign in [-1,1]:cases.append(dict(id=f"section-{policy}-{k['id']}-{phase}-{sign}",cipher=part['runes'],ends=part['explicit_ends'],key=key[phase:]+key[:phase],sign=sign,phase=phase,policy=policy))
 return cases

def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['references','section']);ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=999);args=ap.parse_args();lm=LM();out=O/args.mode;out.mkdir(exist_ok=True)
 cases=(references() if args.mode=='references' else section())[args.start:args.start+args.count]
 for case in cases:
  r=run(case,lm,retain=256 if args.mode=='references' else 16);p=out/(case['id']+'.json.gz');p.write_bytes(gzip.compress(json.dumps(r).encode(),mtime=0));print(json.dumps(dict(id=case['id'],best=r['exact'][0]['score'],seconds=r['seconds'],beam_gaps={w:b['gap'] for w,b in r['beams'].items()},truth=r.get('truth_metrics'),maxrss_bytes=r['maxrss_bytes'])),flush=True)
if __name__=='__main__':main()
