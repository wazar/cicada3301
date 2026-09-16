"""Complete binary literal-F path enumeration on preregistered short controls."""
import json,pathlib,random,time,itertools
import p01
s=p01.s;O=p01.O

def exact(c,k,sign,q):
 sites=[i for i,v in enumerate(c) if v==0];best=[];count=0
 for choices in itertools.product([False,True],repeat=len(sites)):
  lit={i for i,b in zip(sites,choices) if b};p=[];u=0
  for i,v in enumerate(c):
   if i in lit:p.append(0)
   else:p.append((v+sign*k[u])%29);u+=1
  row=dict(score=q(p),plain=p,literal_positions=sorted(lit),used=u);count+=1;best.append(row)
 best.sort(key=lambda r:r['score'],reverse=True)
 return best,count

def main():
 data,pages,queue,excluded=p01.setup();defs={x['id']:x for x in data['keys']};truth=json.loads((O/'plant/truth.json').read_text());q=s.Score();out=[];t=time.monotonic()
 for pid in [49,51,55]:
  target=truth[str(pid)];cell=target['cell'];plain=target['plain'];key=p01.clues.key_for(cell,defs,len(plain));cipher=[];u=0
  for v in plain:
   cipher.append(0 if v==0 else (v-cell['sign']*key[u])%29);u+=v!=0
  hypotheses=[dict(key_id=x['id'],offset=0,sign=sign,periodic=True) for x in data['keys'][:16] for sign in [-1,1]]
  if not any(all(h[k]==cell[k] for k in ['key_id','offset','sign']) for h in hypotheses):hypotheses.append({k:cell[k] for k in ['key_id','offset','sign','periodic']})
  for mode in ['plant','null']:
   c=cipher.copy()
   if mode=='null':random.Random(330105+pid).shuffle(c)
   rows=[]
   for hyp in hypotheses:
    k=p01.clues.key_for(hyp,defs,len(c));allpaths,count=exact(c,k,hyp['sign'],q);exacttruth=next((i+1 for i,x in enumerate(allpaths) if x['plain']==plain),None);beams=[]
    for width in [4,16,64,256]:
     alts,diag=s.fbeam(c,k,hyp['sign'],q,width=width);beams.append(dict(width=width,best=alts[0]['score'],exact_best_survives=any(x['plain']==allpaths[0]['plain'] for x in alts),truth_top16=any(x['plain']==plain for x in alts),truth_rune_errors=sum(x!=y for x,y in zip(alts[0]['plain'],plain)),alternatives=alts,diagnostics=diag))
    row=dict(hypothesis=hyp,exact_path_count=count,exact_truth_rank=exacttruth,exact_top16=allpaths[:16],beams=beams);rows.append(row)
   rows.sort(key=lambda x:x['exact_top16'][0]['score'],reverse=True);out.append(dict(page=pid,mode=mode,cipher=c,truth=plain,hypotheses=rows))
   s.dump(O/'p04-results.json',dict(elapsed=time.monotonic()-t,results=out));print(pid,mode,len(rows),'elapsed',time.monotonic()-t,flush=True)
if __name__=='__main__':main()
