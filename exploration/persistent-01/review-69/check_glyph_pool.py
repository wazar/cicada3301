from pathlib import Path
from collections import Counter
import json,random,hashlib
D=Path(__file__).parent;O=Path('exploration/persistent-01/worker-p/P06');g=O/'geometry-audit.json';s=O/'selection.json';report=O/'REPORT.md';code=Path('exploration/persistent-01/worker-p/p06_prepare.py')
# Read geometry/selection metadata only: neither images nor hidden rune labels.
a=json.loads(g.read_text());selected=json.loads(s.read_text());records=a['records'];eligible=[r for r in records if r['black']];assert random.Random(130106).sample(eligible,100)==selected
key=lambda r:(r['page'],r['row'],r['row_component'],tuple(r['box']))
assert len(set(map(key,records)))==len(records);assert len(set(map(key,selected)))==100;assert set(map(key,selected))<=set(map(key,eligible));remain=[r for r in eligible if key(r) not in set(map(key,selected))];assert len(records)==178 and len(eligible)==168 and len(remain)==68;assert sum(r['components'] for r in a['rows'])==178
quote=next(x for x in report.read_text().splitlines() if '168eligible' in x)
out={'PASS':True,'metadata_records_excluding_two_dropcaps':len(records),'black_eligible':len(eligible),'excluded_heading_records':len(records)-len(eligible),'selected':len(selected),'eligible_remaining':len(remain),'eligible_by_page':dict(Counter(r['page'] for r in eligible)),'selected_by_page':dict(Counter(r['page'] for r in selected)),'remaining_by_page':dict(Counter(r['page'] for r in remain)),'selection_rng_replay':True,'source_quote':quote,'read_no_images_or_truth_label_files':True,'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [g,s,report,code]]};(D/'glyph-pool-correction.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['sources','source_quote']})
