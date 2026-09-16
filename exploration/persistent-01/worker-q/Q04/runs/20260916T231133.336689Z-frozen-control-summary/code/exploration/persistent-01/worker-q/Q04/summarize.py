import pathlib,json,gzip,hashlib,statistics
R=pathlib.Path(__file__).parent;rows=[]
for kind in ['held','model']:
 for group in range(4):
  p=R/f'{kind}-{group}-result.json.gz';r=json.load(gzip.open(p,'rt'));s=r['summary'].copy();packet=r['packet'];plain=packet['plain'];cipher=packet['cipher'];cut=packet['cut'];used=set(cipher)
  oracle=[]
  for a in r['alternatives']:
   oracle.append({'restart':a['restart'],'accuracy':sum(x==y for x,y in zip(a['decoded'],plain))/len(plain),'suffix_accuracy':sum(a['decoded'][i]==plain[i] for i in range(cut,len(plain)))/(len(plain)-cut),'observable_map_accuracy':sum(a['map'][v]==packet['truth'][v] for v in used)/len(used),'exact_full_map':a['map']==packet['truth']})
  s['oracle_among8_max_suffix_accuracy']=max(x['suffix_accuracy'] for x in oracle);s['oracle_among8_max_plaintext_accuracy']=max(x['accuracy'] for x in oracle);s['any_exact_map']=any(x['exact_full_map'] for x in oracle);s['oracle_metrics']=oracle
  if kind=='held':s['original_P05_accuracy']=packet['old_accuracy'];s['original_P05_suffix_accuracy']=packet['old_suffix_accuracy']
  rows.append(s)
summary={'status':'COMPLETE_NO_REAL_SEARCH','reason':'Neither held-source nor model-generated controls show reliable unknown-map recovery under frozen finite procedure.','packets':rows,'counts':{k:sum(x[k] for x in rows) for k in ['nominal_proposals','valid_proposals','accepted_proposals']},'median_suffix':{kind:statistics.median(x['suffix_accuracy'] for x in rows if x['label'].startswith(kind)) for kind in ['held','model']},'exact_maps_among64':sum(x['exact_full_map'] for row in rows for x in row['oracle_metrics'])};(R/'results.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='packets'}));print([(x['label'],x['suffix_accuracy'],x['oracle_among8_max_suffix_accuracy'],x.get('original_P05_suffix_accuracy')) for x in rows])
files=[]
for p in sorted(R.iterdir()):
 if p.is_file() and p.name not in ['search','publication-manifest.json']:files.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'publication-manifest.json').write_text(json.dumps(files,indent=2))
