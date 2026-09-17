from pathlib import Path
import zlib,json,hashlib,inspect,random,datetime
D=Path(__file__).parent;O=D.parent/'N18'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,25,tzinfo=datetime.timezone.utc)
def digest(b):return hashlib.sha256(b).hexdigest()
def compress(b,name):
 c=zlib.compress(b,level=9);assert zlib.decompress(c)==b;assert c==zlib.compress(b,level=9);(D/(name+'.zlib')).write_bytes(c);return {'bytes':len(b),'size':len(c),'input_sha256':digest(b),'compressed_sha256':digest(c),'file':name+'.zlib'}
api={'signature':str(inspect.signature(zlib.compress)),'doc':zlib.compress.__doc__,'build_version':zlib.ZLIB_VERSION,'runtime_version':zlib.ZLIB_RUNTIME_VERSION};(D/'api.json').write_text(json.dumps(api,indent=2))
periodic=bytes([0,1,2,3]*128);rg=random.Random(619001);aperiodic=bytes(rg.randrange(29) for _ in range(512));assert all(aperiodic!=aperiodic[i:]+aperiodic[:i] for i in range(1,512));(D/'tiny-periodic.bin').write_bytes(periodic);(D/'tiny-aperiodic.bin').write_bytes(aperiodic);tiny={'seed':619001,'periodic':compress(periodic,'tiny-periodic'),'aperiodic':compress(aperiodic,'tiny-aperiodic')};assert tiny['periodic']['size']<tiny['aperiodic']['size'];(D/'tiny.json').write_text(json.dumps(tiny,indent=2))
rows=[]
for i in range(4):
 packetpath=O/f'packet-{i}.json';path=O/f'packet-{i}-main.json';packet=json.loads(packetpath.read_text());main=json.loads(path.read_text());items=[];truth=bytes(packet['truth'])
 for out in main['outputs']:
  b=bytes(out['runes']);assert len(b)==len(truth);items.append({'sentinel_position':out['sentinel_position'],'is_truth':b==truth,**compress(b,f"control-{i}-position-{out['sentinel_position']}")})
 assert sum(x['is_truth'] for x in items)==1;tr=next(x for x in items if x['is_truth']);smaller=sum(x['size']<tr['size'] for x in items);ties=[x['sentinel_position'] for x in items if x['size']==tr['size']];minimum=min(x['size'] for x in items);best=[x['sentinel_position'] for x in items if x['size']==minimum];rows.append({'control':i,'packet_sha256':digest(packetpath.read_bytes()),'outputs_sha256':digest(path.read_bytes()),'truth_position':packet['truth_sentinel_position'],'items':items,'truth_competition_rank':1+smaller,'truth_ties':ties,'shortest_positions':best,'gate_pass':best==[packet['truth_sentinel_position']]})
gate=all(r['gate_pass'] for r in rows);result={'api':api,'rows':rows,'gate_pass':gate,'actual_or_null_scored':False,'scope':'All four controls only; full size vectors preserved.'};(D/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({'gate_pass':gate,'controls':[{'control':r['control'],'rank':r['truth_competition_rank'],'truth_ties':r['truth_ties'],'shortest_positions':r['shortest_positions'],'size_vector':[x['size'] for x in r['items']]} for r in rows]},indent=2))
# Passing gate only licenses a separately logged fixed continuation; this batch never scores actual/null.
