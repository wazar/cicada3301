import pathlib,json,hashlib,random
from fractions import Fraction
from header_controls import header_read
R=pathlib.Path(__file__).parent;P=R.parent/'worker-p/P11';mine=json.loads((R/'independent-results.json').read_text());rows=[]
for page,z in enumerate(mine):
 theirs=json.loads((P/f'actual-{page}.json').read_text());raw=(R/f'p{page}-eligible-bits.bin').read_bytes();assert raw==(P/f'actual-{page}-bits.packed').read_bytes();bits=''.join(f'{b:08b}' for b in raw)[:z['eligible_count']];h=header_read(bits);assert (h['width'],h['size'],h['available'])==(theirs['header']['width'],theirs['header']['length'],theirs['header']['capacity_bytes']);start=5+h['width'];available=bytes(int(bits[k:k+8],2) for k in range(start,start+8*h['available'],8));assert available==(P/f'actual-{page}-available-payload.bin').read_bytes();flushed=available[:len(available)//1024*1024];assert flushed==(P/f'actual-{page}-historical-sink.bin').read_bytes();st=theirs['sink'];assert st['open']==1 and st['buffer_bytes']==len(available)%1024 and st['fileindex']==len(available) and st['bitindex']==7-(len(bits)-start)%8
 prob=Fraction();minimal=Fraction()
 for width in range(32):
  availablebytes=(len(bits)-5-width)//8;end=min(2**width-1,availablebytes)
  prob+=Fraction(max(0,end),32*2**width)
  minimal+=Fraction(max(0,end-max(1,2**(width-1) if width else 1)+1),32*2**width)
 assert float(prob)==theirs['faircoin_probability_positive_capacity'] and float(minimal)==theirs['faircoin_probability_minimal_capacity'];rng=random.Random(330111+page)
 for null in theirs['null']:
  w=rng.getrandbits(5);n=rng.getrandbits(w) if w else 0;assert (w,n)==(null['width'],null['length']);assert null['positive_capacity']==(0<n<=(len(bits)-5-w)//8)
 rows.append({'page':page,'all_bits_and_available_payload_and_sink_flush_match':True,'exact_faircoin_probability':str(prob),'exact_minimal_probability':str(minimal),'header':h})
controls=json.loads((P/'controls.json').read_text());assert controls['status']=='PASS';assert len(controls['stream_controls'])==11 and len(controls['reader_probes'])==6;assert controls['stream_controls'][0]['source_bits']==0;assert controls['stream_controls'][0]['exact_coefficient_match']
out={'status':'PASS','actual':rows,'source_control_counts':{'stream':11,'reader':6,'jpeg':1},'python_source_sha256':hashlib.sha256((P.parent/'p11.py').read_bytes()).hexdigest(),'actual_summary_sha256':hashlib.sha256((P/'actual-summary.json').read_bytes()).hexdigest()};(R/'FINAL-CHECK.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
