import json,pathlib
R=pathlib.Path(__file__).parent;S=json.load(open(R/'experiment01-result.json'));D=json.load(open('audit/parallel-01/inputs/dataset.json'));W=json.load(open(R/'experiment01-discovery-cells.json'));ps={p['original_page']:p for p in D['pages'] if p['original_page'] in S['pages']};ws={p['page']:p['cells'] for p in W}
def eligible(v,n,b):return all(0<=x-b<n for x in v)
for s in S['sources']:
 for b in [0,1]:assert eligible(s['values'],2000,b) and not eligible(s['values'],10,b)
out=[];checks=0
for si,s in enumerate(S['sources']):
 for n,p in ps.items():
  for unit,items in [('rune',p['indices']),('word',ws[n])]:
   for b in [0,1]:
    checks+=1
    if eligible(s['values'],len(items),b):out.append({'grid':si,'page':n,'unit':unit,'base':b,'positions':[v-b for v in s['values']],'selected':[items[v-b] for v in s['values']]})
x={'checks':checks,'complete_count':len(out),'complete':out,'source_unique_indices':[len(set(s['values'])) for s in S['sources']],'source_centrosymmetric':[s['values']==s['values'][::-1] for s in S['sources']],'rune_page_max':max(len(p['indices']) for p in ps.values()),'word_page_max':max(len(p) for p in ws.values()),'controls_pass':True}
(R/'experiment03-result.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({k:v for k,v in x.items() if k!='complete'},indent=2))
