import checks as c
challenge=c.ROOT/'audit/parallel-01/coordination/blind-challenge.json'
x=c.json.loads(challenge.read_text());print(x.keys())
cs=x.get('ciphertext_pages',x.get('pages',x.get('ciphertexts')))
assert cs is not None
rows=[dict(candidate_id=i,**c.select(cs,k)) for i,k in zip(x['candidate_ids'],x['keys'])]
rows.sort(key=lambda r:(-r['second'],-r['best'],r['candidate_id']))
y={'challenge_sha256':c.hashlib.sha256(challenge.read_bytes()).hexdigest(),'matrix_sha256':c.hashlib.sha256((c.OUT/'MATRIX.md').read_bytes()).hexdigest(),'ranking':rows}
p=c.OUT/'blind-ranking.json';p.write_text(c.json.dumps(y,indent=2));print(c.hashlib.sha256(p.read_bytes()).hexdigest());print([(r['candidate_id'],r['second']) for r in rows])
