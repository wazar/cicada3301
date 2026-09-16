import itertools,json,pathlib
O=pathlib.Path(__file__).resolve().parent
rows=[]
def inverse(c,alphabet):
 loc={v:i for i,v in enumerate(alphabet)};at=dict(enumerate(alphabet));out=[]
 for v in c:
  k=loc[v];out.append(k);old=at[0];at[0]=v;at[k]=old;loc[v]=0;loc[old]=k
 return out
for n in [3,4]:
 total=0
 for cipher in itertools.product(range(n),repeat=5):
  canonical=inverse(cipher[1:],[cipher[0]]+[x for x in range(n) if x!=cipher[0]])
  for initial in itertools.permutations(range(n)):
   decoded=inverse(cipher,initial)[1:];f={0:0};rev={0:0}
   for a,b in zip(decoded,canonical):assert f.setdefault(a,b)==b and rev.setdefault(b,a)==a
   total+=1
 rows.append({'alphabet_size':n,'ciphertext_length':5,'ciphertexts':n**5,'initial_alphabets':__import__('math').factorial(n),'checks':total,'passed':total})
(O/'j01-verify-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
