import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).parent;M=json.loads((D/'maps.json').read_text());P=json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text());a=dict(np.load(D/'actual.npz'));off=0;desc=[]
for p,m in zip(P,M):
 n=len(p['indices']);c=a['cipher'][off:off+n];z=a['nulls'][:,off:off+n];e=np.array(m['novel_edges']);v=(c[e[:,0]]==c[e[:,1]]).sum();stats=(z[:,e[:,0]]==z[:,e[:,1]]).sum(axis=1);desc.append({'page':p['page'],'novel_edges':len(e),'repeats':int(v),'null_mean':float(stats.mean()),'runes':n,'route_inherited_ordinary_edges':n-1-len(e)});off+=n
(D/'per-page-descriptive.json').write_text(json.dumps(desc,indent=2))
report='''# N14 — page circumference traversal

One frozen, speculative interpretation of solved p57 was executed: clockwise peeling of ragged physical rune rows. The instruction does not uniquely define this page-level route. It is distinct from P21's word endpoint deletion and G01's six mirror/column routes; no route was added after results.

Actual: **72 repeats among 2,440 newly created adjacencies**, versus fitted-null mean **91.4625**, nominal lower tail **.018** (17/999 null totals at or below actual; add-one). Ordinary ±1 flattened adjacencies were excluded from the statistic. All 45 admitted pages contribute; no reserve, image50, English scoring or key search occurred. The 12 source-backed controls produced 5–22 repeats and all reached .005 with199nulls each. Controls cycle four actual solved rune sources, explicitly skip repeated output with probability .83, and plant along the route at actual page shapes. They establish sensitivity to this large planted deficit, not natural-text recovery or power at the much smaller actual effect.

This is a small exploratory source-route discrepancy, not evidence of a decoded message. Critically the null fixes first runes and every ordinary repeated/nonrepeated edge but uses smoothed empirical destination weights, not conditional MLE and not an exact fixed-inventory randomization. Finite-sample concentration of estimated page weights can inflate expected collisions compared with inventory-conditioned data. Row/prose correlations are not modeled. Many earlier campaign tests were run. Therefore .018 is not a candidate-level significance claim, and no route reading should be promoted on it.

Decision: freeze this recipe and investigate null adequacy before any further route interpretation. A single uniform-destination exact-mask sensitivity would isolate the fitted-marginal issue cheaply; an exact inventory-and-mask conditional sampler would be stronger but requires validated sampling. Do not expand routes or inspect fragments. No follow-up is included in this result.

Independent no-import verification reconstructed all45 route permutations and source-character maps, all12 control source positions/acceptance RNG, all3387 saved null masks/counts/tails, and all34,808,149 RNG variates; categorical probability inequalities were checked with separate scalar arithmetic for the first2 rows of each null family. All passed. Full arrays, controls,source traces, per-page descriptives and logs are retained. Pilot .212s, full1.962s, verification1.018s. No failed scientific execution; initial read-only inspection accidentally printed a long admitted F06 JSON line, a logged output-volume mistake without reserved data.
'''
(D/'REPORT.md').write_text(report)
files=[p for p in D.rglob('*') if p.is_file() and p.name!='MANIFEST.json'];(D/'MANIFEST.json').write_text(json.dumps([{'path':str(p.relative_to(D)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)],indent=2))
print('files',len(files))
