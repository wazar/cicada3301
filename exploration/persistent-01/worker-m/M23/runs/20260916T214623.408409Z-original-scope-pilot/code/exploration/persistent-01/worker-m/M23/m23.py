import pathlib,sys,importlib.util,json,gzip,hashlib,random,time,datetime,zlib,collections
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];D=ROOT/'exploration/persistent-01/worker-d';spec=importlib.util.spec_from_file_location('d_matrix',D/'matrix.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def gate():
 assert not(R.parent.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):(R/(name+'.json')).write_text(json.dumps(x,indent=2))
def stats(p):
 cnt=collections.Counter(p);return dict(ioc_times_n=sum(n*(n-1) for n in cnt.values())/max(1,len(p)-1),min32distinct=min(len(set(p[j:j+32])) for j in range(max(1,len(p)-31))),zlib_bytes=len(zlib.compress(bytes(p))),runes=len(p),non_english_lm='N/A same frozen English rune LM only')
def save(name,x):
 with gzip.open(R/'cells'/(name+'.json.gz'),'wt') as f:json.dump(x,f)
def verify(c,row,cell):
 u=0;out=[];lit=set(row['literal_positions'])
 for i,p in enumerate(row['plain']):
  if i in lit:assert p==0;out.append(0)
  else:out.append((p-cell['sign']*cell['key'][u%25])%29);u+=1
 assert out==c and u==row['used']

def main(mode):
 gate();(R/'cells').mkdir(exist_ok=True);lm=d.m.LM();source,arrays,cells=d.setup();old=json.load(open(D/'pilot/construction.json'));assert dict(sources=source,arrays=arrays,cells=cells)==old;assert len(cells)==400;byid={x['id']:x for x in cells};dump('construction',dict(sources=source,arrays=arrays,cells=cells,nominal_aliases=sum(len(c['aliases']) for c in cells),unique_signedkeys=len(cells)))
 if mode=='pilot':
  replay=[]
  for name in d.m.CHECK:
   p=D/'pilot'/('control-'+name+'.json');oldctl=json.load(open(p));a,diag=d.f.kbest(oldctl['cipher'],set(oldctl['ends']),oldctl['plant']['key'],oldctl['plant']['sign'],lm,retain=16);assert a==oldctl['planted_alternatives'];assert a[0]['plain']==oldctl['truth'];verify(oldctl['cipher'],a[0],oldctl['plant']);replay.append(dict(source=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),prior_fullsearch_control=oldctl['control'],selected_truekey_replay=True,alternatives=len(a)))
  prior=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted((D/'pilot').glob('*.json'))];dump('inherited-evidence',dict(controls=replay,prior_files=prior,model_sources=lm.files))
 maps=json.load(open(ROOT/'exploration/persistent-01/worker-f/F06-maps.json'));cfg=json.load(open(ROOT/'exploration/persistent-01/config.json'));pages=[x for x in maps if x['page']<=55 and x['page'] not in cfg['reserved_original_pages']+[0,1,50]];assert len(pages)==43;dump('scope',dict(remaining_pages=[x['page'] for x in pages],preserved_prior_pages=[0,1],model_sources=lm.files));summary=json.load(open(R/'summary.json')) if (R/'summary.json').exists() else []
 for page in pages:
  if mode=='pilot' and page!=pages[0]:break
  pid=page['page'];c,ends=d.m.parse(page['raw_joined']);assert c==page['indices'];pair=[('real',c)];null=c.copy();random.Random(33011500+pid).shuffle(null);pair.append(('null',null))
  for kind,c in pair:
   name=kind+'-'+str(pid)
   if (R/'cells'/(name+'.json.gz')).exists():continue
   gate();start=time.monotonic();rows=[];expanded=0
   for cell in cells:
    gate();key=cell['key'];sign=cell['sign'];p=[(v+sign*key[i%25])%29 for i,v in enumerate(c)];row=dict(id=cell['id'],model='ordinary',score=lm.score(p,ends),plain=p,literal_positions=[],used=len(c));verify(c,row,cell);row['statistics']=stats(p);rows.append(row)
    a,diag=d.f.kbest(c,ends,key,sign,lm,retain=1);expanded+=diag['expanded'];row=dict(id=cell['id'],model='literal-F',**a[0],diagnostics=diag);verify(c,row,cell);row['statistics']=stats(row['plain']);rows.append(row)
   rows.sort(key=lambda x:x['score'],reverse=True);retained=0;extraexp=0
   for row in rows[:20]:
    if row['model']=='literal-F':
     cell=byid[row['id']];row['alternatives'],row['top16_diagnostics']=d.f.kbest(c,ends,cell['key'],cell['sign'],lm,retain=16);extraexp+=row['top16_diagnostics']['expanded'];retained+=len(row['alternatives'])
     for a in row['alternatives']:verify(c,a,cell);a['statistics']=stats(a['plain'])
    row['runes']=''.join(d.m.ABC[x] for x in row['plain']);row['text']=d.gp.indices_to_translit(row['plain'])
   seconds=time.monotonic()-start;out=dict(name=name,page=pid,kind=kind,cipher=c,ends=sorted(ends),source_map=page,null_seed=33011500+pid if kind=='null' else None,rows=rows,cells=len(rows),path_expansions=expanded,retention_path_expansions=extraexp,top16_retained_paths=retained,seconds=seconds);save(name,out);compact=dict(name=name,page=pid,kind=kind,score=rows[0]['score'],key_id=rows[0]['id'],model=rows[0]['model'],cells=len(rows),seconds=seconds,path_expansions=expanded,retention_path_expansions=extraexp,top16_retained_paths=retained);summary.append(compact);dump('summary',summary);print(json.dumps(compact),flush=True)
 if mode=='pilot':dump('cost-decision',dict(pilot_page=pages[0]['page'],pilot_pair_seconds=sum(x['seconds'] for x in summary),projected43_pairs_seconds=sum(x['seconds'] for x in summary)*43,proceed=sum(x['seconds'] for x in summary)*43<=1800))
 else:
  assert len(summary)==86;dump('result',dict(pages=43,paired_searches=86,cells=sum(x['cells'] for x in summary),real_cells=sum(x['cells'] for x in summary if x['kind']=='real'),null_cells=sum(x['cells'] for x in summary if x['kind']=='null'),path_expansions=sum(x['path_expansions'] for x in summary),retention_path_expansions=sum(x['retention_path_expansions'] for x in summary),retained_top16_paths=sum(x['top16_retained_paths'] for x in summary),seconds=sum(x['seconds'] for x in summary),best_real=max((x for x in summary if x['kind']=='real'),key=lambda x:x['score']),best_null=max((x for x in summary if x['kind']=='null'),key=lambda x:x['score'])))
if __name__=='__main__':main(sys.argv[1])
