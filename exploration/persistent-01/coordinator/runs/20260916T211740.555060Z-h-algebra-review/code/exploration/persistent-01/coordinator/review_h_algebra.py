from pathlib import Path
import json,gzip,math,itertools,collections
R=Path(__file__).resolve().parents[3];H=R/'exploration/persistent-01/worker-h/publication-20260916T2113Z';O=Path(__file__).resolve().parent
load=lambda n:json.loads(gzip.decompress((H/n).read_bytes())) if n.endswith('.gz') else json.loads((H/n).read_text())
counts={};summaries={}
for tag in ['H17','H18']:
 report=load(tag+'-result.json');e=load(tag+'-evidence.json.gz');roots=report['roots'];ncheck=0;nreal=0
 for root,streams in zip(roots,e['outputs']):
  for previous in range(29):
   if tag=='H17':
    scale=pow(root,previous,29);inverse=pow(scale,-1,29)
    for x in range(29):assert (x*scale%29)*inverse%29==x;ncheck+=1
   else:
    exponent=pow(root,previous,28);inverse=pow(exponent,-1,28)
    for x in range(29):assert pow(pow(x,exponent,29),inverse,29)==x;ncheck+=1
  for cipher,decoded in zip(e['real_cipher'],streams):
   previous=0;out=[]
   for x in cipher:
    out.append(x*pow(root,previous,29)%29 if tag=='H17' else pow(x,pow(root,previous,28),29));previous=x
   assert out==decoded;nreal+=len(out)
 assert ncheck==report['exhaustive_inverse_checks']
 assert (1+sum(s>=report['best_score'] for s in report['null']))/(len(report['null'])+1)==report['tail']
 summaries[tag]={'inverse_cells':ncheck,'real_output_runes':nreal,'tail':report['tail'],'common_parameter_and_pooled_distribution':True}
# The complete quotient of nonzero GF29 triples by nonzero scale.
directions=[(1,a,b) for a in range(29) for b in range(29)]+[(0,1,b) for b in range(29)]+[(0,0,1)];freq=collections.Counter()
for vec in itertools.product(range(29),repeat=3):
 if vec==(0,0,0):continue
 first=next(x for x in vec if x);inv=pow(first,-1,29);freq[tuple(x*inv%29 for x in vec)]+=1
assert set(freq)==set(directions) and set(freq.values())=={28}
r=load('H19-result.json');e=load('H19-evidence.json.gz');matrix_checks=0
for result,ciphers in [(r['real'],e['real_cipher'])]+[(c['result'],c['cipher']) for c in e['controls']]:
 for phase in result['phases']:
  mat=phase['matrix'];inverse=phase['inverse'];out=[];pre=[];test=[];offset=0
  assert [list(directions[i]) for i in phase['selected']]==mat
  assert [[sum(mat[i][k]*inverse[k][j] for k in range(3))%29 for j in range(3)] for i in range(3)]==[[1,0,0],[0,1,0],[0,0,1]]
  for cipher,mp in zip(ciphers,phase['maps']):
   start=phase['phase'];blocks=[cipher[i:i+3] for i in range(start,len(cipher)-2,3)];h=len(blocks)//2
   assert len(blocks)==mp['block_count'] and h==mp['prefix_blocks']
   for b in blocks:
    y=[sum(a*x for a,x in zip(row,b))%29 for row in mat];assert [sum(a*x for a,x in zip(row,y))%29 for row in inverse]==b;out.append(y)
   pre.extend(range(offset,offset+h));test.extend(range(offset+h,offset+len(blocks)));offset+=len(blocks)
  assert out==phase['output'];q=[]
  for j in range(3):
   counts=collections.Counter(out[i][j] for i in pre);q.append([(counts[a]+1)/(len(pre)+29) for a in range(29)])
  assert q==phase['prefix_probabilities']
  score=sum(math.log(29*q[j][out[i][j]]) for i in test for j in range(3))/(3*len(test));assert abs(score-phase['suffix_score'])<1e-12;matrix_checks+=1
 assert result['selected_phase']==max(range(3),key=lambda i:result['phases'][i]['prefix_score'])
assert (1+sum(v['score']>=r['real']['score'] for v in r['null']))/200==r['tail']
summaries['H19']={'nonzero_triples':sum(freq.values()),'directions':len(freq),'vectors_per_direction':28,'matrix_output_and_suffix_replays':matrix_checks,'tail':r['tail'],'scope':'One common matrix/phase and shared coordinate distributions across five real pages. No per-page key search.'}
(O/'H-algebra-review.json').write_text(json.dumps(summaries,indent=2)+'\n');print(json.dumps(summaries,indent=2))
