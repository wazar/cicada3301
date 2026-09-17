import pathlib,json,gzip
B=pathlib.Path('exploration/persistent-01/worker-s')
def load(name):return json.loads(gzip.decompress((B/name).read_bytes()))
controls=[];actual=[];cells=0;expanded=0;seconds=0;outputs=[]
for ix in range(7):
 main=load(f'S14-packet{ix}-main.json.gz');assert main['complete'] and len(main['cells'])==1944;cells+=len(main['cells']);expanded+=sum(r['diagnostics']['expanded'] for r in main['cells']);seconds+=main['seconds']
 if ix<4:controls.append({'packet':ix,'name':main['packet']['name'],'n':len(main['cipher']),**main['control'],'maximum':main['maximum']})
 else:
  nulls=[]
  for j in range(19):
   n=load(f'S14-packet{ix}-null{j:02}.json.gz');assert n['complete'] and len(n['cells'])==1944;cells+=len(n['cells']);expanded+=sum(r['diagnostics']['expanded'] for r in n['cells']);seconds+=n['seconds'];nulls.append({'j':j,'seed':n['seed'],'maximum':n['maximum'],'selected_id':n['global16'][0]['id']})
  actual.append({'packet':ix,'name':main['packet']['name'],'n':len(main['cipher']),'maximum':main['maximum'],'null_maxima':nulls,'tail':(1+sum(n['maximum']>=main['maximum'] for n in nulls))/20,'best_id':main['global16'][0]['id'],'best_by_exponent':[{'e':e,'cell':max((r for r in main['cells'] if r['e']==e),key=lambda r:r['score'])['id'],'score':max(r['score'] for r in main['cells'] if r['e']==e)} for e in [1,3,5,9,11,13,15,17,19,23,25,27]],'global16':main['global16']})
  outputs.append({'page':main['packet']['name'],'boundaries':main['ends'],'alternatives':[{'id':r['id'],'score':r['score'],'canonical_runes':r['plain'],'power_runes':r['power_plain'],'literal_positions':r['literal_positions'],'used':r['used']} for r in main['global16']]})
assert cells==124416
r={'controls':controls,'actual':actual,'nominal_cells':cells,'beam_nodes_expanded':expanded,'sum_search_seconds_including_checkpoint_archives':seconds,'family':'power-conjugate additive with optional literalF','scorer':'frozenP03 English-rune/boundary LM','beam':'width64, max over beam-retained paths, not exactFDP'};(B/'S14-summary.json').write_text(json.dumps(r,indent=2)+'\n');(B/'S14-actual-full-alternatives.json').write_text(json.dumps(outputs,indent=2)+'\n');print(json.dumps({**r,'actual':[{k:v for k,v in a.items() if k not in ['global16','best_by_exponent','null_maxima']} for a in actual]},indent=2))
