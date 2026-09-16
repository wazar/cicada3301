import sys,pathlib,json,gzip
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import n01 as n
import numpy as np
O=pathlib.Path(__file__).resolve().parent;rng=np.random.default_rng(33011431);n.rng=np.random.default_rng(33011432)
PAIRS=[(0,1),(1,2),(2,3),(4,5),(5,6),(6,7)];IDS=[0,1,2,3,5,6,7,8]
def canonical(a):
 d={};out=[]
 for x in a:
  x=int(x)
  if x not in d:d[x]=len(d)
  out.append(d[x])
 return bytes(out)
def procedure(cs,detail=False):
 tabs=[]
 for c in cs:
  d={}
  for i in range(len(c)-11):d.setdefault(canonical(c[i:i+12]),[]).append(i)
  tabs.append(d)
 best=0;hits=0;matches=[];by=[]
 for a,b in PAIRS:
  local=0
  for pat,ii in tabs[a].items():
   for j in tabs[b].get(pat,[]):
    for i in ii:
     hits+=1;f={};g={};L=0
     for x,y in zip(cs[a][i:i+64],cs[b][j:j+64]):
      x=int(x);y=int(y)
      if (x in f and f[x]!=y) or (y in g and g[y]!=x):break
      f[x]=y;g[y]=x;L+=1
     assert L>=12;best=max(best,L);local=max(local,L)
     if detail:matches.append({'pages':[IDS[a],IDS[b]],'offsets':[i,j],'length':L,'partial_bijection':sorted(f.items()),'canonical_seed':list(pat)})
  by.append(local)
 out={'statistic':best,'seed_matches':hits,'pair_maxima':by}
 if detail:out['matches']=matches
 return out
def save(name,x):
 with gzip.open(O/name,'wt') as f:json.dump(x,f)
def main():
 n.check();cfg=json.loads((n.O.parent/'config.json').read_text());p=n.R/'audit/parallel-01/inputs/dataset.json';assert n.sha(p)==cfg['dataset_sha256'];assert not set(IDS)&set(cfg['reserved_original_pages'])
 pages=[p for p in json.loads(p.read_text())['pages'] if p['original_page'] in IDS];assert [p['original_page'] for p in pages]==IDS;cs=[np.array(p['indices']) for p in pages];real=procedure(cs,True)
 sims=[n.simulations(c,399) for c in cs];null=[]
 for b in range(399):
  if b%20==0:n.check()
  null.append(procedure([s[b] for s in sims]))
 pval=lambda v:(1+sum(x['statistic']>=v for x in null))/400
 real['p']=pval(real['statistic']);save('evidence.json.gz',{'seed':[33011431,33011432],'input_sha256':n.sha(p),'pages':pages,'pairs':[[IDS[a],IDS[b]] for a,b in PAIRS],'real':real,'null':null,'null_parameters':[{'q':n.fit([c])[0].tolist(),'repeat_weight':n.fit([c])[1]} for c in cs]})
 print('REAL',real['statistic'],real['p'],real['pair_maxima'],flush=True)
 with gzip.open(n.O/'N01-control-0-0-0.json.gz','rt') as f:sources=json.load(f)['sources']
 src=np.array(sum([s['runes'] for s in sources],[]));rows=[]
 for register in ['matched_markov','solved_source']:
  for L in [16,24,40]:
   for rep in range(5):
    pair=PAIRS[rep%len(PAIRS)];a,b=pair;cc=[n.simulations(c,1)[0] for c in cs];i=int(rng.integers(len(cc[a])-L+1));j=int(rng.integers(len(cc[b])-L+1));source_start=None
    if register=='solved_source':source_start=int(rng.integers(len(src)-L+1));cc[a][i:i+L]=src[source_start:source_start+L]
    key=rng.permutation(29);cc[b][j:j+L]=key[cc[a][i:i+L]]
    assert canonical(cc[a][i:i+L])==canonical(cc[b][j:j+L])
    for error in [0,1]:
     dd=[c.copy() for c in cc];edit=None
     if error:
      pos=j+L//2;old=int(dd[b][pos]);v=int(rng.integers(28));dd[b][pos]=v+(v>=old);edit=[pos,old,int(dd[b][pos])]
     result=procedure(dd,True);result['p']=pval(result['statistic'])
     if not error:assert result['statistic']>=L
     row={'register':register,'length':L,'rep':rep,'errors':error,'pages':[c.tolist() for c in dd],'copy_pages':[IDS[a],IDS[b]],'offsets':[i,j],'key':key.tolist(),'source_start':source_start,'edit':edit,'result':result}
     save(f'control-{register}-{L}-{rep}-{error}.json.gz',row);rows.append({k:row[k] for k in ['register','length','rep','errors']}|{k:result[k] for k in ['statistic','p']})
 save('controls-sources.json.gz',{'sources':sources,'concat':src.tolist()})
 out={'real':{k:v for k,v in real.items() if k!='matches'},'controls':rows,'null_histogram':{str(k):sum(z['statistic']==k for z in null) for k in sorted(set(z['statistic'] for z in null))},'counts':{'real_procedures':1,'null_procedures':399,'control_procedures':60,'pairs_per_procedure':6,'real_seed_matches':real['seed_matches'],'real_offset_pairs':sum((len(cs[a])-11)*(len(cs[b])-11) for a,b in PAIRS)}}
 (O/'summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['null_histogram']),flush=True)
if __name__=='__main__':main()
