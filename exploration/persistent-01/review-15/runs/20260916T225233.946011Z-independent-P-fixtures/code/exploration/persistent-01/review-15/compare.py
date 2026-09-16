import importlib.util,pathlib,json
from independent import inspect
R=pathlib.Path(__file__).parent;p=R.parent/'worker-p/p10.py';spec=importlib.util.spec_from_file_location('worker_p_p10',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
results=[]
paths=[pathlib.Path(f'liber-primus/data/relikd/p{x}.jpg') for x in [0,1]]+sorted((R/'fixtures').glob('*-[02]*.jpg'))
for path in paths:
 a=inspect(path);b,raw,tail,coef=mod.parse(path.read_bytes());assert a['mcus']==b['mcus'];assert a['dc_symbols']==b['blocks'];assert a['consumed_bits']==b['entropy_bits'];assert a['eoi_offset']==b['eoi_offset'];assert a['last_required_rawbyte']==b['final_data_byte_offset'];assert len(a['final_pad_bits'])==b['pad_bits'];assert b['pad_value']==int(a['final_pad_bits'] or '0',2);assert a['tail_unstuffed_hex']==tail.hex();assert a['stuffed_ff_count']==len(b['entropy_stuffed_zero_offsets'])+len(b['tail_stuffed_zero_offsets']);results.append({'path':str(path),'entropy_bits':a['consumed_bits'],'blocks':a['dc_symbols'],'tail_bytes':len(tail),'agreement':True})
(R/'comparison.json').write_text(json.dumps(results,indent=2));print(json.dumps({'compared':len(results),'all_exact':True}))
