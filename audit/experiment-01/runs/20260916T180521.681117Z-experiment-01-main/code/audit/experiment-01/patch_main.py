"""Auditable pre-main wiring; no scientific execution."""
from pathlib import Path
p=Path(__file__).with_name('control.py');s=p.read_text()
s=s.replace("a.add_argument('--start',type=int,default=0);args=a.parse_args()", "a.add_argument('--start',type=int,default=0);a.add_argument('--main',action='store_true');args=a.parse_args()")
s=s.replace("summary['elapsed_seconds']=time.monotonic()-start", """if args.main and summary['outcome']!='BLOCKED_BY_POSITIVE_CONTROL':
  assert args.start==1 and args.limit==319
  prior=json.loads((O/'outputs/20260916T180424.220919Z/summary.json').read_text())
  assert prior['preregistration_sha256']==fr['preregistration_sha256'] and prior['executed']==[{'ordinal':0,'cell_index':0,'case':0,'passed':True,'path':'case-000.json','required_exact':True,'selected_exact':True,'planted_is_tied_top':True}]
  assert len(summary['executed'])==319 and all(x['passed'] for x in summary['executed'])
  import continuation,sys
  summary.update(continuation.finish(sys.modules[__name__],sk,keys,fixtures,spec,outdir))
 summary['elapsed_seconds']=time.monotonic()-start""")
p.write_text(s)
