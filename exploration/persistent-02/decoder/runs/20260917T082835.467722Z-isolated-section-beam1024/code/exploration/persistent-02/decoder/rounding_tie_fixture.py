import json
from exact import decode

def extend(ctx,r,end):
 return (ctx[1],r),(-1e-16 if ctx==(29,29) and r==0 else -100. if r==1 else 0.)
x,d=decode([0,1,1,2],[1],extend,retain=16)
print(json.dumps(dict(paths=x,diagnostics=d),indent=2))
assert len(x)==2 and x[0]['total']==x[1]['total']==-100.
assert int(d['optimal_path_ties'])==2,'Original tie-count claim fails under float rounding'
