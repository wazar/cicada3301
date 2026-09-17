from pathlib import Path
import ast,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];src=R/'liber-primus/analysis/round12/C1/feedback.py';tree=ast.parse(src.read_text());wanted={'f_sum','_prime_hist','decode','encipher'};defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted];assert len(defs)==4
primes=[];v=2
while len(primes)<29:
 if all(v%d for d in range(2,int(v**.5)+1)):primes.append(v)
 v+=1
ns={'N':29,'PRIMES':primes};exec(compile(ast.Module(body=defs,type_ignores=[]),str(src)+'::selected_arithmetic_definitions','exec'),ns);rows=[]
for file in sorted(O.glob('control?.json')):
 x=json.loads(file.read_text());t=x['control'];p=t['truth'];k=t['k'];seed=t['seed'];c=x['cipher'];assert ns['encipher'](p,ns['f_sum'],k,seed,source='pt',sign=-1)==c;assert ns['decode'](c,ns['f_sum'],k,seed,source='pt',sign=-1)==p;eq=[]
 for s in range(29):
  out=ns['decode'](c,ns['f_sum'],k,[s]*k,source='pt',sign=-1);e=[(a-b)%29 for a,b in zip(out,p)];period=e[:k]+[-sum(e[:k])%29];assert any(period) and sum(period)%29==0;assert all(v==period[i%(k+1)] for i,v in enumerate(e));eq.append(dict(seed=[s]*k,error_period=period,errors=sum(bool(v) for v in e),tail_last_period=e[-(k+1):]))
 rows.append(dict(name=x['name'],k=k,true_seed=seed,length=len(p),equal_seed_cases=eq,best_equal_seed_errors=min(r['errors'] for r in eq)))
result=dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),selected_functions=sorted(wanted),controls=rows,pass_=True,claim_scope='For sum/plaintext/sign−1, a nonzero seed error persists periodically. This source arithmetic counterexample does not assess every C1 function.')
(O/'inherited-arithmetic-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(pass_=True,controls=len(rows),wrong_equal_seed_cases=116,best_errors=[r['best_equal_seed_errors'] for r in rows])))
