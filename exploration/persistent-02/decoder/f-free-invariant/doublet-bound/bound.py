"""Conservative seed/mask-independent forced ciphertext-doublet positions."""
def forced(plain,k):
 assert k in (2,3) and all(type(p)==int and 0<=p<29 for p in plain);runs=[];start=None;positions=[];eligible=[]
 for i,p in enumerate(list(plain)+[0]):
  if p!=0 and start is None:start=i
  if p==0 and start is not None:
   runs.append([start,i]);eligible.extend(range(start+k+1,i));positions.extend(j for j in range(start+k+1,i) if plain[j]==plain[j-k-1]);start=None
 assert len(set(positions))==len(positions)
 return dict(length=len(plain),k=k,runs=runs,eligible_positions=eligible,forced_doublet_positions=positions,lower_bound=len(positions),eligible=len(eligible))

def scalar_encode(p,seed,mask,include_literal,N=29):
 history=[];normal=0;c=[];k=len(seed)
 for i,x in enumerate(p):
  if i in mask:
   assert x==0;c.append(0)
   if include_literal:history.append(x)
  else:
   key=seed[normal] if normal<k else sum(history[-k:]);c.append((x+key)%N);history.append(x);normal+=1
 return c
