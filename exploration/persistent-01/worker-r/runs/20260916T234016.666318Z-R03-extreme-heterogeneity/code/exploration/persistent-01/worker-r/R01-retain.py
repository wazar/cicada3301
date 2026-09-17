import pathlib,json,hashlib,collections
p=pathlib.Path('exploration/persistent-01/worker-r');ns={};s=(p/'R01.py').read_text();ns['__file__']=str((p/'R01.py').resolve());exec(s.split('# Isolated evaluator arithmetic:')[0],ns)
x=json.loads((p/'R01-results.json').read_text());ret=[]
for row in x['controls']:
 ds=ns['control'](row['seed'],row['planted']);z,c=ns['fit'](ds);v=sum(q['starts_count'] for q in ns['evaluate'](ds,z));assert (z,v)==(row['selected_zero'],row['violations'])
 ret.append(dict(seed=row['seed'],planted=row['planted'],pages=[dict(page=q['page'],indices=q['indices']) for q in ds]))
(p/'R01-control-streams.json').write_text(json.dumps(ret)+'\n')
c=collections.Counter(q['indices'][i] for q in ns['D'] for i in ns['points'](q));print('all-discovery start counts',dict(sorted(c.items())));assert len(c)==29
print('Retained and replay-checked',len(ret),'complete control streams with source positions inherited from R01-input.json.')
