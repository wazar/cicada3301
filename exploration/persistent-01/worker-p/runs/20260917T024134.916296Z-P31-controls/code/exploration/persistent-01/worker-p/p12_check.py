import p10 as p
import p11 as j
import json,numpy as np,subprocess
R=p.R.parent/'P12';summary=json.loads((R/'summary.json').read_text());inv=json.loads((R/'inventory.json').read_text());assert summary['completed']==summary['expected']==43;assert [r['page'] for r in summary['rows']]==inv['selection'];checks=[]
for row in summary['rows']:
 p.gate();page=row['page'];bits=np.unpackbits(np.frombuffer((R/f'page-{page}-bits.packed').read_bytes(),dtype=np.uint8));n=row['eligible_bits'];assert len(bits)-n<8 and not bits[n:].any();bits=bits[:n];width=0
 for x in bits[:5]:width=width*2+int(x)
 declared=0
 for x in bits[5:5+width]:declared=declared*2+int(x)
 capacity=(n-5-width)//8;assert width==row['header']['width'] and declared==row['header']['length'] and capacity==row['header']['capacity_bytes'];count=min(declared,capacity);payload=np.packbits(bits[5+width:5+width+count*8]).tobytes();assert payload==(R/f'page-{page}-available.bin').read_bytes();assert p.sha(payload)==row['available_sha256']
 # The historical sink consumes only eligible parity bits; a signed−2/−1 stream replays that interface exactly.
 f=R/'check-current.i16';(bits.astype('<i2')-2).tofile(f);out=R/'check-current.bin';cmd=[str(j.R/'harness'),'sink',str(f),str(out)];r=subprocess.run(cmd,capture_output=True);(R/f'check-{page}.stderr').write_bytes(r.stderr);assert r.returncode==0;state=json.loads(r.stderr);assert state==row['sink_state'];actual=out.read_bytes();assert actual==(R/f'page-{page}-historical.bin').read_bytes();checks.append(dict(page=page,eligible_bits=n,declared=declared,capacity=capacity,packed_sha256=p.sha((R/f'page-{page}-bits.packed').read_bytes()),sink_exit=r.returncode,sink=state,output_sha256=p.sha(actual)))
(R/'check.json').write_text(json.dumps(dict(status='PASS',count=len(checks),checks=checks,temporary_probe_files_reconstructible=True),indent=2)+'\n');print('PASS',len(checks))
