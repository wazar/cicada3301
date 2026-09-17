import p11 as j
import p10 as p
import json,pathlib,numpy as np,subprocess,time,sys,collections
R=p.R.parent/'P12'
def dump(n,x):(R/(n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def control():
 p.gate();src=p.R/'control-8-clean.jpg';dst=R/'color-control.jpg';payload=j.R/'payload-127.bin';cmd=[str(j.R/'harness'),'jpeg',str(src),str(dst),str(payload)];r=subprocess.run(cmd,capture_output=True);(R/'color-control.stderr').write_bytes(r.stderr);dump('color-control-command',dict(command=cmd,exit_code=r.returncode));assert r.returncode==0;meta,_,_,ar=p.parse(dst.read_bytes());assert len(meta['frame']['components'])==3;vals,pos=j.stream(meta,{str(k):v for k,v in ar.items()});bits=np.array([int(v)&1 for v in vals if j.eligible(int(v))],dtype=np.uint8);h,out=j.header(bits);assert out==payload.read_bytes();sim,ss,errs=j.sink_sim(bits);assert sim==out and not ss['open'];(R/'color-control-extracted.bin').write_bytes(out);vf=R/'color-control.i16';vals.tofile(vf);cmd=[str(j.R/'harness'),'sink',str(vf),str(R/'color-control-c-output.bin')];q=subprocess.run(cmd,capture_output=True);(R/'color-control-sink.stderr').write_bytes(q.stderr);assert q.returncode==0 and json.loads(q.stderr)==ss and (R/'color-control-c-output.bin').read_bytes()==out;dump('control',dict(status='PASS',input=str(src),input_sha256=p.sha(src.read_bytes()),output_sha256=p.sha(dst.read_bytes()),payload_sha256=p.sha(out),header=h,sink=ss,metadata=meta,commands=[cmd],exit_code=q.returncode));print('RGB420 CONTROL PASS')
def run():
 p.gate();assert json.loads((R/'control.json').read_text())['status']=='PASS';inv=json.loads((R/'inventory.json').read_text());assert len(inv['selection'])==43;rows=[];start=time.monotonic()
 for item in inv['rows']:
  p.gate();page=item['page'];assert page not in inv['reserved']+[0,1,50];t=time.monotonic();f=p.ROOT/item['path'];b=f.read_bytes();assert p.sha(b)==item['sha256'];row=dict(page=page,path=item['path'],image_sha256=item['sha256'])
  if item['status']!='SUPPORTED':row['status']='SKIP_'+item['status']
  else:
   try:
    meta,_,_,ar=p.parse(b);vals,pos=j.stream(meta,{str(k):v for k,v in ar.items()});eligible=vals[(vals!=0)&(vals!=1)];bits=(eligible&1).astype(np.uint8);packed=np.packbits(bits).tobytes();(R/f'page-{page}-bits.packed').write_bytes(packed);h,out=j.header(bits);(R/f'page-{page}-available.bin').write_bytes(out);historical,state,errors=j.sink_sim(bits);(R/f'page-{page}-historical.bin').write_bytes(historical);row.update(status=h['status'],eligible_bits=len(bits),packed_sha256=p.sha(packed),header=h,available_bytes=len(out),available_sha256=p.sha(out),historical_bytes=len(historical),historical_sha256=p.sha(historical),sink_state=state,sink_error_count=len(errors),eligible_map_sha256=p.sha(pos.tobytes()),coefficient_hashes=meta['coefficient_sha256'],metadata=meta);dump('page-'+str(page),row)
   except (p.Unsupported,p.Invalid,AssertionError) as e:row.update(status='UNSUPPORTED_OR_PARSE_ERROR',error=repr(e));dump('page-'+str(page),row)
  row['seconds']=time.monotonic()-t;rows.append({k:v for k,v in row.items() if k!='metadata'});dump('summary',dict(completed=len(rows),expected=43,seconds=time.monotonic()-start,counts=dict(collections.Counter(x['status'] for x in rows)),rows=rows));print(page,row['status'],row.get('header'),round(row['seconds'],3),flush=True)
 print('DONE',len(rows),time.monotonic()-start)
if __name__=='__main__':{'control':control,'run':run}[sys.argv[1]]()
