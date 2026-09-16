import pathlib,json,hashlib,datetime
O=pathlib.Path(__file__).resolve().parent;P=O.parent/'worker-p/P06'
# Manually read from source-pixel contact sheets using view_image; no classifier/labels/code consumed.
sheets=[
[19,0,16,9,1,9,10,13,9,16,5,1,5,28,28,9,15,14,3,19],
[5,10,18,24,1,21,7,19,1,4,15,6,10,25,18,18,18,10,0,18],
[19,4,26,1,10,18,3,4,3,7,8,1,4,9,18,16,19,7,4,20],
[19,25,18,10,0,19,15,18,9,15,8,9,19,5,9,4,7,0,27,1],
[24,15,3,18,18,10,24,7,0,3,10,1,18,19,7,5,27,21,5,19]
]
notes={2:'F branches clear; lower stem partly faint/clipped.',11:'C main glyph; thin neighboring vertical fragment ignored.',14:'EA forked upper branches; neighboring thin vertical ignored.',15:'EA; neighboring thin vertical ignored.',19:'Two bent right branches read as O using generic canonical legend.',24:'Upper branch bent, lower straight: A.',34:'Two straight descending branches: AE.',47:'Two bent right branches: O.',49:'Two bent right branches: O.',62:'Two straight descending branches: AE.',74:'C; thin neighboring vertical fragment ignored.',79:'Crossed arms with central staff read as IA; historical glyph variant.',81:'Upper bent and lower straight right branches: A.',83:'Two bent right branches: O.',87:'Upper bent and lower straight right branches: A.',90:'Two bent right branches: O.',96:'C; neighboring thin vertical ignored.',97:'Crossed arms with central staff read as IA; historical glyph variant.',99:'C; neighboring thin vertical ignored.'}
medium={2,14,15,19,24,34,47,49,62,79,81,83,87,90,97}
rows=[]
for si,values in enumerate(sheets):
 assert len(values)==20
 for j,rune in enumerate(values):
  number=si*20+j+1;rows.append({'number':number,'rune_id':rune,'confidence':'medium' if number in medium else 'high','note':notes.get(number,'Direct source-pixel glyph reading.')})
assert len(rows)==100 and [r['number'] for r in rows]==list(range(1,101))
inputs=[]
for name in [f'sheet-{i}.png' for i in range(1,6)]+['unicode-legend.png']:
 p=P/name;inputs.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out={'reader':'review-11 / persistent_n','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'truth_seen':False,'first_reader_predictions_seen':False,'method':'Personal view_image inspection of all five numbered sheets and generic Unicode canonical legend; manually entered predictions. No target source-index labels, P06 code, truth or data labelvectors read.','sample_n':100,'same_sample_as_first_reader':True,'inputs':inputs,'predictions':rows}
p=O/'predictions-frozen.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');digest=hashlib.sha256(p.read_bytes()).hexdigest();(O/'predictions-frozen.sha256').write_text(digest+'  predictions-frozen.json\n');print(digest)
