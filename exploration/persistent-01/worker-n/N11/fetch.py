from pathlib import Path
import urllib.request,hashlib,json,tarfile,datetime
R=Path(__file__).parent;url='https://www.provos.org/uploads/outguess-0.2.tar.gz'
with urllib.request.urlopen(url,timeout=30) as f:b=f.read();meta=dict(url=url,effective_url=f.url,status=f.status,headers=dict(f.headers),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
p=R/'outguess-0.2.tar.gz';p.write_bytes(b);meta.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),sha1=hashlib.sha1(b).hexdigest(),md5=hashlib.md5(b).hexdigest());(R/'retrieval.json').write_text(json.dumps(meta,indent=2));assert meta['sha1']=='d8d7ff3d8f492c3fbb075ecd2c6e87ce7cf13b80' and meta['md5']=='321f23dc0badaba4350fa66b59829064'
with tarfile.open(p) as t:
 for m in t.getmembers():assert not m.name.startswith('/') and '..' not in Path(m.name).parts and not m.issym() and not m.islnk()
 t.extractall(R/'source',filter='data')
print(meta)
