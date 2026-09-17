"""Zero-sum cyclic trigram branch-and-bound, with explicit remaining-search bounds.

For offset period m=k+1, maximize sum_j W[j,e[j-2],e[j-1],e[j]],
subject to sum(e)%29=0. First two variables are conditioned. Suffix Viterbi
bounds retain all cyclic closing factors but relax only the modular sum.
No score model or cipher construction changes. Caps return a feasible lower
bound and a rigorous mathematical upper bound (subject to float64 roundoff),
never an unqualified exactness claim.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[key]='1'
import numpy as np,heapq,time

def value(W,e):
 m=len(e);return float(sum(W[j,e[(j-2)%m],e[(j-1)%m],e[j]] for j in range(m)))

def solve(W,max_nodes=100000,max_seconds=30.,topn=16):
 start=time.monotonic();m=len(W);assert W.shape==(m,29,29,29) and m>=3
 aa=np.repeat(np.arange(29),29);bb=np.tile(np.arange(29),29)
 U=np.empty((m+1,841,29,29));u=np.arange(29)[:,None];v=np.arange(29)[None,:]
 for r,(a,b) in enumerate(zip(aa,bb)):U[m,r]=W[0,u,v,a]+W[1,v,a,b]
 for j in range(m-1,1,-1):
  for lo in range(0,841,29):U[j,lo:lo+29]=np.max(W[j][None,:,:,:]+U[j+1,lo:lo+29,None,:,:],axis=3)
 build=time.monotonic()-start;best=-np.inf;alts={};evaluated=0
 def offer(e):
  nonlocal best,evaluated
  assert sum(e)%29==0
  score=value(W,e);evaluated+=1;key=tuple(e)
  if score>best:best=score
  if key not in alts:alts[key]=score
  if len(alts)>topn*2:
   for x,_ in sorted(alts.items(),key=lambda x:(-x[1],x[0]))[topn:]:del alts[x]
 # Fixed feasible incumbents from each unconstrained root optimum, with last
 # variable set by the exact modular constraint. This is only a lower bound.
 for r,(a,b) in enumerate(zip(aa,bb)):
  e=[int(a),int(b)]
  for j in range(2,m-1):e.append(int(np.argmax(W[j,e[-2],e[-1]]+U[j+1,r,e[-1]])))
  e.append((-sum(e))%29);offer(e)
 heap=[];serial=0;discarded_upper=-np.inf
 for r,(a,b) in enumerate(zip(aa,bb)):
  bound=float(U[2,r,a,b])
  if bound>best+1e-10:heap.append((-bound,serial,r,(int(a),int(b)),0.,int(a+b)%29));serial+=1
  else:discarded_upper=max(discarded_upper,bound)
 heapq.heapify(heap);popped=0;generated=len(heap);peak=len(heap);reason='exhausted';interrupted_bound=None
 while heap:
  if popped>=max_nodes:reason='node_limit';break
  if time.monotonic()-start>=max_seconds:reason='time_limit';break
  neg,_,r,e,score,total=heapq.heappop(heap);bound=-neg
  if bound<=best+1e-10:discarded_upper=max(discarded_upper,bound);continue
  popped+=1;j=len(e);a,b=e[0],e[1];u,v=e[-2:]
  if j==m-1:offer(e+((-total)%29,));continue
  if j==m-2:
   for x in range(29):offer(e+(x,(-total-x)%29))
   continue
  if len(heap)+29>max_nodes*2:
   interrupted_bound=bound;reason='frontier_limit';break
  for x in range(29):
   sc=score+float(W[j,u,v,x]);ub=sc+float(U[j+1,r,v,x])
   if ub>best+1e-10:
    heapq.heappush(heap,(-ub,serial,r,e+(x,),sc,(total+x)%29));serial+=1;generated+=1
   else:discarded_upper=max(discarded_upper,ub)
  peak=max(peak,len(heap))
 upper=max([best,discarded_upper]+([-heap[0][0]] if heap else [])+([interrupted_bound] if interrupted_bound is not None else []))
 top=sorted(alts.items(),key=lambda x:(-x[1],x[0]))[:topn]
 return dict(maximum=best,upper_bound=upper,gap=max(0.,upper-best),certified_within_1e_10=upper<=best+1e-10,termination=reason,alternatives=[dict(offset=list(e),score=s) for e,s in top],nodes_popped=popped,nodes_generated=generated,peak_frontier=peak,feasible_evaluations=evaluated,suffix_table_bytes=U.nbytes,build_seconds=build,seconds=time.monotonic()-start,limits=dict(nodes=max_nodes,seconds=max_seconds,time_semantics='checked at branch loop boundaries after uninterruptible suffix-build and841 incumbent constructions; external logger separately caps process'),pruned_upper_bound=discarded_upper,scope='best value to float64 tolerance; alternatives are retained feasible outputs, not guaranteed global n-best; ties not completely enumerated')
