import checks as c,statistics,platform
x=c.json.loads((c.OUT/'raw-results.json').read_text());summary=[]
for cell in x['cells']+x['challenges']:
    ps=cell['positive'];r={'L':cell['L'],'construction':cell.get('construction','reset'),'register':cell.get('register','english'),'positive_n':len(ps),'accepted':sum(p['final']['accept'] for p in ps),'selected_exact_pages':sum(p['best']['exact'] for row in ps for p in row['rows']),'selected_mean_rune_recovery':statistics.mean(p['best']['recovery'] for row in ps for p in row['rows'])}
    if 'negative' in cell:r.update(wrong_n=len(cell['negative']),wrong_accepted=sum(p['final']['accept'] for p in cell['negative']),zero_false_accept_one_sided_95_upper=1-.05**(1/len(cell['negative'])),twenty_of_twenty_two_sided_95_lower=.025**(1/20))
    summary.append(r)
(c.OUT/'summary.json').write_text(c.json.dumps(summary,indent=2))
source_paths=['liber-primus/verify_solution.py','liber-primus/analysis/campaign18_skip/skipdecode.py','liber-primus/benchmark/null.py','liber-primus/src/lp/score.py','liber-primus/data/english_quadgrams.txt','liber-primus/analysis/round19/I1/driftbeam.py','liber-primus/analysis/round19/I2/adjudicate.py','liber-primus/analysis/round21/L1-seal-realmode-proxy/audit_catch.py','liber-primus/analysis/round21/L1-seal-realmode-proxy/catch_surface.json','liber-primus/analysis/round21/L1-seal-realmode-proxy/hitfn21_folds.py','liber-primus/analysis/round20/HITFN/hitfn20.py']
files=source_paths+[str(p.relative_to(c.ROOT)) for p in c.OUT.iterdir() if p.is_file() and p.name!='manifest.json']
manifest={'working_commit_as_assigned':'95e11e918ace77a51de4b612a48e74c298e67e58','inherited_baseline':'396001a9ce55e0e85ddef19e405afc6a13954588','python':platform.python_version(),'platform':platform.platform(),'sha256':{p:c.hashlib.sha256((c.ROOT/p).read_bytes()).hexdigest() for p in files}}
(c.OUT/'manifest.json').write_text(c.json.dumps(manifest,indent=2));print(c.json.dumps(summary,indent=2))
