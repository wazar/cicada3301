import json,gzip,pathlib,collections,importlib.util
D=pathlib.Path('exploration/persistent-01/worker-p/P04');assert not D.parents[1].joinpath('STOP').exists()
e=json.load(gzip.open(D.parent/'P03/evidence.json.gz','rt'));pages=[]
for p in e['real']:
 assert len(p['output_counts_by_rune'])==29 and all(v>0 for r,v in p['output_counts_by_rune']);groups={}
 for case in p['cases']:
  if case['result']['status']!='FEASIBLE':continue
  for prov in case['provenance']:
   cnt=prov['letter_counts'];support=''.join(chr(i+65) for i,n in enumerate(cnt) if n);key=tuple(cnt);g=groups.setdefault(support,{});g.setdefault(key,[]).append(prov)
 pages.append(dict(page=p['page'],output_counts_by_rune=p['output_counts_by_rune'],groups={s:[dict(counts=list(c),aliases=a) for c,a in sorted(g.items())] for s,g in sorted(groups.items())}))
common=sorted(set.intersection(*(set(p['groups']) for p in pages)));out=dict(pages=pages,common_supports=common)
with gzip.open(D/'support-evidence.json.gz','wt') as f:json.dump(out,f)
summary=dict(common_supports=common,pages=[dict(page=p['page'],supports={s:dict(distinct_vectors=len(g),alias_windows=sum(len(c['aliases']) for c in g)) for s,g in p['groups'].items()}) for p in pages]);(D/'support-results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));print('scipy_available',bool(importlib.util.find_spec('scipy')))
