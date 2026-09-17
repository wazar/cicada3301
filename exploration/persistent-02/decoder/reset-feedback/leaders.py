from common import *
import json
sys.path.insert(0,str(R/'liber-primus/src'));from lp.gematria import indices_to_runes,runes_to_translit
def main():
 s=json.loads((O/'summary.json').read_text());ends=set(json.loads((O/'inputs.json').read_text())['actual']['ends']);out=[]
 for row in s['results']:
  a=row['panels'][0];words=[];buf=[]
  for i,x in enumerate(a['plaintext']):
   buf.append(x)
   if i in ends:words.append(runes_to_translit(indices_to_runes(buf)));buf=[]
  if buf:words.append(runes_to_translit(indices_to_runes(buf)))
  out.append(dict(model=row['model'],mode=row['mode'],k=a['selected_k'],seed=a['seed'],fit=a['fit'],continuation=a['continuation'],full=a['full'],best_null_fit=max(x['fit'] for x in row['panels'][1:]),best_null_continuation=max(x['continuation'] for x in row['panels'][1:]),text=' '.join(words)))
 dump('leaders.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
