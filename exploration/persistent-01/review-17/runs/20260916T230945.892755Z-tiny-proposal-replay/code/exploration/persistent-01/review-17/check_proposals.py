from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import ast,json,math,subprocess
O=Path(__file__).resolve().parent;P=O.parent/'worker-p/P05'
source=(O/'kernel-local.cpp').read_text();assert source.count('rep<8')==1 and source.count('k<5000')==1
source=source.replace('rep<8','rep<1').replace('k<5000','k<200')
needle='if(ns>=s||U(rng)<exp((ns-s)/T)){'
assert source.count(needle)==1
source=source.replace(needle,'double draw=ns>=s?-1:U(rng);bool take=ns>=s||draw<exp((ns-s)/T);cerr<<setprecision(17)<<k<<" "<<a<<" "<<b<<" "<<sw<<" "<<ne<<" "<<s<<" "<<ns<<" "<<T<<" "<<draw<<" "<<take<<"\\n";if(take){')
needle='  auto final=score(bm);'
assert source.count(needle)==1
source=source.replace(needle,'  array<int,17> actual_counts{};for(auto label:m)actual_counts[label]++;if(actual_counts!=counts)return 9;\n'+needle)
(O/'proposal-harness.cpp').write_text(source);command=['c++','-O2','-std=c++17',str(O/'proposal-harness.cpp'),'-o',str(O/'proposal-harness')];build=subprocess.run(command,capture_output=True,text=True);(O/'proposal-build.json').write_text(json.dumps(dict(command=command,returncode=build.returncode,stdout=build.stdout,stderr=build.stderr,scope='local bounded instrumented harness, one restart200nominal proposals; not product search'),indent=2));assert build.returncode==0
p=subprocess.run([str(O/'proposal-harness'),str(P/'model.txt'),str(P/'control-0-0-cipher.txt'),'130205'],capture_output=True,text=True);(O/'proposal-stdout.json').write_text(p.stdout);(O/'proposal-trace.txt').write_text(p.stderr);assert p.returncode==0
out=json.loads(p.stdout)[0];tokens=(P/'control-0-0-cipher.txt').read_text().split();n,cut=map(int,tokens[:2]);cipher=list(map(int,tokens[2:]));ns=dict(F=F,math=math,M=json.loads((P/'model.json').read_text()));tree=ast.parse((O/'fixtures.py').read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['branch','score']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'independent-objective','exec'),ns)
mapping=out['initial_map'];current=ns['score'](mapping,cipher,cut)['prefix_joint'];best=current;bestmap=mapping[:];accepted=0;rejected=0;swapcount=reassigncount=0
for line in p.stderr.splitlines():
 k,a,b,sw,ne,oldscore,newscore,T,draw,take=line.split();k,a,b,sw,ne,take=map(int,[k,a,b,sw,ne,take]);oldscore,newscore,T,draw=map(float,[oldscore,newscore,T,draw]);assert abs(oldscore-current)<1e-8;candidate=mapping[:]
 if sw:
  assert mapping[a]!=mapping[b];candidate[a],candidate[b]=candidate[b],candidate[a];swapcount+=1
 else:
  assert Counter(mapping)[mapping[a]]>1 and ne!=mapping[a];candidate[a]=ne;reassigncount+=1
 assert set(candidate)==set(range(17));expected=ns['score'](candidate,cipher,cut)['prefix_joint'];assert abs(newscore-expected)<1e-8;assert abs(T-3*(.05/3)**(k/4999))<1e-12
 assert take==int(newscore>=oldscore or draw<math.exp((newscore-oldscore)/T));assert (draw==-1)==(newscore>=oldscore)
 if take:
  mapping=candidate;current=newscore;accepted+=1
  if current>best:best=current;bestmap=mapping[:]
 else:rejected+=1
assert bestmap==out['map'] and abs(best-out['score'])<1e-8;assert accepted==out['accepted'];assert accepted+rejected==out['valid_proposals']
result=dict(status='PASS',nominal_proposals=200,valid=accepted+rejected,accepted=accepted,rejected=rejected,swaps=swapcount,reassignments=reassigncount,final_count_recount=True,best_map_exact=True)
(O/'proposal-results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
