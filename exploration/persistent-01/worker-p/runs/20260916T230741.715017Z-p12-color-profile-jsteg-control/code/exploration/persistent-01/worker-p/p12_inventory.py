import p10 as p
import json,struct,math,collections
R=p.R.parent/'P12';cfg=json.loads((p.ROOT/'exploration/persistent-01/config.json').read_text());fpath=p.ROOT/'exploration/persistent-01/worker-f/F06-maps.json';ids=sorted({m['page'] for m in json.loads(fpath.read_text())}-{0,1,50}-set(cfg['reserved_original_pages']));mp=p.ROOT/'audit/parallel-01/inputs/page-map.json';assert p.sha(mp.read_bytes())==cfg['map_sha256'];maps={m['original_page']:m for m in json.loads(mp.read_text())['pages']};rows=[]
def profile(d):
 p.need(d[:2]==b'\xff\xd8','notJPEG');i=2;frame=None;dri=0;markers=[]
 while True:
  m,i,fill=p.marker(d,i);ln=int.from_bytes(d[i:i+2],'big');p.need(ln>=2 and i+ln<=len(d),'segment');b=d[i+2:i+ln];i+=ln;markers.append(m)
  if m in set(range(0xc0,0xd0))-{0xc4,0xc8,0xcc}:
   prec,h,w,n=struct.unpack('>BHHB',b[:6]);frame=dict(marker=m,precision=prec,height=h,width=w,components=[dict(id=b[6+3*k],h=b[7+3*k]>>4,v=b[7+3*k]&15) for k in range(n)])
  if m==0xdd:dri=int.from_bytes(b,'big')
  if m==0xda:
   ns=b[0];scan=dict(components=[b[1+2*k] for k in range(ns)],parameters=list(b[-3:]));break
 p.need(frame is not None,'noSOF');cs=frame['components'];hm=max(c['h'] for c in cs);vm=max(c['v'] for c in cs);mw=math.ceil(frame['width']/(8*hm));mh=math.ceil(frame['height']/(8*vm));coded=mw*mh*sum(c['h']*c['v'] for c in cs);stored=sum(math.ceil(frame['width']*c['h']/(8*hm))*math.ceil(frame['height']*c['v']/(8*vm)) for c in cs);supported=frame['marker']==192 and frame['precision']==8 and len(cs) in [1,3] and scan['components']==[c['id'] for c in cs] and scan['parameters']==[0,63,0] and dri==0 and coded==stored
 return dict(frame=frame,scan=scan,restart_interval=dri,markers=markers,sos_end=i,dummy_blocks=coded-stored,supported_profile=supported)
p.gate()
for page in ids:
 m=maps[page];path=m['local_image'];row=dict(page=page,map=m,path=path)
 if path is None or not(p.ROOT/path).is_file():row['status']='MISSING_MAPPED_IMAGE'
 else:
  b=(p.ROOT/path).read_bytes();row.update(bytes=len(b),sha256=p.sha(b));row['status']='HASH_MISMATCH' if row['sha256']!=m['image_sha256'] else 'AVAILABLE'
  if row['status']=='AVAILABLE':row['profile']=profile(b);row['status']='SUPPORTED' if row['profile']['supported_profile'] else 'UNSUPPORTED_PROFILE'
 rows.append(row)
result=dict(selection=ids,excluded_already_tested=[0,1],excluded_special=[50],reserved=cfg['reserved_original_pages'],f06_sha256=p.sha(fpath.read_bytes()),map_sha256=p.sha(mp.read_bytes()),config_sha256=p.sha((p.ROOT/'exploration/persistent-01/config.json').read_bytes()),rows=rows,counts=dict(collections.Counter(r['status'] for r in rows)))
(R/'inventory.json').write_text(json.dumps(result,indent=2)+'\n');print('INVENTORY',len(ids),result['counts']);print('PROFILES',collections.Counter(json.dumps(r.get('profile',{}).get('frame'),sort_keys=True) for r in rows))
