import pathlib,json,gzip,hashlib
R=pathlib.Path(__file__).parent;load=lambda n:json.load(gzip.open(R/'snapshots'/(n+'.json.gz'),'rt'));abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def scan(raw):
 indices=[];ends=[];inside=False
 for ch in raw+' ':
  if ch in abc:indices.append(abc.index(ch));inside=True
  elif inside:ends.append(len(indices)-1);inside=False
 return indices,ends
for ix in range(4):
 f=load('fixture-'+str(ix));p=[];ends=[]
 for m in f['maps']:
  q,e=scan(pathlib.Path(m['path']).read_text());offset=len(p);p+=q;ends +=[offset+i for i in e]
 assert p==f['plain'] and ends==f['ends']
real=load('real');p=[];ends=[]
for m in load('real-maps'):
 q,e=scan(m['raw_joined']);offset=len(p);p+=q;ends += [offset+i for i in e]
assert p==real['cipher'] and ends==real['ends']
report=R.parent/'worker-p/P14/REPORT.md';(R/'P14-REPORT-snapshot.md').write_bytes(report.read_bytes())
(R/'source-ends.json').write_text(json.dumps({'status':'PASS','packets':5,'report_sha256':hashlib.sha256(report.read_bytes()).hexdigest()}));print('source ends PASS')
