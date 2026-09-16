import pathlib,json,gzip,hashlib,collections
D=pathlib.Path(__file__).resolve().parent/'p11';rows={};files=sorted((D/'search').glob('batch-*.jsonl'))
for p in files:
 for line in p.read_text().splitlines():
  if line:r=json.loads(line);assert r['ordinal'] not in rows;rows[r['ordinal']]=r
assert sorted(rows)==list(range(len(rows)))
TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split();models={};retained=[]
for model in ['english','rune']:
 models[model]={}
 for mode in ['real','null']:
  ranked=sorted(rows.values(),key=lambda r:r['scores'][mode][model],reverse=True);models[model][mode]=dict(maximum=ranked[0]['scores'][mode][model],leading_cell=ranked[0],top20_ordinals=[r['ordinal'] for r in ranked[:20]])
  for rank,r in enumerate(ranked[:20],1):
   fp=D/'search'/f'cell-{r["ordinal"]:05}.json.gz'
   with gzip.open(fp,'rt') as f:cell=json.load(f)
   m=next(z for z in cell['output'][mode]['models'] if z['model']==model);top=m['alternatives'][0];retained.append(dict(rank=rank,mode=mode,model=model,ordinal=r['ordinal'],cell=cell['cell'],source=str(fp),source_sha256=hashlib.sha256(fp.read_bytes()).hexdigest(),score=top['score'],english=top['english'],rune_lm=top['rune_lm'],statistics=top['statistics'],plain=top['plain'],transliteration=''.join(TOK[x] for x in top['plain']),literal_positions=top['literal_positions'],used=top['used'],boundary_consumption=top['boundary_consumption']))
 perpage=[]
 for pid in sorted(set(x['page'] for x in rows.values())):
  rr=[r for r in rows.values() if r['page']==pid];real=max(r['scores']['real'][model] for r in rr);null=max(r['scores']['null'][model] for r in rr);perpage.append(dict(page=pid,key_cells=len(rr),real_max=real,null_max=null,difference=real-null))
 models[model]['perpage']=perpage
summary=dict(cells=len(rows),total=11520,complete=len(rows)==11520,model_beam_searches=len(rows)*4,real_keypage_cells=len(rows),matched_null_keypage_cells=len(rows),models=models,claim='EXPLORATORY_RANKING_ONLY; one full matched null, no significance from maxima; no plaintext or key claim')
(D/'summary.json').write_text(json.dumps(summary,indent=2));(D/'leaders.json').write_text(json.dumps(retained,indent=2));print(json.dumps({'cells':len(rows),'maxima':{m:{k:v[k]['maximum'] for k in ['real','null']} for m,v in models.items()}))
