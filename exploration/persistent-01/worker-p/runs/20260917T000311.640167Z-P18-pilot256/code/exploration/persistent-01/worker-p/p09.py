import p08 as p
import collections,math,json,random,time
R=p.R.parent/'P09'
def dump(n,x):(R/(n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
class FreeLM:
 def __init__(self):
  self.c=[collections.Counter() for _ in range(3)];self.t=[collections.Counter() for _ in range(3)];self.cache={}
  for q in p.read('sources')['caesar']['selected']:
   ctx=(29,29)
   for r in q['plain']:
    for n in range(3):z=ctx[-n:] if n else ();self.c[n][z+(r,)]+=1;self.t[n][z]+=1
    ctx=(ctx[-1],r)
 def extend(self,ctx,r,end=False):
  z=ctx+(r,)
  if z not in self.cache:
   v=(self.c[0][(r,)]+.5)/(self.t[0][()]+14.5)
   for n,alpha in [(1,8),(2,5)]:s=ctx[-n:];v=(self.c[n][s+(r,)]+alpha*v)/(self.t[n][s]+alpha)
   self.cache[z]=math.log(v)
  return (ctx[-1],r),self.cache[z]
 def score(self,plain,ends):
  ctx=(29,29);total=0
  for r in plain:ctx,v=self.extend(ctx,r);total+=v
  return total/len(plain)
def main():
 p.gate();models,env,cells,parse=p.setup();free=FreeLM();out=[]
 for ix in range(4):
  d=p.read('control-'+str(ix));f=d['fixture'];n=len(f['plain']);m=len(f['ends']);rel=[(j*n+m-1)//m-1 for j in range(1,m+1)];assert len(set(rel))==m and rel[-1]==n-1;results={}
  for name,model,ends in [('free',free,[]),('relocated_aware',models['latin'],rel)]:
   rows=p.search(f['cipher'],ends,model,env,cells);a=rows[0]['decode']['alternatives'][0];tr=next(q for q in rows if q['id']==f['cell']);truthskips=[len(x['rejected']) for x in f['events']];errs=[i for i,(a,b) in enumerate(zip(a['plain'],f['plain'])) if a!=b]
   results[name]=dict(rows=rows,key_correct=rows[0]['id']==f['cell'],key_rank=1+sum(q['score']>tr['score'] for q in rows),error_positions=errs,path_correct=a['reject_counts']==truthskips,used_correct=a['used']==f['used'],complete=rows[0]['id']==f['cell'] and not errs and a['reject_counts']==truthskips,truth_lm=model.score(f['plain'],set(ends)))
  row=dict(index=ix,fixture=f,original_ends=f['ends'],relocated_ends=rel,overlap=len(set(rel)&set(f['ends'])),results=results);out.append(row);dump('control-'+str(ix),row);print(ix,{k:{a:b for a,b in v.items() if a!='rows'} for k,v in results.items()},flush=True)
 gap=[q['index'] for q in out if q['results']['free']['complete'] and not q['results']['relocated_aware']['complete']];dump('summary',dict(controls=[dict(index=q['index'],n=len(q['fixture']['plain']),separators=len(q['original_ends']),overlap=q['overlap'],models={k:{a:b for a,b in v.items() if a!='rows'} for k,v in q['results'].items()}) for q in out],gap_controls=gap,real_authorized=bool(gap)))
if __name__=='__main__':main()
