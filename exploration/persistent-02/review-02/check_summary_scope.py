"""Read-only reproduction of the unfiltered A04 summarizer scope problem."""
import pathlib,json,collections,hashlib
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];S=R/'exploration/persistent-02/section'
rows=[json.loads(p.read_text()) for p in sorted((S/'A04').glob('*.json'))];counts=collections.Counter(r['batch'] for r in rows);old=json.loads((S/'A04-summary.json').read_text());intended=[r for r in rows if r['batch'] in ['A01','A02']]
out=dict(source_sha256=hashlib.sha256((S/'summarize_forest.py').read_bytes()).hexdigest(),all_json_panels=len(rows),counts_by_batch=dict(counts),stored_summary_counts=old['counts'],intended_p03_panels=len(intended),intended_p03_candidates=sum(x['candidate_count'] for x in intended),unfiltered_candidates=sum(x['candidate_count'] for x in rows),finding='Unfiltered glob includes later A05 records; filter A01/A02 before computing original summary counts/controls.')
(O/'summary-scope-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
