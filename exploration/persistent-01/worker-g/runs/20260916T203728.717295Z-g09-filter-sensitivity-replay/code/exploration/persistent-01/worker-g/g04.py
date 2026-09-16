import pathlib,json,math,binascii,random
O=pathlib.Path(__file__).parent;D=json.loads((O.parents[2]/'audit/parallel-01/inputs/dataset.json').read_text());P={p['original_page']:p for p in D['pages'] if p['original_page']in[3,7]};rng=random.Random(30404)
def search(v,retain=False):
 width=int(len(v)*math.log(29,256));hits=[];outputs=[];counts={'nominal':0,'overflow':0,'eligible':0,'checks':0}
 for shift in range(29):
  for sign in [1,-1]:
   for reverse in [False,True]:
    digits=[(sign*x+shift)%29 for x in (v[::-1] if reverse else v)];z=0
    for x in digits:z=z*29+x
    for endian in ['little','big']:
     counts['nominal']+=1;key=[shift,sign,reverse,endian]
     if z>=256**width:counts['overflow']+=1;continue
     raw=z.to_bytes(width,endian);counts['eligible']+=1;match=[]
     for csize,init in [(4,None),(2,0),(2,65535)]:
      if len(raw)<=csize:continue
      check=binascii.crc32(raw[:-csize]) if init is None else binascii.crc_hqx(raw[:-csize],init)
      for order in ['little','big']:
       counts['checks']+=1
       if check==int.from_bytes(raw[-csize:],order):match.append([csize,init,order])
     if match:hits.append({'key':key,'hex':raw.hex(),'matches':match})
     if retain:outputs.append({'key':key,'hex':raw.hex()})
 return {'counts':counts,'hits':hits,'outputs':outputs}
result={'seed':30404,'fields':[],'controls':[]}
for page,lo,hi in [(3,0,16),(3,119,122),(7,194,208)]:
 v=P[page]['indices'][lo:hi];r=search(v,True);r.update(page=page,offsets=list(range(lo,hi)),source_char_positions=P[page]['source_char_positions'][lo:hi],indices=v)
 r['null_hits']=[]
 for j in range(100):
  shuffled=v.copy();rng.shuffle(shuffled);s=search(shuffled);r['null_hits'].append({'count':len(s['hits']),'counts':s['counts'],'hits':s['hits']})
 result['fields'].append(r)
 if len(v)>3:
  width=int(len(v)*math.log(29,256));payload=bytes(range(1,width-3));raw=payload+binascii.crc32(payload).to_bytes(4,'big');z=int.from_bytes(raw,'big');d=[]
  for _ in v:d.append(z%29);z//=29
  assert not z;plant=[(7-x)%29 for x in d[::-1]];res=search(plant);assert any(h['hex']==raw.hex() for h in res['hits']);result['controls'].append({'n':len(v),'indices':plant,'truth':raw.hex(),'search':res})
(O/'g04-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'fields':[{'page':x['page'],'offsets':[x['offsets'][0],x['offsets'][-1]],'counts':x['counts'],'hits':x['hits'],'null_total_hits':sum(n['count']for n in x['null_hits'])}for x in result['fields']],'positive_controls':len(result['controls'])},indent=2))
