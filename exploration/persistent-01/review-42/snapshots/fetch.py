from pathlib import Path
import urllib.request,datetime,hashlib,json
O=Path(__file__).resolve().parent
rows=[]
for n in [218,227]:
 u=f'https://www.gutenberg.org/cache/epub/{n}/pg{n}.txt'
 with urllib.request.urlopen(u,timeout=30) as r:b=r.read();record=dict(url=u,final_url=r.url,status=r.status,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 p=O/f'pg{n}.txt';assert not p.exists();p.write_bytes(b);rows.append(record);print(json.dumps(record),flush=True)
(O/'retrieval.json').write_text(json.dumps(rows,indent=2)+'\n')
