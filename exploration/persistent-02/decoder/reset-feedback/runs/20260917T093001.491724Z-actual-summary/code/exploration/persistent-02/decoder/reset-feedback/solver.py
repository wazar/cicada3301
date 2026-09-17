"""C02 conditioned cyclic suffix B&B with cross-reset conditional unary terms.
Adapted from feedback/structured.py; exact-real admissibility, float64 tolerance.
"""
import numpy as np,heapq,time,math
from model import value
def solve(W,B,max_nodes=100000,max_seconds=30.,topn=16):
 start=time.monotonic();m=len(W)
 if m<3 or W.shape!=(m,29,29,29) or B.shape!=(m,29,29) or not np.isfinite(W).all() or not np.isfinite(B).all():raise ValueError('finite factor shapes')
 if type(max_nodes)!=int or max_nodes<0 or not math.isfinite(max_seconds) or max_seconds<0 or type(topn)!=int or topn<1:raise ValueError('limits')
 aa=np.repeat(np.arange(29),29);bb=np.tile(np.arange(29),29);U=np.empty((m+1,841,29,29));u=np.arange(29)[:,None];v=np.arange(29)[None,:]
 for r,(a,b) in enumerate(zip(aa,bb)):U[m,r]=W[0,u,v,a]+W[1,v,a,b]+B[0,a,a]+B[1,a,b]
 for j in range(m-1,1,-1):
  for lo in range(0,841,29):
   # Root index r fixes a=x0; its conditioned unary is B[j,a,xj].
   unary=B[j,aa[lo:lo+29],:][:,None,None,:]
   U[j,lo:lo+29]=np.max(W[j][None,:,:,:]+unary+U[j+1,lo:lo+29,None,:,:],axis=3)
 build=time.monotonic()-start;best=-np.inf;alts={};evaluated=0
 def offer(x):
  nonlocal best,evaluated
  assert sum(x)%29==0
  score=value(W,B,x);evaluated+=1;key=tuple(x);best=max(best,score)
  if key not in alts:alts[key]=score
  if len(alts)>topn*2:
   for a,_ in sorted(alts.items(),key=lambda z:(-z[1],z[0]))[topn:]:del alts[a]
 for r,(a,b) in enumerate(zip(aa,bb)):
  x=[int(a),int(b)]
  for j in range(2,m-1):x.append(int(np.argmax(W[j,x[-2],x[-1]]+B[j,a]+U[j+1,r,x[-1]])))
  x.append((-sum(x))%29);offer(x)
 heap=[];serial=0;discarded=-np.inf
 for r,(a,b) in enumerate(zip(aa,bb)):
  bound=float(U[2,r,a,b])
  if bound>best+1e-10:heap.append((-bound,serial,r,(int(a),int(b)),0.,int(a+b)%29));serial+=1
  else:discarded=max(discarded,bound)
 heapq.heapify(heap);popped=0;generated=len(heap);peak=len(heap);reason='exhausted';interrupted=None
 while heap:
  if popped>=max_nodes:reason='node_limit';break
  if time.monotonic()-start>=max_seconds:reason='time_limit';break
  neg,_,r,x,score,total=heapq.heappop(heap);bound=-neg
  if bound<=best+1e-10:discarded=max(discarded,bound);continue
  popped+=1;j=len(x);a=x[0];u,v=x[-2:]
  if j==m-1:offer(x+((-total)%29,));continue
  if j==m-2:
   for z in range(29):offer(x+(z,(-total-z)%29))
   continue
  if len(heap)+29>max_nodes*2:interrupted=bound;reason='frontier_limit';break
  for z in range(29):
   sc=score+float(W[j,u,v,z]+B[j,a,z]);ub=sc+float(U[j+1,r,v,z])
   if ub>best+1e-10:heapq.heappush(heap,(-ub,serial,r,x+(z,),sc,(total+z)%29));serial+=1;generated+=1
   else:discarded=max(discarded,ub)
  peak=max(peak,len(heap))
 upper=max([best,discarded]+([-heap[0][0]] if heap else [])+([interrupted] if interrupted is not None else []));top=sorted(alts.items(),key=lambda z:(-z[1],z[0]))[:topn]
 return dict(maximum=best,upper_bound=upper,gap=max(0.,upper-best),certified_within_1e_10=upper<=best+1e-10,termination=reason,alternatives=[dict(offset=list(x),score=s) for x,s in top],nodes_popped=popped,nodes_generated=generated,peak_frontier=peak,feasible_evaluations=evaluated,suffix_table_bytes=U.nbytes,build_seconds=build,seconds=time.monotonic()-start,limits=dict(nodes=max_nodes,seconds=max_seconds,time_semantics='branch-loop checks after uninterruptible suffix build and841 incumbents; logger separately caps process'),pruned_upper_bound=discarded,scope='same sharedseed at fixed boundary resets; no interruptions; float64/tolerance maximum; feasible alternatives not globaln-best or tie census')
