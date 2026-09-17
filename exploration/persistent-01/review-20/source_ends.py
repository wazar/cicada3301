from pathlib import Path
import gzip,json,hashlib
R=Path(__file__).parent;Q=R.parent/'worker-p/P15';abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
load=lambda name:json.load(gzip.open(Q/(name+'.json.gz'),'rt'))
def scan(raw):
 p=[];ends=[];inside=False
 for ch in raw+' ':
  if ch in abc:p.append(abc.index(ch));inside=True
  elif inside:ends.append(len(p)-1);inside=False
 return p,ends
for ix in range(4):
 f=load('fixture-'+str(ix));p,ends=scan(Path(f['source']['path']).read_text());assert p==f['plain'] and ends==f['ends']
for ix in [0,17]:
 m=load('map-'+str(ix));z=load('real-'+str(ix));p,ends=scan(m['raw_joined']);assert p==z['cipher']==m['indices'] and ends==z['ends']
for name in ['summary','map-0','map-17','actual-check','edge-probes']:
 p=Q/(name+'.json.gz')
 if p.exists():(R/'snapshots'/p.name).write_bytes(p.read_bytes())
(R/'source-ends.json').write_text(json.dumps({'status':'PASS','packets':6}));print('source ends PASS')
