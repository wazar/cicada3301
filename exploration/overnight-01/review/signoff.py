import pathlib,json,hashlib,collections,datetime
R=pathlib.Path(__file__).resolve().parents[3];B=R/'exploration/overnight-01';O=pathlib.Path(__file__).parent
hashes={}
def read(p):
 b=p.read_bytes();hashes[str(p.relative_to(R))]=hashlib.sha256(b).hexdigest();return json.loads(b)
checks=[]
for name in ['checked.json','binary_checked.json']:checks+=read(O/name)['checked']
ck={(r['source_file'],str(r['id']),r.get('page') if '/r06/' in r['source_file'] else None) for r in checks if r['independently_reproduced']}
p=B/'candidate-registry.jsonl';raw=p.read_bytes();hashes[str(p.relative_to(R))]=hashlib.sha256(raw).hexdigest();entries=[json.loads(x) for x in raw.splitlines()];counts=collections.Counter();sources={};origins=0
for e in entries:
 assert e['status']=='REPRODUCIBLE_CANDIDATE'
 for origin in e['origins']:
  origins+=1;counts[origin['lane']]+=1;src=origin['source_file'];payload=origin['payload'];pg=payload.get('original_page',payload.get('page'));assert (src,str(origin['local_id']),pg if '/r06/' in src else None) in ck;assert origin['independently_reproduced']
  if src not in sources:sources[src]=read(R/src)
  assert hashes[src]==origin['source_sha256'];rows=sources[src][origin['lane']] if isinstance(sources[src],dict) else sources[src];assert payload in rows
assert len(entries)==584 and origins==608
p=B/'REPORT.md';hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
out={'reviewer':'/root/overnight_review','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coordinator_report_material_mismatch':False,'registry_unique_records':len(entries),'registry_origins':origins,'lane_origin_counts':dict(counts),'registry_payloads_unchanged':True,'registry_statuses_match_independent_checks':True,'reserved_pages_revealed':[],'scientific_search_rerun':False,'signoff':'No material mismatch in final report/registry. Counts, bounds, controls, no-credible-text conclusion and no-validation promotion match review. Publication prefix-only redaction with original/both-hash retention does not change scientific signoff.','minor_editorial_note':'Report says reviewer schema/import assumptions; reviewer failures were schema field assumptions only, not imports. Optional correction to schema assumptions.','source_hashes':hashes}
(O/'final-signoff.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='source_hashes'},indent=2))
