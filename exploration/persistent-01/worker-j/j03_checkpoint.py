import json,gzip,pathlib,collections,math
import numpy as np
O=pathlib.Path(__file__).resolve().parent
D=json.loads((O/'j02-results.json').read_text());act=[a['pairs']for a in D['actual']];results=[]
for label in ['j02','j03']:
 W=json.load(gzip.open(O/(label+'-windows.json.gz'),'rt'));dist=np.array([1],dtype=np.int64);off=0;weights=[];ns=[];compatible=[]
 for ws,a in zip(W['windows'],act):
  counts=collections.Counter(w['bound']for w in ws);lo=min(counts);h=np.array([counts[x]for x in range(lo,max(counts)+1)],dtype=np.int64);dist=np.convolve(dist,h);off+=lo;ns.append(len(ws));compatible.append(sum(w['bound']<=a for w in ws));weights.append(dict(collections.Counter(w['group']for w in ws)))
 denominator=math.prod(ns);assert denominator<2**63 and int(dist.sum())==denominator
 numerator=int(dist[:max(0,sum(act)-off+1)].sum());joint=math.prod(compatible)
 results.append({'model':label,'window_counts':ns,'source_window_counts_by_page':weights,'aggregate_numerator':numerator,'denominator':denominator,'aggregate_fraction':numerator/denominator,'conjunction_numerator':joint,'conjunction_fraction':joint/denominator,'arithmetic':'integer histogram convolution in int64; all nonnegative coefficients and complete sum below2**63, checked sum equals product of window counts','zero_count_source_types':'not allocated slots: deliberately optimistic bound; any codebook requiring slots for absent symbols has weakly higher collision minimum','weighting':'uniform over all windows, so long source files get proportionally more weight; NOT uniform over files'})
(O/'j03-exact-checkpoint.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
