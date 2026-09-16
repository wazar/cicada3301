import gzip,json,hashlib
import numpy as np
from search import ROOT,OWNER,seqs,Score,dump,ABC
from extras import beam
cfg=json.loads((ROOT/'exploration/overnight-01/config.json').read_text());pages={p['original_page']:p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages']};seq=seqs(15000);s=Score();counts={'numeric':0,'periodic':0,'literal_f':0}
for r in json.loads((OWNER/'r03/top_candidates.json').read_text()):
 c=pages[r['page']]['indices'];p=r['rune_indices'];k=seq[r['family']][r['key_start']:];assert all((v-r['sign']*int(k[i]))%29==c[i] for i,v in enumerate(p));counts['numeric']+=1
for path in (OWNER/'r04').glob('cell-*.json.gz'):
 with gzip.open(path,'rt') as f:rows=json.load(f)
 for r in rows:
  c=np.array(pages[r['page']]['indices']);c=np.random.default_rng(330104+r['page']).permutation(c) if r['control'] else c;p=r['rune_indices'];assert all((v+r['key'][i%r['period']])%29==c[i] for i,v in enumerate(p));assert r['page'] not in cfg['reserved_original_pages'];counts['periodic']+=1
for path in (OWNER/'r03-f').glob('cell-*.json'):
 r=json.loads(path.read_text());assert r['page'] not in cfg['reserved_original_pages'];c=pages[r['page']]['indices'];key=seq[r['family']][r['offset']:]
 for out in r['choices']:
  j=0
  for i,v in enumerate(out['rune_indices']):
   if i in out['literal_positions']:assert c[i]==v==0
   else:assert (v-r['sign']*int(key[j]))%29==c[i];j+=1
  counts['literal_f']+=1
plain=[ABC.index(x) for x in (ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt').read_text() if x in ABC];c=np.random.default_rng(33991).integers(0,29,len(plain));out=beam(c,seq['prime_minus_one'][37:],-1,s);dump(OWNER/'r03/f-corrupted-control.json',{'seed':33991,'top16':out,'top_rune_errors':sum(a!=b for a,b in zip(plain,out[0]['rune_indices'])),'truth_found':any(r['rune_indices']==plain for r in out)})
dump(OWNER/'verification.json',{'fixed_path_reencryption_counts':counts,'passed':True,'reserved_pages_untouched':cfg['reserved_original_pages'],'note':'Independent scalar inverse loops in this module, shared deterministic sequence generator; no claim this makes plaintext meaningful.'});print(counts)
