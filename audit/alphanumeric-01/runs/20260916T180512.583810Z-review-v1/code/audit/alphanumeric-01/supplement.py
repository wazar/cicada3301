"""Persist human/model visual observations and prior artifact identity; no cipher runs."""
import hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE=ROOT/'audit/alphanumeric-01/v1';OUT=ROOT/'audit/alphanumeric-01/v1-review';OUT.mkdir(exist_ok=False)
t=json.loads((BASE/'transcription.json').read_text());cells=t['cells']
observations={
2:('2l','2I / 2L','Plain bar extends above digit cap; no foot. Ascender-height reading l; subtle I/l distinction.'),
25:('3I','3i / 3l','Undotted plain bar at digit cap height, unlike taller l at2.'),
45:('1l','1L / 1I','No bottom foot; bar taller than digit1, matches l ascender. Reject L directly.'),
50:('0l','0L / 0I','No bottom foot; taller than adjacent0; lowercase l.'),
72:('2i','2j','Distinct dot; stem ends at baseline, unlike descender j164.'),
90:('3I','3l','Plain bar cap-height reference; no dot or foot.'),
164:('1j','1i','Dot plus descender below digit baseline; j despite no hook.'),
165:('0I','0l','Bar cap-height, shorter than l samples.'),
172:('2S','2s','S reaches digit cap height; lowercase s elsewhere x-height.'),
175:('0I','0i / 0l','No dot; cap-height bar.'),
182:('2l','2L / 2I','No foot; bar rises above cap-height2.'),
186:('0J','0I / OJ','J has clear curved foot; first glyph narrow oval0, compare wide O215. Prior automatic splitter failed this cell.'),
198:('1j','1i','Dot and descender as164; not i72.'),
199:('0l','0L / 0I','Plain tall bar without foot; taller than0.'),
209:('2t','2t06 as one cell','Lowercase crossed t, separate from adjacent06; old grid fused neighbor.'),
210:('06','missing token','Narrow oval zero and sloping6; directly legible in full row. New bbox contains minor neighbor ink in padded crop.'),
211:('11','1I / two singleton tokens','Both glyphs have angled top flags of digit1. Pair separated from06 and1A. Old grid split this pair.'),
215:('1O','05 / 10','First glyph angled flag1; second broad circular capital O, unlike narrow oval zero186; no S/5 shape.'),
237:('0W','0w','W cap-height, unlike x-height w in p51 row4.'),
246:('3I','3i / 3l','No dot; cap-height plain bar; lowercase i excluded directly.')}
lines=['# Visual uncertainty table — v1 review','', 'Zero-based indices/rows/columns. Direct, unblinded review of all three block crops and the20-site comparison sheet on2026-09-16. No numerical accuracy claim. The finer I/l classifications remain qualitative typography judgments; independent blinded verification is still useful. Coordinates refer to original2400×3600 pixels.','', '| Index | Page,row,column | Rectangle | Reading | Alternatives | Observation |','|---|---|---|---|---|---|']
for i,(reading,alts,obs) in observations.items():
 c=cells[i];lines.append(f"| {i} | {c['page']},{c['row']},{c['column']} | {c['bbox']} | `{reading}` | {alts} | {obs} |")
lines+=['','All remaining tokens received an unblinded row-by-row visual comparison with the three block crops, with no additional disagreement noticed. This is weaker than a fresh blinded transcription; it does not promote inherited agreement to independent ground truth. All leading0 symbols are narrow ovals; capital O instances are wider circular forms; lower o instances are shorter. Original rasters remain authoritative for spacing and glyph identity.']
(OUT/'UNCERTAINTY.md').write_text('\n'.join(lines)+'\n')
paths=['liber-primus/analysis/pp49_51/CAMPAIGN-VII-FINDINGS.md','liber-primus/analysis/pp49_51/keytest.py','liber-primus/analysis/pp49_51/CAMPAIGN-IX-FINDINGS.md','liber-primus/analysis/pp49_51/campaign9.py','liber-primus/analysis/pp49_51/CAMPAIGN-XX-EXTCIPHER.md','liber-primus/analysis/pp49_51/campaign20_extcipher.py','liber-primus/analysis/round13/B05/sweep_results.json','liber-primus/analysis/round13/B05/sweep.log','liber-primus/analysis/round13/B05/control_results.json','liber-primus/analysis/round19/C1/RESULTS.md','liber-primus/analysis/round19/C1/out_b05_sweeprow.jsonl','liber-primus/analysis/round19/C1/out_b05_readjudicated.json','liber-primus/analysis/round19/C1/out_propagation.json','liber-primus/analysis/round19/C1/out_e01.json','liber-primus/analysis/round19/C1/out_e01_cryptrsa.json','liber-primus/analysis/round19/C1/out_singletons.json']
manifest=[]
for path in paths:
 b=(ROOT/path).read_bytes();row={'path':path,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 if path.endswith('jsonl'):row['line_count']=len(b.splitlines());row['header']=b.splitlines()[0].decode()
 manifest.append(row)
(OUT/'prior-artifacts.json').write_text(json.dumps(manifest,indent=2)+'\n')
s=(BASE/'scream-local.txt').read_text();chunks=[s.split(f'## {p+17}.jpg - {p}.jpg')[1].split('\n## ')[0] for p in (49,50,51)]
dec=[]
for chunk in chunks:
 for line in chunk.splitlines():
  if re.fullmatch(r'\s*\d{1,3}(?:\s+\d{1,3}){7}\s*',line):dec.extend(map(int,line.split()))
assert len(dec)==256
alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx';diff=[]
for c,d in zip(cells,dec):
 value=60*alphabet.index(c['token'][0])+alphabet.index(c['token'][1])
 if value!=d:diff.append({'index':c['index'],'token':c['token'],'conditional_base60':value,'scream_decimal':d})
(OUT/'decimal-disagreements.json').write_text(json.dumps(diff,indent=2)+'\n')
print('visual sites',len(observations),'prior artifacts',len(manifest),'decimal differences',len(diff),'retained sweep lines',next(x['line_count'] for x in manifest if 'line_count' in x))
