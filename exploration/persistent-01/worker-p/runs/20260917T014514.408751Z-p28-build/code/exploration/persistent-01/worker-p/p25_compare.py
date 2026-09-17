from pathlib import Path
import json,gzip,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'exploration/persistent-01/worker-p';OLD=BASE/'P25';NEW=BASE/'P25-clean'
def load(f):
 with gzip.open(f,'rt') as z:return json.load(z)
TRANS=[r['transliteration'] for r in json.loads((ROOT/'KNOWLEDGE.json').read_text())['gematria_primus']['table']]
rows=[];cellrows=[];scores_changed=0;winners_changed=0;winner_path_changed=0;cellpath_changed=0;maxdelta=0
for ix in range(7):
 assert json.loads((OLD/f'packet-{ix}.json').read_text())==json.loads((NEW/f'packet-{ix}.json').read_text())
 for ni in [-1]+list(range(19)):
  name=f'packet-{ix}-'+('main' if ni<0 else f'null-{ni:02}')
  a=load(OLD/(name+'.json.gz'));b=load(NEW/(name+'.json.gz'));assert a['cipher']==b['cipher'] and a['ends']==b['ends'] and a['null_seed']==b['null_seed']
  oldranks={x['id']:1+sum(z['top_score']>x['top_score'] for z in a['cells']) for x in a['cells']}
  newranks={x['id']:1+sum(z['top_score']>x['top_score'] for z in b['cells']) for x in b['cells']}
  for x,y in zip(a['cells'],b['cells']):
   assert x['id']==y['id'];delta=y['top_score']-x['top_score'];maxdelta=max(maxdelta,abs(delta));scores_changed+=delta!=0
   def paths(z):return {(tuple(v['plain']),tuple(v['literal_positions'])) for v in z['alternatives']}
   changed=paths(x)!=paths(y);cellpath_changed+=changed
   cellrows.append(dict(packet=name,id=x['id'],old_score=x['top_score'],clean_score=y['top_score'],delta=delta,old_rank=oldranks[x['id']],clean_rank=newranks[y['id']],pathset_changed=changed,retained_path_intersection=len(paths(x)&paths(y))))
  x=a['global16'][0];y=b['global16'][0];wc=x['id']!=y['id'];pc=(x['plain'],x['literal_positions'])!=(y['plain'],y['literal_positions']);winners_changed+=wc;winner_path_changed+=pc
  rows.append(dict(packet=name,old_maximum=a['maximum'],clean_maximum=b['maximum'],old_winner=x['id'],clean_winner=y['id'],winner_changed=wc,winner_path_changed=pc,old_control=a.get('control'),clean_control=b.get('control')))
  if ni<0 and ix>=4:
   text=[]
   for j,z in enumerate(b['global16']):
    output=''.join(TRANS[v]+(' ' if k in b['ends'] else '') for k,v in enumerate(z['plain']))
    text.append(str(j+1)+' '+z['id']+' score='+str(z['score'])+' aliases='+repr(z['aliases'])+'\n'+output)
   (NEW/f'packet-{ix}-full-top16.txt').write_text('\n\n'.join(text)+'\n')
with gzip.open(NEW/'all-cell-comparison.json.gz','wt') as f:json.dump(cellrows,f,separators=(',',':'))
with gzip.open(NEW/'all-packet-comparison.json.gz','wt') as f:json.dump(rows,f,separators=(',',':'))
summary=dict(packets=len(rows),cells=len(cellrows),identical_inputs=True,changed_cell_scores=scores_changed,maximum_absolute_topscore_change=maxdelta,changed_cell_pathsets=cellpath_changed,changed_winner_ids=winners_changed,changed_winner_paths=winner_path_changed,packet_summary=[])
for ix in range(7):
 a=json.loads((OLD/f'packet-{ix}-summary.json').read_text());b=json.loads((NEW/f'packet-{ix}-summary.json').read_text())
 r=next(r for r in rows if r['packet']==f'packet-{ix}-main')
 summary['packet_summary'].append(dict(packet=ix,name=a['name'],old_maximum=a['maximum'],clean_maximum=b['maximum'],old_tail=a['tail'],clean_tail=b['tail'],old_winner=r['old_winner'],clean_winner=r['clean_winner'],winner_path_changed=r['winner_path_changed'],old_control=r['old_control'],clean_control=r['clean_control']))
(NEW/'comparison-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='packet_summary'}))
for r in summary['packet_summary']:print(json.dumps({k:v for k,v in r.items() if k not in ['old_control','clean_control']}))
