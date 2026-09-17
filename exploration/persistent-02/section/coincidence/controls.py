from pathlib import Path
from collections import Counter
import gzip,json,hashlib,datetime,sys,math
import core
O=Path(__file__).resolve().parent;R=O.parents[3];SOURCE=R/'exploration/persistent-02/section/A07-inputs.json'
def freeze():
 assert not (O/'inputs.json').exists();s=json.loads(SOURCE.read_text());out=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=str(SOURCE.relative_to(R)),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),grid=s['grid'],controls=s['controls'],objective='sum within-major-segment ordered equal-rune pairs',mask_cap=65536)
 (O/'inputs.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(controls=len(out['controls']),source=out['source'],source_sha256=out['sha256'])))
def truth_metrics(segments,truth,literals):
 metrics=[];dist=Counter({0:1});truth_total=0
 for s in segments:
  a,b=s['start'],s['stop'];rows=s['result']['rows'];wanted=[i-a for i in literals if a<=i<b];row=next(r for r in rows if r['literal_positions']==wanted);assert row['plain']==truth[a:b];v=row['score'];truth_total+=v;freq=Counter(r['score'] for r in rows);new=Counter()
  for left,m in dist.items():
   for right,n in freq.items():new[left+right]+=m*n
  dist=new;metrics.append(dict(start=a,stop=b,truth_score=v,maximum=s['result']['maximum'],strict_rank=1+sum(r['score']>v for r in rows),score_ties=sum(r['score']==v for r in rows),truth_best=v==s['result']['maximum'],truth_mask=row['mask']))
 return dict(segments=metrics,truth_total=truth_total,strict_rank=1+sum(count for v,count in dist.items() if v>truth_total),score_ties=dist[truth_total],legal_complete_masks=sum(dist.values()),truth_in_best=truth_total==max(dist))
def representative(segments):return sum((next(r['plain'] for r in s['result']['rows'] if r['mask']==s['result']['best_masks'][0]) for s in segments),[])
def run(ix):
 data=json.loads((O/'inputs.json').read_text());assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==data['sha256'];s=data['controls'][ix];grid=data['grid'][s['family']];cut=s['spans'][0][1];rows=[];folder=O/f'control{ix:02}-cells';folder.mkdir(exist_ok=True);pins=dict(input_sha256=hashlib.sha256((O/'inputs.json').read_bytes()).hexdigest(),core_sha256=hashlib.sha256((O/'core.py').read_bytes()).hexdigest(),index=ix)
 try:
  # Reject known oversized segments before allocating any full-grid output.
  for a,b in core.splits(len(s['cipher']),s['reset_before']):
   count=1<<s['cipher'][a:b].count(0)
   if count>65536:raise core.Unresolved(f'segment {a}:{b}: {count} masks exceed cap65536')
  for ci,cell in enumerate(grid):
   path=folder/f'cell{ci:02}.json.gz'
   if path.exists():
    with gzip.open(path,'rt') as f:record=json.load(f)
    assert record['pins']==pins and record['row']['cell_id']==cell['id'];row=record['row']
   else:
    row=core.gridcase(s['cipher'],s['reset_before'],cut,cell,s['family']=='periodic')
    with gzip.open(path,'wt') as f:json.dump(dict(pins=pins,row=row),f,separators=(',',':'))
   compact={k:row[k] for k in ['cell_id','full_maximum','prefix_maximum','continuation_maximum','prefix_tie_product','full_tie_product']};plain=representative(row['full']);compact.update(plain=plain,errors=sum(a!=b for a,b in zip(plain,s['truth'])),F_count=plain.count(0),future_states=len(row['continuations']),mask_enumerations=sum(q['result']['mask_count'] for q in row['full']))
   if cell['id']==s['plant']['id']:compact.update(full_truth=truth_metrics(row['full'],s['truth'],s['truth_literal_positions']),prefix_truth=truth_metrics(row['prefix'],s['truth'],s['truth_literal_positions']))
   rows.append(compact);del row
   if 'record' in locals():del record
   print(json.dumps(dict(index=ix,cell=ci,complete=True)),flush=True)
 except core.Unresolved as e:
  (O/f'control{ix:02}-summary.json').write_text(json.dumps(dict(outcome='UNRESOLVED',id=s['id'],error=str(e)))+'\n');print('UNRESOLVED',ix,str(e));return
 fullmax=max(r['full_maximum'] for r in rows);prefmax=max(r['prefix_maximum'] for r in rows);fullbest=[r for r in rows if r['full_maximum']==fullmax];prebest=[r for r in rows if r['prefix_maximum']==prefmax];true=next(r for r in rows if r['cell_id']==s['plant']['id']);tm=true['full_truth'];pm=true['prefix_truth'];render=[dict(cell_id=r['cell_id'],plain=r['plain'],errors=r['errors'],F_count=r['F_count'],tie_product=r['full_tie_product'],representative_only=True) for r in fullbest]
 summary=dict(outcome='COMPLETE',storage='streamed individual cell files; arithmetic unchanged',index=ix,id=s['id'],family=s['family'],true_cell=s['plant']['id'],grid_cells=len(rows),full_maximum=fullmax,prefix_maximum=prefmax,full_best_cells=[r['cell_id'] for r in fullbest],prefix_best_cells=[r['cell_id'] for r in prebest],true_key_full_rank=1+sum(r['full_maximum']>true['full_maximum'] for r in rows),true_key_prefix_rank=1+sum(r['prefix_maximum']>true['prefix_maximum'] for r in rows),known_key_full=tm,known_key_prefix=pm,truth_in_globally_best_full=s['plant']['id'] in [r['cell_id'] for r in fullbest] and tm['truth_in_best'],truth_in_prefix_frozen_set=s['plant']['id'] in [r['cell_id'] for r in prebest] and pm['truth_in_best'],prefix_tied_paths=sum(r['prefix_tie_product'] for r in prebest),prefix_future_states=sum(r['future_states'] for r in prebest),continuation_maximum_over_frozen_set=max(r['continuation_maximum'] for r in prebest),truth_F_count=s['truth'].count(0),full_representatives=render,mask_enumerations=sum(r['mask_enumerations'] for r in rows),peak_process_rss_bytes=__import__('resource').getrusage(__import__('resource').RUSAGE_SELF).ru_maxrss,scope='All per-segment masks and prefix tied states retained; representative plaintext does not claim unique recovery; conditional continuation maximum is over prefix-frozen ties')
 (O/f'control{ix:02}-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:summary[k] for k in ['index','id','true_key_full_rank','true_key_prefix_rank','truth_in_globally_best_full','truth_in_prefix_frozen_set','prefix_tied_paths','prefix_future_states','mask_enumerations']}),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='freeze':freeze()
 else:
  for i in map(int,sys.argv[1:]):run(i)
