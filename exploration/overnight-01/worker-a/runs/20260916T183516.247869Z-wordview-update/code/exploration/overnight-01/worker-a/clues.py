"""Frozen exact-source rune phrases and nonwrapping running texts; ordinary then fixed+shortlisted F."""
import argparse,gzip,hashlib,json,pathlib,random,re,time
import search as s
O=s.O
SOURCES=['solved_0_warning.txt','solved_0_wisdom.txt','solved_0_welcome.txt','solved_0_loss_of_divinity.txt','solved_0_koan_1.txt','solved_jpg107-167.txt','solved_p56_an_end.txt','solved_p57_parable.txt']
def freeze():
 out=O/'r02';out.mkdir(exist_ok=True);p=out/'keys.json'
 if p.exists():return json.loads(p.read_text())
 keys=[];seen={};texts=[]
 for filename in SOURCES:
  path=s.ROOT/'audit/parallel-01/reference/sources'/filename;raw=path.read_text();words=list(re.finditer('['+s.ABC+']+',raw));runes=[s.ABC.index(c) for c in raw if c in s.ABC];offset=0;starts=[]
  for line in raw.splitlines():
   starts.append(offset);offset+=sum(c in s.ABC for c in line)
  texts.append(dict(id='text:'+filename,key=runes,offsets=sorted(set(starts))[:1024],source=str(path.relative_to(s.ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),connection='Verified solved Liber Primus plaintext: immediate internal puzzle text',wrapping=False))
  for width in [1,2]:
   for i in range(len(words)-width+1):
    phrase=words[i:i+width];key=[s.ABC.index(c) for w in phrase for c in w.group()]
    if not (4<=len(key)<=32):continue
    alias=dict(source=str(path.relative_to(s.ROOT)),character_start=phrase[0].start(),character_end=phrase[-1].end(),raw=raw[phrase[0].start():phrase[-1].end()],conversion='exact rune indices; delimiters removed; no Latin re-tokenization')
    k=tuple(key)
    if k in seen:keys[seen[k]]['aliases'].append(alias)
    elif len(keys)<256:seen[k]=len(keys);keys.append(dict(id=f'clue:{len(keys):03}',key=key,aliases=[alias]))
 data=dict(seed=330102,keys=keys,texts=texts,selection='first 256 distinct one/two-word source-order phrases 4..32 runes across ordered sources; aliases retained; exact solved sources, not invented dictionary',F_selection='top 256 ordinary cells plus independent Random(330102) sample of 256 cell ordinals; deduplicated union');s.dump(p,data);return data

def cells(data,ps):
 out=[]
 for k in data['keys']:
  for off in range(len(k['key'])):
   for sign in [-1,1]:
    for p in ps:out.append(dict(key_id=k['id'],offset=off,sign=sign,original_page=p['original_page'],periodic=True))
 for k in data['texts']:
  for off in k['offsets']:
   for sign in [-1,1]:
    for p in ps:
     if off+len(p['indices'])<=len(k['key']):out.append(dict(key_id=k['id'],offset=off,sign=sign,original_page=p['original_page'],periodic=False))
 return out

def key_for(cell,defs,n):
 k=defs[cell['key_id']]['key'];off=cell['offset'];return [k[(i+off)%len(k)] for i in range(n)] if cell['periodic'] else k[off:off+n]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['ordinary','literal_f']);ap.add_argument('--seconds',type=int,default=780);a=ap.parse_args();t=time.monotonic();data=freeze();ps=s.pages();lookup={p['original_page']:p for p in ps};queue=cells(data,ps);defs={x['id']:x for x in data['keys']+data['texts']};q=s.Score();stage=O/'r02'/a.mode;stage.mkdir(exist_ok=True)
 if a.mode=='literal_f':
  plan=O/'r02'/'f-plan.json'
  if not plan.exists():
   top=json.loads((O/'r02/ordinary/checkpoint.json').read_text())['top'];fixed=random.Random(data['seed']).sample(range(len(queue)),min(256,len(queue)));short=[int(x['id'].split(':')[-1]) for x in top];s.dump(plan,dict(shortlist=short,independent_fixed=fixed,queue=sorted(set(short+fixed))))
  ordinals=json.loads(plan.read_text())['queue']
 else:ordinals=list(range(len(queue)))
 cp=stage/'checkpoint.json';state=json.loads(cp.read_text()) if cp.exists() else dict(cursor=0,top=[]);start=state['cursor'];top=state['top'];retain=256 if a.mode=='ordinary' else 20
 with gzip.open(stage/f'scores-{start:07d}.jsonl.gz','wt') as f:
  for j in range(start,len(ordinals)):
   ix=ordinals[j];cell=queue[ix];page=lookup[cell['original_page']];c=page['indices'];k=key_for(cell,defs,len(c));sign=cell['sign'];alts=[];diag={}
   if a.mode=='ordinary':p=[(v+sign*k[i])%29 for i,v in enumerate(c)];score=q(p)
   else:alts,diag=s.fbeam(c,k,sign,q);p=alts[0]['plain'];score=alts[0]['score']
   r=dict(id=f'r02:{a.mode}:{ix}',mode=a.mode,**cell,n=len(c),score=score,statistics=s.stats(p));f.write(json.dumps(r)+'\n')
   if len(top)<retain or score>top[-1]['score']:
    r.update(plain=p,transliteration=s.render(p,page),alternatives=alts,diagnostics=diag,status='UNREVIEWED');top.append(r);top.sort(key=lambda x:x['score'],reverse=True);top=top[:retain]
   state=dict(cursor=j+1,total=len(ordinals),enumerator_cells=len(queue),top=top,seconds_this_batch=time.monotonic()-t)
   if (j+1)%2000==0 or a.mode=='literal_f' and (j+1)%20==0:s.dump(cp,state);f.flush();print(json.dumps(dict(mode=a.mode,cursor=j+1,total=len(ordinals),elapsed=time.monotonic()-t,best=top[0]['score'])),flush=True)
   if time.monotonic()-t>a.seconds:break
 s.dump(cp,state);s.dump(stage/'top20.json',top[:20]);print(json.dumps(dict(mode=a.mode,cursor=state['cursor'],total=len(ordinals),seconds=time.monotonic()-t)),flush=True)
if __name__=='__main__':main()
