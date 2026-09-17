import pathlib,json,hashlib
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];out=O/'inspection'/'major-marks';out.mkdir(exist_ok=True);packet=json.loads((O/'section-packet.json').read_text());joins=json.loads((O/'inspection'/'remaining-joins'/'manifest.json').read_text());records=[]
for page in packet['pages']:
 pid=page['original_page'];im=Image.open(R/page['image'])
 for gap in page['explicit_gaps']:
  if '.' not in gap['text']:continue
  line=next(l for l in page['lines'] if l['rune_start']<=gap['previous']<l['rune_end']);j=line['source_line'];w=next(x for x in joins if x['page']==pid and x['previous_line']==j);box=[580,w['boxes'][0][1],1830,w['boxes'][0][3]];name=f'p{pid}-line{j}-after{gap["previous"]}.png';im.crop(tuple(box)).save(out/name);records.append(dict(page=pid,line=j,after_page_rune=gap['previous'],reset_before_section_rune=page['section_start']+gap['next'],source_image=page['image'],bbox=box,crop=name,crop_sha256=hashlib.sha256((out/name).read_bytes()).hexdigest(),source_raw=line['raw']))
(out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records))
