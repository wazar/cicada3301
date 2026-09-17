import json,pathlib,sys,argparse
H=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent))
from common import guard
from summary import select

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case',type=int,required=True,choices=range(5));args=ap.parse_args();guard();rows=[json.loads(p.read_text()) for p in sorted((H/'cells'/f'case{args.case}').glob('*.json'))];assert len(rows)==320;out=[]
 for name in ('p03','complementary'):
  for mode in ('full','prefix'):
   panels=[]
   for panel in range(20):
    rr=[r for r in rows if r['model']==name and r['mode']==mode and r['panel']==panel];assert len(rr)==4;r=select(rr);a=r['alternatives'][0];panels.append(dict(panel=panel,selected_k=r['k'],seed=a['seed'],plaintext=a['plaintext'],fit=a['fit_score'],upper=max(z['upper_normalized'] for z in rr),continuation=a['continuation_score'],full=a['full_score'],all_certified=all(z['certified_within_1e_10'] for z in rr),truth_errors=a.get('truth_errors')))
   actual=panels[0];null=panels[1:];out.append(dict(model=name,mode=mode,panels=panels,fit_rank_lower=1+sum(r['fit']>actual['upper']+1e-12 for r in null),fit_rank_upper=1+sum(r['upper']>=actual['fit']-1e-12 for r in null),fit_rank_count_ge=1+sum(r['fit']>=actual['fit']-1e-12 for r in null),continuation_rank_count_ge=1+sum(r['continuation']>=actual['continuation']-1e-12 for r in null) if mode=='prefix' else None))
 result=dict(case_index=args.case,case_id=rows[0]['case_id'],cells=len(rows),reused=sum('reused_original_path' in r for r in rows),certified=sum(r['certified_within_1e_10'] for r in rows),maximum_bound_gap=max(r['gap'] for r in rows),results=out,qualification='Single frozen histogram-conditioned sensitivity, no extra draws. Retrospective to R01. Ranks conservative with ties; numerical bounds are float64/tolerance. Prefix selection uses fit only. No plaintext inference from coarse ranks.');path=H/f'summary-case{args.case}.json';assert not path.exists();path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({**{k:v for k,v in result.items() if k!='results'},'ranks':[{k:v for k,v in r.items() if k!='panels'} for r in out]}))
if __name__=='__main__':main()
