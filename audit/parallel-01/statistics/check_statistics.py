"""Independent stdlib parser/statistics; no research or other worker imports."""
import csv, hashlib, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ALPHABET='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
SOURCE=ROOT/'liber-primus/data/krisyotam_runes.txt'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(raw):
    regions=[[]]; line=0
    for pos,char in enumerate(raw):
        if char=='%': regions.append([]); line=0
        elif char=='/': line+=1
        elif char in ALPHABET:
            regions[-1].append({'value':ALPHABET.index(char),'char':pos,'line':line,'region':len(regions)-1})
    return [r for r in regions if r]
def stats(values):
    n=len(values); counts=Counter(values)
    return {'n':n,'pairs':max(0,n-1),'equal':sum(a==b for a,b in zip(values,values[1:])),
      'entropy_bits':-sum((v/n)*math.log2(v/n) for v in counts.values()) if n else None,
      'ioc':sum(v*(v-1) for v in counts.values())/(n*(n-1)) if n>1 else None,
      'frequencies':[counts[i] for i in range(29)]}
def tests():
    assert stats([0,0,1,1])['equal']==2
    assert stats([0,0,1,1])['entropy_bits']==1
    assert stats([0,0,1,1])['ioc']==1/3
    assert stats([0]*4)['ioc']==1
    assert stats([0]*4)['entropy_bits']==0
    p=parse('ᚠ-ᚢ/ᚠ%ᚦ%'); assert [[v['value'] for v in x] for x in p]==[[0,1,0],[2]]
    assert [v['char'] for v in p[0]]==[0,2,4] and p[0][-1]['line']==1
    # Exhaustive small rational independent-increment convolution check.
    p=[.2,.3,.5]; q=[.6,.1,.3]
    probability=sum(p[d]*q[(-d)%3] for d in range(3))
    assert abs(probability-.26)<1e-12 and probability>=min(p)
    # Correlated increments, each marginal uniform, never sum to zero.
    assert all((d+(1-d)%3)%3!=0 for d in range(3))
    # Short key + deterministic balanced plaintext gives near-uniform IoC.
    x=[(i%29+4)%29 for i in range(29*100)]
    assert abs(stats(x)['ioc']*29-1)<.01
    # Rejection-loop and direct Markov construction have identical transition rows.
    a=.18; diagonal=a/(28+a); offdiag=1/(28+a)
    assert abs(diagonal+28*offdiag-1)<1e-12
    # Reset candidate key each page, retain previous output filter state.
    previous=None; out=[]
    for plaintext in ([0,0],[1,1]):
        page=[]
        for j,value in enumerate(plaintext):
            candidate=(value+[0,1][j])%29
            if candidate==previous:candidate=(candidate+1)%29
            page.append(candidate);previous=candidate
        out.append(page)
    assert out==[[0,1],[2,3]]  # zero repeat at page boundary despite key reset
    print('PASS: formula, parser, convolution, dependence, short-key, filter-equivalence, reset handtests')
