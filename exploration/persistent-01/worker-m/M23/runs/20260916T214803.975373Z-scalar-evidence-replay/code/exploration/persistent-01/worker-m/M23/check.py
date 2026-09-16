import pathlib,json,gzip,hashlib,random,collections
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];D=ROOT/'exploration/persistent-01/worker-d';summary=json.load(open(R/'summary.json'));assert len(summary)==86;construction=json.load(open(R/'construction.json'));byid={x['id']:x for x in construction['cells']};assert len({tuple(c['sign']*v%29 for v in c['key']) for c in byid.values()})==400
prior=json.load(open(R/'inherited-evidence.json'))
for item in prior['prior_files']:assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
rows=[];count=0;retained=0
for s in summary:
 with gzip.open(R/'cells'/(s['name']+'.json.gz'),'rt') as f:r=json.load(f)
 c=r['cipher'];assert len(r['rows'])==800 and len({(x['id'],x['model']) for x in r['rows']})==800;expected=r['source_map']['indices'].copy()
 if r['kind']=='null':random.Random(33011500+r['page']).shuffle(expected)
 assert expected==c;assert sorted(r['rows'],key=lambda x:x['score'],reverse=True)==r['rows'];assert r['rows'][0]['score']==s['score']
 for row in r['rows']:
  cell=byid[row['id']];u=0;p=[];lit=set(row['literal_positions'])
  for i,x in enumerate(c):
   if i in lit:assert x==0;p.append(0)
   else:p.append((x+cell['sign']*cell['key'][u%25])%29);u+=1
  assert p==row['plain'] and u==row['used'];assert row['statistics']['runes']==len(p);count+=1
  retained+=len(row.get('alternatives',[]))
 rows.append(dict(page=r['page'],kind=r['kind'],score=s['score'],id=s['key_id'],model=s['model'],text=r['rows'][0]['text'],path=str((R/'cells'/(s['name']+'.json.gz')).relative_to(ROOT))))
real={x['page']:x for x in rows if x['kind']=='real'};null={x['page']:x for x in rows if x['kind']=='null'};pairs=[dict(page=p,real=real[p]['score'],null=null[p]['score'],delta=real[p]['score']-null[p]['score']) for p in sorted(real)];top=sorted(real.values(),key=lambda x:x['score'],reverse=True)[:10]
out=dict(replayed_cells=count,retained_alternatives=retained,prior_files_unchanged=True,paired_pages=len(pairs),real_above_paired_null=sum(x['delta']>0 for x in pairs),pairs=pairs,top10_real=top,bestnull=max(null.values(),key=lambda x:x['score']))
(R/'check-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
