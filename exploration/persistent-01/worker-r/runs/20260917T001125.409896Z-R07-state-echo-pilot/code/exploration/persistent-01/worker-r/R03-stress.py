import pathlib,json,gzip,time
p=pathlib.Path(__file__).resolve().parent;ns={'__file__':str(p/'R03.py')};exec((p/'R03.py').read_text().split('a=argparse.ArgumentParser()')[0],ns)
np=ns['np'];w=np.geomspace(1,100,29);w/=w.sum();out=[];t=time.monotonic()
with gzip.open(p/'R03-stress-full.jsonl.gz','wt') as f:
 for i in range(2):
  iv=ns['inversion'](484010+i) if i==0 else None;vs=ns['generate'](w,484001+i,iv);z=ns['experiment'](vs,4841000+1000*i,19,f,str(i),iv);z['planted']=i==0;out.append(z);print(i,z['held_stat'],z['p_lower'],z.get('true_pairs_recovered'))
(p/'R03-stress-results.json').write_text(json.dumps(dict(panels=out,seconds=time.monotonic()-t),indent=2)+'\n')
