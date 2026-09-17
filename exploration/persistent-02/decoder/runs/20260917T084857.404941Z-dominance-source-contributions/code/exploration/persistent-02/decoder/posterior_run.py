import argparse,json,gzip,hashlib,time
from compare import O,LM,references,section
from complementary import LM as OtherLM
from posterior import analyze,beam_pool,mass

def read(folder,name):return json.loads(gzip.decompress((O/folder/(name+'.json.gz')).read_bytes()))
def save_pool(pool):
 return [dict(total=p['total'],literal_positions=p['literal_positions'],used=p['used'],plaintext_sha256=hashlib.sha256(bytes(p['plain'])).hexdigest()) for p in pool]
def cases(mode,model):
 if mode=='section':
  folder='section' if model=='p03' else 'complementary-section'
  for c in section():
   prior=read(folder,c['id']);yield c,[249,515] if c['policy']=='body' else [262,528],prior['exact']
 elif mode=='references':
  folder='references' if model=='p03' else 'complementary-references'
  for c in references():
   prior=read(folder,c['id']);yield c,[len(c['cipher'])//2],prior['exact']
 else:
  for c0 in json.loads((O/'continuation-inputs.json').read_text())['cases']:
   c=dict(c0,ends=c0['ends_primary']);prior=read('continuation',model+'-'+c['id']);yield c,[c['prefix_length']],prior['joint']

def run(c,cuts,prior,lm):
 cipher=c['cipher'];key=c['key'];sign=c.get('sign',-1);periodic=c.get('periodic',True);ends=set(c['ends']);t=time.monotonic();posterior=analyze(cipher,key,lm.extend,sign=sign,periodic=periodic,ends=ends,cuts=cuts)
 pools={}
 for width in [64,256,1024]:
  tick=time.monotonic();pool=beam_pool(cipher,key,lm,sign=sign,periodic=periodic,ends=ends,width=width);pools[str(width)]=dict(pool_mass=mass(pool,posterior['log_partition']),returned16_mass=mass(pool[:16],posterior['log_partition']),terminal_paths=save_pool(pool),seconds=time.monotonic()-tick)
 prefix=[]
 for cut in cuts:
  pre=analyze(cipher[:cut],key,lm.extend,sign=sign,periodic=periodic,ends={i for i in ends if i<cut},cuts=[cut]);prefix.append(dict(cut=cut,posterior=pre))
 return dict(id=c['id'],cipher=cipher,key=key,sign=sign,periodic=periodic,ends=sorted(ends),full=posterior,prefix_only=prefix,exact_top16_mass=mass(prior[:16],posterior['log_partition']),exact_retained_mass=mass(prior,posterior['log_partition']),exact_retained_paths=save_pool(prior),beams=pools,seconds=time.monotonic()-t,conditioning='All reported distributions conditional on this fixed key/sign/phase and supplied boundaries. Prefix-only has no future weights; full uses whole available text. No key-prior mixing.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['references','fresh','section']);a=ap.parse_args();out=O/('posterior-'+a.mode);out.mkdir(exist_ok=True)
 for name,lm in [('p03',LM()),('complementary',OtherLM())]:
  for c,cuts,prior in cases(a.mode,name):
   result=run(c,cuts,prior,lm);(out/(name+'-'+c['id']+'.json.gz')).write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0));print(json.dumps(dict(model=name,id=c['id'],logz=result['full']['log_partition'],paths=result['full']['number_of_legal_decision_paths'],top16_mass=result['exact_top16_mass']['mass'],beam_pool_mass={w:v['pool_mass']['mass'] for w,v in result['beams'].items()},seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
