from pathlib import Path
import urllib.request,json,hashlib,datetime,time
O=Path(__file__).resolve().parent/'sources'
urls={
'relikd-README.md':'https://raw.githubusercontent.com/relikd/LiberPrayground/master/README.md',
'rtkd-README.md':'https://raw.githubusercontent.com/rtkd/iddqd/master/README.md',
'56.jpg':'https://raw.githubusercontent.com/cicada-solvers/documenting-cicada3301/master/assets/2014/liber-primus-complete/73.jpg',
'57.jpg':'https://raw.githubusercontent.com/cicada-solvers/documenting-cicada3301/master/assets/2014/liber-primus-complete/74.jpg',
'archive-files.xml':'https://archive.org/download/ky2khlqdf7qdznac.onion/ky2khlqdf7qdznac.onion_files.xml'}
rows=[]
for name,url in urls.items():
 t=time.monotonic(); r=dict(name=name,url=url,retrieval_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  b=urllib.request.urlopen(url,timeout=25).read(); (O/name).write_bytes(b); r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),status='ok')
 except Exception as e: r.update(status='error',error=str(e))
 r['elapsed_seconds']=time.monotonic()-t; rows.append(r)
(O/'retrieval.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
