import pathlib,json,gzip,hashlib,shutil,tarfile
D=pathlib.Path(__file__).resolve().parent/'p11';ROOT=D.parents[3];O=D/'publication';O.mkdir(exist_ok=True)
cp=json.loads((D/'search/checkpoint.json').read_text());assert cp['cursor']==cp['total']==11520
summary=json.loads((D/'summary.json').read_text());assert summary['complete'];manifest=[];leaders={};nrows=0;alternative_counts={'real':{'english':0,'rune':0},'null':{'english':0,'rune':0}}
with gzip.open(O/'all-cell-selected-statistics.jsonl.gz','wt') as out:
 for ix in range(11520):
  fp=D/'search'/f'cell-{ix:05}.json.gz';b=fp.read_bytes();manifest.append(dict(path=str(fp.relative_to(ROOT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
  with gzip.open(fp,'rt') as f:r=json.load(f)
  assert r['ordinal']==ix;row=dict(ordinal=ix,**r['cell'],outputs={})
  for mode in ['real','null']:
   row['outputs'][mode]={}
   for m in r['output'][mode]['models']:
    a=m['alternatives'][0];model=m['model'];alternative_counts[mode][model]+=len(m['alternatives']);row['outputs'][mode][model]=dict(score=a['score'],english=a['english'],rune_lm=a['rune_lm'],statistics=a['statistics'],runes_sha256=hashlib.sha256(bytes(a['plain'])).hexdigest(),n=len(a['plain']),used=a['used'],literal_count=len(a['literal_positions']),alternatives=len(m['alternatives']),reencryption_all=all(z['reencryption'] for z in m['alternatives']),diagnostics=m['diagnostics'])
    k=(mode,model,r['cell']['page'])
    if k not in leaders or a['score']>leaders[k]['score']:leaders[k]=dict(ordinal=ix,score=a['score'])
  out.write(json.dumps(row)+'\n');nrows+=1
selected=set(z['ordinal'] for z in leaders.values())
for model in ['english','rune']:
 for mode in ['real','null']:selected.update(summary['models'][model][mode]['top20_ordinals'])
C=O/'retained-candidate-cells';C.mkdir(exist_ok=True)
for ix in sorted(selected):shutil.copyfile(D/'search'/f'cell-{ix:05}.json.gz',C/f'cell-{ix:05}.json.gz')
with tarfile.open(O/'full-controls.tar.gz','w:gz') as tar:tar.add(D/'controls',arcname='controls')
for name in ['summary.json','leaders.json','manifest.json','pilot-source-manifest.json','phi.npz','queue.json']:shutil.copyfile(D/name,O/name)
shutil.copyfile(D/'search/checkpoint.json',O/'checkpoint.json')
shutil.copyfile(D.parent/'P11-CARD.md',O/'P11-CARD.md')
paths=['exploration/persistent-01/worker-i/p11.py','exploration/persistent-01/worker-i/summarize_p11.py','exploration/persistent-01/worker-i/publish_p11.py','exploration/overnight-01/worker-a/search.py','exploration/persistent-01/worker-c/p03_frozen.py','liber-primus/data/english_quadgrams.txt']
for r in json.loads((D/'manifest.json').read_text())['frozen_lm_sources']:paths.append(r['path'])
codehash=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),bytes=(ROOT/p).stat().st_size) for p in paths]
metadata=dict(raw_shards_local_only=True,retained_alternative_counts=alternative_counts,raw_bytes=sum(x['bytes'] for x in manifest),raw_shards=manifest,cursor=cp,code_and_scorer_hashes=codehash,selected_statistics_rows=nrows,selected_statistics_scope='All11520key/page cells, bothreal/null and bothEnglish/rune-model-selected paths. Structuralmetrics describe thoseselectedpaths; noindependentstructuralsearch.',retained_full_candidate_cells=len(selected),retained_cell_ordinals=sorted(selected),per_page_model_leaders=[dict(mode=k[0],model=k[1],page=k[2],**v) for k,v in leaders.items()],controls='full-controls.tar.gz contains all256key outputs/model/fixture, allretained16alternatives, rawfixtureplain/cipher and rankings',raw_retention='Allraw11520cellshards remain unchanged locally; only selectedfullcells are copiedinto publication. No claimallrawalternatives published.',resume='.venv/bin/python exploration/persistent-01/worker-i/p11.py search --limit 11520 --seconds 780 (completedcursor; nofurthercells)')
(O/'raw-retention-manifest.json').write_text(json.dumps(metadata,indent=2));print(json.dumps({k:metadata[k] for k in ['raw_bytes','selected_statistics_rows','retained_full_candidate_cells']}))
