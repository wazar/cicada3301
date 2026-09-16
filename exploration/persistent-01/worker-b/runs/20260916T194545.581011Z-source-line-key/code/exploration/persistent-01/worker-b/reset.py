import pathlib,json,random,math,time,importlib.util
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('bsearch',OUT/'search.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
hold=set(b.load('exploration/persistent-01/config.json')['reserved_original_pages'])
data={p['original_page']:[np.array(l['indices']) for l in p['lines'] if l['indices']] for p in b.load('audit/parallel-01/inputs/dataset.json')['pages'] if p['original_page'] not in hold and p['original_page']<=55}
def score(pages):
 out=[];sum_delta=sum_var=0
 for p,lines in pages.items():
  delta=var=hits=pairs=0
  hist=[np.bincount(a,minlength=29)/len(a) for a in lines]
  for i,a in enumerate(lines[::2]):
   for j,c in enumerate(lines[1::2]):
    n=min(len(a),len(c));observed=int(np.sum(a[:n]==c[:n]));base=float(np.sum(hist[2*i]*hist[2*j+1]));delta+=observed-n*base;var+=n*base*(1-base);hits+=observed;pairs+=n
  sum_delta+=delta;sum_var+=var;out.append(dict(page=p,z=delta/math.sqrt(var) if var else 0,hits=hits,pairs=pairs))
 out.append(dict(page='pooled',z=sum_delta/math.sqrt(sum_var) if sum_var else 0))
 return sorted(out,key=lambda x:x['z'],reverse=True)
def shifted(pg,rng):return {p:[np.roll(l,int(rng.integers(len(l)))) for l in lines] for p,lines in pg.items()}
def main():
 start=time.monotonic();rng=np.random.default_rng(9200901);real=score(data);null=[score(shifted(data,rng))[0]['z'] for _ in range(499)]
 source=ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt';plain=np.array([b.old.ABC.index(r) for r in source.read_text() if r in b.old.ABC]);controls=[]
 for mode in ('line_reset','continuous'):
  for rep in range(10):
   pg={}
   for p,lines in data.items():
    stream=np.resize(np.roll(plain,int(rng.integers(len(plain)))),sum(map(len,lines)));key=rng.integers(29,size=len(stream));pos=0;pg[p]=[]
    for l in lines:
     n=len(l);k=key[:n] if mode=='line_reset' else key[pos:pos+n];pg[p].append((stream[pos:pos+n]+k)%29);pos+=n
   observed=score(pg);nn=[score(shifted(pg,rng))[0]['z'] for _ in range(19)];controls.append(dict(mode=mode,rep=rep,max=observed[0],pooled=next(z for z in observed if z['page']=='pooled'),null_maxima=nn,p=(1+sum(z>=observed[0]['z'] for z in nn))/20))
 b.save('reset-results.json',dict(real=real,null_maxima=null,p_max=(1+sum(z>=real[0]['z'] for z in null))/500,controls=controls,seed=9200901,seconds=time.monotonic()-start,page_count=len(data),line_count=sum(map(len,data.values()))));print(real[0],(1+sum(z>=real[0]['z'] for z in null))/500)
if __name__=='__main__':main()
