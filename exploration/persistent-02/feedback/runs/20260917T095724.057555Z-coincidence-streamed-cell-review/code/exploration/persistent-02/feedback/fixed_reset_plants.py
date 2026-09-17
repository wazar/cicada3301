import reset_plants as rp
from fixed_reset import Engine,Refused
from reset_literal import encode
import extend as ex
import json,hashlib,resource,sys,time
O=ex.O/'C10';O.mkdir(exist_ok=True)
def prepare():
 src=ex.O/'C08/plants.json';kp=ex.R/'exploration/persistent-02/section/key-grid.json';keys=json.loads(kp.read_text())['keys'];cases=[]
 for d in json.loads(src.read_text())['cases']:
  for key in keys:
   row={k:d[k] for k in ['id','truth','ends','reset_before','literal_positions']};row.update(key_id=key['id'],seed=key['runes'],cipher=encode(d['truth'],key['runes'],d['literal_positions'],d['reset_before']));cases.append(row)
 p=O/'plants.json';assert not p.exists();p.write_text(json.dumps(dict(sources={str(x.relative_to(ex.R)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [src,kp]},cases=cases),separators=(',',':'))+'\n');print('frozen',len(cases))
def run(ix,name):
 ex.guard();path=O/f'{name}-plant{ix:02}.json'
 if path.exists():return
 d=json.loads((O/'plants.json').read_text())['cases'][ix];L=rp.model(name);start=time.monotonic()
 try:
  out=Engine(d['seed'],L).solve(d['cipher'],d['ends'],d['reset_before']);truth=rp.total(d['truth'],set(d['ends']),L);assert out['maximum']>=truth-1e-8
  for a in out['alternatives']:assert encode(a['plain'],a['seed'],a['literal_positions'],d['reset_before'])==d['cipher'];assert abs(rp.total(a['plain'],set(d['ends']),L)-a['total'])<1e-8
  row=dict(outcome='COMPLETE',index=ix,id=d['id'],key=d['key_id'],model=name,result=out,truth_gap=out['maximum']-truth,selected_rune_errors=sum(a!=b for a,b in zip(out['alternatives'][0]['plain'],d['truth'])),truth_in_retained=any(a['plain']==d['truth'] for a in out['alternatives']))
 except Refused as e:row=dict(outcome='UNRESOLVED_RESOURCE_REFUSAL',index=ix,id=d['id'],key=d['key_id'],model=name,error=str(e))
 row.update(seconds=time.monotonic()-start,peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);path.write_text(json.dumps(row,separators=(',',':'))+'\n');print(json.dumps({k:v for k,v in row.items() if k!='result'}),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:
  for ix in map(int,sys.argv[2:]):run(ix,sys.argv[1])
