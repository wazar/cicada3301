"""Find a small witness that current normal history cannot replace immutable seed."""
import itertools,json,pathlib
OUT=pathlib.Path(__file__).with_name('reset-seed-counterexample.json')
def paths(c,seed,a):
 states=[([],[],[],0)]
 for v in c:
  nxt=[]
  for plain,hist,mask,n in states:
   key=seed[n] if n<len(seed) else sum(hist[-len(seed):])%a
   p=(v-key)%a;nxt.append((plain+[p],hist+[p],mask+[False],n+1))
   if v==0:nxt.append((plain+[0],hist,mask+[True],n))
  states=nxt
 return states
for a in (2,3):
 for k in (1,2):
  for n in range(2,8):
   for c in itertools.product(range(a),repeat=n):
    seen={}
    for seed in itertools.product(range(a),repeat=k):
     for plain,hist,mask,used in paths(c,seed,a):
      if used<k:continue
      state=(min(used,k),tuple(hist[-k:]),tuple(plain[-2:]))
      old=seen.get(state)
      if old and old['seed'][0]!=seed[0]:
       new={'seed':list(seed),'plain':plain,'literal':mask,'normal_count':used}
       witness={'alphabet':a,'k':k,'cipher_prefix':list(c),'omitted_seed_state':state,'path1':old,'path2':new,'reset_next_cipher':1%a,'path1_next_normal_plain':(1-old['seed'][0])%a,'path2_next_normal_plain':(1-seed[0])%a,'interpretation':'At the fixed next reset, histories clear but the two immutable seeds produce different next ordinary plaintexts. Matching active history/context alone is not a sufficient state.'}
       OUT.write_text(json.dumps(witness,indent=2)+'\n');print(json.dumps(witness));raise SystemExit
      seen[state]={'seed':list(seed),'plain':plain,'literal':mask,'normal_count':used}
raise RuntimeError('no witness in frozen finite grid')
