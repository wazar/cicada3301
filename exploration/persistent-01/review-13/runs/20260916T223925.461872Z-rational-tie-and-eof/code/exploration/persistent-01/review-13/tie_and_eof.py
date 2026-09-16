"""Resolve preserved numerical-tie failure and explicit historical EOF witnesses."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,re,ast,random
O=Path('exploration/persistent-01/review-13');d=json.loads((O/'tiny-failure.json').read_text())
abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';counts=[Counter() for _ in range(3)];totals=[Counter() for _ in range(3)]
for name in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229']:
 raw=(Path('audit/parallel-01/reference/sources')/('solved_'+name+'.txt')).read_text();tokens=[]
 for word in re.findall('['+abc+']+',raw):tokens.extend([abc.index(x) for x in word]+[29])
 ctx=(29,29)
 for t in tokens:
  for n in range(3):q=ctx[-n:] if n else ();counts[n][q+(t,)]+=1;totals[n][q]+=1
  ctx=ctx[1],t
def exact(p):
 ctx=(29,29);ans=F(1)
 for i,x in enumerate(p):
  for t in ([x,29] if i in {2,5,9} else [x]):
   v=F(2*counts[0][(t,)]+1,2*totals[0][()]+30)
   for n,a in [(1,8),(2,5)]:q=ctx[-n:];v=(counts[n][q+(t,)]+a*v)/(totals[n][q]+a)
   ans*=v;ctx=ctx[1],t
  mass=F(1);prob=F(0);prev=d['cipher'][i-1] if i else None;feedback=d['a']*prev%29 if i else 0
  for j in range(i,len(d['key'])):
   c=(x-d['sign']*(d['key'][j]+feedback))%29
   if prev is None or c!=prev:
    if c==d['cipher'][i]:prob+=mass
    break
   if c==d['cipher'][i]:prob+=mass*(1 if j==len(d['key'])-1 else F(17,100))
   if j==len(d['key'])-1:break
   mass*=F(83,100)
  ans*=prob
 return ans
a=d['actual'][11];b=d['expected'][11];ea=exact(a['plain']);eb=exact(b['plain']);assert ea==eb
source=Path('liber-primus/analysis/campaign18_skip/armada2/selfref_skip.py');node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='encipher_ctfeedback');ns=dict(random=random,N=29);exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns)
fixtures=[]
for key in [[0,0],[0,0,1],[0,0,0,1]]:
 for seed in [0,1]:
  c=ns['encipher_ctfeedback']([0,0],key,k=1,coeffs=[0,1],sign=1,supp=.83,seed=seed)
  fixtures.append(dict(key=key,seed=seed,cipher=c))
assert fixtures[0]['cipher']==fixtures[1]['cipher']==[0,0]
assert fixtures[2]['cipher']==[0,0] and fixtures[3]['cipher']==[0,28]
out=dict(status='PASS',preserved_trial=d['trial'],rank=d['rank'],exact_rational_probability_ratio=str(ea/eb),actual_float=a['joint_total'],independently_summed_float=b['score'],finite_ast_fixtures=fixtures,probability_witnesses={'key_00_at_i1':{'repeat':'1'},'key_001_at_i1':{'repeat':'17/100','different':'83/100'},'key_0001_at_i1':{'repeat':'3111/10000','different':'6889/10000'}})
(O/'tie-and-eof.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
