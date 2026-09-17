import ast,collections,datetime,gzip,hashlib,itertools,json,pathlib,time,random
D=pathlib.Path('exploration/persistent-01/worker-p/P03');B=pathlib.Path('exploration/persistent-01');rng=random.Random(130103)
def guard():
 assert not (B/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
# inspected solver definitions only; preserve parent worker files
p=B/'worker-o/o02.py';tree=ast.parse(p.read_text());nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['necessary','Limit','solve','brute']];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p)+'::definitions','exec'))
J=json.load(gzip.open(B/'worker-j/j03-windows.json.gz','rt'));M=json.loads((B/'worker-f/F06-maps.json').read_text());pages=[0,1,3,7,17];maps={m['page']:m for m in M if m['page'] in pages};names=['0_koan_1','0_loss_of_divinity','0_welcome','jpg107-167'];vowels=set('AEIOU');T=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
transform_controls=[dict(rune=i,latin=t,consonants=''.join(c for c in t if c not in vowels)) for i,t in enumerate(T)];assert transform_controls[26]['consonants']=='Y';assert transform_controls[12]['consonants']=='';assert transform_controls[2]['consonants']=='TH'
texts=[]
for name in names:
 t=next(x for x in J['texts'] if x['name']==name);rows=[];seq=[];runes=collections.defaultdict(list)
 for i,(letter,m) in enumerate(zip(t['source'],t['source_map'])):
  c=chr(letter+65);assert T[m['rune']][m['letter_offset']]==c
  row=dict(m,expanded_index=i,letter=c,keep=c not in vowels,consonant_index=len(seq) if c not in vowels else None);rows.append(row);runes[m['source_rune_index']].append(row)
  if row['keep']:seq.append(letter)
 assert [ord(r['letter'])-65 for r in rows]==t['source'];assert [ord(r['letter'])-65 for r in rows if r['keep']]==seq
 assert all(''.join(r['letter'] for r in rs)==T[rs[0]['rune']] for rs in runes.values())
 texts.append(dict(name=name,source=seq,all_letter_map=rows,rune_map=[dict(source_rune_index=i,rune=rs[0]['rune'],expanded_indices=[r['expanded_index'] for r in rs],retained_indices=[r['consonant_index'] for r in rs if r['keep']],removed_expanded_indices=[r['expanded_index'] for r in rs if not r['keep']]) for i,rs in sorted(runes.items())],original_expanded_n=len(rows),consonantal_n=len(seq),deleted=sum(not r['keep'] for r in rows)))
guard();tiny=[]
for z in range(200):
 n=rng.randrange(2,7);k=rng.randrange(1,min(n,3)+1);items=[rng.randrange(1,5) for _ in range(n)];cuts=sorted(rng.sample(range(1,sum(items)),k-1));targets=[b-a for a,b in zip([0]+cuts,cuts+[sum(items)])];r=solve(items,targets);truth=brute(items,targets);assert (r['status']=='FEASIBLE')==truth and r['status']!='UNKNOWN';tiny.append(dict(items=items,targets=targets,result=r,brute=truth))
controls=[];real=[];startall=time.monotonic()
for page in pages:
 guard();observed=collections.Counter(maps[page]['indices']);items=sorted(observed.values());n=sum(items)
 planted=[0]*15;perm=items[:];rng.shuffle(perm)
 for i,v in enumerate(perm):planted[i%15]+=v
 for targets,want in [(planted,'FEASIBLE'),([1]*(items.count(1)+1)+[n-items.count(1)-1],'INFEASIBLE')]:
  r=solve(items,targets);assert r['status']==want;controls.append(dict(page=page,items=items,targets=targets,result=r))
 cases={};weights=[]
 for t in texts:
  kept=[r for r in t['all_letter_map'] if r['keep']];weights.append(dict(group=t['name'],windows=max(0,len(t['source'])-n+1)))
  for start in range(max(0,len(t['source'])-n+1)):
   cnt=collections.Counter(t['source'][start:start+n]);counts=[cnt[i] for i in range(26)];key=tuple(sorted(cnt.values()));cases.setdefault(key,[]).append(dict(group=t['name'],start=start,end=start+n,letter_counts=counts,expanded_span=[kept[start]['expanded_index'],kept[start+n-1]['expanded_index']+1],source_rune_span=[kept[start]['source_rune_index'],kept[start+n-1]['source_rune_index']+1]))
 results=[]
 for targets,provenance in sorted(cases.items()):
  guard();reason=necessary(items,targets)
  if reason:r=dict(status='INFEASIBLE',reason=reason,nodes=0)
  elif time.monotonic()-startall>240:r=dict(status='UNKNOWN',reason=dict(kind='global_budget'))
  else:r=solve(items,targets)
  if r['status']=='FEASIBLE':
   available=collections.defaultdict(list)
   for rune,num in sorted(observed.items()):available[num].append(rune)
   groups=[[available[num].pop(0) for num in group] for group in r['groups']];r['output_rune_groups']=groups;assert sorted(sum(groups,[]))==sorted(observed)
   for prov in provenance:
    letters=sorted((num,letter) for letter,num in enumerate(prov['letter_counts']) if num);prov['letter_to_output_runes']=[dict(letter_index=letter,output_runes=group) for (num,letter),group in zip(letters,groups)]
  results.append(dict(targets=targets,provenance=provenance,result=r))
 real.append(dict(page=page,n=n,output_counts_by_rune=sorted(observed.items()),items=items,source_weights=weights,windows=sum(len(c['provenance']) for c in results),deduplicated_cases=len(cases),cases=results))
 print('page',page,'windows',real[-1]['windows'],flush=True)
summary=[]
for page in real:
 count=collections.Counter();reasons=collections.Counter();bygroup={t['name']:collections.Counter() for t in texts}
 for c in page['cases']:
  r=c['result'];count[r['status']]+=len(c['provenance'])
  if 'reason' in r:reasons[r['reason']['kind']]+=len(c['provenance'])
  for p in c['provenance']:bygroup[p['group']][r['status']]+=1
 summary.append(dict(page=page['page'],n=page['n'],windows=page['windows'],deduplicated_cases=page['deduplicated_cases'],statuses_weighted=dict(count),reasons_weighted=dict(reasons),source_weights=page['source_weights'],source_statuses={k:dict(v) for k,v in bygroup.items()}))
e=dict(real=real,texts=texts,tiny_controls=tiny,actual_controls=controls,transform_controls=transform_controls,seed=130103,source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [B/'worker-j/j03-windows.json.gz',B/'worker-f/F06-maps.json',B/'worker-o/o02.py']})
with gzip.open(D/'evidence.json.gz','wt') as f:json.dump(e,f)
out=dict(pages=summary,texts=[{k:v for k,v in t.items() if k not in ['source','all_letter_map','rune_map']} for t in texts],tiny_controls=len(tiny),actual_controls=len(controls),elapsed=time.monotonic()-startall);(D/'results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
