import json,pathlib
O=pathlib.Path(__file__).parent;D=json.loads((O.parents[2]/'audit/parallel-01/inputs/dataset.json').read_text());P={p['original_page']:p for p in D['pages']if p['original_page']in[3,7,17]};M=json.loads((O/'g06-results.json').read_text());out=[]
for page,p in P.items():
 gaps=[]
 for line in p['lines']:
  offset=line['rune_start']
  for c in line['raw']:
   if '\u16a0'<=c<='\u16ff':offset+=1
   elif c=='.':gaps.append({'line':line['source_line'],'rune_gap':offset,'preceding_source_char':p['source_char_positions'][offset-1]if offset else None})
 dots=[g for g in M['pages'][str(page)]['original-130'] if g['count']>1]
 # frozen actual image y rows from observed component centers; sorted row then x
 centers={3:[730+188.25*i for i in range(6)]+[2158+188.25*i for i in range(5)],7:[729]+[954+188.25*i for i in range(8)]+[2515],17:[730+188.25*i for i in range(12)]}[page]
 for g in dots:g['line']=min(range(len(centers)),key=lambda i:abs(g['center'][1]-centers[i]))
 dots.sort(key=lambda g:(g['line'],g['center'][0]))
 for line in range(len(centers)):
  gs=[g for g in dots if g['line']==line];ts=[t for t in gaps if t['line']==line]
  if page==7 and line==9:
   first=gs.pop(0);out.append({'page':page,'source_marker':'structural &; no period before first rune','rune_gap':194,'image':first})
  assert len(gs)==len(ts),(page,line,len(gs),len(ts))
  out +=[{'page':page,'source_marker':'.',**t,'image':g}for t,g in zip(ts,gs)]
(O/'g06-source-gap-map.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{'page':x['page'],'rune_gap':x['rune_gap'],'source_marker':x['source_marker'],'dot_count':x['image']['count'],'center':x['image']['center']}for x in out],indent=2))
