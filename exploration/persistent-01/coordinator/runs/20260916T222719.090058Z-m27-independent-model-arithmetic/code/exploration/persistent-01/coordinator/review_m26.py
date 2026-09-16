"""Independent scalar accounting/path replay, no inherited decoder execution."""
import pathlib,json,gzip,math,hashlib,random
import numpy as np
B=pathlib.Path(__file__).resolve().parents[1];D=B/'worker-m/M26';tab=np.load(B/'review-08/independent-lm-table.npy');keys={x['id']:x for x in json.loads((D/'keys.json').read_text())};rng=random.Random(330828);paths=visits=searches=0
rows=json.loads((D/'results.json').read_text());assert len(rows)==43
cfg=json.loads((B/'config.json').read_text());pages={r['page'] for r in rows};assert len(pages)==43 and not pages.intersection(cfg['reserved_original_pages']+[0,17])
for row in rows:
 c=row['map']['indices'];cases=[('real-'+str(row['page']),c)]
 for n in row['null']:
  cc=[rng.randrange(29)]
  for i in range(1,len(c)):
   if c[i]==c[i-1]:cc.append(cc[-1])
   else:
    v=rng.randrange(28);cc.append(v+(v>=cc[-1]))
  cases.append((n['name'],cc))
 for name,expected in cases:
  with gzip.open(D/'evidence'/(name+'.json.gz'),'rt') as f:r=json.load(f)
  assert r['cipher']==expected;ends=set(r['ends']);assert all(0<=x<len(expected) for x in ends)
  for ident,decoded in [(x['id'],x['decode']) for x in r['rows']]+[(r['rows'][0]['id'],r['top16'])]:
   key=keys[ident];buf=key['key'];sign=key['sign']
   for a in decoded['alternatives']:
    assert len(a['plain'])==len(a['reject_counts'])==len(expected)
    used=0;score=0.;ctx=(29,29)
    for i,(plain,t) in enumerate(zip(a['plain'],a['reject_counts'])):
     assert type(t)==int and t>=0 and (i>0 or t==0);accepted=used+2*t;assert accepted<len(buf)
     for j in range(used,accepted,2):assert (plain-sign*buf[j])%29==expected[i-1]
     assert (plain-sign*buf[accepted])%29==expected[i]
     if 'key_walk' in a:assert a['key_walk'][i]==dict(input_index=i,key_start=used,rejected=list(range(used,accepted,2)),burned=list(range(used+1,accepted,2)),accepted=accepted,key_after=accepted+1)
     score+=float(tab[ctx[0],ctx[1],plain]);ctx=(ctx[1],plain)
     if i in ends:score+=float(tab[ctx[0],ctx[1],29]);ctx=(ctx[1],29)
     score+=t*math.log(.83)+(math.log(.17) if i and expected[i]==expected[i-1] else 0);used=accepted+1;visits+=1
    assert used==a['used'];assert abs(score/(len(expected)+len(ends))-a['score'])<2e-12;paths+=1
  searches+=1
 assert row['tail']==(1+sum(n['score']>=row['score'] for n in row['null']))/20
old=json.loads((D/'old-evidence-manifest.json').read_text())
for f in old['files']:assert hashlib.sha256((B.parents[1]/f['path']).read_bytes()).hexdigest()==f['sha256']
out=dict(searches=searches,retained_paths=paths,rune_visits=visits,regenerated_nulls=817,page_tails=43,prior_files_unchanged=len(old['files']),scope='Independent scalar re-encryption/scoring of every saved path and exact null regeneration; DP search optimality inherits separate review10, not rerun.')
(B/'coordinator/M26-path-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
