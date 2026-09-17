from pathlib import Path
import importlib.util,json,hashlib,time,sys
import numpy as np
D=Path(__file__).parent;O=Path('exploration/persistent-01/worker-p/P31');source=Path('exploration/persistent-01/worker-p/p31.py');spec=importlib.util.spec_from_file_location('frozen_p31',source);p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def inventory():
 rows=[];jobs=[]
 for ix in range(4):
  path=O/f'packet-{ix}.json';packet=json.loads(path.read_text());truth=bytes(packet['truth']);carrier=bytes(packet['indices']);assert p.forward(truth)==carrier
  starts=sorted(range(len(truth)),key=lambda i:truth[i:]+truth[:i]);srcidx=[(i-1)%len(truth) for i in starts];srcpos=[packet['source']['source_char_positions'][i] for i in srcidx];assert bytes(truth[i] for i in srcidx)==carrier
  rows.append({'control':ix,'packet_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source':packet['source'],'truth':list(truth),'carrier':list(carrier),'carrier_to_source_rune':srcidx,'carrier_to_source_char':srcpos})
  for j in range(len(carrier)-1):
   if carrier[j]!=carrier[j+1]:jobs.append({'job':len(jobs),'control':ix,'positions':[j,j+1],'source_rune_positions':[srcidx[j],srcidx[j+1]],'source_char_positions':[srcpos[j],srcpos[j+1]],'before':[carrier[j],carrier[j+1]]})
 return rows,jobs
def run(job,controls):
 name=f"swap-{job['job']:04d}";file=D/(name+'.json')
 if file.exists():return json.loads(file.read_text())
 control=controls[job['control']];x=list(control['carrier']);a,b=job['positions'];x[a],x[b]=x[b],x[a];t=time.monotonic();r=p.test(bytes(x));truecanon=p.canonical(bytes(control['truth']));retained=any(bool(valid) and bytes(g)==truecanon for g,valid in zip(r['groups'],r['valid']));assert not retained
 np.savez_compressed(D/(name+'.npz'),input=np.array(x,dtype=np.uint8),**r)
 out={**job,'compatible':bool(r['valid'].any()),'valid_groups':np.flatnonzero(r['valid']).tolist(),'original_necklace_retained':retained,'candidate_groups':len(r['groups']),'primary_rows':len(x),'seconds':time.monotonic()-t};file.write_text(json.dumps(out));return out
if __name__=='__main__':
 controls,jobs=inventory();mode=sys.argv[1]
 if mode=='pilot':
  (D/'inputs.json').write_text(json.dumps({'parser_path':str(source),'parser_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controls':controls,'jobs':jobs},indent=2));results=[run(j,controls) for j in jobs[:20]];elapsed=sum(x['seconds'] for x in results);size=sum((D/f"swap-{x['job']:04d}.npz").stat().st_size for x in results);out={'jobs':len(jobs),'pilot':20,'seconds':elapsed,'forecast_seconds':elapsed*len(jobs)/20,'pilot_bytes':size,'forecast_bytes':size*len(jobs)/20};(D/'pilot.json').write_text(json.dumps(out,indent=2));print(out)
 else:
  old=json.loads((D/'inputs.json').read_text());assert old['controls']==controls and old['jobs']==jobs;assert old['parser_sha256']==hashlib.sha256(source.read_bytes()).hexdigest();results=[]
  for job in jobs:
   p.guard();results.append(run(job,controls))
   if job['job']%100==0:print('job',job['job'],flush=True)
  summaries=[{'control':i,'length':len(c['carrier']),'swaps':sum(x['control']==i for x in results),'compatible':sum(x['compatible'] for x in results if x['control']==i),'source_necklace_retained':sum(x['original_necklace_retained'] for x in results if x['control']==i)} for i,c in enumerate(controls)];out={'rows':summaries,'jobs':len(jobs),'compatible':sum(x['compatible'] for x in results),'seconds':sum(x['seconds'] for x in results),'npz_bytes':sum((D/f"swap-{j['job']:04d}.npz").stat().st_size for j in jobs)};(D/'result.json').write_text(json.dumps(out,indent=2));print(out)
