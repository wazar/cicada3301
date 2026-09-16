"""Independent certificate checking, no experimental solver imports."""
import collections,gzip,json,pathlib
R=pathlib.Path(__file__).resolve().parent;d=json.load(gzip.open(R/'O02-evidence.json.gz','rt'))
def reason_ok(items,targets,reason):
 kind=reason['kind']
 if kind=='minimum':assert min(targets)<min(items)
 elif kind=='total':assert sum(items)!=sum(targets)
 elif kind=='support':assert len(targets)>len(items)
 elif kind=='small_capacity':
  t=reason['threshold'];assert sum(x for x in targets if x<=t)>sum(x for x in items if x<=t)
 elif kind=='subset_support':
  sums={0}
  for x in items:sums|={v+x for v in sums}
  assert reason['target'] not in sums
 else:raise AssertionError(kind)
def check_result(items,targets,result):
 if result['status']=='FEASIBLE':
  assert sorted(sum(result['groups'],[]))==sorted(items)
  assert sorted(map(sum,result['groups']))==sorted(targets)
  return
 assert result['status']=='INFEASIBLE'
 if 'reason' in result:reason_ok(items,targets,result['reason']);return
 dag=result['proof_dag'];key=str(tuple(sorted(items)))+'/'+str(tuple(sorted(targets)));assert key in dag
 for key,node in dag.items():
  ii=node['items'];tt=node['targets']
  if 'reason' in node:reason_ok(ii,tt,node['reason']);continue
  # Alternate exhaustive submultiset construction by adding individual items,
  # deduplicating equal-valued subsets. Unlike solver count-product recursion.
  subsets={()}
  for item in ii:subsets|={tuple(sorted(s+(item,))) for s in subsets if sum(s)+item<=tt[0]}
  exact={s for s in subsets if sum(s)==tt[0]}
  assert exact=={tuple(c['selected']) for c in node['children']}
  assert len(exact)==len(node['children'])
  for child in node['children']:
   left=list(ii)
   for value in child['selected']:left.remove(value)
   childkey=str(tuple(left))+'/'+str(tuple(tt[1:]));assert childkey==child['child'] and childkey in dag
   assert dag[childkey]['items']==left and dag[childkey]['targets']==tt[1:]
counts=collections.Counter();checked_dag=0
for p in d['real']:
 actual=dict(p['output_counts_by_rune'])
 for c in p['cases']:
  check_result(p['items'],c['targets'],c['result']);counts[c['result']['status']]+=len(c['provenance']);checked_dag+=len(c['result'].get('proof_dag',{}))
  if c['result']['status']=='FEASIBLE':
   for prov in c['provenance']:
    mapped=prov['letter_to_output_runes'];assert sorted(sum([m['output_runes'] for m in mapped],[]))==sorted(actual)
    for m in mapped:assert sum(actual[r] for r in m['output_runes'])==prov['letter_counts'][m['letter_index']]
for c in d['actual_controls']+d['tiny_controls']:check_result(c['items'],c['targets'],c['result'])
out={'weighted_case_counts':dict(counts),'real_proof_dag_nodes_checked':checked_dag,'control_certificates_checked':len(d['actual_controls'])+len(d['tiny_controls']),'verdict':'PASS'}
(R/'O02-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
