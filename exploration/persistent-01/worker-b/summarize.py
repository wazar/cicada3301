import pathlib,json,gzip,collections
OUT=pathlib.Path(__file__).resolve().parent

def read(name):return json.loads((OUT/name).read_text())
def rows(name):return {x['id']:x for x in (json.loads(line) for line in gzip.open(OUT/name,'rt'))}
def main():
 summary={}
 for typ in ('real','null92001'):
  old={**rows('0-100-'+typ+'-scores.jsonl.gz'),**rows('100-29948-'+typ+'-scores.jsonl.gz')};new=rows('repaired-0-30048-'+typ+'-scores.jsonl.gz');changes=[]
  for idx,x in old.items():
   y=new[idx];assert y['score'] is not None
   if x['score'] is not None and abs(y['score']-x['score'])>1e-10:changes.append(dict(id=idx,before=x['score'],after=y['score'],difference=y['score']-x['score']))
  result=read('repaired-0-30048-'+typ+'-results.json')
  summary[typ]=dict(attempted=len(new),baseline_no_path=sum(x['score'] is None for x in old.values()),changed_successes=len(changes),improvements=sum(x['difference']>0 for x in changes),deteriorations=sum(x['difference']<0 for x in changes),largest_changes=sorted(changes,key=lambda x:abs(x['difference']),reverse=True)[:20],best=result['top'][0],seconds=result['seconds'])
 (OUT/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
 print({k:{a:v for a,v in z.items() if a not in ('best','largest_changes')} for k,z in summary.items()})
if __name__=='__main__':main()
