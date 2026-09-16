import json,urllib.request,hashlib,datetime,pathlib
out=pathlib.Path(__file__).parent/'sources'
base='https://raw.githubusercontent.com/relikd/LiberPrayground/main/'
names=['0_koan_1','0_loss_of_divinity','0_warning','0_welcome','0_wisdom','jpg107-167','jpg229','p56_an_end','p57_parable']
records=[]
for name in [p+'.txt' for n in names for p in [n,'solved_'+n]]+['../solver.py','../RuneSolver.py','../Rune.py']:
    suffix='pages/'+name if not name.startswith('../') else name[3:]
    url=base+suffix
    try:
        data=urllib.request.urlopen(url,timeout=30).read()
        path=out/pathlib.Path(name).name;path.write_bytes(data)
        records.append(dict(url=url,path=str(path.relative_to(out.parent)),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
    except Exception as e:records.append(dict(url=url,error=str(e)))
(out/'retrieval.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))
