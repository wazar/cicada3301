import pathlib,json,gzip,hashlib,random
R=pathlib.Path(__file__).resolve().parent;O=R/'P18'
load=lambda n:json.load(gzip.open(O/(n+'.json.gz'),'rt'))
km=load('key-map');key=km['key'];names=['control-'+str(i) for i in range(4)]+['real-0','null-0','real-17','null-17'];summary=[];tokens='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
for name in names:
 r=load(name+'-aggregate');a=r['top16'][0];f=r['packet'];batch=load(name+'-batch-0');maps=[]
 for job in a['aliases']:
  maps.append(dict(**job,consumed=a['used'],key_rune_interval=[job['offset'],job['offset']+a['used']],first=km['map'][job['offset']],last=km['map'][job['offset']+a['used']-1]))
 row=dict(name=name,n=len(f['cipher']),cipher_F=f['cipher'].count(0),adjacent_repeats=sum(x==y for x,y in zip(f['cipher'],f['cipher'][1:])),cells=r['cells'],feasible=r['feasible'],best_score=r['best_score'],rerun_cells=r['rerun_cells'],seconds=batch['seconds'],compressed_bytes=batch['bytes'],best_source_maps=maps,literal_F_count=len(a['literal_positions']))
 if 'truth' in f:row.update({k:r[k] for k in ['truth_job_score_rank','best_errors','key_recovered','literal_path_recovered','truth_global_ranks']})
 summary.append(row)
 ends=set(f['ends']);out=[]
 for rank,alt in enumerate(r['top16'],1):
  text=''.join(tokens[v]+(' ' if i in ends else '') for i,v in enumerate(alt['plain']));out.append('Rank '+str(rank)+' score '+str(alt['score'])+' aliases '+json.dumps(alt['aliases'])+'\n'+text+'\n')
 (O/(name+'-full-top16-transliterations.txt')).write_text('\n'.join(out))
for pid in [0,17]:
 r=load('real-'+str(pid)+'-aggregate')['packet'];n=load('null-'+str(pid)+'-aggregate')['packet'];rng=random.Random(331819+pid);c=[rng.randrange(29)]
 for i in range(1,len(r['cipher'])):
  if r['cipher'][i]==r['cipher'][i-1]:c.append(c[-1])
  else:c.append([v for v in range(29) if v!=c[-1]][rng.randrange(28)])
 assert c==n['cipher'];assert [x==y for x,y in zip(c,c[1:])]==[x==y for x,y in zip(r['cipher'],r['cipher'][1:])]
result=dict(status='PASS',key_sha256=hashlib.sha256(bytes(key)).hexdigest(),key_length=len(key),packets=summary,total_cells=sum(x['cells'] for x in summary),total_bytes=sum(x['compressed_bytes'] for x in summary),total_main_seconds=sum(x['seconds'] for x in summary),total_top16_rerun_cells=sum(x['rerun_cells'] for x in summary),null_rng_verified=True,null_count_perpage=1,inference='descriptive fullsearch comparison only; no empirical significance tail')
(O/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
