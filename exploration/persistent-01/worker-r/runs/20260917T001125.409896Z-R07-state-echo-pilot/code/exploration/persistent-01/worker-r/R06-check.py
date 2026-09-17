import pathlib,json,hashlib,numpy as np
from PIL import Image
P=pathlib.Path(__file__).resolve().parent/'R06';POPC=[i.bit_count() for i in range(256)]
def scalar(b):
 h=sum((b[y*8+x]&1)==(b[y*8+x+1]>>7) for y in range(32) for x in range(7));v=sum(8-POPC[b[i]^b[i+8]] for i in range(248));return h,v,(h/224+v/1984)/2
checked=0;cases=[]
for f in sorted(P.glob('*.npz')):
 d=np.load(f);b=d['input_bytes'].tobytes();h,v,s=scalar(b);saved=json.loads(f.with_suffix('.json').read_text());assert h==saved['horizontal_agree'] and v==saved['vertical_agree'] and s==saved['statistic'];assert hashlib.sha256(b).hexdigest()==saved['input_sha256'];assert np.array_equal(np.asarray(Image.open(P/(f.stem+'-native.png'))),255*(1-d['bits']));assert bytes(sum(int(d['bits'][y,x+i])<<(7-i) for i in range(8)) for y in range(32) for x in range(0,64,8))==b;perms=d['permutations'];assert np.all(np.sort(perms,axis=1)==np.arange(256));upper=0
 for j,p in enumerate(perms):
  bb=d['input_bytes'][p].tobytes();hh,vv,ss=scalar(bb);assert (hh,vv)==tuple(d['null_counts'][j]);assert ss==d['null_scores'][j];upper+=ss>=s
 assert (upper+1)/(len(perms)+1)==saved['p_upper'];checked+=len(perms)+1;cases.append(dict(name=f.stem,panels=len(perms)+1,p_upper=saved['p_upper']))
m=json.loads((P/'actual-pixel-map.json').read_text());b=(P/'actual.bin').read_bytes();assert len(m)==2048
for q in m:assert q['byte_index']==q['y']*8+q['x']//8 and q['msb_first_bit_index']==q['x']%8 and q['bit_value']==((b[q['byte_index']]>>(7-q['msb_first_bit_index']))&1)
r=dict(panels_recomputed=checked,pixel_maps_checked=len(m),cases=cases);(P/'check.json').write_text(json.dumps(r,indent=2)+'\n');print('CHECKED',checked,'PANELS',len(m),'PIXEL MAPS')
