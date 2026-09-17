import json,gzip
from compare import O
summary={}
for model,folder in [('p03','section'),('complementary','complementary-section')]:
 actual=[json.loads(gzip.decompress(p.read_bytes())) for p in (O/folder).glob('*.gz')];nulls=[json.loads(gzip.decompress(p.read_bytes())) for p in sorted((O/'null-calibration').glob(model+'-*.gz'))];r={}
 assert len(actual)==84 and len(nulls)==19
 for policy in ['body','whole','both']:
  best=max(x['exact'][0]['score'] for x in actual if policy=='both' or x['case']['policy']==policy);nv=[max(x['exact']['score'] for x in n['rows'] if policy=='both' or x['policy']==policy) for n in nulls];r[policy]=dict(actual=best,null_maxima=nv,exceedances=sum(v>=best for v in nv),tail=(1+sum(v>=best for v in nv))/20)
 summary[model]=r
(O/'null-calibration-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
