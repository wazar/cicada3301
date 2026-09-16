import argparse,gzip,json,math
import numpy as np
from search import ROOT,OWNER,dump,txt
from structural import align,metric
ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['r05','r06']);args=ap.parse_args();lane=OWNER/args.mode;s=json.loads((lane/'checkpoint.json').read_text())
if args.mode=='r05':
 rows=[];cribrows=[]
 for p in lane.glob('pair-*.json.gz'):
  with gzip.open(p,'rt') as f:
   for row in json.load(f):
    (cribrows if row[0].endswith(':crib') else rows).append(row)
 cribs=json.loads((lane/'cribs.json').read_text())['cribs'];pages={p['original_page']:p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages']};top=[]
 for row in sorted(cribrows,key=lambda r:r[3],reverse=True)[:20]:
  aa,bb,reset,off,_=row[0].split(':');a=pages[int(aa)];b=pages[int(bb)];pairs=align(a,b,int(off),reset);ai=pairs[0][0];bi=pairs[0][1];crib=cribs[row[1]];n=len(crib['indices']);dif=(np.array(b['indices'])[bi[:n]]-np.array(a['indices'])[ai[:n]])%29;pred=(np.array(crib['indices'])+row[2]*dif)%29;top.append({'id':row[0]+f':{row[1]}:{row[2]}','pages':[int(aa),int(bb)],'positions_a':ai[:n],'positions_b':bi[:n],'crib':crib,'crib_side':'A' if row[2]==1 else 'B','predicted_side':'B' if row[2]==1 else 'A','predicted_indices':pred.tolist(),'transliteration':txt(pred),'score':row[3],'matched_random_score':row[4],'reset':reset,'offset':int(off),'noncrib_prediction':None,'status':'UNREVIEWED'})
 dump(lane/'top_crib_implications.json',top)
 # Test same actual offset enumerator against a planted shared pad, and corrupted twin.
 rng=np.random.default_rng(777105);c=rng.integers(0,29,250).tolist();d=rng.integers(0,29,260).tolist();d[5:255]=c;fake=lambda x:{'indices':x,'lines':[{'rune_start':0,'rune_end':len(x)}]};control=[]
 for corrupt in [False,True]:
  bb=fake(rng.permutation(d).tolist() if corrupt else d);scores=[]
  for off in range(-16,17):
   pieces=align(fake(c),bb,off,'page');a,b=pieces[0];dif=(np.array(bb['indices'])[b]-np.array(c)[a])%29;scores.append((metric(dif)[0],off))
  scores.sort(reverse=True);control.append({'corrupted':corrupt,'truth_offset_rank':1+sum(v>next(v for v,o in scores if o==5) for v,o in scores),'top':scores[:5]})
 dump(lane/'controls.json',control);out={'pairs':s['cursor'],'relations':len(rows),'crib_implications':len(cribrows),'real_relation_max':max((r[2]-1/29)*math.sqrt(r[1]) for r in rows),'random_relation_max':max((r[5]-1/29)*math.sqrt(r[1]) for r in rows),'real_crib_max':max(r[3] for r in cribrows),'random_crib_max':max(r[4] for r in cribrows)}
else:
 real=[];random=[]
 for p in lane.glob('cell-*.json.gz'):
  with gzip.open(p,'rt') as f:r=json.load(f)
  (random if r['control'] else real).extend(v for _,v in r['scores'])
 out={'pages':s['cursor'],'real_candidates':len(real),'matched_random_candidates':len(random),'real_max':max(real),'random_max':max(random),'real_mean':float(np.mean(real)),'random_mean':float(np.mean(random))}
dump(lane/'summary.json',out);print(out)
