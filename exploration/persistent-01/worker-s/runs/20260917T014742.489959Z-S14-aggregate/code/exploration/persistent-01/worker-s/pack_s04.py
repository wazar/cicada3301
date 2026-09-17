import json,gzip,hashlib,pathlib
base=pathlib.Path('exploration/persistent-01/worker-s');p=base/'S04-result.json';raw=p.read_bytes();packed=gzip.compress(raw,mtime=0);assert gzip.decompress(packed)==raw
(base/'S04-evidence.json.gz').write_bytes(packed)
r=json.loads(raw);(base/'S04-summary-witnesses.json').write_text(json.dumps({'summary':r['summary'],'real':r['real'],'tiny':r['tiny'],'full_evidence':{'path':'S04-evidence.json.gz','uncompressed_sha256':hashlib.sha256(raw).hexdigest(),'compressed_sha256':hashlib.sha256(packed).hexdigest()}},indent=2)+'\n')
p.unlink();print(json.dumps({'raw_bytes':len(raw),'gzip_bytes':len(packed),'roundtrip':'PASS'}))
