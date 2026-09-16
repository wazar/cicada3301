import sys,pathlib,importlib.util,json,re,hashlib,math,random,time,argparse,datetime
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2]
def imp(name,p):
 s=importlib.util.spec_from_file_location(name,R/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=imp('rune_model','exploration/persistent-01/worker-c/p03_frozen.py');f=imp('kbest','exploration/persistent-01/worker-c/frozen_kbest.py');gp=imp('gp','liber-primus/src/lp/gematria.py')
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def phi(n):return sum(math.gcd(n,k)==1 for k in range(1,n+1))
def setup():
 arrays=[];source=[];cells={}
 for name in ['0_wisdom','jpg229']:
  p=R/('audit/parallel-01/reference/sources/solved_'+name+'.txt');raw=p.read_text();lines=raw.splitlines()[-5:];tokens=[re.findall(r'[0-9]+|['+m.ABC+']+',l) for l in lines];assert all(len(x)==5 for x in tokens)
  a=[[int(t) if t.isdigit() else sum(gp.RUNE_TO_PRIME[c] for c in t) for t in row] for row in tokens]
  source.append(dict(name=name,path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),tokens=tokens,integers=a,row_sums=list(map(sum,a)),column_sums=[sum(row[i] for row in a) for i in range(5)],diagonal_sums=[sum(a[i][i] for i in range(5)),sum(a[i][4-i] for i in range(5))]))
  for transform in ['raw','phi']:
   for route in ['row','column']:
    key=[(phi(a[i][j]) if transform=='phi' else a[i][j])%29 for i,j in ([(i,j) for i in range(5) for j in range(5)] if route=='row' else [(i,j) for j in range(5) for i in range(5)])];ident=f'{name}:{transform}:{route}';arrays.append(dict(id=ident,key=key))
    for phase in range(25):
     k=key[phase:]+key[:phase]
     for sign in [-1,1]:
      signature=tuple(sign*x%29 for x in k);alias=f'{ident}:{phase}:{sign}'
      if signature not in cells:cells[signature]=dict(id=alias,key=k,sign=sign,aliases=[])
      cells[signature]['aliases'].append(alias)
 return source,arrays,list(cells.values())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['pilot','full'],default='pilot');a=ap.parse_args();out=O/a.mode;out.mkdir(exist_ok=True);lm=m.LM();source,arrays,cells=setup();save(out/'construction.json',dict(sources=source,arrays=arrays,cells=cells));t=time.monotonic();summary=[]
 def run(label,c,ends,truth=None,plant=None,truthpath=None):
  path=out/(label+'.json')
  if path.exists():return
  rows=[]
  for cell in cells:
   if (R/'exploration/persistent-01/STOP').exists() or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00'):raise SystemExit('STOP/deadline')
   key=cell['key'];sign=cell['sign'];p=[(x+sign*key[i%25])%29 for i,x in enumerate(c)];rows.append(dict(id=cell['id'],model='ordinary',score=lm.score(p,ends),plain=p,literal_positions=[],used=len(c)))
   alts,diag=f.kbest(c,ends,key,sign,lm,retain=1);rows.append(dict(id=cell['id'],model='literal-F',**alts[0]))
  rows.sort(key=lambda x:x['score'],reverse=True);byid={x['id']:x for x in cells}
  for row in rows[:20]:
   if row['model']=='literal-F':
    cell=byid[row['id']];row['alternatives'],row['diagnostics']=f.kbest(c,ends,cell['key'],cell['sign'],lm,retain=16)
   row['runes']=''.join(m.ABC[x] for x in row['plain']);row['text']=gp.indices_to_translit(row['plain'])
  result=dict(label=label,n=len(c),cipher=c,ends=sorted(ends),count=len(rows),scores=[{k:x[k] for k in ['id','model','score']} for x in rows],top=rows[:20])
  compact=dict(label=label,n=len(c),count=len(rows),best_score=rows[0]['score'],best_id=rows[0]['id'],elapsed=time.monotonic()-t)
  if truth is not None:
   tr=next(x for x in rows if x['id']==plant['id'] and x['model']=='literal-F');alts,_=f.kbest(c,ends,plant['key'],plant['sign'],lm,retain=16);compact.update(truth_key_rank=1+sum(x['score']>tr['score'] for x in rows),planted_errors=sum(x!=y for x,y in zip(tr['plain'],truth)),best_errors=sum(x!=y for x,y in zip(rows[0]['plain'],truth)),truth_top16=any(x['plain']==truth for x in alts));result.update(truth=truth,plant=plant,truthpath=truthpath,planted_alternatives=alts,control=compact)
  save(path,result);summary.append(compact);save(out/'summary.json',summary);print(json.dumps(compact),flush=True)
 if a.mode=='pilot':
  for ix,name in enumerate(m.CHECK):
   p,ends=m.parse((R/f'audit/parallel-01/reference/sources/solved_{name}.txt').read_text());plant=cells[[17,121,233,319][ix]%len(cells)];u=0;c=[];truthpath=[]
   for i,x in enumerate(p):
    if x==0 and i%3!=1:c.append(0);truthpath.append(i)
    else:c.append((x-plant['sign']*plant['key'][u%25])%29);u+=1
   run('control-'+name,c,ends,p,plant,truthpath);random.Random(330115+ix).shuffle(c);run('control-null-'+name,c,ends)
 cfg=json.loads((R/'exploration/persistent-01/config.json').read_text());dp=R/'audit/parallel-01/inputs/dataset.json';assert hashlib.sha256(dp.read_bytes()).hexdigest()==cfg['dataset_sha256'];pages=json.loads(dp.read_text())['pages']
 for p in pages:
  pid=p['original_page']
  if pid>55 or pid==50 or pid in cfg['reserved_original_pages'] or (a.mode=='pilot' and pid not in [0,1]):continue
  c,ends=m.parse('/'.join(l['raw'] for l in p['lines']));assert c==p['indices'];run('real-'+str(pid),c,ends);random.Random(33011500+pid).shuffle(c);run('null-'+str(pid),c,ends)
 print(json.dumps(dict(done=True,seconds=time.monotonic()-t,cells=len(cells))),flush=True)
if __name__=='__main__':main()
