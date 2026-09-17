import p13 as q
import p10 as p
import numpy as np,json,collections
p.gate();results=[]
for page in [0,1]:
 d=json.loads((q.R/f'actual-{page}.json').read_text());m=d['metadata'];raw=(p.ROOT/d['path']).read_bytes();assert p.sha(raw)==d['sha256'];sos=next(h for h in m['headers'] if h['marker']==218);body=raw[sos['offset']+4:sos['offset']+2+sos['length']];selectors={body[1+2*k]:(body[2+2*k]>>4,body[2+2*k]&15) for k in range(body[0])};arc=np.load(p.R/f'actual-{page}-coefficients.npz');hist={key:[0]*256 for key in m['symbol_histograms']};mw,mh=m['mcu_grid']
 for c in m['frame']['components']:
  a=arc[str(c['id'])];assert p.sha(a.tobytes())==m['coefficient_sha256'][str(c['id'])];rows=a.reshape(mh,c['v'],mw,c['h'],64).transpose(0,2,1,3,4).reshape(-1,64);dc,ac=selectors[c['id']];last=0
  for block in rows:
   v=int(block[0]);hist[f'0:{dc}'][abs(v-last).bit_length()]+=1;last=v;seq=block[p.ZZ];nz=np.flatnonzero(seq[1:])+1;prev=0
   for k in nz:
    run=int(k)-prev-1
    while run>=16:hist[f'1:{ac}'][240]+=1;run-=16
    hist[f'1:{ac}'][16*run+abs(int(seq[k])).bit_length()]+=1;prev=int(k)
   if prev<63:hist[f'1:{ac}'][0]+=1
 assert hist==m['symbol_histograms'];results.append(dict(page=page,status='PASS',totals={k:sum(v) for k,v in hist.items()}))
(q.R/'check.json').write_text(json.dumps(dict(status='PASS',method='independent coefficient-to-DCdifference/ACrun histogram, separate vectorized component ordering',results=results),indent=2)+'\n');print('PASS',results)
