from pathlib import Path
import numpy as np,json,hashlib
from collections import Counter
D=Path(__file__).parent;inp=json.loads((D/'inputs.json').read_text());assert hashlib.sha256(Path(inp['parser_path']).read_bytes()).hexdigest()==inp['parser_sha256'];GP='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def pack(s):
 x=0
 for v in s:x=(x<<5)|int(v)
 return x
def rotations(s):
 x=pack(s);n=len(s);mask=(1<<(5*n))-1;shift=5*(n-1);rs=[]
 for _ in range(n):rs.append(x);x=((x<<5)&mask)|(x>>shift)
 return rs
expected=[]
for control in inp['controls']:
 raw=Path(control['source']['path']).read_text();pos=[i for i,ch in enumerate(raw) if ch in GP];truth=[GP.index(raw[i]) for i in pos];assert truth==control['truth'];rots=rotations(truth);starts=sorted(range(len(truth)),key=lambda i:(rots[i],i));sourceidx=[(i-1)%len(truth) for i in starts];assert sourceidx==control['carrier_to_source_rune'];assert [pos[i] for i in sourceidx]==control['carrier_to_source_char'];assert [truth[i] for i in sourceidx]==control['carrier'];assert hashlib.sha256(Path(control['source']['path']).read_bytes()).hexdigest()==control['source']['sha256']
 for i in range(len(truth)-1):
  if control['carrier'][i]!=control['carrier'][i+1]:expected.append((control['control'],i))
assert expected==[(j['control'],j['positions'][0]) for j in inp['jobs']]
rows=[];primary=groups=0
for job in inp['jobs']:
 name=f"swap-{job['job']:04d}";meta=json.loads((D/(name+'.json')).read_text());a=dict(np.load(D/(name+'.npz')));control=inp['controls'][job['control']];source=control['carrier'];c=source.copy();i,j=job['positions'];assert j==i+1 and c[i]!=c[j];c[i],c[j]=c[j],c[i];assert c==a['input'].tolist();assert Counter(c)==Counter(source)
 assert job['before']==[source[i],source[j]];assert job['source_rune_positions']==[control['carrier_to_source_rune'][i],control['carrier_to_source_rune'][j]];assert job['source_char_positions']==[control['carrier_to_source_char'][i],control['carrier_to_source_char'][j]]
 pairs=sorted((v,i) for i,v in enumerate(c));first=np.array([v for v,i in pairs],np.uint8);psi=np.array([i for v,i in pairs]);lf=np.argsort(psi);assert np.array_equal(lf,a['lf']);idx=np.arange(len(c));table=np.empty_like(a['candidates'])
 for t in range(len(c)):table[:,t]=first[idx];idx=psi[idx]
 rowmap=np.arange(len(c))
 for _ in range(len(c)):rowmap=lf[rowmap]
 assert np.array_equal(table[rowmap],a['candidates']);packedgroups=[pack(g) for g in a['groups']];assert sorted(set(map(int,a['group_for_primary'])))==list(range(len(packedgroups)))
 for k,cand in enumerate(a['candidates']):assert min(rotations(cand))==packedgroups[int(a['group_for_primary'][k])]
 good=[]
 for k,g in enumerate(a['groups']):
  rs=rotations(g);assert min(rs)==packedgroups[k];last=[x&31 for x in sorted(rs)];assert last==a['forward_columns'][k].tolist();assert (last==c)==bool(a['valid'][k])
  if last==c:good.append(k)
 assert good==meta['valid_groups'] and bool(good)==meta['compatible'];assert not any(packedgroups[k]==min(rotations(control['truth'])) for k in good);assert meta['original_necklace_retained'] is False
 primary+=len(c);groups+=len(packedgroups);rows.append({'control':job['control'],'job':job['job'],'compatible':bool(good)})
 if job['job']%100==0:print('checked',job['job'],flush=True)
summary=json.loads((D/'result.json').read_text());assert summary['jobs']==len(rows) and summary['compatible']==sum(r['compatible'] for r in rows)
for s in summary['rows']:assert s['swaps']==sum(r['control']==s['control'] for r in rows);assert s['compatible']==sum(r['control']==s['control'] and r['compatible'] for r in rows)
out={'PASS':True,'swaps':len(rows),'all_primary_candidates':primary,'groups':groups,'compatible':sum(r['compatible'] for r in rows),'source_necklace_retained':0};(D/'verification.json').write_text(json.dumps(out,indent=2));print(out)
