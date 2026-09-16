import n03 as x
n=x.n;np=x.np;json=x.json;gzip=x.gzip;O=x.O
rng=np.random.default_rng(33011441);n.rng=np.random.default_rng(33011442)
def procedure(cs,detail=False):
 best=0;count=0;matches=[]
 for L in [24,40]:
  tabs=[];skip=L//2
  for c in cs:
   d={}
   for i in range(len(c)-L+1):
    w=np.r_[c[i:i+skip],c[i+skip+1:i+L]];d.setdefault(x.canonical(w),[]).append(i)
   tabs.append(d)
  for a,b in x.PAIRS:
   for pat,ii in tabs[a].items():
    for j in tabs[b].get(pat,[]):
     for i in ii:
      best=max(best,L);count+=1
      if detail:
       keep=[k for k in range(L) if k!=skip];f={int(cs[a][i+k]):int(cs[b][j+k]) for k in keep}
       assert len(set(f.values()))==len(f)
       matches.append({'length':L,'pages':[x.IDS[a],x.IDS[b]],'offsets':[i,j],'wildcard_relative':skip,'partial_bijection':sorted(f.items()),'wildcard_values':[int(cs[a][i+skip]),int(cs[b][j+skip])]})
 out={'statistic':best,'matches_count':count}
 if detail:out['matches']=matches
 return out
def main():
 n.check()
 with gzip.open(O/'evidence.json.gz','rt') as f:old=json.load(f)
 cs=[np.array(p['indices']) for p in old['pages']];real=procedure(cs,True);sims=[n.simulations(c,399) for c in cs];null=[]
 for b in range(399):
  if b%20==0:n.check()
  null.append(procedure([s[b] for s in sims]))
 pval=lambda v:(1+sum(z['statistic']>=v for z in null))/400
 real['p']=pval(real['statistic']);rows=[]
 for path in sorted(O.glob('control-*.json.gz')):
  with gzip.open(path,'rt') as f:r=json.load(f)
  result=procedure([np.array(c) for c in r['pages']],True);result['p']=pval(result['statistic']);rows.append({'source_file':path.name,**{k:r[k] for k in ['register','length','rep','errors']},'result':result})
 with gzip.open(O/'controls-sources.json.gz','rt') as f:src=np.array(json.load(f)['concat'])
 additional=[]
 for register in ['matched_markov','solved_source']:
  for rep in range(10):
   L=40;a,b=x.PAIRS[rep%6];cc=[n.simulations(c,1)[0] for c in cs];i=int(rng.integers(len(cc[a])-L+1));j=int(rng.integers(len(cc[b])-L+1));ss=None
   if register=='solved_source':ss=int(rng.integers(len(src)-L+1));cc[a][i:i+L]=src[ss:ss+L]
   key=rng.permutation(29);cc[b][j:j+L]=key[cc[a][i:i+L]];err=int(rng.integers(L));oldval=int(cc[b][j+err]);v=int(rng.integers(28));cc[b][j+err]=v+(v>=oldval)
   result=procedure(cc,True);result['p']=pval(result['statistic']);row={'register':register,'rep':rep,'copy_pages':[x.IDS[a],x.IDS[b]],'offsets':[i,j],'length':L,'source_start':ss,'key':key.tolist(),'error_relative':err,'old_value':oldval,'pages':[c.tolist() for c in cc],'result':result};additional.append(row)
 x.save('N04-evidence.json.gz',{'seeds':[33011441,33011442],'real':real,'null':null,'replayed_controls':rows,'additional_controls':additional})
 summary={'real':real,'null_histogram':{str(k):sum(z['statistic']==k for z in null) for k in sorted(set(z['statistic'] for z in null))},'replayed_controls':[{k:r[k] for k in ['register','length','rep','errors']}|{k:r['result'][k] for k in ['statistic','p']} for r in rows],'additional_controls':[{'register':r['register'],'error_relative':r['error_relative'],**{k:r['result'][k] for k in ['statistic','p']}} for r in additional],'counts':{'real':1,'null':399,'replayed_controls':60,'new_controls':20,'windows':[24,40],'pairs':6}}
 (O/'N04-summary.json').write_text(json.dumps(summary,indent=2));print('REAL',json.dumps(real),flush=True)
if __name__=='__main__':main()
