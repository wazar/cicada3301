"""Preregistered composite-panel comparison, no decoding/search performed."""
from pathlib import Path
import json, hashlib, math, statistics
R=Path(__file__).resolve().parents[3]
O=Path(__file__).resolve().parent

def aggregate(matrix):
 assert matrix and all(len(row)==len(matrix[0]) for row in matrix)
 standardized=[]
 for row in matrix:
  assert all(math.isfinite(x) for x in row)
  mean=statistics.fmean(row);sd=statistics.pstdev(row)
  standardized.append([(x-mean)/sd if sd else 0. for x in row])
 maxima=[max(row[j] for row in standardized) for j in range(len(matrix[0]))]
 return standardized,maxima,(1+sum(x>=maxima[0] for x in maxima[1:]))/len(maxima)

def controls():
 z,m,p=aggregate([[0.,1.,2.],[0.,0.,0.]])
 assert all(abs(x-y)<1e-12 for x,y in zip(z[0],[-math.sqrt(1.5),0.,math.sqrt(1.5)]))
 assert m==[0.,0.,math.sqrt(1.5)] and p==1.
 matrix=[[4.,1.,2.,3.],[0.,5.,2.,1.],[8.,8.,8.,8.]]
 z,m,p=aggregate(matrix);order=[2,0,3,1]
 zz,mm,pp=aggregate([[row[i] for i in order] for row in matrix])
 assert all(abs(mm[i]-m[j])<1e-12 for i,j in enumerate(order))
 assert aggregate([[1.,1.,1.],[2.,2.,2.]])[2]==1.
 return {'hand_matrix':True,'column_relabelling':True,'constant_rows':True,'ties':True}

def main():
 checks=controls(); cfg=json.loads((O.parent/'config.json').read_text())
 pages=[x['page'] for x in json.loads((R/'exploration/persistent-01/worker-f/F06-maps.json').read_text()) if x['page'] not in cfg['reserved_originals']+[0,17,55]]
 assert len(pages)==42 and len(set(pages))==42
 matrix=[]; sources=[]; seeds=set(); leaders=[]
 for page in pages:
  values=[]
  for j in range(20):
   p=O.parent/'feedback/C01'/f"actual{page}{'-null%02d'%(j-1) if j else ''}.json"
   b=p.read_bytes(); x=json.loads(b); sources.append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(b).hexdigest()})
   assert x['seeds']==732511 and [r['k'] for r in x['rows']]==[2,3,4]
   assert x['maximum']==max(r['top16'][0]['score'] for r in x['rows'])
   if j:
    seed=x['null_seed']; assert seed==2026091700+100*page+j-1 and seed not in seeds;seeds.add(seed)
   else:
    assert x['null_seed'] is None
    leaders.append({'page':page,'seed':x['global16'][0]['seed'],'k':x['global16'][0]['k'],'maximum':x['maximum']})
   values.append(x['maximum'])
  matrix.append(values)
 z,m,p=aggregate(matrix)
 for row,zz,lead in zip(matrix,z,leaders):
  lead.update(actual_standardized=zz[0],within_page_rank=(1+sum(x>=row[0] for x in row[1:]))/20)
 out={'controls':checks,'pages':pages,'maxima_by_page_actual_then_19_nulls':matrix,'standardized_by_page':z,'panel_maxima':m,'composite_upper_tail_rank':p,'leaders':sorted(leaders,key=lambda x:-x['actual_standardized']),'sources':sources,'scope':'Exploratory composite-panel rank under exact first-rune/equality-mask uniform comparator; not a global discovery probability or plaintext proof. Pooled standardization symmetric across panel labels.'}
 (O/'C01-aggregate.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'pages':len(pages),'composite_upper_tail_rank':p,'leaders':out['leaders'][:5],'controls':checks},indent=2))
if __name__=='__main__':
 import sys
 if '--selftest' in sys.argv:print(json.dumps(controls()))
 else:main()
