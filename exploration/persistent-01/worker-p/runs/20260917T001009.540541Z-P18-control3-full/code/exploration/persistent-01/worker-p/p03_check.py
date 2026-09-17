import ast,collections,gzip,json,pathlib,math,fractions
B=pathlib.Path('exploration/persistent-01');D=B/'worker-p/P03';assert not (B/'STOP').exists()
p=B/'worker-o/check_o02.py';m=ast.parse(p.read_text());nodes=[n for n in m.body if isinstance(n,ast.FunctionDef) and n.name in ['reason_ok','check_result']];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p)+'::certificate_definitions','exec'))
e=json.load(gzip.open(D/'evidence.json.gz','rt'));j=json.load(gzip.open(B/'worker-j/j03-windows.json.gz','rt'));tby={t['name']:t for t in j['texts']};mapped={t['name']:t for t in e['texts']};mapchecks=0
for t in e['texts']:
 original=tby[t['name']];raw=''.join(chr(v+65) for v in original['source']);expected=''.join(c for c in raw if c not in 'AEIOU');assert expected==''.join(chr(v+65) for v in t['source']);rows=t['all_letter_map'];assert len(rows)==len(raw)
 for i,(r,c,m) in enumerate(zip(rows,raw,original['source_map'])):
  assert r['expanded_index']==i and r['letter']==c and r['keep']==(c not in 'AEIOU');assert all(r[k]==v for k,v in m.items());mapchecks+=1
 kept=[r for r in rows if r['keep']];assert [r['consonant_index'] for r in kept]==list(range(len(expected)))
 flat=sorted(i for r in t['rune_map'] for i in r['expanded_indices']);assert flat==list(range(len(rows)))
 for rm in t['rune_map']:
  rr=[rows[i] for i in rm['expanded_indices']];assert all(r['source_rune_index']==rm['source_rune_index'] and r['rune']==rm['rune'] for r in rr);assert rm['retained_indices']==[r['consonant_index'] for r in rr if r['keep']];assert rm['removed_expanded_indices']==[r['expanded_index'] for r in rr if not r['keep']]
counts=collections.Counter();windows=0;feasibleby=[];totalby=[];lex=[]
for p in e['real']:
 actual=dict(p['output_counts_by_rune']);seen=set();feasible=0;feasibleprovs=[]
 for case in p['cases']:
  result=case['result'];check_result(p['items'],case['targets'],result)
  for prov in case['provenance']:
   key=(prov['group'],prov['start']);assert key not in seen;seen.add(key);t=mapped[prov['group']];s=t['source'][prov['start']:prov['end']];cnt=collections.Counter(s);assert len(s)==p['n'] and [cnt[i] for i in range(26)]==prov['letter_counts'] and sorted(cnt.values())==case['targets'];kept=[r for r in t['all_letter_map'] if r['keep']];a,b=kept[prov['start']],kept[prov['end']-1];assert prov['expanded_span']==[a['expanded_index'],b['expanded_index']+1] and prov['source_rune_span']==[a['source_rune_index'],b['source_rune_index']+1]
   if result['status']=='FEASIBLE':
    mapping=prov['letter_to_output_runes'];assert sorted(sum([m['output_runes'] for m in mapping],[]))==sorted(actual)
    for m in mapping:assert sum(actual[r] for r in m['output_runes'])==cnt[m['letter_index']]
    feasible+=1;feasibleprovs.append(prov)
   counts[result['status']]+=1;windows+=1
 expected={(t['name'],start) for t in e['texts'] for start in range(max(0,len(t['source'])-p['n']+1))};assert seen==expected
 feasibleby.append(feasible);totalby.append(len(expected));lex.append(dict(page=p['page'],provenance=min(feasibleprovs,key=lambda r:(r['group'],r['start']))))
for c in e['tiny_controls']+e['actual_controls']:check_result(c['items'],c['targets'],c['result'])
f=fractions.Fraction(math.prod(feasibleby),math.prod(totalby));out=dict(verdict='PASS',letter_maps_checked=mapchecks,windows_checked=windows,weighted_statuses=dict(counts),controls_checked=210,feasible_by_page=feasibleby,windows_by_page=totalby,independent_uniform_window_conjunction=dict(numerator=f.numerator,denominator=f.denominator,value=float(f)),lexicographically_first_pagewise_witnesses=lex,interpretation='Only pagewise necessary count compatibility. The tuple is not a shared codebook or candidate plaintext. Uniform independent draws are imposed descriptive weights, not natural-language independence.')
(D/'check.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='lexicographically_first_pagewise_witnesses'},indent=2))
