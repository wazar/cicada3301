import json,pathlib,re
from reference import *
from fixtures import first
D=pathlib.Path(__file__).parent;ROOT=D.parents[2]
raw=(ROOT/'liber-primus/data/scream314_lp.md').read_text()
sections={m[1]:indices('\n'.join(l[4:] for l in m[2].splitlines() if l.startswith('    ') and any(c in ALPHABET for c in l))) for m in re.finditer(r'^## (.+)\n([\s\S]*?)(?=^## |\Z)',raw,re.M)}
configs=[('03.jpg','0_welcome','keyed',[23,10,1,10,9,10,16,26],[3,5,6,7,10,12,14]),('05.jpg','0_wisdom','plain',[],[]),('06.jpg','0_koan_1','atbash_shift3',[],[]),('14.jpg','jpg107-167','keyed',[0,10,4,0,1,19,0,18,4,18,9,0,18],[2,3]),('LP2 page 56','p56_an_end','totient',[],[4]),('LP2 page 57','p57_parable','plain',[],[]),('Runes - 01.jpg','0_warning','atbash',[],[])]
output=(D/'logs/inherited.stdout.txt').read_text();rows=[]
for label,case,method,key,interrupts in configs:
    if label.startswith('LP2'):cipher=indices((ROOT/'liber-primus/data/sources'/('relikd_'+case+'.txt')).read_text())
    else:cipher=sections[next(k for k in sections if k==label or k.startswith(label+' -'))]
    expected=indices((D/'sources'/('solved_'+case+'.txt')).read_text())
    match=re.search(r'page\s+: '+re.escape(label)+r'\n([\s\S]*?)(?=\npage\s+:|\Z)',output)
    printed=''.join(re.findall(r'^  ([A-Z]+)$',match[1],re.M))
    got=decode(cipher,method,key,interrupts,drop=True)
    assert render(got)==printed,(label,render(got),printed)
    diff=first(got,expected)
    rows.append(dict(label=label,case=case,cipher_runes=len(cipher),expected_full_group_runes=len(expected),inherited_output_runes=len(got),first_difference=diff,full_group_match=got==expected,expected_rune=None if diff is None or diff>=len(expected) else expected[diff],inherited_rune=None if diff is None or diff>=len(got) else got[diff],expected_context=None if diff is None else render(expected[max(0,diff-5):diff+10]),inherited_context=None if diff is None else render(got[max(0,diff-5):diff+10]),independent_reconstruction_matches_printed_output=True))
(D/'inherited-comparison.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
