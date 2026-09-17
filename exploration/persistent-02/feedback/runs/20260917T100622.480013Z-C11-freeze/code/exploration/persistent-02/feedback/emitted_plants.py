import extend as ex
from emitted_feedback import Engine,encode,Refused
import reset_plants as rp
import json,hashlib,sys,resource,time
O=ex.O/'C11';O.mkdir(exist_ok=True)
def decode(c,seed,literal,include):
 literal=set(literal);hist=[];out=[];phase=0;k=len(seed)
 for i,x in enumerate(c):
  if i in literal:p=0
  else:key=seed[phase] if phase<k else sum(hist[-k:]);p=(x-key)%29;phase+=1
  if include or i not in literal:hist.append(p)
  out.append(p)
 return out
def prepare():
 src=ex.O/'C05/plants.json';old=json.loads(src.read_text());cases=[]
 for d in old['cases']:
  row=dict(d);row['old_cipher']=d['cipher'];row['cipher']=encode(d['truth'],d['seed'],d['literal_positions']);assert decode(row['cipher'],d['seed'],d['literal_positions'],True)==d['truth'];row['old_transition_on_new_errors']=sum(a!=b for a,b in zip(decode(row['cipher'],d['seed'],d['literal_positions'],False),d['truth']));row['new_transition_on_old_errors']=sum(a!=b for a,b in zip(decode(d['cipher'],d['seed'],d['literal_positions'],True),d['truth']));cases.append(row)
 path=O/'plants.json';assert not path.exists();path.write_text(json.dumps(dict(source=str(src.relative_to(ex.R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),cases=cases),separators=(',',':'))+'\n');print('frozen',len(cases))
def run(ix,name):
 ex.guard();path=O/f'{name}-plant{ix:02}.json'
 if path.exists():return
 d=json.loads((O/'plants.json').read_text())['cases'][ix];L=rp.model(name);start=time.monotonic()
 try:
  r=Engine(d['k'],L).solve(d['cipher'],d['ends']);truth=rp.total(d['truth'],set(d['ends']),L);assert r['maximum']>=truth-1e-8
  for a in r['alternatives']:assert encode(a['plain'],a['seed'],a['literal_positions'])==d['cipher'];assert abs(rp.total(a['plain'],set(d['ends']),L)-a['total'])<1e-8
  out=dict(outcome='COMPLETE',index=ix,id=d['id'],k=d['k'],model=name,result=r,truth_gap=r['maximum']-truth,selected_rune_errors=sum(a!=b for a,b in zip(r['alternatives'][0]['plain'],d['truth'])),truth_in_retained=any(a['plain']==d['truth'] for a in r['alternatives']),old_transition_on_new_errors=d['old_transition_on_new_errors'],new_transition_on_old_errors=d['new_transition_on_old_errors'])
 except Refused as e:out=dict(outcome='UNRESOLVED_RESOURCE_REFUSAL',index=ix,id=d['id'],k=d['k'],model=name,error=str(e))
 out.update(seconds=time.monotonic()-start,peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);path.write_text(json.dumps(out,separators=(',',':'))+'\n');print(json.dumps({k:v for k,v in out.items() if k!='result'}),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:
  for ix in map(int,sys.argv[2:]):run(ix,sys.argv[1])
