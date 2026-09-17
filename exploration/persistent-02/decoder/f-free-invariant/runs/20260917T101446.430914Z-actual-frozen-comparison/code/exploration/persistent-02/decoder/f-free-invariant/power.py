import json,pathlib,hashlib
from invariant import statistic,family
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 data=json.loads((O/'inputs.json').read_text());assert all(H(R/p)==h for p,h in data['source_pins'].items());out=O/'controls';out.mkdir(exist_ok=True);summary=[]
 for case in data['controls']:
  path=out/f'{case["index"]:02d}.json';assert not path.exists();rows=[[statistic(c,k) for k in (2,3)] for c in case['panels']];result=family(rows);truth=case['original']['truth'];k=case['original']['k'];planted=rows[0][k-2];num=den=0
  for run in planted['runs']:
   for j in range(k+1):
    p=truth[run['start']+j:run['stop']:k+1];num+=sum(x==y for i,x in enumerate(p) for z,y in enumerate(p) if i!=z);den+=len(p)*(len(p)-1)
  assert (num,den)==(planted['numerator'],planted['denominator']);record=dict(index=case['index'],construction=case['construction'],id=case['original']['id'],source=case['original']['source'],planted_k=k,planted_truth_pair_equality_verified=True,rows=rows,**result);path.write_text(json.dumps(record,separators=(',',':'))+'\n');summary.append({key:record[key] for key in ['index','construction','id','planted_k','rank_count_ge','rank_fraction']});print(json.dumps(summary[-1]),flush=True)
 gates={label:dict(cases=sum(r['construction']==label for r in summary),passing=sum(r['construction']==label and r['rank_count_ge']<=2 for r in summary)) for label in ('excluded','emitted')};result=dict(controls=summary,gate=gates,proceed_to_actual=all(r['passing']>=6 for r in gates.values()),criterion='atleast6/8rank<=2of20ineachconstruction; fixedbeforepower',actual_geometry=data['actual_geometry'],actual_scores_computed=False);(O/'power-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['gate']))
if __name__=='__main__':main()
