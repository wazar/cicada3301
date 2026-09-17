"""A01 fixed-key exact prefix selection and frozen-state section continuation."""
import pathlib,json,sys,importlib.util,random,time,hashlib,argparse,gzip
R=pathlib.Path(__file__).resolve().parents[3]; O=pathlib.Path(__file__).resolve().parent

def module(name,path):
 s=importlib.util.spec_from_file_location(name,R/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=module('p03','exploration/persistent-01/worker-c/p03_frozen.py'); K=module('kb','exploration/persistent-01/worker-c/frozen_kbest.py'); REF=module('ref','audit/parallel-01/reference/reference.py')

def dump(path,x):path.write_text(json.dumps(x,indent=2)+'\n')
def ctxt(p,ends,start=(29,29)):
 s=start
 for i,r in enumerate(p):
  s=(s[-1],r)
  if i in ends:s=(s[-1],29)
 return s

def sliceends(ends,a,b):return {i-a for i in ends if a<=i<b}
def forward(p,key,sign,literal,used=0):
 out=[]
 for i,v in enumerate(p):
  if i in literal:assert v==0;out.append(0)
  else:out.append((v-sign*key[used%len(key)])%29);used+=1
 return out,used

def run(label,c,ends,spans,lm,cells,truth=None,plant=None):
 t=time.monotonic();a,b=spans[0];assert a==0
 pe=sliceends(ends,a,b); rows=[]
 for cell in cells:
  alts,diag=K.kbest(c[:b],pe,cell['key'],cell['sign'],lm,retain=16)
  rows.append(dict(cell=cell,score=alts[0]['score'],alternatives=alts,diagnostics=diag))
 rows.sort(key=lambda x:x['score'],reverse=True);winner=rows[0];cell=winner['cell']; continuations=[]
 for policy in ['continuous','page-reset']:
  for rank,first in enumerate(winner['alternatives']):
   plains=list(first['plain']);paths=list(first['literal_positions']);used=first['used'];s=ctxt(plains,pe);parts=[dict(span=spans[0],score=first['score'],used_end=used,plain=first['plain'],literal_positions=first['literal_positions'])]
   for a,b in spans[1:]:
    u0=used if policy=='continuous' else 0;e=sliceends(ends,a,b); alts,d=K.kbest(c[a:b],e,cell['key'],cell['sign'],lm,retain=16,start_context=s,start_used=u0);top=alts[0]
    # Re-encrypt every retained conditional alternative, not only the score winner.
    for alt in alts:assert forward(alt['plain'],cell['key'],cell['sign'],set(alt['literal_positions']),u0)==(c[a:b],alt['used'])
    parts.append(dict(span=[a,b],score=top['score'],used_start=u0,used_end=top['used'],plain=top['plain'],literal_positions=top['literal_positions'],alternatives=alts,diagnostics=d));used=top['used'];s=ctxt(top['plain'],e,s);plains.extend(top['plain']);paths.extend(a+i for i in top['literal_positions'])
   result=dict(policy=policy,prefix_path_rank=rank+1,parts=parts,plain=plains,literal_positions=paths,score=lm.score(plains,ends),transliteration=REF.render(plains))
   if truth is not None:result['errors_by_part']=[sum(x!=y for x,y in zip(plains[a:b],truth[a:b])) for a,b in spans]
   continuations.append(result)
 # Same fitted key, no literal branch, with each clock convention.
 ordinary=[]
 for policy in ['continuous','page-reset']:
  pp=[];u=0
  for a,b in spans:
   if policy=='page-reset':u=0
   for v in c[a:b]:pp.append((v+cell['sign']*cell['key'][u%len(cell['key'])])%29);u+=1
  ordinary.append(dict(policy=policy,plain=pp,score=lm.score(pp,ends),transliteration=REF.render(pp)))
 out=dict(label=label,cipher=c,ends=sorted(ends),spans=spans,prefix_cells=[dict(cell=r['cell'],score=r['score']) for r in rows],prefix_top=rows[:5],selected_cell=cell,continuations=continuations,ordinary=ordinary,seconds=time.monotonic()-t)
 if truth is not None:
  out.update(truth=truth,plant=plant,truth_prefix_key_rank=1+sum(r['score']>next(z['score'] for z in rows if z['cell']['id']==plant['id']) for r in rows),truth_prefix_score=lm.score(truth[:spans[0][1]],pe))
 with gzip.open(O/'A01'/(label+'.json.gz'),'wt') as f:json.dump(out,f)
 brief=dict(label=label,seconds=out['seconds'],selected_cell=cell['id'],prefix_score=rows[0]['score'],continuation_scores={r['policy']:[p['score'] for p in r['parts'][1:]] for r in continuations if r['prefix_path_rank']==1})
 if truth is not None:brief.update(errors={r['policy']:r['errors_by_part'] for r in continuations if r['prefix_path_rank']==1},truth_prefix_key_rank=out['truth_prefix_key_rank'])
 print(json.dumps(brief),flush=True);return brief

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--batch',choices=['controls','actual','nulls'],required=True);ap.add_argument('--null-start',type=int,default=0);ap.add_argument('--null-count',type=int,default=19);a=ap.parse_args();(O/'A01').mkdir(exist_ok=True)
 packet=json.loads((O/'section-packet.json').read_text());grid=json.loads((O/'key-grid.json').read_text());lm=M.LM();cells=[]
 for k in grid['keys']:
  for phase in range(len(k['runes'])):
   for sign in grid['signs']:cells.append(dict(id=f"{k['id']}:{phase}:{sign}",key_id=k['id'],phase=phase,sign=sign,key=k['runes'][phase:]+k['runes'][:phase]))
 results=[]
 if a.batch=='controls':
  for j,name in enumerate(M.CHECK):
   p,ends=M.parse((R/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text());n=len(p);cuts=[0,n//3,2*n//3,n];spans=list(zip(cuts,cuts[1:]));cell=cells[[9,37,64,80][j]];policy=['continuous','page-reset'][j%2];c=[];u=0
   for x,y in spans:
    if policy=='page-reset':u=0
    pp=p[x:y];literal={i for i,v in enumerate(pp) if v==0 and (i+x)%3!=1};cc,u=forward(pp,cell['key'],cell['sign'],literal,u);c.extend(cc)
   results.append(run('control-'+name,c,ends,spans,lm,cells,p,dict(**cell,policy=policy)))
 else:
  for variant in ['body','whole']:
   c=packet['body']['runes'] if variant=='body' else packet['runes'];ends=set(packet['body']['explicit_ends'] if variant=='body' else packet['explicit_ends']);spans=packet['body']['page_spans'] if variant=='body' else [[0,262],[262,528],[528,729]]
   if a.batch=='actual':results.append(run('actual-'+variant,c,ends,spans,lm,cells))
   else:
    rng=random.Random(9020101+(variant=='whole'))
    for j in range(a.null_start+a.null_count):
     d=[c[0]]
     for i,v in enumerate(c[1:],1):
      if v==c[i-1]:d.append(d[-1])
      else:z=rng.randrange(28);d.append(z+(z>=d[-1]))
     if j>=a.null_start:results.append(run(f'null-{variant}-{j:02}',d,ends,spans,lm,cells))
 dump(O/'A01'/f'summary-{a.batch}-{a.null_start:02}.json',results)
if __name__=='__main__':main()
