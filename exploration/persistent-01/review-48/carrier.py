from pathlib import Path
import urllib.request,json,hashlib,datetime
R=Path(__file__).parent;url='https://raw.githubusercontent.com/cijhho123/cicada3301/main/2016/2016/additional%20images/4gq25.jpg'
with urllib.request.urlopen(url,timeout=30) as f:b=f.read();meta=dict(url=url,effective_url=f.url,status=f.status,headers=dict(f.headers),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(R/'4gq25.jpg').write_bytes(b);meta.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),sha1=hashlib.sha1(b).hexdigest());(R/'retrieval.json').write_text(json.dumps(meta,indent=2));assert len(b)==26342 and meta['sha256']=='a8340ad04b83fb3130e7ed9172867a440812e87089d6aa2b932d97c6ae38aebe'
a=Path('corpus/A-primary-artifacts/micheloosterhof_cicada-2016/stage01/4gq25.jpg.outguess');c=Path('liber-primus/analysis/armada_osint/extracts/T5-4gq25-2016.outguess.txt');payloads=[]
for p in [a,c]:
 x=p.read_bytes();payloads.append(dict(path=str(p),bytes=len(x),sha256=hashlib.sha256(x).hexdigest()));(R/p.name).write_bytes(x)
(R/'payloads.json').write_text(json.dumps(payloads,indent=2));print(meta);print(payloads)
