"""Qualify source-word aliases without changing any scientific key or input."""
import pathlib,importlib.util,json,hashlib
R=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('gp',R/'liber-primus/src/lp/gematria.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
s=importlib.util.spec_from_file_location('fixture',R/'audit/parallel-01/reference/fixtures.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
actual=next(x[2] for x in f.CASES if x[0]=='jpg107-167');word=g.keyword_to_indices('CIRCUMFERENCE');literal=g.keyword_to_indices('FIRFUMFERENFE')
assert literal==actual and g.keyword_to_indices('C')==[5] and g.keyword_to_indices('F')==[0]
out={'circumference_word_indices':word,'verified_reference_key_indices':actual,'reference_key_transliteration':g.indices_to_translit(actual),'differing_positions':[i for i,(a,b) in enumerate(zip(word,actual)) if a!=b],'source_claim':'SOLVED-PAGES.json says C and F share a rune; that contradicts this repository alphabet and is not used here as a key-derivation justification.','scope':'Existing reference and P02 key vectors remain unchanged. No new key admitted, search performed or inherited evidence edited. Historical intention/pun not established by this source check.','source_hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'liber-primus/SOLVED-PAGES.json',R/'liber-primus/src/lp/gematria.py',R/'audit/parallel-01/reference/fixtures.py']}}
(O/'key-source-qualification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
