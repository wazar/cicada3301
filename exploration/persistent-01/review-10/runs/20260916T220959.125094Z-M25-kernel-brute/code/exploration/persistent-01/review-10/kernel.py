import pathlib,json,ast,collections,math,itertools,random,gzip,hashlib,datetime
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];M=O.parent/'worker-m/M25';tab=np.load(O.parent/'review-08/independent-lm-table.npy')
class LM:
 def extend(self,ctx,p,end):
  a,b=ctx;s=float(tab[a,b,p]);out=(b,p)
  if end:s+=float(tab[b,p,29]);out=(p,29)
  return out,s
 def score(self,p,ends):
  ctx=(29,29);s=0
  for i,v in enumerate(p):ctx,w=self.extend(ctx,v,i in ends);s+=w
  return s/(len(p)+len(ends))
lm=LM();tree=ast.parse((M/'m25.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['transitions','decode']];ns={'lm':lm,'math':math,'collections':collections,'S':.83};exec(compile(ast.Module(body=nodes,type_ignores=[]),'M25-inspected-AST','exec'),ns)
def transitions(c,prev,j,key,sign,stride):
 out=[]
 for a in range(j,len(key),stride):
  if prev is None and a!=j:continue
  p=(c+sign*key[a])%29
  if all((p-sign*key[z])%29==prev for z in range(j,a,stride)):out.append((p,a+1,(a-j)//stride))
 return out

def brute(cipher,ends,key,sign,stride):
 rows=[]
 def visit(i,j,ctx,score,plain,ts):
  if i==len(cipher):rows.append({'score':score,'plain':plain,'reject_counts':ts,'used':j});return
  for a in range(j,len(key),stride):
   if i==0 and a!=j:continue
   p=(cipher[i]+sign*key[a])%29;tests=list(range(j,a,stride))
   if any((p-sign*key[z])%29!=cipher[i-1] for z in tests):continue
   ss,w=lm.extend(ctx,p,i in ends);w+=len(tests)*math.log(.83)+(math.log(.17) if i and cipher[i]==cipher[i-1] else 0)
   visit(i+1,a+1,ss,score+w,plain+[p],ts+[len(tests)])
 visit(0,0,(29,29),0,[],[]);return sorted(rows,key=lambda r:r['score'],reverse=True)
def main():
 assert not(O.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00');rng=random.Random(33011001);checks=0
 keycases=[[0],[0,1],[0,1,0],[0,0,0,0,0],[0,1,0,2,0,3]]+[[rng.randrange(4) for _ in range(8)] for z in range(20)]
 for key in keycases:
  for j in range(len(key)+1):
   for sign,stride,prev,c in itertools.product([-1,1],[1,2],[None,0,1,2,3],range(4)):
    a=transitions(c,prev,j,key,sign,stride);b=ns['transitions'](c,prev,j,key,sign,stride);assert sorted(a)==sorted(b);checks+=1
 cases=[]
 for ix in range(80):
  key=[rng.randrange(4) for _ in range(rng.randrange(2,14))];c=[rng.randrange(4) for _ in range(rng.randrange(1,6))];ends={i for i in range(len(c)) if rng.random()<.4};sign=rng.choice([-1,1]);stride=rng.choice([1,2]);expected=brute(c,ends,key,sign,stride);got=ns['decode'](c,ends,{'key':key,'sign':sign},stride,16)
  assert got['feasible']==bool(expected);assert len(got['alternatives'])==min(16,len(expected))
  for a,b in zip(got['alternatives'],expected):assert abs(a['joint_total']-b['score'])<1e-12 and a['used']<=len(key)
  cases.append({'cipher':c,'key':key,'ends':sorted(ends),'sign':sign,'stride':stride,'paths':len(expected),'top_scores':[x['score'] for x in expected[:16]],'feasible':bool(expected)})
 for stride in [1,2]:
  assert not ns['decode']([0,0],set(),{'key':[0],'sign':1},stride,16)['feasible']
  assert ns['decode']([0],set(),{'key':[0],'sign':1},stride,16)['alternatives'][0]['used']==1
 out={'transition_cases':checks,'brute_cases':len(cases),'complete_paths_enumerated':sum(c['paths'] for c in cases),'infeasible_brute_cases':sum(not c['feasible'] for c in cases),'both_signs_strides':True,'finite_no_wrap_checks':True,'m25_source_sha256':hashlib.sha256((M/'m25.py').read_bytes()).hexdigest(),'independent_lm_table_sha256':hashlib.sha256((O.parent/'review-08/independent-lm-table.npy').read_bytes()).hexdigest()};(O/'kernel-findings.json').write_text(json.dumps(out,indent=2));(O/'brute-cases.json').write_text(json.dumps(cases,indent=2));print(json.dumps(out))
if __name__=='__main__':main()
