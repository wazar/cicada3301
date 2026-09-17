import pathlib,json,hashlib
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];S=R/'exploration/persistent-02/section';manifest=json.loads((S/'inspection/major-marks/manifest.json').read_text());packet=json.loads((S/'section-packet.json').read_text());whole=[13,154,275,297,350,394,434,531];body=[141,262,284,337,381,421,518]
assert len(manifest)==8 and [x['reset_before_section_rune'] for x in manifest]==whole
for x in manifest:
 assert x['reset_before_section_rune']=={0:0,1:262,2:528}[x['page']]+x['after_page_rune']+1
 assert hashlib.sha256((S/'inspection/major-marks'/x['crop']).read_bytes()).hexdigest()==x['crop_sha256']
assert [x-13 for x in whole if x>13]==body
assert all(x-1 in packet['explicit_ends'] for x in whole)
assert all(x-1 in packet['body']['explicit_ends'] for x in body)
assert len(packet['runes'])==729 and len(packet['body']['runes'])==716
out=dict(passed=True,whole_resets=whole,body_resets=body,crop_hashes_checked=8,scope='Coordinate/hash/explicit-boundary consistency, not a fresh allglyph or allmark visual reread. Reviewer separately viewed p1-line0 crop and observed four-dot major mark among single-dot delimiters.')
(O/'mark-coordinate-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
