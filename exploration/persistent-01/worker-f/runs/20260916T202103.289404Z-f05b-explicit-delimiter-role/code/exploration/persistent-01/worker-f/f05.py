import pathlib,json,numpy as np,gzip,re,datetime
R=pathlib.Path(__file__).parent;D=json.load(open('audit/parallel-01/inputs/dataset.json'));M=json.load(open(R/'F01-maps.json'));P={p['original_page']:p for p in D['pages'] if p['original_page'] in {m['page'] for m in M}};rng=np.random.default_rng(2026091715);events=[];strata={}
for m in M:
 raw=''.join(l['raw'] for l in P[m['page']]['lines']);chars=[(i,D['alphabet'].index(c)) for i,c in enumerate(raw) if c in D['alphabet']];assert [r for i,r in chars]==m['indices'];length=np.zeros(len(chars),int)
 for w in m['words']:length[w['start']:w['end']]=min(8,w['end']-w['start'])-1
 for j,((i,x),(ii,y)) in enumerate(zip(chars,chars[1:])):
  gap=raw[i+1:ii]
  if '.' not in gap and '-' not in gap:continue
  k=(m['page'],m['labels'][2][j+1]);strata.setdefault(k,[]).append(len(events));events.append({'page':m['page'],'previous':j,'next':j+1,'raw_gap':gap,'period':int('.' in gap),'features':[x,y,int(length[j]),int(length[j+1])],'raw_positions':[i,ii]})
y=np.array([e['period'] for e in events]);xx=np.array([e['features'] for e in events]);ss=[np.array(v) for v in strata.values()]
def G(t):
 e=t.sum(1)[:,None]*t.sum(0)[None,:]/t.sum();ok=t>0;return float(2*np.sum(t[ok]*np.log(t[ok]/e[ok])))
def stat(y):return [G(np.bincount(y*n+xx[:,k],minlength=2*n).reshape(2,n)) for k,n in enumerate([29,29,8,8])]
def trial(y,n):
 real=stat(y);null=[];maps=[]
 for rep in range(n):
  z=y.copy()
  for s in ss:z[s]=rng.permutation(z[s])
  null.append(stat(z));maps.append(np.flatnonzero(z).tolist())
 null=np.array(null);tails=(1+(null>=real).sum(0))/(n+1);return {'real':real,'tails':tails.tolist(),'bonferroni4':np.minimum(1,4*tails).tolist(),'null':null.tolist(),'period_maps':maps,'labels':y.tolist()}
real=trial(y,1999);controls=[]
for typ in ['baseline','next_rune','next_length']:
 for rep in range(8):
  assert not (R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
  prob=np.full(len(y),.06) if typ=='baseline' else np.where(xx[:,1]<7,.3,.01) if typ=='next_rune' else np.where(xx[:,3]>=5,.3,.01)
  t=trial((rng.random(len(y))<prob).astype(int),199);t.update(type=typ,rep=rep);controls.append(t)
def strip(t):return {k:v for k,v in t.items() if k not in ['null','period_maps','labels']}
summary={'event_count':len(y),'periods':int(y.sum()),'hyphens':int(len(y)-y.sum()),'real':strip(real),'controls':[strip(t) for t in controls],'detections':{typ:sum(min(t['bonferroni4'])<=.05 for t in controls if t['type']==typ) for typ in ['baseline','next_rune','next_length']},'counts':{'real':1,'real_null':1999,'controls':24,'control_null':4776},'seed':2026091715}
with gzip.open(R/'F05-evidence.json.gz','wt') as f:json.dump({'events':events,'strata':[s.tolist() for s in ss],'real':real,'controls':controls},f)
(R/'F05-result.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
