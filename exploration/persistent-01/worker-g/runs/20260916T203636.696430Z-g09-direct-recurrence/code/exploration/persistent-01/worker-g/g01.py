import json,hashlib,pathlib,random,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).parent
D=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text());P={p['original_page']:p for p in D['pages'] if p['original_page'] in [3,7,17]}
rng=random.Random(310717)
def routes(rows):
 out={}
 for align in ['left','right']:
  m=max(map(len,rows));grid=[([None]*(m-len(r))+r if align=='right' else r+[None]*(m-len(r))) for r in rows]
  for snake in [False,True]:
   out[align+('_snake' if snake else '_columns')]=[v for j in range(m) for v in ([r[j] for r in grid][::(-1 if snake and j%2 else 1)]) if v is not None]
 out['boustrophedon']=[v for i,r in enumerate(rows) for v in r[::(-1 if i%2 else 1)]]
 out['mirror_row_pairs']=[v for i in range((len(rows)+1)//2) for r in ([rows[i],rows[-1-i][::-1]] if i!=len(rows)-1-i else [rows[i]]) for v in r]
 return out
def repeats(x):return sum(a==b for a,b in zip(x,x[1:]))
result={'seed':310717,'null_replicates':2000,'pages':{},'method':'six predeclared source-index routes; row cyclic shifts preserve content and all cyclic within-row adjacencies; no glyph x-coordinate claim'}
# planted route inverse control: assign nonrepeating values along every proposed route then recover
controls={}
for name,order in routes([list(range(0,11)),list(range(11,21)),list(range(21,34))]).items():
 planted={v:i%29 for i,v in enumerate(order)}
 controls[name]=repeats([planted[v] for v in order])==0
assert all(controls.values());result['controls']=controls
for page,p in P.items():
 rows=[r['indices'] for r in p['lines'] if r['indices']];mapped=[];k=0
 for line,r in enumerate(rows):mapped.append(list(range(k,k+len(r))));k+=len(r)
 rr=routes(rows);counts={n:repeats(v) for n,v in rr.items()};null={n:[] for n in rr}
 for b in range(2000):
  shifted=[]
  for r in rows:
   s=rng.randrange(len(r));shifted.append(r[s:]+r[:s])
  for n,v in routes(shifted).items():null[n].append(repeats(v))
 result['pages'][page]={'n':k,'row_lengths':list(map(len,rows)),'ordinary_repeats':repeats(p['indices']),'routes':{n:{'repeats':counts[n],'lower_tail':(1+sum(v<=counts[n] for v in null[n]))/2001,'null_counts':null[n],'output':rr[n],'source_rune_offsets':routes(mapped)[n],'source_char_positions':[p['source_char_positions'][i] for i in routes(mapped)[n]]}for n in rr}}
(O/'g01-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'controls':controls,'pages':{p:{'ordinary':v['ordinary_repeats'],'routes':{n:{k:x[k] for k in ['repeats','lower_tail']}for n,x in v['routes'].items()}} for p,v in result['pages'].items()}},indent=2))
