import extend as ex
from literal_feedback import Engine,encode
import json,random,pathlib,hashlib,resource,sys
O=ex.O/'C05';O.mkdir(exist_ok=True)
def prepare():
 sources=[]
 for ix in range(4):
  d=ex.q.packet(ix);sources.append(dict(id='held-'+str(ix),truth=d['truth'],ends=d['ends'],source=d['source']))
 src=ex.R/'exploration/persistent-02/decoder/fresh-controls.json';fresh=json.loads(src.read_text())
 for case in fresh['cases']:sources.append(dict(id=case['id'],truth=case['truth'],ends=case['ends'],source=dict(packet=str(src.relative_to(ex.R)),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),source_id=case['source'],rune_span=case['source_rune_span'])))
 rng=random.Random(2026092102);cases=[]
 for s in sources:
  for k in [2,3]:
   seed=[rng.randrange(29) for _ in range(k)];literal=[i for i,v in enumerate(s['truth']) if v==0 and rng.random()<.5];c=encode(s['truth'],seed,literal)
   cases.append(dict(**s,k=k,seed=seed,literal_positions=literal,cipher=c))
 path=O/'plants.json';assert not path.exists();path.write_text(json.dumps(dict(rng_seed=2026092102,cases=cases),separators=(',',':'))+'\n');print('frozen',len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
def run(ix):
 ex.guard();path=O/f'plant{ix:02}.json'
 if path.exists():return
 d=json.loads((O/'plants.json').read_text())['cases'][ix];result=Engine(d['k'],ex.q.L).solve(d['cipher'],set(d['ends']),retain=16,block=32);norm=len(d['cipher'])+len(d['ends']);truthscore=ex.q.lm.score(d['truth'],set(d['ends']))*norm;assert result['maximum']>=truthscore-1e-9
 for alt in result['alternatives']:
  assert all(x is not None for x in alt['seed']);assert encode(alt['plain'],alt['seed'],alt['literal_positions'])==d['cipher'];assert abs(ex.q.lm.score(alt['plain'],set(d['ends']))*norm-alt['total'])<2e-9
 top=result['alternatives'][0];row=dict(index=ix,id=d['id'],k=d['k'],result=result,truth_score=truthscore,truth_gap=result['maximum']-truthscore,selected_rune_errors=sum(a!=b for a,b in zip(top['plain'],d['truth'])),selected_seed=top['seed'],truth_seed=d['seed'],literal_count=len(d['literal_positions']),ordinary_cipher_F=sum(v==0 for i,v in enumerate(d['cipher']) if i not in d['literal_positions']),truth_in_retained_representatives=any(a['plain']==d['truth'] and a['literal_positions']==d['literal_positions'] for a in result['alternatives']),peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 path.write_text(json.dumps(row,separators=(',',':'))+'\n');print(json.dumps({k:v for k,v in row.items() if k!='result'}),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:
  for ix in map(int,sys.argv[1:]):run(ix)
