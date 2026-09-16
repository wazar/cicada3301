from pathlib import Path
from collections import defaultdict
import json,subprocess,hashlib,shutil,random
O=Path(__file__).resolve().parent;Q=O.parent/'worker-q/Q04';P=O.parent/'worker-p/P05'
(O/'fixtures').mkdir(exist_ok=True);source=(Q/'search.cpp').read_bytes();(O/'kernel-local.cpp').write_bytes(source);(O/'Q04-CARD-snapshot.md').write_bytes((Q/'CARD.md').read_bytes())
compiler=subprocess.run(['c++','--version'],capture_output=True,text=True);command=['c++','-O2','-std=c++17',str(O/'kernel-local.cpp'),'-o',str(O/'kernel-local')];build=subprocess.run(command,capture_output=True,text=True)
record=dict(command=command,exit_code=build.returncode,stdout=build.stdout,stderr=build.stderr,compiler=compiler.stdout,source_sha256=hashlib.sha256(source).hexdigest(),binary_scope='locally compiled, platform-specific');(O/'build.json').write_text(json.dumps(record,indent=2));assert build.returncode==0
f=json.loads((O/'fixtures.json').read_text());groups=defaultdict(list)
for row in f['fixtures']:groups[tuple(row['cipher']),row['cut']].append(row)
checked=0;maxerror=0.;outputs=[]
for group,((cipher,cut),rows) in enumerate(groups.items()):
 cf=O/'fixtures'/f'cipher-{group}.txt';mf=O/'fixtures'/f'maps-{group}.txt';cf.write_text(f'{len(cipher)} {cut}\n'+' '.join(map(str,cipher)));mf.write_text('\n'.join(' '.join(map(str,r['mapping'])) for r in rows))
 cmd=[str(O/'kernel-local'),str(P/'model.txt'),str(cf),'0',str(mf)];p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr;answer=json.loads(p.stdout);assert len(answer)==len(rows)
 for row,got in zip(rows,answer):
  for a,b in [('lm','prefix_lm'),('emission','prefix_emission'),('joint','prefix_joint')]:
   err=abs(got[a]-row['expected'][b]);maxerror=max(maxerror,err);assert err<1e-9,(row['id'],a,got[a],row['expected'][b])
  outputs.append(dict(fixture=row['id'],actual=got));checked+=1
 (O/'fixtures'/f'output-{group}.json').write_text(p.stdout)
# Same mapping + prefix; adversarial replacement of all held symbols leaves kernel output exact.
rng=random.Random(1717002);isolation=[]
for ix,row in enumerate(f['fixtures'][-12:]):
 c=row['cipher'][:row['cut']]+[rng.randrange(29) for _ in row['cipher'][row['cut']:]];cf=O/'fixtures'/f'isolation-{ix}.txt';mf=O/'fixtures'/f'isolation-map-{ix}.txt';cf.write_text(f'{len(c)} {row["cut"]}\n'+' '.join(map(str,c)));mf.write_text(' '.join(map(str,row['mapping'])))
 p=subprocess.run([str(O/'kernel-local'),str(P/'model.txt'),str(cf),'0',str(mf)],capture_output=True,text=True);assert p.returncode==0;got=json.loads(p.stdout)[0];expected=next(v['actual'] for v in outputs if v['fixture']==row['id']);assert got==expected;isolation.append(dict(fixture=row['id'],cipher=c,score=got))
out=dict(status='PASS',fixtures_checked=checked,score_processes=len(groups),max_score_error=maxerror,score_only_suffix_perturbations=len(isolation),source_sha256=record['source_sha256'],isolation=isolation)
(O/'kernel-results.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='isolation'},indent=2))
