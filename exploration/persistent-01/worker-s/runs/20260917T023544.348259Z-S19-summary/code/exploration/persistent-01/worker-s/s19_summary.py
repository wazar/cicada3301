import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,gzip,collections,math,random,re
import numpy as np
B=Path('exploration/persistent-01/worker-s');O=B/'S19';M=Path('exploration/persistent-01/coordinator/Q05-latin-clean');meta=json.loads((O/'manifest.json').read_text());packets=json.loads((O/'packets.json').read_text());train=json.loads(gzip.decompress((M/'train-maps.json.gz').read_bytes()));raw=(M/'pg218.txt').read_bytes().decode('utf-8-sig');table='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split();lookup={s:i for i,s in enumerate(table)};lookup.update(V=1,K=5,Z=15,Q=5)
def parse(text,offset):
 ids=[];spans=[];i=0;text=text.upper()
 while i<len(text):
  two=text[i:i+2];take=2 if two in lookup else 1;token=text[i:i+take];ids.append(lookup[token]);spans.append([offset+i,offset+i+take]);i+=take
 return ids,spans
flat=[]
for w in train['words']:
 assert raw[w['start']:w['end']]==w['text'];ids,spans=parse(w['text'],w['start']);assert ids==w['runes'] and spans==w['rune_char_spans'];flat+=ids
saved=[{tuple(r['key']):r['count'] for r in a} for a in json.loads(gzip.decompress((O/'counts.json.gz').read_bytes()))]
c=[collections.Counter((x,) for x in flat),collections.Counter(zip([29]+flat,flat)),collections.Counter(zip([29,29]+flat,[29]+flat,flat))];assert c==saved;t=[]
for cc in c:
 sums=collections.Counter()
 for key,v in cc.items():sums[key[:-1]]+=v
 t.append(sums)
def logprob(a,b,x):
 v=(c[0][(x,)]+.5)/(len(flat)+14.5)
 for n,alpha in [(1,8),(2,5)]:ctx=(a,b)[-n:];v=(c[n][ctx+(x,)]+alpha*v)/(t[n][ctx]+alpha)
 return math.log(v)
model=np.fromfile(O/'model-table.bin',dtype='<f8').reshape(30,30,30);maxmodelerr=0
for a in range(30):
 for b in range(30):
  for x in range(29):maxmodelerr=max(maxmodelerr,abs(model[a,b,x]-logprob(a,b,x)))
assert maxmodelerr<1e-12 and np.isnan(model[:,:,29]).all()
rawv=(M/'pg227.txt').read_bytes().decode('utf-8-sig')
for p,book in zip(packets[:4],['I','IV','VII','X']):
 h=re.search(r'^  LIBER '+book+r'\s*$',rawv,re.M);after=re.search(r'^  LIBER [IVX]+\s*$',rawv[h.end():],re.M);limit=h.end()+after.start() if after else rawv.index('*** END OF THE PROJECT GUTENBERG');ids=[];spans=[]
 for m in re.finditer('[A-Za-z]+',rawv[h.end():limit]):
  rr,ss=parse(m.group(),h.end()+m.start());ids+=rr;spans+=ss
  if len(ids)>=2355:break
 assert ids[:2355]==[x for a in p['truth'] for x in a];assert spans[:2355]==[m['source_char_span'] for m in p['source_maps']];assert [[p['truth_map'][x] for x in a] for a in p['chunks']]==p['truth']

def scores(chunks):
 out=[]
 for chunk in chunks:
  a=b=29;s=0
  for x in chunk:s+=logprob(a,b,x);a,b=b,x
  out.append(s)
 return out
controls=[];rows=[];outputs=[];maxerr=0;evals=0;accepted=0;seconds=0
paths=[O/f'control{i}.json' for i in range(4)]+[O/'actual.json']+[O/f'null{j:02}.json' for j in range(19)]
for path in paths:
 r=json.loads(path.read_text());assert r['complete'] and r['exit']==0;assert len(r['restarts'])==24;seconds+=r['seconds'];chunks=r['cipher_chunks'];assert list(map(len,chunks))==meta['chunk_sizes']
 if r['j'] is not None:
  j=r['j'];data=json.loads((O/f'null{j:02}.input.json').read_text());rng=random.Random(1709192619+j);assert data['seed']==1709192619+j
  for original,got,perm in zip(packets[4]['chunks'],chunks,data['permutations']):
   pp=list(range(len(original)));rng.shuffle(pp);assert pp==perm and got==[original[k] for k in pp] and sorted(got)==sorted(original)
 else:assert chunks==packets[r['packet']]['chunks']
 for row in r['restarts']:
  assert sorted(row['map'])==list(range(29));inv=[row['map'].index(i) for i in range(29)];assert [[inv[x] for x in a] for a in row['plain_chunks']]==chunks;ss=scores(row['plain_chunks']);err=abs(sum(ss)-row['score']);maxerr=max(maxerr,err);assert err<1e-7;evals+=row['evaluations'];accepted+=row['accepted_sa']
  if path.name=='actual.json':outputs.append({'restart':row['restart'],'score':row['score'],'map':row['map'],'per_page_scores':ss,'page_ids':meta['page_ids'],'canonical_chunks':row['plain_chunks'],'unsegmented_page_transliterations':[''.join(table[x] for x in a) for a in row['plain_chunks']]})
 best=max(r['restarts'],key=lambda r:r['score']);assert r['best_restart']==best['restart'] and r['maximum']==best['score'];rows.append({'name':path.stem,'maximum':r['maximum'],'mean_rune_score':r['mean_rune_score']})
 if r['packet']<4:controls.append({'name':packets[r['packet']]['name'],**r['control'],'generated_filler_runes':packets[r['packet']]['generated_total_filler_runes'],'used_labels':len(packets[r['packet']]['used_labels'])})
actual=next(r for r in rows if r['name']=='actual');nulls=[r['maximum'] for r in rows if r['name'].startswith('null')];tail=(1+sum(s>=actual['maximum'] for s in nulls))/20;outputs.sort(key=lambda r:r['score'],reverse=True)
summary={'controls':controls,'actual':actual,'null_maxima':nulls,'exceedances':sum(s>=actual['maximum'] for s in nulls),'tail':tail,'searches':len(rows),'restarts':len(rows)*24,'nominal_sa_proposals':len(rows)*24*30000,'total_swap_evaluations':evals,'accepted_sa':accepted,'engine_seconds':seconds,'model_cells_checked':30*30*29,'max_model_error':maxmodelerr,'max_independent_full_score_error':maxerr,'source_train_runes':len(flat),'actual_observed_length_labels':len(packets[4]['used_labels']),'actual_filler_runes':packets[4]['actual_total_filler_runes'],'chunk_sizes':meta['chunk_sizes']};(O/'summary.json').write_text(json.dumps(summary,indent=2));(O/'actual-full-alternatives.json').write_text(json.dumps(outputs,indent=2));(O/'selected-output.txt').write_text('\n'.join(f'page {p}: {s}' for p,s in zip(outputs[0]['page_ids'],outputs[0]['unsegmented_page_transliterations']))+'\n');print(json.dumps({**summary,'controls':[{k:v for k,v in c.items() if k not in ['errors','all_retained_error_counts']} for c in controls]},indent=2))
