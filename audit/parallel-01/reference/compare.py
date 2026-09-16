import pathlib,json,re
from reference import *
from fixtures import CASES,first
D=pathlib.Path(__file__).parent;ROOT=D.parents[2]
text=(ROOT/'liber-primus/data/scream314_lp.md').read_text()
sections={}
for m in re.finditer(r'^## (.+)\n([\s\S]*?)(?=^## |\Z)',text,re.M):
    # Only indented source rune rows, excluding prose mentioning F.
    sections[m[1]]='\n'.join(l[4:] for l in m[2].splitlines() if l.startswith('    ') and any(c in ALPHABET for c in l))
joins={'0_warning':['Runes - 01.jpg'],'0_welcome':['03.jpg','04.jpg'],'0_wisdom':['05.jpg'],'0_koan_1':['06.jpg','09.jpg'],'0_loss_of_divinity':['10.jpg - index.1.jpg','13.jpg - index.4.jpg'],'jpg107-167':['14.jpg - 107.jpg'],'jpg229':['16.jpg - 229.jpg'],'p56_an_end':['73.jpg - 56.jpg'],'p57_parable':['74.jpg - 57.jpg']}
rows=[]
for name,method,key,interrupts,pages in CASES:
    local=indices(''.join(sections[x] for x in joins[name]));external=indices((D/'sources'/(name+'.txt')).read_text())
    expected=indices((D/'sources'/('solved_'+name+'.txt')).read_text())
    got=decode(local,method,key,interrupts)
    rows.append(dict(case=name,local_sections=joins[name],local_count=len(local),external_count=len(external),input_first_difference=first(local,external),decode_first_difference=first(got,expected),complete_match=got==expected,context=None if got==expected else dict(position=first(got,expected),expected=render(expected[max(0,first(got,expected)-5):first(got,expected)+10]),actual=render(got[max(0,first(got,expected)-5):first(got,expected)+10]))))
dataset=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text());lp2=[]
for p in dataset['pages'][-2:]:
    case='p56_an_end' if p['original_filename']=='56.jpg' else 'p57_parable'
    external=indices((D/'sources'/(case+'.txt')).read_text())
    lp2.append(dict(original_filename=p['original_filename'],segment_id=p['segment_id'],first_difference=first(p['indices'],external),equal=p['indices']==external))
(D/'input-comparison.json').write_text(json.dumps(dict(local_vs_external=rows,A_v1_lp2_joins=lp2),indent=2)+'\n')
print(json.dumps(dict(local_vs_external=rows,A_v1_lp2_joins=lp2),indent=2))