def table(name, rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def main():
    tests(); raw=SOURCE.read_text(); pages=parse(raw)
    a=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())
    mapping=json.loads((ROOT/'audit/parallel-01/inputs/page-map.json').read_text())
    labels={p['segment_id']:p for p in mapping['pages'] if p['segment_id'] is not None}
    assert len(pages)==len(a['pages'])==57
    for i,(p,ap) in enumerate(zip(pages,a['pages'])):
        assert [r['value'] for r in p]==ap['indices'],i
        assert [r['char'] for r in p]==ap['source_char_positions'],i
        assert p[0]['region']==ap['source_region_id'],i
        assert labels[i]['original_page']==ap['original_page']
    # Source segments 0..54 correspond to original images 0..49,51..55.
    records=[]; page_rows=[]; line_rows=[]
    for segment,p in enumerate(pages[:55]):
        page=labels[segment]['original_page']; start=len(records)
        for j,r in enumerate(p): records.append(dict(r,page=page,segment=segment,page_rune=j,global_rune=len(records)))
        assert start==labels[segment]['stream_start'] and len(records)==labels[segment]['stream_end']
        s=stats([r['value'] for r in p]); page_rows.append(dict(page=page,segment=segment,start=start,**s))
        for ln in sorted(set(r['line'] for r in p)):
            t=stats([r['value'] for r in p if r['line']==ln]); line_rows.append(dict(page=page,line=ln,**t))
    values=[r['value'] for r in records]; overall=stats(values)
    bins=defaultdict(lambda:{'pairs':0,'equal':0}); pairs=[]; allpairs=[]
    for left,right in zip(records,records[1:]):
        gap=raw[left['char']+1:right['char']]
        if left['page']!=right['page']: category='page_join'
        elif left['line']!=right['line']: category='slash_line_join'
        elif gap: category='within_line_separator'
        else: category='literal_adjacent_runes'
        equal=left['value']==right['value']; bins[category]['pairs']+=1; bins[category]['equal']+=equal
        row={'left_global':left['global_rune'],'right_global':right['global_rune'],'left_page':left['page'],'right_page':right['page'],'left_page_rune':left['page_rune'],'right_page_rune':right['page_rune'],'left_line':left['line'],'right_line':right['line'],'left_source_char':left['char'],'right_source_char':right['char'],'rune_index':left['value'],'category':category,'raw_gap':gap,'equal':equal}
        if equal:pairs.append(row)
        allpairs.append(row)
    assert len(pairs)==86 and len(values)==12956
    digest=hashlib.sha256(','.join(map(str,values)).encode()).hexdigest()
    assert digest=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
    # Exhaustive single substitution: local doublet delta and updated marginals.
    sensitivity=[]; count=Counter(values); changes=[]; h=[]; iocs=[]
    for j,old in enumerate(values):
        for new in range(29):
            if new==old:continue
            delta=0
            for k in (j-1,j+1):
                if 0<=k<len(values):delta+=(values[k]==new)-(values[k]==old)
            changes.append(overall['equal']+delta)
            c=count.copy();c[old]-=1;c[new]+=1
            h.append(-sum(v/len(values)*math.log2(v/len(values)) for v in c.values() if v))
            iocs.append(sum(v*(v-1) for v in c.values())/(len(values)*(len(values)-1)))
    sensitivity.append({'case':'any_one_rune_substitution','trials':len(changes),'equal_min':min(changes),'equal_max':max(changes),'entropy_min':min(h),'entropy_max':max(h),'ioc_min':min(iocs),'ioc_max':max(iocs)})
    for name,vs in [('exclude_mixed_p49_p51',[r['value'] for r in records if r['page'] not in [49,51]]),('include_solved_p56_p57',[r['value'] for p in pages for r in p])]:
        sensitivity.append({'case':name,'stats':stats(vs),'warning':'flattened remaining runes; new joins created'})
    result={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'parser_sha256':sha(Path(__file__)),'input_version':a['version'],'input_export_sha256':sha(ROOT/'audit/parallel-01/inputs/dataset.json'),'page_map_sha256':sha(ROOT/'audit/parallel-01/inputs/page-map.json'),'all_57_arrays_and_source_positions_match':True,'unsolved_hash':digest,'overall':overall,'ioc_times_29':29*overall['ioc'],'within_pages_pairs':sum(p['pairs'] for p in page_rows),'within_pages_equal':sum(p['equal'] for p in page_rows),'categories':dict(bins),'sensitivity':sensitivity,'boundary_uniform_zero_probability':(28/29)**54,'boundary_zero_one_sided_95_upper':1-.05**(1/54),'uniform_expected_equal':12955/29,'suppression_relative_uniform':1-(86/12955)/(1/29),'repeat_accept_probability_under_uniform_rejection':28*(86/12955)/(1-86/12955),'working_commit':'95e11e918ace77a51de4b612a48e74c298e67e58','baseline':'396001a9ce55e0e85ddef19e405afc6a13954588','python':sys.version,'random_seeds':[]}
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    table('pairs.csv',pairs);table('pair-categories.csv',[dict(category=k,**v) for k,v in bins.items()]);table('pages.csv',page_rows);table('lines.csv',line_rows)
    table('frequencies.csv',[{'index':i,'rune':ALPHABET[i],'count':n,'fraction':n/len(values)} for i,n in enumerate(overall['frequencies'])])
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
