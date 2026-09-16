from pathlib import Path
import json,hashlib
b=Path('exploration/persistent-01/worker-p/P12');out=Path('exploration/persistent-01/coordinator/P12-check');d=json.loads((b/'summary.json').read_text());reserves={4,9,14,19,24,29,34,39,44,54};checks=[]
for r in d['rows']:
 p=r['page'];assert p not in reserves|{0,1,50};raw=(b/f'page-{p}-bits.packed').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['packed_sha256'];n=r['eligible_bits'];assert len(raw)==(n+7)//8
 def bit(i):return (raw[i//8]>>(7-i%8))&1
 def uint(start,count):
  v=0
  for i in range(start,start+count):v=(v<<1)|bit(i)
  return v
 width=uint(0,5);length=uint(5,width);offset=5+width;capacity=(n-offset)//8
 payload=bytes(uint(offset+8*i,8) for i in range(capacity));assert payload==(b/f'page-{p}-available.bin').read_bytes();historical=payload[:1024*(len(payload)//1024)];assert historical==(b/f'page-{p}-historical.bin').read_bytes();assert width==31 and length==2**31-1 and length>capacity;assert not any(bit(i) for i in range(n,len(raw)*8))
 assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['image_sha256'];checks.append(dict(page=p,width=width,length=length,capacity=capacity,eligible_bits=n,historical_bytes=len(historical)))
assert len(checks)==43==len(set(c['page'] for c in checks));report=dict(status='PASS',count=43,total_bits=sum(c['eligible_bits'] for c in checks),total_bytes=sum(c['capacity'] for c in checks),scope='Independent scalar bit/header/capacity/buffering replay and original image hashes. Not independent JPEG entropy decoding.',checks=checks);(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
