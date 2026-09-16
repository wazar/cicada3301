import pathlib,json,gzip,itertools
O=pathlib.Path(__file__).resolve().parent
with gzip.open(O/'snapshots/exploration/persistent-01/worker-p/P04/support-evidence.json.gz','rt') as f:e=json.load(f)
assert e['common_supports']==['BCDFGHLMNPRSTWY'];support=e['common_supports'][0];pages=e['pages'];h=[dict(p['output_counts_by_rune']) for p in pages];vecs=[[z['counts'] for z in p['groups'][support]] for p in pages];checks=[]
for name in ['B','P']:
 letter=ord(name)-65;sets=[set(v[letter] for v in vv) for vv in vecs];upper=[max(z) for z in sets];eligible=[];excluded=[]
 for rune in range(29):
  profile=[hh[rune] for hh in h];viol=[j for j,(a,b) in enumerate(zip(profile,upper)) if a>b]
  if not viol:eligible.append(rune)
  else:excluded.append({'rune':rune,'profile':profile,'violated_page':pages[viol[0]]['page'],'upper':upper[viol[0]]})
 all_subsets=[];valid=[]
 for bits in itertools.product([0,1],repeat=len(eligible)):
  rs=[r for r,on in zip(eligible,bits) if on];profile=[sum(hh[r] for r in rs) for hh in h];ok=all(v in s for v,s in zip(profile,sets));row={'runes':rs,'profile':profile,'allowed':ok};all_subsets.append(row)
  if ok:valid.append(rs)
 assert valid==([[7]] if name=='B' else [[7],[3]])
 checks.append({'letter':name,'allowed_counts_per_page':[sorted(s) for s in sets],'eligible_runes':eligible,'excluded_runes':excluded,'all_eligible_subsets':all_subsets,'compatible_subsets':valid})
# One output rune maps to exactly one source letter; B owns7, leaving P=3.
assert set(checks[0]['compatible_subsets'][0])=={7};remaining=[s for s in checks[1]['compatible_subsets'] if not set(s)&{7}];assert remaining==[[3]]
contradictions=[]
for p,hh,vv in zip(pages,h,vecs):
 pairs=sorted(set((v[1],v[15]) for v in vv));required=[hh[7],hh[3]];kept=sum([v[1],v[15]]==required for v in vv);contradictions.append({'page':p['page'],'required_B_P_counts':required,'source_B_P_pairs':pairs,'remaining_vectors':kept})
assert next(z for z in contradictions if z['page']==1)['remaining_vectors']==0
out={'verdict':'EXACT_INTEGER_CONTRADICTION','scope':'P03-certified finite consonantal source windows, shared rune-to-letter assignment across five pages','common_support':support,'page_order':[p['page'] for p in pages],'rare_letter_certificates':checks,'forced_assignment':{'B':[7],'P':[3]},'pagewise_joint_count_checks':contradictions,'uses_MILP_status':False,'uses_floating_point':False};(O/'elementary-certificate.json').write_text(json.dumps(out,indent=2));print(json.dumps(contradictions,indent=2))
