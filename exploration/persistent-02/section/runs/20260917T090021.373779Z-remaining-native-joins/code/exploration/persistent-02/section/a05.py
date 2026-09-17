"""Same frozen two-rule grids under B's one independent complementary model."""
import pathlib,sys,json,gzip,argparse,hashlib
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];sys.path.insert(0,str(O));import a02 as A
sys.path.insert(0,str(R/'exploration/persistent-02/decoder'));from complementary import LM
PERIODIC=A.A.module('oldkbest_for_a05','exploration/persistent-01/worker-c/frozen_kbest.py')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--family',choices=['periodic','finite'],required=True);ap.add_argument('--kind',choices=['controls','actual','nulls'],required=True);a=ap.parse_args();out=O/('A05-'+a.family);out.mkdir(exist_ok=True);lm=LM();original='A01' if a.family=='periodic' else 'A02';A.A.K=PERIODIC if original=='A01' else A.Finite
 cells=[]
 if original=='A01':
  for k in json.loads((O/'key-grid.json').read_text())['keys']:
   for phase in range(len(k['runes'])):
    for sign in [-1,1]:cells.append(dict(id=f"{k['id']}:{phase}:{sign}",key_id=k['id'],phase=phase,sign=sign,key=k['runes'][phase:]+k['runes'][:phase]))
 else:
  primes=A.A.REF.primes(800);cells=[dict(id=f'{name}:{sign}',key_id=name,phase=0,sign=sign,key=[(p-delta)%29 for p in primes]) for name,delta in [('primes',0),('totients-of-primes',1)] for sign in [-1,1]]
 models=['exploration/persistent-02/decoder/complementary.py','exploration/persistent-02/decoder/complementary-model.json'];(out/'model.json').write_text(json.dumps(dict(id='P02-complementary-v1',sources={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in models},grid_cells=len(cells),original_input_batch=original),indent=2)+'\n')
 if a.kind=='controls':names=['control-'+n for n in A.A.M.CHECK]
 elif a.kind=='actual':names=['actual-body','actual-whole']
 else:names=[f'null-{v}-{i:02}' for v in ['body','whole'] for i in range(19)]
 results=[]
 for name in names:
  d=json.load(gzip.open(O/original/(name+'.json.gz'),'rt'));results.append(A.A.run(name,d['cipher'],set(d['ends']),d['spans'],lm,cells,d.get('truth'),d.get('plant'),resultdir=out))
 (out/f'summary-{a.kind}.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
