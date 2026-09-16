import random,time,json
import search as s,clues

def main():
 t=time.monotonic();data=clues.freeze();defs={x['id']:x for x in data['keys']+data['texts']};q=s.Score();raw=(s.ROOT/'audit/parallel-01/reference/sources/solved_p57_parable.txt').read_text();truth=[s.ABC.index(c) for c in raw if c in s.ABC];page=dict(original_page=-1,indices=truth);queue=clues.cells(data,[page]);results=[]
 for mode,plantno in [('ordinary',0),('literal_f',17)]:
  plant=data['keys'][plantno];pk=plant['key'];K=[pk[i%len(pk)] for i in range(len(truth))];used=0;cipher=[];path=[]
  for i,p in enumerate(truth):
   literal=mode=='literal_f' and p==0
   if literal:cipher.append(0);path.append(i)
   else:cipher.append((p+K[used])%29);used+=1
  ranks=[]
  for ix,c in enumerate(queue):
   k=clues.key_for(c,defs,len(truth));p=[(v+c['sign']*k[i])%29 for i,v in enumerate(cipher)];ranks.append((q(p),ix,p))
  ranks.sort(reverse=True,key=lambda x:x[0]);plantix=next(i for i,c in enumerate(queue) if c['key_id']==plant['id'] and c['sign']==-1 and c['offset']==0)
  fixed=random.Random(data['seed']).sample(range(len(queue)),min(256,len(queue)));selected=sorted(set([x[1] for x in ranks[:256]]+fixed));evaluated=[]
  if mode=='literal_f':
   for ix in selected:
    cell=queue[ix];k=clues.key_for(cell,defs,len(truth));alts,diag=s.fbeam(cipher,k,cell['sign'],q);evaluated.append((alts[0]['score'],ix,alts[0]['plain'],alts,diag))
  else:evaluated=[(sc,ix,p,[],{}) for sc,ix,p in ranks]
  evaluated.sort(reverse=True,key=lambda x:x[0]);pr=next((r for r in evaluated if r[1]==plantix),None);corrupt=K.copy();corrupt[0]=(corrupt[0]+1)%29
  ca,_=s.fbeam(cipher,corrupt,-1,q);best=evaluated[0]
  results.append(dict(mode=mode,plant_id=plant['id'],plain=truth,cipher=cipher,literal_positions=path,ordinary_trials=len(queue),F_trials=len(selected) if mode=='literal_f' else 0,planted_rigid_rank=1+next(i for i,r in enumerate(ranks) if r[1]==plantix),planted_survived=pr is not None,truth_hypothesis_rank=None if pr is None else 1+sum(r[0]>pr[0] for r in evaluated),best_errors=sum(a!=b for a,b in zip(best[2],truth)),planted_errors=None if pr is None else sum(a!=b for a,b in zip(pr[2],truth)),truth_in_planted_top16=None if pr is None else any(x['plain']==truth for x in pr[3]) if pr[3] else pr[2]==truth,top=[dict(score=r[0],cell=queue[r[1]],plain=r[2]) for r in evaluated[:20]],planted_alternatives=[] if pr is None else pr[3],corrupted_key_errors=sum(a!=b for a,b in zip(ca[0]['plain'],truth))))
 s.dump(s.O/'r02/controls.json',dict(source='audit/parallel-01/reference/sources/solved_p57_parable.txt',caveat='Control text is a separately held solved page; is present as one running-text candidate, not quadgram training. Two examples do not measure broad register power.',results=results,seconds=time.monotonic()-t));print(json.dumps([dict(mode=x['mode'],planted_survived=x['planted_survived'],truth_hypothesis_rank=x['truth_hypothesis_rank'],best_errors=x['best_errors'],planted_errors=x['planted_errors']) for x in results]))
if __name__=='__main__':main()
