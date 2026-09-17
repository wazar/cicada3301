import pathlib,gzip,json
from compare import O
TOKENS='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def text(p,ends):return ''.join(TOKENS[r]+(' ' if i in ends else '') for i,r in enumerate(p))
summary={}
for name in ['references','fresh','section','complementary-references','complementary-fresh','complementary-section']:
 rows=[read(p) for p in sorted((O/name).glob('*.gz'))]
 if not rows:continue
 summary[name]=dict(cases=len(rows),exact_seconds=sum(r['seconds'] for r in rows),beams={w:dict(misses=sum(r['beams'][w]['gap']>1e-12 for r in rows),max_gap=max(r['beams'][w]['gap'] for r in rows),seconds=sum(r['beams'][w]['seconds'] for r in rows)) for w in ['64','256','1024']})
 if 'section' not in name:
  summary[name]['truth']=[dict(id=r['case']['id'],**r['truth_metrics']) for r in rows]
  errors=[]
  for r in rows:
   if r['truth_metrics']['best_errors']:
    t=r['case']['truth'];p=r['exact'][0]['plain'];es=[i for i,(a,b) in enumerate(zip(t,p)) if a!=b];errors.append(dict(id=r['case']['id'],error_positions=es,truth=text(t,set(r['case']['ends'])),best=text(p,set(r['case']['ends'])),truth_literals=r['case'].get('truth_literal_positions'),best_literals=r['exact'][0]['literal_positions']))
  (O/(name+'-ranking-errors.json')).write_text(json.dumps(errors,indent=2)+'\n')
 else:
  alts=[]
  for policy in ['body','whole']:
   group=[r for r in rows if r['case']['policy']==policy];choices=sorted([(a['score'],r,a) for r in group for a in r['exact']],key=lambda x:-x[0]);seen=set();retained=[]
   for score,r,a in choices:
    plain=tuple(a['plain'])
    if plain in seen:continue
    seen.add(plain);retained.append(dict(id=r['case']['id'],policy=policy,**a,transliteration=text(a['plain'],set(r['case']['ends']))))
    if len(retained)==16:break
   alts.extend(retained);summary[name][policy]=dict(best=choices[0][0],best_id=choices[0][1]['case']['id'],global_distinct_retained=len(retained),scope='top16 distinct among retained celltop16, not globally certified top16 distinct plaintexts')
  (O/(name+'-global-alternatives.json')).write_text(json.dumps(alts,indent=2)+'\n');(O/(name+'-full-alternatives.txt')).write_text('\n\n'.join(f"{a['id']} {a['score']}\n{a['transliteration']}" for a in alts)+'\n')
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:{q:v for q,v in s.items() if q!='truth'} for k,s in summary.items()},indent=2))
