import pathlib,json,gzip,random,importlib.util
R=pathlib.Path(__file__).parent;Q=R/'snapshots';load=lambda name:json.load(gzip.open(Q/(name+'.json.gz'),'rt'))
spec=importlib.util.spec_from_file_location('subject',R.parent/'worker-p/p14.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
real=load('real');maps=load('real-maps');cipher=[];cuts=[]
for ix,m in enumerate(maps):
 assert m['page']==ix
 if cipher:cuts.append(len(cipher))
 cipher+=m['indices']
assert cipher==real['cipher'] and cuts==real['cuts']==[262,528,729] and len(cipher)==946
rng=random.Random(331419);null=[];boundary=[]
for ix in range(19):
 row=load('null-'+str(ix));c=[rng.randrange(29)]
 for i in range(1,len(cipher)):
  v=c[-1] if cipher[i]==cipher[i-1] else None
  if v is None:
   draw=rng.randrange(28);v=draw+int(draw>=c[-1])
  c.append(v)
 assert c==row['cipher'] and row['ends']==real['ends'] and row['cuts']==cuts and not row['reset']
 assert all((c[i]==c[i-1])==(cipher[i]==cipher[i-1]) for i in range(1,len(c)))
 assert row['rows']==sorted(row['rows'],key=lambda a:a['score'],reverse=True)
 null.append(row['rows'][0]['score']);boundary.append([c[k]==c[k-1] for k in cuts])
summary=load('summary');assert null==[x['score'] for x in summary['null']]
tail=(1+sum(x>=real['rows'][0]['score'] for x in null))/20;assert tail==summary['tail']==.25
prefix=[]
for cell in s.CELLS:
 c=cipher[:262];ends={i for i in real['ends'] if i<262};s.CAP=2048;a=s.decode(c,ends,[],cell)
 small={**cell,'key':cell['key'][:1024]};s.CAP=1024;b=s.decode(c,ends,[],small)
 assert a==b;prefix.append({'id':cell['id'],'max_queried':a['max_queried'],'identical':True})
s.CAP=2048
control=[]
for ix in range(4):
 f=load('fixture-'+str(ix));r=load('control-'+str(ix));truthskips=[len(e['rejected']) for e in f['events']]
 errs=[i for i,(a,b) in enumerate(zip(f['plain'],r['top16']['alternatives'][0]['plain'])) if a!=b]
 ranks=[i+1 for i,a in enumerate(r['top16']['alternatives']) if a['plain']==f['plain'] and a['reject_counts']==truthskips]
 assert errs==([] if ix!=2 else [290]);assert ranks==([2] if ix==2 else [1])
 control.append({'ix':ix,'errors':errs,'full_truth_path_rank':ranks})
# Deliberately finite cap: both a pending start beyond cap and a rejected final draw disappear.
cell={'key':[0,0,9,1],'sign':1};s.CAP=4
short=s.decode([3,2],{1},{1},cell,False,16)
assert any(a['plain']==[3,3] and a['reject_counts']==[0,1] for a in short['alternatives'])
cell2={'key':[0,0],'sign':1};s.CAP=2;cap=s.decode([3,2],{1},{1},cell2,False,16)
assert not any(a['plain']==[3,3] for a in cap['alternatives']) and cap['cap_excluded']>0
out={'status':'PASS','nulls':19,'null_scores':null,'tail':tail,'cross_cut_repeat_mask':[cipher[k]==cipher[k-1] for k in cuts],'null_cut_masks':boundary,'prefix_identity':prefix,'controls':control,'finite_cap_probe':cap}
(R/'accounting.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ('null_scores','null_cut_masks','finite_cap_probe')})
