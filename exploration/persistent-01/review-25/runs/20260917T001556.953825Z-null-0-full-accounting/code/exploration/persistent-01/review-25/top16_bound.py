from pathlib import Path
import json,random
R=Path(__file__).parent
def limited(cells):
 top=sorted([c[0] for c in cells if c],key=lambda a:a[1],reverse=True);seen=set();distinct=[]
 for path,score in top:
  if path not in seen:seen.add(path);distinct.append((path,score))
  if len(distinct)==16:break
 cutoff=distinct[-1][1] if len(distinct)==16 else float('-inf');chosen=[c for c in cells if c and c[0][1]>=cutoff];pool={path:score for c in chosen for path,score in c[:16]};return sorted(pool.values(),reverse=True)[:16],cutoff,len(chosen)
# Labels stand for distinct (plaintext,literal positions), shared labels have equal score.
cases=[]
for seed in range(100):
 rng=random.Random(62500+seed);scores={i:rng.randrange(10) for i in range(120)};cells=[]
 for _ in range(30):
  ids=rng.sample(list(scores),rng.randrange(1,35));cells.append(sorted([(i,scores[i]) for i in ids],key=lambda a:a[1],reverse=True))
 expected=sorted({i:score for c in cells for i,score in c}.values(),reverse=True)[:16];observed,cutoff,n=limited(cells);assert observed==expected;cases.append({'seed':seed,'cutoff':cutoff,'rerun_cells':n})
cells=[[(0,100),(i+1,90-i)] for i in range(20)]+[[(100,95)]];got,cutoff,n=limited(cells);assert cutoff==float('-inf') and n==21 and got==sorted({p:s for c in cells for p,s in c}.values(),reverse=True)[:16]
(R/'top16-bound.json').write_text(json.dumps({'status':'PASS','random_alias_tie_cases':cases,'fallback_case':{'unique_top1':2,'cutoff':'-inf','rerun_cells':n}},indent=2));print('PASS 100 alias/tie cases + fewer-than16 fallback')
