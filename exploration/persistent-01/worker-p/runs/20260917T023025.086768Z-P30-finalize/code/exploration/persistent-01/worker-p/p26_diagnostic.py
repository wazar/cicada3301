import p26 as m
import json
backup={}
for i in range(4):
 name=f'control-{i}.json';r=json.loads((m.OUT/name).read_text());backup[name]=r['order_recovery'];r['order_recovery']=[m.affine(c['cycle'],r['cycle']) for c in r['candidates']];m.save(name,r)
 name=f'control-{i}-summary.json';s=json.loads((m.OUT/name).read_text());backup[name]=s['selected_order_recovery'];s['selected_order_recovery']=r['order_recovery'][r['selected']];m.save(name,s)
m.save('diagnostic-before-translation.json',dict(reason='Partial-match translation must be optimized even though exact equality gauge fixes it; no scores/orders/selection changed.',previous=backup))
print('Full affine partial agreement:',[json.loads((m.OUT/f'control-{i}-summary.json').read_text())['selected_order_recovery'] for i in range(4)])
