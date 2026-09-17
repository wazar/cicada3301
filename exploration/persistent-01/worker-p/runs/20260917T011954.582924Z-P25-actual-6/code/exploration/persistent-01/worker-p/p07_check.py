import pathlib,gzip,json,collections
D=pathlib.Path('exploration/persistent-01/worker-p/P07');assert not D.parents[1].joinpath('STOP').exists();e=json.load(gzip.open(D/'evidence.json.gz','rt'));pr=[i for i in range(2,110) if len([j for j in range(1,i+1) if i%j==0])==2];assert pr==e['prime_table'];packets=[dict(streams=e['streams'],result=e['real'])]+e['controls']+e['ordinary'];n=0
for packet in packets:
 r=packet['result'];profiles=[]
 for page in [3,7]:
  c=packet['streams'][str(page)];values=[pr[x] for x in c];pref=[0]
  for v in values*2:pref.append(pref[-1]+v)
  fields=[f for f in e['fields'] if f['page']==page];res=[[(pref[f['end']+s]-pref[f['start']+s])%29 for f in fields] for s in range(len(c))];original=next(p for p in r['profiles'] if p['page']==page);assert res==original['residues_by_phase'];profiles.append([row.count(0) for row in res])
 hist=collections.Counter(a+b for a in profiles[0] for b in profiles[1]);assert dict(hist)=={int(k):v for k,v in r['null_histogram'].items()};assert r['tail_numerator']==sum(v for k,v in hist.items() if k>=r['successes']);assert r['tail_denominator']==sum(hist.values());n+=1
out=dict(verdict='PASS',packets_checked=n,all_phase_profiles_replayed=True,all_cartesian_null_histograms_replayed=True,source_fields=[dict(page=f['page'],start=f['start'],end=f['end'],source_positions=len(f['source_char_positions'])) for f in e['fields']]);(D/'check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
