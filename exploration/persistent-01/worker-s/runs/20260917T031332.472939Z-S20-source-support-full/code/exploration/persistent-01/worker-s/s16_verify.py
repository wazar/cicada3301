from pathlib import Path
import json,hashlib
B=Path('exploration/persistent-01/worker-s');src=Path('exploration/persistent-01/worker-f/F06-maps.json');pages={p['page']:p for p in json.loads(src.read_text())};res=json.loads((B/'S16-result.json').read_text());assert res['source_sha256']==hashlib.sha256(src.read_bytes()).hexdigest();checked=[]
for result in res['pages']:
 p=pages[result['page']];cert=result['result']['witness'];assert len(cert)==2
 arrows=[]
 for e in cert:
  w=p['words'][e['word_index']];seq=p['indices'][w['start']:w['end']];r=e['rotation'];rotated=seq[r:]+seq[:r];k=next(i for i,(a,b) in enumerate(zip(seq,rotated)) if a!=b)
  assert k==e['mismatch'];assert seq==e['runes'] and w==e['word_map'];assert (seq[k],rotated[k])==(e['a'],e['b']);assert e['source_a']==p['source_char_positions'][w['start']+k];assert e['source_b']==p['source_char_positions'][w['start']+(k+r)%len(seq)];arrows.append((seq[k],rotated[k]))
 assert arrows[0]==arrows[1][::-1] and arrows[0][0]!=arrows[0][1]
 checked.append({'page':p['page'],'contradictory_inequalities':arrows,'source_words':[e['word_index'] for e in cert],'valid':True,'shortest_possible_nontrivial_cycle':True})
(B/'S16-proof-check.json').write_text(json.dumps(checked,indent=2));print(json.dumps(checked))
