from pathlib import Path
import json,zlib,hashlib,random,inspect,datetime
B=Path('exploration/persistent-01');O=B/'review-72';O.mkdir(exist_ok=True);N=B/'worker-n/N19';P=B/'worker-n/N18';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
assert not (B/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,26,tzinfo=datetime.timezone.utc)
sha=lambda b:hashlib.sha256(b).hexdigest()
def compressed(data):
 c=zlib.compressobj(level=9,method=zlib.DEFLATED,wbits=15,memLevel=8,strategy=zlib.Z_DEFAULT_STRATEGY);return c.compress(data)+c.flush(zlib.Z_FINISH)
def checkbytes(data,item):
 c=compressed(data);stored=(N/item['file']).read_bytes();assert c==stored and zlib.decompress(stored)==data;assert item['bytes']==len(data) and item['size']==len(c) and item['input_sha256']==sha(data) and item['compressed_sha256']==sha(c)
 a=1;b=0
 for x in data:a=(a+x)%65521;b=(b+a)%65521
 assert int.from_bytes(c[-4:],'big')==(b<<16)+a and int.from_bytes(c[:2],'big')%31==0 and c[0]&15==8
 return len(c)
d=json.loads((N/'result.json').read_text());api=json.loads((N/'api.json').read_text());assert d['api']==api and api==dict(signature=str(inspect.signature(zlib.compress)),doc=zlib.compress.__doc__,build_version=zlib.ZLIB_VERSION,runtime_version=zlib.ZLIB_RUNTIME_VERSION)
tiny=json.loads((N/'tiny.json').read_text());rng=random.Random(619001);periodic=bytes([0,1,2,3]*128);aperiodic=bytes(rng.randrange(29) for _ in range(512));assert (N/'tiny-periodic.bin').read_bytes()==periodic and (N/'tiny-aperiodic.bin').read_bytes()==aperiodic;assert all(any(aperiodic[j]!=aperiodic[(j+k)%512] for j in range(512)) for k in range(1,512));assert checkbytes(periodic,tiny['periodic'])<checkbytes(aperiodic,tiny['aperiodic'])
rows=[];files=[N/'CARD.md',N/'n19.py',N/'result.json',N/'api.json',N/'tiny.json',N/'tiny-periodic.bin',N/'tiny-aperiodic.bin']
for i in range(4):
 packetpath=P/f'packet-{i}.json';outpath=P/f'packet-{i}-main.json';packet=json.loads(packetpath.read_text());outs=json.loads(outpath.read_text());r=d['rows'][i];assert r['control']==i and r['packet_sha256']==sha(packetpath.read_bytes()) and r['outputs_sha256']==sha(outpath.read_bytes());source=packet['source'];f=Path(source['path']);assert sha(f.read_bytes())==source['sha256'] and f.read_text()==source['raw'];positions=[j for j,x in enumerate(source['raw']) if x in ABC];truth=[ABC.index(source['raw'][j]) for j in positions];assert positions==source['source_char_positions'] and truth==packet['truth'];assert len(outs['outputs'])==len(r['items']);sizes=[];truthidx=[]
 for j,(out,item) in enumerate(zip(outs['outputs'],r['items'])):
  a=bytes(out['runes']);assert len(a)==len(truth) and item['sentinel_position']==out['sentinel_position'];is_truth=list(a)==truth;assert item['is_truth']==is_truth
  if is_truth:truthidx.append(j)
  sizes.append(checkbytes(a,item));seq=bytes(x+1 for x in a)+b'\0';rotations=sorted(seq[k:]+seq[:k] for k in range(len(seq)));last=bytes(x[-1] for x in rotations);assert last.index(0)==out['sentinel_position'] and [x-1 for x in last if x]!=[];assert [x-1 for x in last if x]==packet['indices'];files.append(N/item['file'])
 assert len(truthidx)==1;ti=truthidx[0];truesize=sizes[ti];rank=1+sum(x<truesize for x in sizes);ties=[x['sentinel_position'] for x,v in zip(outs['outputs'],sizes) if v==truesize];best=[x['sentinel_position'] for x,v in zip(outs['outputs'],sizes) if v==min(sizes)];assert r['truth_position']==packet['truth_sentinel_position']==outs['outputs'][ti]['sentinel_position'];assert r['truth_competition_rank']==rank and r['truth_ties']==ties and r['shortest_positions']==best and r['gate_pass']==(best==[r['truth_position']]);rows.append(dict(control=i,outputs=len(sizes),sizes=sizes,truth_size=truesize,rank=rank,ties=len(ties),gate_pass=r['gate_pass']));files += [packetpath,outpath,f]
assert d['gate_pass']==all(r['gate_pass'] for r in rows)==False and d['actual_or_null_scored']==False
assert len(list(N.glob('control-*.zlib')))==sum(r['outputs'] for r in rows)
files += [N/'tiny-periodic.zlib',N/'tiny-aperiodic.zlib',Path(__file__)]
(O/'manifest.json').write_text(json.dumps([dict(path=str(f),sha256=sha(f.read_bytes())) for f in files],indent=2));result=dict(status='PASS',gate_pass=False,actual_or_null_scored=False,control_outputs=sum(r['outputs'] for r in rows),rows=rows,tiny_sizes=[len(compressed(periodic)),len(compressed(aperiodic))],build_version=zlib.ZLIB_VERSION,runtime_version=zlib.ZLIB_RUNTIME_VERSION);(O/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
