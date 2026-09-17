import pathlib,sys,json,datetime,hashlib,itertools,numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];P=R/'exploration/persistent-02'
def guard():
 config=json.loads((P/'config.json').read_text());deadline=datetime.datetime.fromisoformat(config['deadline_utc'].replace('Z','+00:00'))
 assert not (P/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<deadline,'fixed research window stopped'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(name,data):(O/name).write_text(json.dumps(data,indent=2)+'\n')
def models():
 sys.path.insert(0,str(P/'decoder'));from compare import LM
 from complementary import LM as Other
 return [('p03',LM()),('complementary',Other())]
def load_table(name):
 with np.load(O/f'model-{name}.npz') as f:return f['L']
def pins():
 paths=['exploration/persistent-02/section/A07-inputs.json','exploration/persistent-02/section/inspection/major-marks/manifest.json','exploration/persistent-02/section/section-packet.json','exploration/persistent-02/decoder/fresh-controls.json','exploration/persistent-02/decoder/null-calibration-inputs.json','exploration/persistent-02/decoder/complementary-model.json','exploration/persistent-01/worker-c/p03_frozen.py','exploration/persistent-02/decoder/complementary.py','exploration/persistent-02/feedback/structured.py']
 return {p:digest(R/p) for p in paths}
