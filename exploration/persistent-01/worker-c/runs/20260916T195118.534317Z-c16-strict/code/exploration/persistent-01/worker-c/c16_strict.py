"""Strict all-plaintextF-literal transition, language-free path feasibility."""
import json,random,time,gzip,collections,importlib.util
from p03_frozen import O,ROOT,LM,parse,dump,cells
from frozen_kbest import kbest

def feasible(c,key,sign,periodic=True):
 states={0:1};expanded=0
 for v in c:
  nxt=collections.defaultdict(int)
  for u,count in states.items():
   if (periodic or u<len(key)) and (v+sign*key[u%len(key)])%29!=0:nxt[(u+1)%len(key) if periodic else u+1]+=count;expanded+=1
   if v==0:nxt[u]+=count;expanded+=1
  states=nxt
  if not states:break
 return dict(compatible=bool(states),paths=sum(states.values()),final_states=len(states),expanded=expanded)
def strict(c,ends,key,sign,lm,retain=16):
 states={(0,(29,29)):[(0.,0,b'',())]};expanded=0
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list)
  for (phase,s),paths in states.items():
   choices=[];normal=(v+sign*key[phase])%29
   if normal!=0:choices.append((normal,False))
   if v==0:choices.append((0,True))
   for r,literal in choices:
    ss,w=lm.extend(s,r,i in ends)
    for sc,u,p,path in paths:
     uu=u+(not literal);nxt[(uu%len(key),ss)].append((sc+w,uu,p+bytes([r]),path+(i,) if literal else path));expanded+=1
  states={}
  for st,paths in nxt.items():paths.sort(key=lambda x:x[0],reverse=True);states[st]=paths[:retain]
  if not states:break
 ordered=sorted([z for paths in states.values() for z in paths],key=lambda x:x[0],reverse=True)[:retain]
 return [dict(score=z[0]/(len(c)+len(ends)),plain=list(z[2]),used=z[1],literal_positions=list(z[3])) for z in ordered],dict(expanded=expanded)
def main():
 out=O/'c16';out.mkdir(exist_ok=True);lm=LM();spec=importlib.util.spec_from_file_location('fcheck',ROOT/'audit/f-interruption-01/check.py');fc=importlib.util.module_from_spec(spec);spec.loader.exec_module(fc);refs=fc.reference_cases();controls=[];t=time.monotonic()
 for ref in refs:
  c=[x['cipher'] for x in ref['trace']];plain=ref['plain'];ends=parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+ref['name']+'.txt')).read_text())[1];key=ref['key'];literal=[r['position'] for r in ref['trace'] if r['action']=='literal_F'];assert literal==[i for i,p in enumerate(plain) if p==0];f=feasible(c,key,-1,False);assert f['compatible'];alts,d=strict(c,ends,key,-1,lm);controls.append(dict(name=ref['name'],literal_F=len(literal),encrypted_plain_F=0,feasibility=f,best_errors=sum(x!=y for x,y in zip(alts[0]['plain'],plain)),truth_in_top16=any(a['plain']==plain for a in alts),alternatives=alts))
 dump(out/'reference-controls.json',controls)
 # Exhaustive arbitrary shortcases, independent branchmask interpreter with strictcondition.
 rng=random.Random(330116);checks=[]
 from p09_viterbi import exhaustive
 for ix in range(100):
  c=[rng.randrange(29) if rng.random()>.3 else 0 for _ in range(rng.randrange(5,18))];key=[rng.randrange(29) for _ in range(rng.randrange(1,9))];ends={len(c)-1};ex=[x for x in exhaustive(c,ends,key,-1,lm) if [i for i,p in enumerate(x['plain']) if p==0]==x['path']];f=feasible(c,key,-1);a,d=strict(c,ends,key,-1,lm);assert f['paths']==len(ex);assert len(a)==min(16,len(ex));assert all(abs(x['score']-y['score'])<1e-12 for x,y in zip(a,ex));checks.append(dict(id=ix,paths=f['paths'],cipher=c,key=key))
 dump(out/'exhaustive-controls.json',checks)
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());pages=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']];cs=cells(16,True);summaries=[]
 for null in [False,True]:
  top=[];count=survived=0;pathcount=0;expanded=0;by_page={}
  with gzip.open(out/('null-scores.jsonl.gz' if null else 'real-scores.jsonl.gz'),'wt') as f:
   for p in pages:
    c,ends=parse('/'.join(l['raw'] for l in p['lines']));assert c==p['indices']
    if null:random.Random(330116+p['original_page']).shuffle(c)
    by_page[p['original_page']]=0
    for cell in cs:
     diag=feasible(c,cell['key'],cell['sign']);count+=1;expanded+=diag['expanded'];row=dict(page=p['original_page'],id=cell['id'],**diag)
     if diag['compatible']:
      survived+=1;by_page[p['original_page']]+=1;pathcount+=diag['paths'];a,d=strict(c,ends,cell['key'],cell['sign'],lm);assert a;row['score']=a[0]['score']
      if len(top)<20 or row['score']>top[-1]['score']:top.append(dict(**row,key=cell['key'],cipher=c,ends=sorted(ends),alternatives=a));top.sort(key=lambda x:x['score'],reverse=True);top=top[:20]
     f.write(json.dumps(row)+'\n')
  summaries.append(dict(null=null,attempted=count,survived=survived,paths=pathcount,expanded=expanded,by_page=by_page,top=top));dump(out/'results.json',summaries)
 print(json.dumps(dict(reference=[{k:x[k] for k in ['name','literal_F','best_errors','truth_in_top16']} for x in controls],realnull=[{k:x[k] for k in ['null','attempted','survived','paths','expanded']} for x in summaries],seconds=time.monotonic()-t)))
if __name__=='__main__':main()
