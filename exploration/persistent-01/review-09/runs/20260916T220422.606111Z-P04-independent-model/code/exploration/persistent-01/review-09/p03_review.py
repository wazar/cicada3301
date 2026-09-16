import pathlib,json,gzip,hashlib,collections,itertools,datetime
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];P=O.parent/'worker-p'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def snapshot(p):
 b=p.read_bytes();dst=O/'snapshots'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b);assert p.read_bytes()==b;return dst,{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def main():
 assert not(O.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00');inputs=[]
 paths=[P/'P03/evidence.json.gz',P/'P03/results.json',P/'P03/check.json',P/'P04/support-evidence.json.gz',P/'P04/CARD.md',P/'p04_milp.py']+list((P/'P04').glob('real-0-*'))
 for path in paths:dst,meta=snapshot(path);inputs.append(meta)
 ep=O/'snapshots'/P.relative_to(R)/'P03/evidence.json.gz'
 with gzip.open(ep,'rt') as f:e=json.load(f)
 T=[r['transliteration'] for r in load(R/'KNOWLEDGE.json')['gematria_primus']['table']];A='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';names=['0_koan_1','0_loss_of_divinity','0_welcome','jpg107-167'];assert [t['name'] for t in e['texts']]==names;reconstructed={};source_meta=[];lettermaps=0
 for name,t in zip(names,e['texts']):
  p=R/'audit/parallel-01/reference/sources'/f'solved_{name}.txt';source_meta.append({'path':str(p.relative_to(R)),'sha256':sha(p)});runes=[A.index(c) for c in p.read_text() if c in A];rows=[];rmap=[];seq=[]
  for i,rune in enumerate(runes):
   rm={'source_rune_index':i,'rune':rune,'expanded_indices':[],'retained_indices':[],'removed_expanded_indices':[]}
   for j,c in enumerate(T[rune]):
    expanded=len(rows);keep=c not in 'AEIOU';row={'source_rune_index':i,'rune':rune,'letter_offset':j,'expanded_index':expanded,'letter':c,'keep':keep,'consonant_index':len(seq) if keep else None};rows.append(row);rm['expanded_indices'].append(expanded)
    if keep:rm['retained_indices'].append(len(seq));seq.append(ord(c)-65)
    else:rm['removed_expanded_indices'].append(expanded)
   rmap.append(rm)
  assert rows==t['all_letter_map'] and rmap==t['rune_map'] and seq==t['source'];assert len(rows)==t['original_expanded_n'] and len(seq)==t['consonantal_n'];reconstructed[name]=(seq,rows);lettermaps+=len(rows)
 assert T[26]=='Y' and len(reconstructed['jpg107-167'][0])==195
 def reason(ii,tt,r):
  k=r['kind']
  if k=='total':assert sum(ii)!=sum(tt)
  elif k=='support':assert len(tt)>len(ii)
  elif k=='minimum':assert min(tt)<min(ii)
  elif k=='small_capacity':assert sum(v for v in tt if v<=r['threshold'])>sum(v for v in ii if v<=r['threshold'])
  elif k=='subset_support':
   possible=[False]*(sum(ii)+1);possible[0]=True
   for v in ii:
    for s in range(len(possible)-1,v-1,-1):possible[s]|=possible[s-v]
   assert not possible[r['target']]
  else:raise AssertionError(k)
 checked_nodes=0
 def certify(ii,tt,res):
  nonlocal checked_nodes
  if res['status']=='FEASIBLE':assert collections.Counter(itertools.chain.from_iterable(res['groups']))==collections.Counter(ii) and sorted(map(sum,res['groups']))==sorted(tt);return
  assert res['status']=='INFEASIBLE'
  if 'reason' in res:reason(ii,tt,res['reason']);return
  dag=res['proof_dag'];root=str(tuple(sorted(ii)))+'/'+str(tuple(sorted(tt)));assert root in dag
  for key,node in dag.items():
   aa=node['items'];bb=node['targets'];assert key==str(tuple(aa))+'/'+str(tuple(bb));checked_nodes+=1
   if 'reason' in node:reason(aa,bb,node['reason']);continue
   assert bb;target=bb[0];freq=collections.Counter(aa);poly=[0]*(target+1);poly[0]=1
   for v,count in sorted(freq.items()):
    new=[0]*(target+1)
    for s,ways in enumerate(poly):
     if ways:
      for n in range(min(count,(target-s)//v)+1):new[s+n*v]+=ways
    poly=new
   children=node['children'];sels=[tuple(c['selected']) for c in children];assert len(children)==len(set(sels))==poly[target]
   for child in children:
    selected=collections.Counter(child['selected']);assert sum(child['selected'])==target and all(cnt<=freq[v] for v,cnt in selected.items());left=sorted((freq-selected).elements());ck=str(tuple(left))+'/'+str(tuple(bb[1:]));assert child['child']==ck and ck in dag;assert dag[ck]['items']==left and dag[ck]['targets']==bb[1:]
 cfg=load(O.parent/'config.json');dataset=R/'audit/parallel-01/inputs/dataset.json';assert sha(dataset)==cfg['dataset_sha256'];ids=[p['page'] for p in e['real']];assert ids==[0,1,3,7,17] and not(set(ids)&set(cfg['reserved_original_pages']));actual={p['original_page']:collections.Counter(p['indices']) for p in load(dataset)['pages'] if p['original_page'] in ids};stats=[];allcounts=collections.Counter();supportgroups=[]
 for page in e['real']:
  observed=actual[page['page']];assert observed==dict(page['output_counts_by_rune']);seen=set();count=collections.Counter();groups=collections.defaultdict(lambda:collections.defaultdict(list))
  for case in page['cases']:
   certify(page['items'],case['targets'],case['result'])
   for prov in case['provenance']:
    name=prov['group'];start=prov['start'];end=prov['end'];key=(name,start);assert key not in seen;seen.add(key);seq,rows=reconstructed[name];chunk=seq[start:end];freq=collections.Counter(chunk);assert end-start==len(chunk)==page['n'];assert [freq[i] for i in range(26)]==prov['letter_counts'] and sorted(freq.values())==case['targets'];kept=[r for r in rows if r['keep']];assert prov['expanded_span']==[kept[start]['expanded_index'],kept[end-1]['expanded_index']+1] and prov['source_rune_span']==[kept[start]['source_rune_index'],kept[end-1]['source_rune_index']+1]
    status=case['result']['status'];count[status]+=1
    if status=='FEASIBLE':
     mappings=prov['letter_to_output_runes'];assert collections.Counter(itertools.chain.from_iterable(m['output_runes'] for m in mappings))==collections.Counter(observed.keys());assert {m['letter_index'] for m in mappings}==set(freq)
     for m in mappings:assert sum(observed[r] for r in m['output_runes'])==freq[m['letter_index']]
     support=''.join(chr(c+65) for c in sorted(freq));groups[support][tuple(prov['letter_counts'])].append((name,start))
  expected={(name,s) for name,(seq,_) in reconstructed.items() for s in range(max(0,len(seq)-page['n']+1))};assert expected==seen and not any(name=='jpg107-167' for name,s in seen);allcounts.update(count);stats.append({'page':page['page'],'windows':len(seen),'statuses':dict(count)});supportgroups.append(groups)
 for c in e['tiny_controls']+e['actual_controls']:certify(c['items'],c['targets'],c['result'])
 for c in e['tiny_controls']:
  truth=False
  for ass in itertools.product(range(len(c['targets'])),repeat=len(c['items'])):
   bins=[0]*len(c['targets'])
   for v,k in zip(c['items'],ass):bins[k]+=v
   if bins==c['targets']:truth=True;break
  assert truth==c['brute']==(c['result']['status']=='FEASIBLE')
 supportpath=O/'snapshots'/P.relative_to(R)/'P04/support-evidence.json.gz'
 with gzip.open(supportpath,'rt') as f:saved=json.load(f)
 common=sorted(set.intersection(*(set(g) for g in supportgroups)));assert common==saved['common_supports']
 for p,g in zip(saved['pages'],supportgroups):
  assert set(p['groups'])==set(g)
  for support,vecs in p['groups'].items():
   assert len(vecs)==len(g[support])
   for v in vecs:assert sorted((q['group'],q['start']) for q in v['aliases'])==sorted(g[support][tuple(v['counts'])])
 out={'verdict':'NO-ERROR-FOUND_P03','input_snapshots':inputs,'source_files':source_meta,'GP_table_file_sha256':sha(R/'KNOWLEDGE.json'),'letter_maps_checked':lettermaps,'source_lengths':{name:len(seq) for name,(seq,_) in reconstructed.items()},'page_results':stats,'all_statuses':dict(allcounts),'infeasible_proof_nodes_checked_including_controls':checked_nodes,'tiny_brute_fixtures':len(e['tiny_controls']),'control_certificates':len(e['tiny_controls'])+len(e['actual_controls']),'common_actual_letter_support':common,'common_support_vectors_per_page':[{s:len(g[s]) for s in common} for g in supportgroups]};(O/'P03-findings.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
if __name__=='__main__':main()
