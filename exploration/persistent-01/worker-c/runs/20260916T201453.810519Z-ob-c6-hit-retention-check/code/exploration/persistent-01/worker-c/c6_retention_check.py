import io,json
from p03_frozen import O,dump
from ob_c6 import scan
controls=json.loads((O/'ob-c6/controls.json').read_text());rows=[]
for control in controls:
 output=io.StringIO();r=scan([dict(id=control['name'],cipher=control['cipher'])],output,True);assert any(h['bytes_hex']==control['target_hex'] for h in r['hits']);rows.append(dict(name=control['name'],retained_bytes_hit=True,cells=len(output.getvalue().splitlines())))
dump(O/'ob-c6/retention-check.json',rows);print(json.dumps(rows))
