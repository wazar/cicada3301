from search import *
allrows=[];runs=[]
for f in OUT.glob('*-results.json'):
 if f.name.startswith('R08'):continue
 z=json.loads(f.read_text());runs.append(dict(file=f.name,completed=z['completed'],jobs=z['total_jobs'],seconds=z['seconds']));
 for r in z['top']:r['evidence_file']=f.name;allrows.append(r)
allrows.sort(key=lambda z:z['score'],reverse=True);unique=[];seen=set()
for z in allrows:
 sig=(z['page'],tuple(z['plain']))
 if sig not in seen:seen.add(sig);unique.append(z)
 if len(unique)>=20:break
r08=json.loads((OUT/'R08-results.json').read_text());out=dict(R07=unique,R08=r08['top'],R08_structural_leads=r08['structural_leads'],replay='Run search.py f/rigid --start ID --stop ID+1 using same job manifest; page55 adds --page55. R08 binary.py deterministically enumerates ids.',sources='Hashes and immutable source snapshots in runs/*/command.json and code; original payload SHA256 verified by assertion.',status='UNREVIEWED');save(OUT/'top_candidates.json',out)
summary=dict(runs=runs,R07_top=[dict(page=r['page'],score=r['score'],text=r['text'],method='F' if r['path'] else 'ordinary-compatible',path=r['path']) for r in unique[:5]],R08=dict(completed=r08['completed'],keys=r08['keys'],structures=len(r08['structural_leads']),best_printable=r08['top'][0]['printable_fraction']),controls=[dict(name=c['name'],truth_rank=c['truth_rank'],errors=c['top_rune_errors']) for c in json.loads((OUT/'controls.json').read_text())]);save(OUT/'summary.json',summary);print(json.dumps(summary,indent=2))
