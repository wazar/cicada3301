import pathlib,json,collections
O=pathlib.Path(__file__).resolve().parent/'C07';inputs=json.loads((O/'inputs.json').read_text());rows=[]
for i,c in enumerate(inputs['controls']):
 local=json.loads((O/f'control{i:02}-local.json').read_text());book=json.loads((O/f'control{i:02}-book.json').read_text());rows.append(dict(index=i,id=c['id'],kind=c['kind'],n=len(c['plain']),k=c['k'],local_rank=local['rank'],book_rank=book['rank'],selected_book_feature=book['selected']))
s=dict(controls=25,language_controls=20,uniform_controls=5,rows=rows,note='Threshold summaries are descriptive; no preregistered all-control perfect gate. Local and full-composite sensitivity differ. Four nested source prefixes, not20independent prose populations.')
(O/'control-summary.json').write_text(json.dumps(s,indent=2)+'\n')
for r in rows:print(r)
