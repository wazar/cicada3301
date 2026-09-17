import pathlib,json,sys
H=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent));from common import guard,digest,O

def main():
 guard();rows=[]
 for case in range(5):
  s=json.loads((H/f'summary-case{case}.json').read_text());rr=[]
  for r in s['results']:
   a=r['panels'][0];rr.append(dict(model=r['model'],mode=r['mode'],fit=a['fit'],continuation=a['continuation'],fit_rank=r['fit_rank_count_ge'],fit_interval=[r['fit_rank_lower'],r['fit_rank_upper']],continuation_rank=r['continuation_rank_count_ge'],selected_k=a['selected_k'],truth_errors=a['truth_errors'],best_null_fit=max(p['fit'] for p in r['panels'][1:]),best_null_continuation=max(p['continuation'] for p in r['panels'][1:])))
  rows.append(dict(case=case,id=s['case_id'],cells=s['cells'],certified=s['certified'],reused=s['reused'],maximum_bound_gap=s['maximum_bound_gap'],results=rr))
 checked=0
 for src in sorted((O/'actual').glob('00-*.json')):
  original=json.loads(src.read_text());new=json.loads((H/'cells/case0'/src.name).read_text());assert all(new[k]==v for k,v in original.items());assert new['reused_original_sha256']==digest(src);checked+=1
 assert checked==16
 result=dict(cases=rows,reused_original_cells_verified=checked,new_optimizations=sum(r['cells']-r['reused'] for r in rows),certified=sum(r['certified'] for r in rows),all_control_selections_exact=all(r['truth_errors']==0 for c in rows[1:] for r in c['results']));path=H/'final-summary.json';assert not path.exists();path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
