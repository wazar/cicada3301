import pathlib,json,gzip,sys,importlib.util,math
B=pathlib.Path('exploration/persistent-01/worker-s');spec=importlib.util.spec_from_file_location('replayp03',B/'S14_p03_frozen.py');p03=importlib.util.module_from_spec(spec);spec.loader.exec_module(p03);lm=p03.LM();ix=int(sys.argv[1]);r=json.loads(gzip.decompress((B/f'S14-packet{ix}-main.json.gz').read_bytes()));assert r['complete'];cs={x['id']:x['cell'] for x in r['cells']};trans=[x['transliteration'] for x in json.loads(pathlib.Path('KNOWLEDGE.json').read_text())['gematria_primus']['table']];outputs=[]
for alt in r['global16']:
 cell=cs[alt['id']];e=cell['e'];inverse=pow(e,-1,28);key=cell['key'];sign=cell['sign'];literal=set(alt['literal_positions']);u=0;cipher=[]
 for i,p in enumerate(alt['plain']):
  assert pow(p,e,29)==alt['power_plain'][i]
  if i in literal:assert p==0;cipher.append(0)
  else:cipher.append(pow((pow(p,e,29)-sign*pow(key[u%len(key)],e,29))%29,inverse,29));u+=1
 assert cipher==r['cipher'] and u==alt['used']
 context=(29,29);logscore=0.;words=[];word='';ends=set(r['ends'])
 for i,p in enumerate(alt['plain']):
  word+=trans[p]
  if i in ends:words.append(word);word=''
  for token in ([p,29] if i in ends else [p]):
   probability=(lm.c[0][(token,)]+.5)/(lm.t[0][()]+15)
   for order,alpha in [(1,8),(2,5)]:
    ctx=context[-order:];probability=(lm.c[order][ctx+(token,)]+alpha*probability)/(lm.t[order][ctx]+alpha)
   logscore+=math.log(probability);context=(context[-1],token)
 if word:words.append(word)
 score=logscore/(len(alt['plain'])+len(ends));assert abs(score-alt['score'])<1e-12
 outputs.append({'id':alt['id'],'score':score,'reencryption':'PASS','power_mapping':'PASS','independent_scalar_rescore':'PASS','transliteration_with_original_word_boundaries':' '.join(words),'canonical_runes':alt['plain'],'literal_positions':alt['literal_positions'],'aliases':alt['aliases']})
(B/f'S14-replay-main{ix}.json').write_text(json.dumps({'packet':ix,'outputs':outputs},indent=2)+'\n');print(json.dumps({'packet':ix,'retained_distinct_global_paths':len(outputs),'all_replays':'PASS','top_id':outputs[0]['id'],'top_transliteration':outputs[0]['transliteration_with_original_word_boundaries']},ensure_ascii=False))
