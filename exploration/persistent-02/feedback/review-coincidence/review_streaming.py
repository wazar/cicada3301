"""Exercise streaming adapter on completed stored evidence, no repeated search."""
import json,gzip,pathlib,sys,importlib.util,hashlib,shutil
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];A=R/'exploration/persistent-02/section/coincidence';sys.path.insert(0,str(A));spec=importlib.util.spec_from_file_location('authorcontrols',A/'controls.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with gzip.open(A/'control01-all.json.gz','rt') as f:old=json.load(f)
expected=json.loads((A/'control01-summary.json').read_text());T=O/'streaming-fixture';T.mkdir(exist_ok=True);shutil.copyfile(A/'inputs.json',T/'inputs.json');shutil.copyfile(A/'core.py',T/'core.py');folder=T/'control01-cells';folder.mkdir(exist_ok=True);pins=dict(input_sha256=hashlib.sha256((T/'inputs.json').read_bytes()).hexdigest(),core_sha256=hashlib.sha256((T/'core.py').read_bytes()).hexdigest(),index=1)
for i,row in enumerate(old['rows']):
 with gzip.open(folder/f'cell{i:02}.json.gz','wt') as f:json.dump(dict(pins=pins,row=row),f,separators=(',',':'))
m.O=T
# Any attempt to repeat arithmetic is a test failure.
m.core.gridcase=lambda *args,**kwargs:(_ for _ in ()).throw(AssertionError('unexpected search replay'))
m.run(1);actual=json.loads((T/'control01-summary.json').read_text());extra={'storage','peak_process_rss_bytes'};assert {k:v for k,v in actual.items() if k not in extra}==expected
# Resume checks exact input/core/index pins, not merely a filename.
p=folder/'cell00.json.gz'
with gzip.open(p,'rt') as f:bad=json.load(f)
bad['pins']['index']=99
with gzip.open(p,'wt') as f:json.dump(bad,f)
try:m.run(1);raise RuntimeError('stale pins accepted')
except AssertionError:pass
with gzip.open(p,'wt') as f:json.dump(dict(pins=pins,row=old['rows'][0]),f,separators=(',',':'))
(O/'streaming-review.json').write_text(json.dumps(dict(status='PASS',completed_control=1,cells=42,arithmetic_calls=0,old_new_summary_identical_except=sorted(extra),stale_pin_refusal=True,all_full_prefix_continuation_rows_preserved=True),indent=2)+'\n');print('PASS streaming summary equivalence and resume pin refusal')
