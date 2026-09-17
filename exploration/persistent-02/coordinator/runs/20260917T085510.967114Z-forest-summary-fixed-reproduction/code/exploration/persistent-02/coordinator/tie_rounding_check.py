from pathlib import Path
import importlib.util,json,hashlib
root=Path(__file__).resolve().parents[3]
p=root/'exploration/persistent-02/decoder/exact.py'
spec=importlib.util.spec_from_file_location('p02exact',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def extend(ctx,r,end):
 return (ctx[1],r),(-1e-16 if ctx==(29,29) and r==0 else -100. if r==1 else 0.)
rows,diag=m.decode([0,1,1,2],[1],extend,retain=16)
# Independently enumerate the two possible first-rune branches.
ex=[]
for literal in [False,True]:
 plain=[0 if literal else 28,0,0,1];ctx=(29,29);score=0.
 for r in plain:ctx,w=extend(ctx,r,False);score+=w
 ex.append({'plain':plain,'score':score})
out={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cipher':[0,1,1,2],'key':[1],'exact_rows':rows,'diag':diag,'enumerated':ex,'enumerated_optimum_ties':sum(x['score']==max(t['score'] for t in ex) for x in ex),'limitation':'Floating-point addition can coalesce unequal prefix scores after a merge; best-prefix tie propagation does not count every terminal floating-point tie.'}
print(json.dumps(out,indent=2))
(root/'exploration/persistent-02/coordinator/tie-rounding-check.json').write_text(json.dumps(out,indent=2)+'\n')
