"""Reuse frozen B05 F-site/equality-mask nulls with A's unchanged prefix procedure."""
import pathlib,sys,json,gzip,hashlib,argparse
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];sys.path.insert(0,str(O));import a02 as A
sys.path.insert(0,str(R/'exploration/persistent-02/decoder'));from complementary import LM
PERIODIC=A.A.module('a06periodic','exploration/persistent-01/worker-c/frozen_kbest.py')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['p03','complementary'],required=True);ap.add_argument('--family',choices=['periodic','finite'],required=True);a=ap.parse_args();batch=f'A06-{a.model}-{a.family}';out=O/batch;out.mkdir(exist_ok=True);original=('A01' if a.family=='periodic' else 'A02') if a.model=='p03' else 'A05-'+a.family
 lm=A.A.M.LM() if a.model=='p03' else LM();A.A.K=PERIODIC if a.family=='periodic' else A.Finite
 packet=json.loads((O/'section-packet.json').read_text());src=R/'exploration/persistent-02/decoder/null-calibration-inputs.json';nulls=json.loads(src.read_text());assert len(nulls['packets'])==19
 whole=json.load(gzip.open(O/original/'actual-whole.json.gz','rt'));body=json.load(gzip.open(O/original/'actual-body.json.gz','rt'));assert whole['cipher']==packet['runes'] and body['cipher']==packet['runes'][13:];assert whole['ends']==packet['explicit_ends'] and body['ends']==packet['body']['explicit_ends'];assert whole['spans']==[[0,262],[262,528],[528,729]] and body['spans']==[[0,249],[249,515],[515,716]]
 # Original declared grid order, not previous score order.
 cells=[x['cell'] for x in whole['prefix_cells']];order={'WELCOME-DIVINITY':0,'KOAN-CIRCUMFERENCE':1,'primes':0,'totients-of-primes':1};cells.sort(key=lambda x:(order[x['key_id']],x['phase'],x['sign']));assert len(cells)==(42 if a.family=='periodic' else 4)
 records=[];results=[]
 for variant,actual in [('body',body),('whole',whole)]:
  for j,full in enumerate(nulls['packets']):
   assert len(full)==729 and [v==0 for v in full]==[v==0 for v in whole['cipher']];assert [v==w for v,w in zip(full,full[1:])]==[v==w for v,w in zip(whole['cipher'],whole['cipher'][1:])]
   c=full[13:] if variant=='body' else full;records.append(dict(variant=variant,replicate=j,first_actual=actual['cipher'][0],first_null=c[0],join_positions=[s[0] for s in actual['spans'][1:]],join_pairs=[[c[s[0]-1],c[s[0]]] for s in actual['spans'][1:]],cipher_sha256=hashlib.sha256(bytes(c)).hexdigest()))
   results.append(A.A.run(f'null-{variant}-{j:02}',c,set(actual['ends']),actual['spans'],lm,cells,resultdir=out))
 (out/'input-checks.json').write_text(json.dumps(dict(source=str(src.relative_to(R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),actual_source_batch=original,identities='exact actual arrays/ends/spans; nullFsites/equalitymask; no first-rune conditioning imposed',records=records),indent=2)+'\n');(out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
