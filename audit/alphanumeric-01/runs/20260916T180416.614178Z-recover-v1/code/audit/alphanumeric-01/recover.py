"""Bounded source/layout reconciliation; no cipher search or inherited imports."""
import collections, datetime, hashlib, json, pathlib, re, urllib.request
from PIL import Image, ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'audit/alphanumeric-01/v1'; OUT.mkdir(exist_ok=False)
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def sha(b): return hashlib.sha256(b).hexdigest()
sources={}
for name,path in {'relikd-local':'liber-primus/data/sources/relikd_p40-53.txt','scream-local':'liber-primus/data/scream314_lp.md'}.items():
 b=(ROOT/path).read_bytes();(OUT/(name+'.txt')).write_bytes(b);sources[name]={'path':path,'sha256':sha(b)}
url='https://raw.githubusercontent.com/relikd/LiberPrayground/master/pages/p40-53.txt'
try:
 with urllib.request.urlopen(url,timeout=30) as r:b=r.read(200000);status=r.status
 (OUT/'relikd-public.txt').write_bytes(b);sources['relikd-public']={'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':status,'sha256':sha(b),'bytes':len(b)}
except Exception as e:sources['relikd-public']={'url':url,'error':str(e),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
pat=re.compile(r'^\s*[0-9A-Za-z]{2}(?:[ \t]+[0-9A-Za-z]{2}){7}\s*$')
def tables(text):
 out=[];cur=[]
 for line in text.splitlines()+['']:
  if pat.match(line):cur.append(line)
  elif cur:out.append(cur);cur=[]
 return [x for x in out if len(x) in (10,13,9)]
tabs={k:tables((OUT/(k+'.txt')).read_text()) for k in sources if (OUT/(k+'.txt')).exists()}
for k,t in tabs.items():assert [len(x) for x in t]==[10,13,9],(k,[len(x) for x in t])
grid=json.loads((ROOT/'liber-primus/analysis/round19/C1/grid.json').read_text())
cells=[];pages=[];idx=0
for p,tab in zip((49,50,51),tabs['scream-local']):
 image_path=f'liber-primus/data/relikd/p{p}.jpg';im=Image.open(ROOT/image_path)
 sources[f'image{p}']={'path':image_path,'sha256':sha((ROOT/image_path).read_bytes()),'dimensions':list(im.size)}
 rows=[]
 for row,line in enumerate(tab):
  words=line.split();boxes=grid[f'p{p}'][8*row:8*(row+1)]
  # Prior splitter fused 2t/06 and split 11 into two cells. Correct with explicit inspection rectangles.
  if p==51 and row==3: boxes[1:4]=[[790,1150,879,1250],[887,1150,1015,1250],[1035,1150,1140,1250]]
  rows.append({'row':row,'text':' '.join(words),'source_line_verbatim':line,'bbox':[min(x[0] for x in boxes),min(x[1] for x in boxes),max(x[2] for x in boxes),max(x[3] for x in boxes)],'inter_token_pixel_gaps':[boxes[n+1][0]-boxes[n][2] for n in range(7)]})
  for col,(tok,box) in enumerate(zip(words,boxes)):
   cells.append({'index':idx,'page':p,'row':row,'column':col,'token':tok,'bbox':box,'coordinate_source':'Round19 C1 grid; p51 row3 columns1-3 inspection override' if p==51 and row==3 else 'Round19 C1 grid (inherited, spot-checked)','sources':{k:t[p-49][row].split()[col] for k,t in tabs.items()}});idx+=1
 pages.append({'page':p,'image':image_path,'rows':rows})
save('sources.json',sources);save('transcription.json',{'version':'alphanumeric-01-v1','indexing':'zero based; image pixels x0,y0,x1,y1; tokens row-major; pages49/50/51','spacing':'Text uses one separator; original source whitespace retained; image bboxes and pixel gaps retain visual spacing. No claim spaces are encoded characters.','pages':pages,'cells':cells})
(OUT/'transcription.txt').write_text('\n\n'.join('PAGE '+str(p['page'])+'\n'+'\n'.join(r['text'] for r in p['rows']) for p in pages)+'\n')
counter=collections.Counter(c['token'] for c in cells)
stats={'rows_per_page':[len(p['rows']) for p in pages],'tokens_per_page':[8*len(p['rows']) for p in pages],'tokens':len(cells),'token_lengths':dict(collections.Counter(map(len,counter.elements()))),'symbol_inventory':''.join(sorted(set(''.join(counter)))),'symbol_counts':dict(sorted(collections.Counter(''.join(c['token'] for c in cells)).items())),'distinct_tokens':len(counter),'duplicate_tokens':{k:v for k,v in sorted(counter.items()) if v>1},'source_disagreements':[c for c in cells if len(set(c['sources'].values()))>1]}
# One named historical representation for identity comparison, not evidence that base60 is intended.
alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx'
b=bytes(alphabet.index(c['token'][0])*60+alphabet.index(c['token'][1]) for c in cells)
stats['conditional_historical_base60']={'rule':'0-9 A-Z a-x; 60*d0+d1','sha256':sha(b),'min':min(b),'max':max(b),'comparisons':{}}
for path in ['liber-primus/analysis/pp49_51/canon_256.bin','liber-primus/analysis/pp49_51/canon_256_decpref.bin','liber-primus/analysis/round19/C1/payload_resolved.bin']:
 old=(ROOT/path).read_bytes();stats['conditional_historical_base60']['comparisons'][path]={'sha256':sha(old),'differing_indices':[i for i,(x,y) in enumerate(zip(b,old)) if x!=y]}
save('structure.json',stats)
local=(OUT/'relikd-local.txt').read_text();parts=local.split('\n\n');start=next(i for i,p in enumerate(parts) if p.startswith('3N\t'))
save('surrounding-runes.json',{'source':'relikd-local.txt','independent_rune_verification':False,'p49':{'bbox':[580,650,1850,1140],'text':parts[start-1]},'p50':{'text':'','note':'No body rune rows visible'},'p51':{'bbox':[580,2220,2100,3090],'text':parts[start+3]},'note':'Inherited rune spelling and separators retained; red terminal mark p49 and botanical ornaments remain in source image; no alteration of rune-only pinned stream.'})
sites=[2,25,45,50,72,90,164,165,172,175,182,186,198,199,209,210,211,215,237,246]
sheet=Image.new('RGB',(1000,((len(sites)+3)//4)*210),'white');draw=ImageDraw.Draw(sheet)
for n,i in enumerate(sites):
 c=cells[i];im=Image.open(ROOT/f"liber-primus/data/relikd/p{c['page']}.jpg");x0,y0,x1,y1=c['bbox'];crop=im.crop((x0-15,y0-15,x1+15,y1+15));crop.thumbnail((230,170));x=(n%4)*250;y=(n//4)*210;sheet.paste(crop,(x,y+25));draw.text((x+5,y+5),f"idx{i} p{c['page']} r{c['row']} c{c['column']}",fill='black')
sheet.save(OUT/'glyph-checks.png')
for p,box in [(49,(630,1220,1785,2955)),(50,(615,600,1790,2870)),(51,(640,605,1755,2180))]:
 Image.open(ROOT/f'liber-primus/data/relikd/p{p}.jpg').crop(box).save(OUT/f'p{p}-block.png')
print(json.dumps(stats,indent=2));print('sources',json.dumps(sources,indent=2));print('wrote',str(OUT.relative_to(ROOT)))
