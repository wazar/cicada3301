"""PERSISTENT-02 Q12 extension: unchanged arithmetic/model; isolated output/guard."""
import os
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']: os.environ[name]='1'
import importlib.util,pathlib,json,datetime,hashlib,ast,random,sys,time,numpy as np
O=pathlib.Path(__file__).resolve().parent; R=O.parents[2]; OLD=R/'exploration/persistent-01/coordinator/Q12-sum-autokey'
spec=importlib.util.spec_from_file_location('q12',OLD/'test.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
CONFIG=json.loads((O.parent/'config.json').read_text()); DEADLINE=datetime.datetime.fromisoformat(CONFIG['deadline_utc'].replace('Z','+00:00'))
def guard():
 assert not (O.parent/'STOP').exists(),'PERSISTENT-02 STOP requested'
 assert datetime.datetime.now(datetime.timezone.utc)<DEADLINE,'fixed window ended'
q.guard=guard
q.O=O/'C01';q.O.mkdir(exist_ok=True)
PAGES=json.loads((R/'exploration/persistent-01/worker-f/F06-maps.json').read_text())
ELIGIBLE=[p['page'] for p in PAGES if p['page'] not in CONFIG['reserved_originals'] and p['page'] not in [0,17,55]]
def packet(page):
 p=next(p for p in PAGES if p['page']==page)
 return dict(name=f'actual{page}',cipher=p['indices'],ends=[w['end']-1 for w in p['words']],source=p)
def pilot():
 guard();src=R/'liber-primus/analysis/round12/C1/feedback.py';tree=ast.parse(src.read_text());wanted={'f_sum','_prime_hist','decode','encipher'};defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted];assert len(defs)==4
 ns={'N':29,'PRIMES':list(range(29))};exec(compile(ast.Module(body=defs,type_ignores=[]),str(src)+'::arithmetic-only','exec'),ns)
 rng=random.Random(2026091701);rows=[];maximum=0
 for k in [2,3,4,5,6,8,12]:
  for rep in range(12):
   p=[rng.randrange(29) for _ in range(5*(k+1)+7)];s=[rng.randrange(29) for _ in range(k)];bad=[(s[i]+(1 if i==rep%k else 0))%29 for i in range(k)]
   c=ns['encipher'](p,ns['f_sum'],k,s,source='pt',sign=-1);assert c==q.enc(p,s)
   assert ns['decode'](c,ns['f_sum'],k,s,source='pt',sign=-1)==p
   wrong=ns['decode'](c,ns['f_sum'],k,bad,source='pt',sign=-1);err=[(a-b)%29 for a,b in zip(wrong,p)];assert any(err) and sum(err[:k+1])%29==0
   assert all(x==err[i%(k+1)] for i,x in enumerate(err));assert all((c[i]-c[i-1])%29==(p[i]-p[i-k-1])%29 for i in range(k+1,len(c)))
   rows.append(dict(k=k,plain=p,seed=s,wrong_seed=bad,cipher=c,error=err))
 for k in [2,3,4]:
  c=[rng.randrange(29) for _ in range(31)];ends={4,11,12,30};v=q.scores(q.table(q.decode(c,[0]*k),ends,k),k)/35
  idxs=range(29**k) if k==2 else [rng.randrange(29**k) for _ in range(200)]
  for idx in idxs:
   direct=q.lm.score(q.decode(c,((-q.OFF[k][idx,:k])%29).tolist()),ends);maximum=max(maximum,abs(float(v[idx])-direct))
  assert maximum<1e-11
 out=dict(passed=True,inherited_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),inherited_functions=sorted(wanted),note='f_sum ignores prime-history values; dummy table does not alter checked sum arithmetic',examples=rows,score_max_abs_error=maximum,eligible=ELIGIBLE,existing=[0,17,55],reserved=CONFIG['reserved_originals'])
 (q.O/'independent-arithmetic.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='examples'}),flush=True)
 q.search(packet(1))
def compact_null(name):
 path=q.O/(name+'.npz');meta=q.O/(name+'.json');x=json.loads(meta.read_text())
 with np.load(path) as a:
  if 'k2_scores' not in a.files:return
  manifest={key:dict(shape=list(a[key].shape),dtype=str(a[key].dtype),sha256_raw_C=hashlib.sha256(a[key].tobytes(order='C')).hexdigest()) for key in a.files if key.endswith('_scores')}
  keep={key:a[key] for key in a.files if not key.endswith('_scores')}
 np.savez_compressed(path,**keep);x['reconstructable_score_arrays']=manifest;x['reconstruction']='scores(k_factors,k)/(len(cipher)+len(ends)); frozen Q12 OFF ordering';meta.write_text(json.dumps(x,separators=(',',':'))+'\n')
def run(pages):
 for page in pages:
  assert page in ELIGIBLE;guard();d=packet(page);main=q.search(d);ns=[]
  for j in range(19):
   seed=2026091700+100*page+j;ns.append(q.search(d,f'actual{page}-null{j:02}',q.null(d['cipher'],seed),seed));compact_null(f'actual{page}-null{j:02}')
  row=dict(page=page,length=len(d['cipher']),boundaries=len(d['ends']),maximum=main['maximum'],nulls=19,tail=(1+sum(r['maximum']>=main['maximum'] for r in ns))/20,total_seeds=20*732511,search_seconds=sum(r['seconds'] for r in [main]+ns))
  (q.O/f'actual{page}-summary.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='pilot':pilot()
 elif sys.argv[1]=='pages':run(list(map(int,sys.argv[2:])))
 elif sys.argv[1]=='inventory':print(ELIGIBLE)
