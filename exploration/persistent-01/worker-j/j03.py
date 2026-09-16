import pathlib,json,gzip,ast,collections
import numpy as np
O=pathlib.Path(__file__).resolve().parent
m=ast.parse((O/'j02.py').read_text());nodes=[x for x in m.body if isinstance(x,ast.FunctionDef) and x.name in ['cost','bound']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'j02.py::cost,bound','exec'))
T=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
D=json.loads((O/'j01-results.json').read_text());C=json.loads((O/'j02-results.json').read_text());texts=[];controls=[];windows=[]
for c in D['controls']:
 if c['mode']!='original':continue
 seq=[];maps=[]
 for i,r in enumerate(c['source']):
  raw=(r-1)%29
  for j,letter in enumerate(T[raw]):seq.append(ord(letter)-65);maps.append({'source_rune_index':i,'rune':raw,'letter_offset':j})
 assert ''.join(T[x['rune']][x['letter_offset']] for x in maps)==''.join(chr(v+65) for v in seq)
 texts.append({'name':c['name'],'source':seq,'source_map':maps,'n':len(seq),'distinct':len(set(seq))})
maxlen=max(a['n'] for a in C['actual']);dist=np.array([1.]);offset=0;summ=[]
for a in C['actual']:
 n=a['n'];ws=[]
 for t in texts:
  if len(t['source'])<maxlen:continue
  for start in range(len(t['source'])-n+1):
   counts=np.bincount(t['source'][start:start+n],minlength=26).tolist();v=bound(counts);ws.append({'group':t['name'],'start':start,'counts':counts,'bound':v})
 vals=[w['bound'] for w in ws];lo=min(vals);hist=np.bincount(np.array(vals)-lo)/len(vals);dist=np.convolve(dist,hist);offset+=lo
 summ.append({'page':a['page'],'n':n,'actual':a['pairs'],'minimum':lo,'windows':len(ws),'compatible':sum(v<=a['pairs'] for v in vals),'fraction':sum(v<=a['pairs'] for v in vals)/len(vals),'median':float(np.median(vals))})
 w=min(ws,key=lambda w:w['bound']);value,ks=bound(w['counts'],allocation=True);cipher=[];source=[];book={};off=0
 for rune,(cnt,k) in enumerate(zip([v for v in w['counts'] if v],ks)):
  book.update({off+j:rune for j in range(k)});cipher.extend(off+j%k for j in range(cnt));source.extend([rune]*cnt);off+=k
 assert sum(v*(v-1)//2 for v in collections.Counter(cipher).values())==value and [book[x] for x in cipher]==source
 controls.append({'page':a['page'],'window':w,'allocation':ks,'cipher':cipher,'source_class_indices':source,'bound':value,'attained':True});windows.append(ws)
with gzip.open(O/'j03-windows.json.gz','wt') as f:json.dump({'texts':texts,'lengths':[a['n'] for a in C['actual']],'windows':windows},f)
actual=sum(a['pairs'] for a in C['actual']);p=float(dist[:max(0,actual-offset+1)].sum());result={'transliteration':T,'summaries':summ,'controls':controls,'aggregate_capacity_compatibility':p,'actual_total':actual,'distribution_offset':offset,'distribution':dist.tolist(),'new_texts':[{'name':t['name'],'n':t['n'],'distinct':t['distinct']} for t in texts]}
(O/'j03-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['distribution','controls','transliteration']}))
