import n01 as n
import numpy as np,json,gzip
O=n.O;rng=np.random.default_rng(33011402);n.rng=np.random.default_rng(33011403)
def main():
 n.check()
 with gzip.open(O/'N01-evidence.json.gz','rt') as f:real=json.load(f)
 cs=[np.array(p['indices']) for p in real['real']];lengths=[len(c) for c in cs]
 r=real['result']; direct=[]
 for model in r['models']:
  sums=[0.,0.];base=np.array(r['baseline']);alt=np.array(model['probabilities']);lam=r['repeat_weight']
  for c,mp in zip(cs,model['maps']):
   for part,k in [('validation',0),('test',1)]:
    for j in mp[part]:
     i=mp['pair_starts'][j];label=mp['pair_labels'][j];weights=np.ones(841)
     if i>0:weights[np.arange(841)//29==c[i-1]]=lam
     ap=alt*weights;bp=base*weights;ap/=ap.sum();bp/=bp.sum();sums[k]+=float(np.log(ap[label]/bp[label]))
  assert np.allclose(sums,[r['validation'][model['phase']],r['test'][model['phase']]])
  direct.append(sums)
 with gzip.open(O/'N01-control-0-0-0.json.gz','rt') as f:a=json.load(f)
 with gzip.open(O/'N01-control-1-0-0.json.gz','rt') as f:b=json.load(f)
 sources=a['sources']+b['sources'];flat=np.array(sum([s['runes'] for s in sources],[]));N=sum(lengths);assert N<=len(flat)
 rows=[]
 for panel,start in enumerate([0,len(flat)-N]):
  cut=np.cumsum([0]+lengths);parts=[flat[start+cut[j]:start+cut[j+1]] for j in range(5)]
  for phase in [0,1]:
   for key in range(3):
    perm=rng.permutation(841);inverse=np.argsort(perm);enc=[];maps=[]
    for src in parts:
     ix=np.arange(phase,len(src)-1,2);orig=29*src[ix]+src[ix+1];lab=perm[orig];assert np.array_equal(inverse[lab],orig)
     c=rng.integers(29,size=len(src));c[ix]=lab//29;c[ix+1]=lab%29;enc.append(c);maps.append({'source_pair_starts':ix.tolist(),'dummy_positions':sorted(set(range(len(src)))-set(ix.tolist())-set((ix+1).tolist()))})
    for mode in ['pure','replace_repeat_83pct']:
     cc=[c.copy() for c in enc];changes=[]
     if mode!='pure':
      for c in cc:
       ch=[]
       for j in range(1,len(c)):
        if c[j]==c[j-1] and rng.random()<.83:
         old=int(c[j]);v=int(rng.integers(28));c[j]=v+(v>=old);ch.append([j,old,int(c[j])])
       changes.append(ch)
     result=n.evaluate(cc,99);row={'panel':panel,'source_global_start':start,'lengths':lengths,'phase':phase,'key':key,'mode':mode,'permutation':perm.tolist(),'source_maps':maps,'cipher':[c.tolist() for c in cc],'changes':changes,'result':result}
     with gzip.open(O/f'N02-{panel}-{phase}-{key}-{mode}.json.gz','wt') as f:json.dump(row,f)
     rows.append({k:row[k] for k in ['panel','phase','key','mode']}|{k:result[k] for k in ['statistic','p','selected_phase']}|{'repeat_rate':sum(np.sum(c[1:]==c[:-1]) for c in cc)/sum(len(c)-1 for c in cc),'changes':sum(map(len,changes))});print(json.dumps(rows[-1]),flush=True)
 uniform=[]
 for j in range(12):
  cc=[rng.integers(29,size=x) for x in lengths];res=n.evaluate(cc,99)
  with gzip.open(O/f'N02-uniform-{j}.json.gz','wt') as f:json.dump({'cipher':[c.tolist() for c in cc],'result':res},f)
  uniform.append({k:res[k] for k in ['statistic','p','selected_phase']})
 out={'seeds':[33011402,33011403],'sources':sources,'source_concat_length':len(flat),'panel_length':N,'panel_overlap':max(0,2*N-len(flat)),'lengths':lengths,'scalar_replay':direct,'controls':rows,'uniform':uniform,'counts':{'control_procedures':36,'null_procedures':3564,'total_model_fits':7200,'new_real_tests':0}}
 (O/'N02-summary.json').write_text(json.dumps(out,indent=2));print('DONE',lengths,len(flat),N,flush=True)
if __name__=='__main__':main()
