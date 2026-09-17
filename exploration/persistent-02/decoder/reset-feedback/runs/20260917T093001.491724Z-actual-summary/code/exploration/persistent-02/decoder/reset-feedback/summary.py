import json
from common import *
def select(rows):
 return sorted(rows,key=lambda r:(-r['maximum_normalized'],r['k'],r['alternatives'][0]['offset']))[0]
def main():
 rows=[json.loads(p.read_text()) for p in sorted((O/'actual').glob('*.json'))];assert len(rows)==320;panels=[]
 for model in ('p03','complementary'):
  for mode in ('full','prefix'):
   results=[]
   for panel in range(20):
    rr=[r for r in rows if r['model']==model and r['mode']==mode and r['panel']==panel];assert len(rr)==4;r=select(rr);a=r['alternatives'][0];results.append(dict(panel=panel,selected_k=r['k'],seed=a['seed'],plaintext=a['plaintext'],fit=a['fit_score'],upper=max(z['upper_normalized'] for z in rr),continuation=a['continuation_score'],full=a['full_score'],all_certified=all(z['certified_within_1e_10'] for z in rr)))
   actual=results[0];null=results[1:];panels.append(dict(model=model,mode=mode,panels=results,actual_fit_rank_lower=1+sum(r['fit']>actual['upper']+1e-12 for r in null),actual_fit_rank_upper=1+sum(r['upper']>=actual['fit']-1e-12 for r in null),actual_fit_rank_count_ge=1+sum(r['fit']>=actual['fit']-1e-12 for r in null),actual_continuation_rank_count_ge=1+sum(r['continuation']>=actual['continuation']-1e-12 for r in null) if mode=='prefix' else None))
 result=dict(cells=len(rows),certified=sum(r['certified_within_1e_10'] for r in rows),maximum_bound_gap=max(r['gap'] for r in rows),results=panels,qualification='Exploratory20-panel conditional comparison, not global probability. Two fixed models reported separately. Encountered alternatives not globalnbest. Prefix continuation uses prefix-selectedk/seed only; if capped, procedure rather than exactglobal selection. Bound rank interval includes ties conservatively. No literalF; sharedseedreset sumfeedback only.');dump('summary.json',result)
 print(json.dumps(dict(cells=len(rows),certified=result['certified'],panels=[{k:v for k,v in x.items() if k!='panels'} for x in panels])))
if __name__=='__main__':main()
