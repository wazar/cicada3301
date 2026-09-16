"""Fixed arithmetic replay of P01 leaders and all retained alternatives."""
import json,random,time
import p01
s=p01.s;O=p01.O

def main():
 data,pages,queue,excluded=p01.setup();defs={x['id']:x for x in data['keys']};lookup={p['original_page']:p for p in pages};q=s.Score();result=[]
 for mode in ['real','null']:
  path=O/mode/'top20.json'
  if not path.exists():continue
  top=json.loads(path.read_text());n=0
  for row in top:
   cell=queue[int(row['id'].split(':')[-1])];assert all(row[k]==v for k,v in cell.items());c=lookup[cell['original_page']]['indices'].copy()
   if mode=='null':random.Random(330104+cell['original_page']).shuffle(c)
   key=p01.clues.key_for(cell,defs,len(c))
   for alt in row['alternatives']:
    lit=set(alt['literal_positions']);rebuilt=[];used=0
    for i,p in enumerate(alt['plain']):
     if i in lit:assert p==0;rebuilt.append(0)
     else:rebuilt.append((p-cell['sign']*key[used])%29);used+=1
    assert rebuilt==c and used==alt['used'];assert abs(q(alt['plain'])-alt['score'])<1e-10;n+=1
   assert row['plain']==row['alternatives'][0]['plain']
  result.append(dict(mode=mode,leaders=len(top),alternatives_checked=n))
 s.dump(O/'replay-results.json',result);print(json.dumps(result))
if __name__=='__main__':main()
