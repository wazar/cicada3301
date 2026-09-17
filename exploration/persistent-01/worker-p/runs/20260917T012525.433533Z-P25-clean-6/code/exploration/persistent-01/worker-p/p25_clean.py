from pathlib import Path
import importlib.util,sys,json,hashlib
import numpy as np
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original_p25',HERE/'p25.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
OLD=HERE/'P25';CLEAN=HERE/'P25-clean';MODEL=p.B/'coordinator/Q05-latin-clean/model.npz'
assert hashlib.sha256(MODEL.read_bytes()).hexdigest()=='f4667652da86ab021af47cfcba098226454415a809ff3b1ecce84a1b4023e92e'
assert p.load(p.Q/'held-controls.json.gz')==p.load(MODEL.parent/'held-controls.json.gz')
class CleanLM(p.LM):
 def __init__(self):self.logp=np.load(MODEL)['logp'].tolist()
p.LM=CleanLM;p.P=CLEAN
original_packet=p.packet
def fixedpacket(ix):
 data=original_packet(ix);assert data==json.loads((OLD/f'packet-{ix}.json').read_text());return data
p.packet=fixedpacket
original_search=p.search
def fixedsearch(name,data,c=None,seed=None):
 old=p.load(OLD/(name+'.json.gz'));assert old['cipher']==(data['cipher'] if c is None else c) and old['ends']==data['ends'] and old['null_seed']==seed
 return original_search(name,data,c,seed)
p.search=fixedsearch
assert p.cells()==json.loads((OLD/'keys.json').read_text())
p.guard()
if sys.argv[1]=='prepare':p.tiny();p.save('keys.json',p.cells())
else:p.run(int(sys.argv[1]))
