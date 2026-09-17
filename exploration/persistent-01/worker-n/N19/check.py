from pathlib import Path
import zlib,json,hashlib,random
D=Path(__file__).parent;O=D.parent/'N18';r=json.loads((D/'result.json').read_text());checked=0
for row in r['rows']:
 i=row['control'];packetpath=O/f'packet-{i}.json';outputpath=O/f'packet-{i}-main.json';assert hashlib.sha256(packetpath.read_bytes()).hexdigest()==row['packet_sha256'];assert hashlib.sha256(outputpath.read_bytes()).hexdigest()==row['outputs_sha256'];p=json.loads(packetpath.read_text());out=json.loads(outputpath.read_text());items=[]
 for item,o in zip(row['items'],out['outputs']):
  b=bytes(o['runes']);assert item['sentinel_position']==o['sentinel_position'];assert hashlib.sha256(b).hexdigest()==item['input_sha256'];obj=zlib.compressobj(level=9);encoded=obj.compress(b[:len(b)//2])+obj.compress(b[len(b)//2:])+obj.flush();saved=(D/item['file']).read_bytes();assert encoded==saved==zlib.compress(b,level=9);assert len(saved)==item['size'] and hashlib.sha256(saved).hexdigest()==item['compressed_sha256'];assert zlib.decompress(saved)==b;assert item['is_truth']==(list(b)==p['truth']);checked+=1;items.append((o['sentinel_position'],len(encoded),item['is_truth']))
 true=next(x for x in items if x[2]);best=min(x[1] for x in items);assert row['truth_competition_rank']==1+sum(x[1]<true[1] for x in items);assert row['truth_ties']==[x[0] for x in items if x[1]==true[1]];assert row['shortest_positions']==[x[0] for x in items if x[1]==best];assert row['gate_pass']==(true[1]==best and sum(x[1]==best for x in items)==1)
tiny=json.loads((D/'tiny.json').read_text());rg=random.Random(tiny['seed']);assert (D/'tiny-aperiodic.bin').read_bytes()==bytes(rg.randrange(29) for _ in range(512));assert (D/'tiny-periodic.bin').read_bytes()==bytes([0,1,2,3]*128)
for name in ['periodic','aperiodic']:
 b=(D/f'tiny-{name}.bin').read_bytes();assert zlib.compress(b,level=9)==(D/f'tiny-{name}.zlib').read_bytes();assert len(zlib.compress(b,level=9))==tiny[name]['size']
assert r['gate_pass']==all(x['gate_pass'] for x in r['rows'])==False;assert r['actual_or_null_scored']==False
out={'PASS':True,'control_outputs':checked,'tiny_outputs':2,'all_gate_checks':False,'actual_or_null_scored':False,'streaming_and_one_shot_bytes_identical':True};(D/'verification.json').write_text(json.dumps(out,indent=2));print(out)
