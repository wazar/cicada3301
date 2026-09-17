"""C08 k2 complete shared-seed-reset fits and frozen-prefix continuation."""
import reset_plants as rp
from reset_literal import Engine,encode
import extend as ex
import json,gzip,itertools,hashlib,resource,sys
O=ex.O/'C08-actual';O.mkdir(exist_ok=True);SP=ex.R/'exploration/persistent-02/section/section-packet.json';NP=ex.R/'exploration/persistent-02/decoder/null-calibration-inputs.json';AP=ex.R/'exploration/persistent-02/section/A07-inputs.json'
s=json.loads(SP.read_text());C=s['body']['runes'];ends=set(s['body']['explicit_ends']);resets={141,262,284,337,381,421,518};panels=[C]+[c[13:] for c in json.loads(NP.read_text())['packets']];assert len(panels)==20
seeds=list(itertools.product(range(29),repeat=2))
def search(c,e,r,L,folder):
 folder.mkdir(exist_ok=True,parents=True);rows=[]
 for part in range(29):
  ex.guard();path=folder/f'part{part:02}.json.gz'
  if path.exists():
   with gzip.open(path,'rt') as f:out=json.load(f)
  else:
   out=Engine(seeds[part*29:(part+1)*29],L).solve(c,e,r);out['partition']=part
   for a in out['alternatives']:
    assert encode(a['plain'],a['seed'],a['literal_positions'],r)==c;assert abs(rp.total(a['plain'],e,L)-a['total'])<1e-8
   with gzip.open(path,'wt') as f:json.dump(out,f,separators=(',',':'))
  rows.append(out)
 return dict(alternatives=sorted([a for x in rows for a in x['alternatives']],key=lambda a:(-a['total'],a['seed']))[:16],seconds=sum(x['seconds'] for x in rows),peak_states=max(x['peak_states'] for x in rows),seed_count=841)
def run(panel,name):
 path=O/f'{name}-panel{panel:02}.json'
 if path.exists():return
 c=panels[panel];L=rp.model(name);folder=O/f'{name}-panel{panel:02}';full=search(c,ends,resets,L,folder/'full');pre=search(c[:249],{i for i in ends if i<249},{i for i in resets if i<249},L,folder/'prefix');chosen=pre['alternatives'][0];hist=[];a=b=29
 for i,p in enumerate(chosen['plain']):
  if i in resets:hist=[]
  if i not in chosen['literal_positions']:hist.append(p)
  a,b=b,p
  if i in ends:a,b=b,29
 tail=Engine([chosen['seed']],L).solve(c[249:],{i-249 for i in ends if i>=249},{i-249 for i in resets if i>=249},initial_history=hist[-2:],initial_context=(a,b));alts=[]
 for x in tail['alternatives']:
  plain=chosen['plain']+x['plain'];literal=chosen['literal_positions']+[i+249 for i in x['literal_positions']];assert encode(plain,chosen['seed'],literal,resets)==c;assert abs(rp.total(plain,ends,L)-chosen['total']-x['total'])<1e-8;alts.append(dict(plain=plain,literal_positions=literal,seed=chosen['seed'],continuation_score=x['score'],continuation_total=x['total']))
 row=dict(panel=panel,model=name,cipher=c,ends=sorted(ends),resets=sorted(resets),full=full,prefix=pre,continuation=alts,maximum=full['alternatives'][0]['score'],continuation_score=alts[0]['continuation_score'],seconds=full['seconds']+pre['seconds']+tail['seconds'],peak_states=max(full['peak_states'],pre['peak_states'],tail['peak_states']),peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_pins={str(p.relative_to(ex.R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SP,NP,AP]})
 path.write_text(json.dumps(row,separators=(',',':'))+'\n');print(name,panel,row['maximum'],row['continuation_score'],row['seconds'],flush=True)
def summary(name):
 rows=[json.loads((O/f'{name}-panel{i:02}.json').read_text()) for i in range(20)];a=rows[0];out=dict(model=name,actual_maximum=a['maximum'],score_rank=(1+sum(r['maximum']>=a['maximum'] for r in rows[1:]))/20,actual_continuation=a['continuation_score'],continuation_rank=(1+sum(r['continuation_score']>=a['continuation_score'] for r in rows[1:]))/20,seconds=sum(r['seconds'] for r in rows),max_states=max(r['peak_states'] for r in rows),max_rss=max(r['peak_process_rss_bytes'] for r in rows),panels=20,seed_count_per_fit=841)
 (O/f'{name}-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':
 if sys.argv[1]=='summary':summary(sys.argv[2])
 else:
  for panel in map(int,sys.argv[2:]):run(panel,sys.argv[1])
