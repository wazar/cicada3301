import pathlib,json
O=pathlib.Path(__file__).resolve().parent;p=json.loads((O/'section-packet.json').read_text());manual={0:[1,1,1,0,0,0,0,1,1,0,0],1:[0,0,0,1,1,0,0,0,0,0,0],2:[1,0,0,0,0,0,0,0]};abc=p['alphabet'];rows=[]
for page in p['pages']:
 pid=page['original_page']
 for i,(a,b) in enumerate(zip(page['lines'],page['lines'][1:])):
  ia=max(j for j,x in enumerate(a['raw']) if x in abc);ib=min(j for j,x in enumerate(b['raw']) if x in abc);gap=a['raw'][ia+1:]+b['raw'][:ib];expected=any(not x.isspace() for x in gap);seen=bool(manual[pid][i]);assert seen==expected,(pid,i,gap)
  rows.append(dict(page=pid,previous_line=i,next_line=i+1,previous_rune=a['rune_end']-1,next_rune=b['rune_start'],raw_gap=gap,visually_seen_delimiter=seen,source_agrees=True))
(O/'inspection'/'remaining-joins'/'checks.json').write_text(json.dumps(dict(method='Native edge sheets directly viewed; manual delimiter vector compared only after visual inspection. End/start rune shapes also compared to source; no all-glyph reread.',rows=rows,explicit_joins=sum(x['visually_seen_delimiter'] for x in rows),uninterrupted_joins=sum(not x['visually_seen_delimiter'] for x in rows)),indent=2)+'\n');print(json.dumps(dict(joins=len(rows),explicit=sum(manual[0]+manual[1]+manual[2]),uninterrupted=len(rows)-sum(manual[0]+manual[1]+manual[2]))))
