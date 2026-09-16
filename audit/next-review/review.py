"""Bounded independent NEXT-01 review; never decodes real puzzle slices."""
import pathlib,json,hashlib,importlib.util,itertools,difflib,datetime
from PIL import Image
R=pathlib.Path(__file__).resolve().parents[2]; O=pathlib.Path(__file__).resolve().parent
def read(p): return json.loads((R/p).read_text())
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
def module(p):
 s=importlib.util.spec_from_file_location('review_production',R/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
out={'started':datetime.datetime.now(datetime.timezone.utc).isoformat()}
A='audit/experiment-01/'
freeze=read(A+'FREEZE.json')
for n in ['preregistration','keys','fixtures','slices']: assert sha(A+n+'.json')==freeze[n+'_sha256']
logs=[read(str(p.relative_to(R))) for p in (R/A/'runs').glob('*/command.json')]
assert freeze['created_utc'] < read(A+'runs/20260916T180424.181107Z-positive-pilot/command.json')['started_utc']
assert freeze['created_utc'] < read(A+'runs/20260916T180521.681117Z-experiment-01-main/command.json')['started_utc']
pilot=read(A+'outputs/20260916T180424.220919Z/summary.json'); main=read(A+'outputs/20260916T180521.719679Z/summary.json')
rows=pilot['executed']+main['executed']; assert [r['ordinal'] for r in rows]==list(range(67))
assert all(r['passed'] for r in rows[:-1]) and not rows[-1]['passed']
assert main['outcome']=='BLOCKED_BY_POSITIVE_CONTROL'
casepaths=sorted((R/A/'outputs').glob('*/case-*.json')); assert len(casepaths)==67
keys=read(A+'keys.json'); sk=module('liber-primus/analysis/campaign18_skip/skipdecode.py')
checked=[]
for ordinal in [0,20,40,65,66]:
 p=next(p for p in casepaths if p.name==f'case-{ordinal:03d}.json');c=json.loads(p.read_text()); recipe=c['cell']['recipe']; sign=c['cell']['sign']; K=keys[recipe]
 for page,P in enumerate(c['plaintext']):
  enc,_,used=sk.encipher_keyskip(P,K,sign=sign,supp=.83 if c['cell']['model']=='rejection_beam' else 0,seed=c['seed_per_page'][page])
  assert enc==c['ciphertext'][page]
  assert used==[t['accepted_key_index'] for t in c['encryption_state_trace'][page]]
 results=[]
 for q in c['choices']:
  f=sk.beam_decode if q['mode']=='beam' else sk.rigid_decode
  got=f(c['ciphertext'][q['page']],keys[q['recipe']],sign=q['sign'],o=0)
  assert all(q[k]==v for k,v in got.items())
  if q['recipe']==recipe and q['sign']==sign and q['mode']==c['required_mode']:
   results.append({'page':q['page'],'exact':got['plain_idx']==c['plaintext'][q['page']],'score':got['score'],'wrong':[i for i,(a,b) in enumerate(zip(got['plain_idx'],c['plaintext'][q['page']])) if a!=b]})
 checked.append({'ordinal':ordinal,'production_choices_checked':len(c['choices']),'required':results})
out['A']={'frozen_hashes_match':True,'executed_ordinal_range':[0,66],'selected_production_reruns':checked,'phase_outputs':sorted(str(p.relative_to(R)) for p in (R/A/'outputs').rglob('*') if p.is_file() and 'case-' not in p.name)}
C='audit/f-interruption-01/'
pilotc=read(C+'results/20260916T180408.121651Z-pilot.json'); mainc=read(C+'results/20260916T180434.839675Z-main.json')
allcases=pilotc['cases']+mainc['cases'];count=0
for row in allcases:
 c=row['fixture'];F=[i for i,v in enumerate(c['cipher']) if v==0]; independent=[]
 for bits in itertools.product([False,True],repeat=len(F)):
  path=[i for i,b in zip(F,bits) if b]; j=0;plain=[]
  for i,v in enumerate(c['cipher']):
   if i in path:plain.append(0)
   else:plain.append((v-c['key'][j])%29);j+=1
  independent.append((tuple(path),tuple(plain),j))
 retained=[(tuple(s['path']),tuple(s['plain']),s['used']) for s in row['exhaustive']]
 assert sorted(independent)==sorted(retained);count+=len(independent)
 for b in row['beams']:
  assert all((tuple(s['path']),tuple(s['plain']),s['used']) in independent for s in b['final_states'])
ref=next(x for x in pilotc['reference'] if x['name']=='jpg107-167')
assert ref['trace'][49]['key_before']==49 and ref['trace'][49]['key_after']==49 and ref['trace'][49]['plain']==0
assert ref['trace'][50]['key_before']==49
before=R/C/'runs/20260916T180418.984354Z-main/code/audit/f-interruption-01/check.py';after=R/C/'check.py'
diff=list(difflib.unified_diff(before.read_text().splitlines(),after.read_text().splitlines()))
assert before.read_text().replace('W A L K F','W A L C F')==after.read_text()
out['C']={'independently_enumerated_paths':count,'reference_handcheck_positions':ref['trace'][48:52],'tiny_case':allcases[0]['fixture'],'fixture_repair_diff':diff}
B='audit/alphanumeric-01/'
t=read(B+'v1/transcription.json'); cells=t['cells'];abc='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx'
payload=bytes(60*abc.index(c['token'][0])+abc.index(c['token'][1]) for c in cells)
assert hashlib.sha256(payload).hexdigest()=='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290'
for rec in read(B+'v1-review/prior-artifacts.json'): assert sha(rec['path'])==rec['sha256']
source=read(B+'v1/sources.json')['image49']; assert sha(source['path'])==source['sha256']
crop=[1320,2070,1520,2260]; path=O/'p49-index45-context.png'; Image.open(R/source['path']).crop(crop).save(path)
out['B']={'tokens':len(cells),'conditional_payload_hash':hashlib.sha256(payload).hexdigest(),'image_source':source,'crop_rectangle':crop,'site':cells[45],'prior_manifest_hashes_verified':True}
out['finished']=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (O/'checks.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(out,indent=2))
