import json,hashlib,random,secrets,pathlib
OUT=pathlib.Path('audit/parallel-01/coordination'); secret=secrets.randbits(128); rng=random.Random(secret)
tokens='F U TH O R C G W H N I J EO P X S T B E M L ING OE D A AE Y IA EA'.split()
def encode(text):
 s=''.join(c for c in text.upper() if c.isalpha()).replace('V','U').replace('K','C').replace('Z','S').replace('Q','C');out=[]
 while s:
  for t in sorted(tokens,key=len,reverse=True):
   if s.startswith(t):out.append(tokens.index(t));s=s[len(t):];break
  else:raise ValueError(s)
 return out
def encrypt(p,k,draw):
 out=[];used=[];j=0
 for x in p:
  while True:
   y=(x+k[j])%29
   if out and y==out[-1] and draw()<.83:j+=1;continue
   out.append(y);used.append(j);j+=1;break
 return out,used
assert encrypt([1,2,3],[0,28,4,5],lambda:0)==([1,6,8],[0,2,3])
assert encode('FUTHORC')==[0,1,2,3,4,5]
texts=[
'On a cold morning the keeper opened the little library beside the river. She placed a clean sheet of paper on the table and counted the books before the first visitor arrived. Outside the window a bird waited for the rain to stop. The room was quiet and bright.',
'The carpenter carried a wooden box across the garden and set it under the apple tree. Inside were a small hammer and three smooth stones. Before lunch he repaired the broken chair and wrote a letter to his sister describing the work he had finished that morning.']
plain=[encode(t)[:120] for t in texts];assert all(len(p)==120 for p in plain)
keys=[[rng.randrange(29) for _ in range(2048)] for _ in range(8)];correct=rng.randrange(8);encoded=[encrypt(p,keys[correct],rng.random) for p in plain]
challenge={'id':'parallel01-blind-v1','candidate_ids':[f'candidate-{i}' for i in range(8)],'keys':keys,'ciphertext_pages':[c for c,u in encoded],'declared_model':{'alphabet_size':29,'key_reset':'each_page','filter_state_reset':'each_page','repeat_rejection_probability':.83,'offset':0,'sign_convention':'c=p+k mod29','key_length':2048,'page_length':120},'generator_hand_checks':'mod29 arithmetic, repeat rejection advances key only, FUTHORC mapping assertions passed'}
answer={'correct_candidate':f'candidate-{correct}','seed':secret,'plaintext_indices':plain,'text_sources':'Fresh coordinator-authored prose, not inherited plant or training fixture','texts':texts,'used_key_positions':[u for c,u in encoded]}
answerbytes=(json.dumps(answer,indent=2)+'\n').encode();pathlib.Path('/tmp/lp_parallel01_blind_answer.json').write_bytes(answerbytes)
(OUT/'blind-challenge.json').write_text(json.dumps(challenge,indent=2)+'\n');(OUT/'blind-commitment.json').write_text(json.dumps({'answer_sha256':hashlib.sha256(answerbytes).hexdigest(),'challenge_sha256':hashlib.sha256((OUT/'blind-challenge.json').read_bytes()).hexdigest(),'created_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'separation':'Answer and generating seed withheld outside supplied worker directory until saved ranking. Shared filesystem; procedural blinding, not an access-control boundary.'},indent=2)+'\n')
print('hand checks PASS; challenge saved; answer commitment saved')
