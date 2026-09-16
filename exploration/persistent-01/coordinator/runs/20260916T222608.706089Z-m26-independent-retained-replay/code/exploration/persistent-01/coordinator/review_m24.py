"""Independent categorical accounting and stationary latent-rank construction."""
import json,gzip,math
from pathlib import Path
B=Path('exploration/persistent-01');W=B/'worker-m/M24';real=json.loads((W/'real.json').read_text());rep=json.load(gzip.open(W/'replicates.json.gz','rt'));checked=0
for r in [real]+rep:
 tr=r['train_counts'];he=r['held_counts'];total=sum(map(sum,tr));base=[(tr[0][i]+tr[1][i]+1)/(total+28) for i in range(28)];q=[[(row[i]+28*base[i])/(sum(row)+28) for i in range(28)] for row in tr];score=sum(he[g][i]*math.log(q[g][i]/base[i]) for g in range(2) for i in range(28))/sum(map(sum,he));assert max(abs(x-y) for x,y in zip(base,r['base']))<1e-14;assert abs(score-r['held_score'])<1e-12;checked+=1
null=[x['held_score'] for x in rep if x['kind']=='null'];tail=(1+sum(x>=real['held_score'] for x in null))/(1+len(null));assert tail==real['tail']
chains=[];pi=3/28
for rho in [0,.3,.6]:
 rows=[]
 for prev in range(28):
  p=pi+rho*(1-pi) if prev<3 else pi*(1-rho);rows.append([p/3 if nxt<3 else (1-p)/25 for nxt in range(28)])
 assert max(abs(sum(r)-1) for r in rows)<1e-14
 assert max(abs(sum(rows[i][j]/28 for i in range(28))-1/28) for j in range(28))<1e-14
 mi=sum(v*math.log(v*28)/28 for row in rows for v in row if v)
 chains.append({'rho':rho,'transition_rows':rows,'stationary_rank_probability':1/28,'latent_mutual_information_nats':mi})
out={'checked_saved_predictors':checked,'held_score':real['held_score'],'tail':tail,'independently_reconstructed_chains':chains,'scope':'Independent saved count-to-table/score accounting and uniform stationary latent-rank proof; worker replay checks output maps. No first-occurrence eligibility or full-rune predictive claim.'};(B/'coordinator/M24-accounting-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checked':checked,'tail':tail,'latent_MI':[x['latent_mutual_information_nats'] for x in chains]}))
