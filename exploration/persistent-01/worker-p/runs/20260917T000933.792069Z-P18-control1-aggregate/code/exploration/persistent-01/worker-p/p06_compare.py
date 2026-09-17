import pathlib,json,hashlib,collections,math
D=pathlib.Path('exploration/persistent-01/worker-p/P06');B=D.parents[1];assert not (B/'STOP').exists()
files=[(D/'predictions.json','7adcd28431e039d1ace415e7e65bccce89e3e8716e6c0e6fea6d20cf239ef30a'),(B/'review-11/predictions-frozen.json','fb505e5d7e29fe83f53e0ee65fbab6f4ee6a68c55d23676ff4cefa9922a8dd96'),(B/'coordinator/P06-third-predictions.json','9cde0ef16cea3212f30b368535357e5eb39010c5c74539154eef567d27466ab9')];readers=[]
for p,h in files:
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 x=json.loads(p.read_text())
 if 'predictions'in x:
  rows=x['predictions'];a={r.get('crop_id',r.get('number')):r['rune_id'] for r in rows};conf={r.get('crop_id',r.get('number')):r.get('confidence') for r in rows}
 else:a={int(k):v for k,v in x.items()};conf={int(k):v for k,v in json.loads((D/'confidence.json').read_text()).items()}
 assert sorted(a)==list(range(1,101));readers.append(dict(path=str(p),sha256=h,predictions=[a[i] for i in range(1,101)],confidence=[conf[i] for i in range(1,101)]))
truth=json.loads((D/'hidden-labels.json').read_text());selection=json.loads((D/'selection.json').read_text());dataset=json.load(open('audit/parallel-01/inputs/dataset.json'));pageby={p['original_page']:p for p in dataset['pages'] if p['original_page'] in [56,57]};assert len(truth)==100
for r,t in zip(selection,truth):assert pageby[r['page']]['indices'][r['page_rune_index']]==t
for r in readers:
 wrong=[dict(crop_id=i+1,predicted=a,reference=b,confidence=r['confidence'][i],source=selection[i]) for i,(a,b) in enumerate(zip(r['predictions'],truth)) if a!=b];r.update(correct=100-len(wrong),errors=wrong,abstentions=sum(v is None or v not in range(29) for v in r['predictions']),gate_pass=len(wrong)<=1)
consensus=[];disagree=[]
for i in range(100):
 cnt=collections.Counter(r['predictions'][i] for r in readers);pred,n=cnt.most_common(1)[0];consensus.append(pred if n>=2 else None)
 if len(cnt)>1:disagree.append(dict(crop_id=i+1,reader_predictions=[r['predictions'][i] for r in readers],reference=truth[i]))
wrong=[dict(crop_id=i+1,predicted=a,reference=b,source=selection[i]) for i,(a,b) in enumerate(zip(consensus,truth)) if a!=b];out=dict(readers=readers,consensus=dict(predictions=consensus,correct=100-len(wrong),errors=wrong,no_majority=sum(v is None for v in consensus),gate_pass=len(wrong)<=1),disagreements=disagree,truth=truth,reference_counts=dict(collections.Counter(truth)),n_unique_glyphs=100,pool_eligible=168,excluded_red_or_dropcap=12,remaining_eligible=68,limits='same100glyphs andsame-modelreaders, correlatederrors; inheritedvisibleciphertextlabels, ordinalgeometryvalidation not freshtranscriptiongroundtruth')
(D/'comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(readers=[dict(path=r['path'],correct=r['correct'],gate_pass=r['gate_pass'],errors=[{k:v for k,v in e.items() if k!='source'} for e in r['errors']]) for r in readers],consensus={k:v for k,v in out['consensus'].items() if k not in ['predictions','errors']},consensus_errors=[{k:v for k,v in e.items() if k!='source'} for e in wrong],disagreements=len(disagree)),indent=2))
