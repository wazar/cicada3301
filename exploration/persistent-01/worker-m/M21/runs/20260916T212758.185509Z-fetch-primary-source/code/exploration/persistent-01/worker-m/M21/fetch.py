import pathlib,urllib.request,hashlib,json,tarfile,io,datetime
r=pathlib.Path(__file__).parent;assert not(r.parent.parent/'STOP').exists();url='https://www.cpan.org/modules/by-module/Crypt/Crypt-RSA-1.99.tar.gz'
req=urllib.request.Request(url,headers={'User-Agent':'CompatibilityResearch/1.0'});resp=urllib.request.urlopen(req,timeout=30);data=resp.read(200001);assert len(data)<200001;(r/'sources/Crypt-RSA-1.99.tar.gz').write_bytes(data)
t=tarfile.open(fileobj=io.BytesIO(data),mode='r:gz');members=t.getmembers();assert sum(x.size for x in members)<2000000
for x in members:assert x.name.startswith('Crypt-RSA-1.99/') and '..' not in pathlib.PurePosixPath(x.name).parts and not x.issym() and not x.islnk()
manifest=[]
for x in members:
 if x.isfile():
  b=t.extractfile(x).read();p=r/'sources'/x.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);manifest.append(dict(path=x.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(r/'sources/manifest.json').write_text(json.dumps(dict(url=url,final_url=resp.url,archive_bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),files=manifest,missing_legacy_path=not pathlib.Path('corpus/A-primary-artifacts/cijhho123/2014/additional docs/scripts/Program to decrypt RSA message in perl.txt').exists()),indent=2));print(len(data),hashlib.sha256(data).hexdigest());print('\n'.join(x['path'] for x in manifest))
