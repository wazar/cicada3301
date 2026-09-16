"""Prepare immutable inputs without importing or calling the detector."""
import json,hashlib,pathlib,datetime
O=pathlib.Path(__file__).resolve().parent
R=O.parents[1]
def save(name,x):
 p=O/name
 with p.open('x') as f: json.dump(x,f,indent=2);f.write('\n')
 return hashlib.sha256(p.read_bytes()).hexdigest()
T='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
def encode(s):
 s=s.upper().translate(str.maketrans({'V':'U','K':'C','Q':'C','Z':'S'}));out=[]
 while s:
  tok=next((t for t in sorted(T,key=len,reverse=True) if s.startswith(t)),None)
  if tok:out.append(T.index(tok));s=s[len(tok):]
  else:
   assert not s[0].isalpha();s=s[1:]
 return out
ps=[];n=2
while len(ps)<2048:
 if all(n%d for d in range(2,int(n**.5)+1)):ps.append(n)
 n+=1
base={'DIVINITY':encode('DIVINITY'),'FIRFUMFERENFE':encode('FIRFUMFERENFE')}
keys={k:(v*2048)[:2048] for k,v in base.items()};keys.update(PRIMES=[p%29 for p in ps],TOTIENTS=[(p-1)%29 for p in ps])
kh=save('keys.json',keys)
nouns=['BAKER','FARMER','PAINTER','TEACHER','SAILOR','GARDENER','CARPENTER','TRAVELLER','READER','WRITER','FISHERMAN','COOK','BUILDER','POTTER','WEAVER','SINGER','BROTHER','SISTER','NEIGHBOUR','FRIEND']
fixtures=[]
for i,noun in enumerate(nouns):
 texts=[f'THE {noun} OPENED THE DOOR BEFORE THE SUN ROSE AND WALKED THROUGH THE QUIET STREET. A CHILD WAS SITTING BESIDE THE WINDOW WITH A BOOK ABOUT THE SEA. WHEN THE RAIN BEGAN THEY WENT INTO THE HOUSE AND PUT THE WET CLOTHES NEAR THE FIRE.', f'AFTER THE EVENING MEAL THE {noun} TOOK A LETTER FROM THE TABLE AND READ IT TO THE FAMILY. IT TOLD OF A LONG JOURNEY THROUGH THE MOUNTAINS AND A LITTLE VILLAGE WHERE PEOPLE GATHERED TO HEAR STORIES. EVERYONE LISTENED UNTIL THE LAST WORD.']
 fixtures.append({'case':i,'texts':texts,'plaintext':[encode(t)[:120] for t in texts]})
fh=save('fixtures.json',fixtures)
ds=json.loads((R/'audit/parallel-01/inputs/dataset.json').read_text());slices=[]
for name in ['0.jpg','1.jpg']:
 p=next(p for p in ds['pages'] if p['original_filename']==name)
 a=p['indices'][:120];slices.append({'original_filename':name,'segment_id':p['segment_id'],'indices':a,'sha256_bytes_indices':hashlib.sha256(bytes(a)).hexdigest()})
sh=save('slices.json',slices)
plan=[]
for recipe in keys:
 for sign in [-1,1]:
  for model in ['unfiltered_rigid','rejection_beam']:
   plan.append({'recipe':recipe,'sign':sign,'model':model,'cases':list(range(20))})
spec={'version':'experiment-01-prereg-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'proposal_verbatim':(R/'audit/parallel-01/coordination/PROPOSED-EXPERIMENT.md').read_text(),'keys_sha256':kh,'fixtures_sha256':fh,'slices_sha256':sh,'alphabet_tokens':T,'key_length':2048,'length':120,'offset':0,'reset':'key and filter at each page','decode_sign':'p=(c+sign*k)%29; encrypt c=(p-sign*k)%29','positive_cells':plan,'positive_cases_total':320,'positive_order':'recipe then sign then model then case; stop at first failure','positive_rule':'Required planted decoder must exactly recover both complete plaintext arrays, planted recipe/sign must be among exact-equality tied maximum joint hypotheses, and at least one tied winning decoder under that hypothesis on each page must exactly recover truth. No tolerance or tie break discards ties. No score floor is added to this positive rule.','beam':{'beam_w':400,'max_skip':3},'rejection':{'probability':0.83,'advance':1,'seed':'910000 + cell_index*1000 + case*2 + page','no_cap_on_encrypt_rejections':True},'selection':'For every recipe/sign choose maximum score over rigid and beam per page, take min of those two maxima, then maximum over recipe/sign. Same recipe and sign across pages.','dedup':'exact identical 2048 arrays grouped preserving labels; no equivalent arrays found is reported; signs grouped if signed mod29 arrays identical','negative_plan':{'calibration_pairs':100,'heldout_pairs':100,'seed':920000,'keys':'persistent Random(seed+case) independent uniform 2048 arrays excluded if signed equivalent to candidate','plaintext':'authored fixtures cycled, new key per pair','model':'alternate unfiltered and rejection .83 per pair; balanced signs, resets per page','full_selection':True},'flag_rule':'both selected page scores >= -5.5 AND joint > calibration maximum +0.5; any heldout flag blocks experiment','shuffle_panel':{'pairs':100,'seed':930000,'source':'real slices only after synthetic positive/calibration gates','separate':True,'warning':'preserves histogram but destroys adjacency including repeat patterns; no threshold tuning'},'budget_seconds':1800,'pilot_seconds_max':300,'main':'one named batch <=1800 only after coordinator approves measured cost budget','language_caveat':'20 authored template variations, not 20 independent language corpora. Texts composed before scoring; none selected or rejected by score.','real_execution':'all 32 page choices once only after all synthetic gates; no offsets/additional pages/recipes'}
ph=save('preregistration.json',spec)
save('FREEZE.json',{'preregistration_sha256':ph,'keys_sha256':kh,'fixtures_sha256':fh,'slices_sha256':sh,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print(json.dumps({'preregistration_sha256':ph,'cells':16,'cases':320,'keys_sha256':kh}))
