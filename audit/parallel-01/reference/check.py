import json,pathlib,hashlib,datetime,sys
from reference import *
D=pathlib.Path(__file__).parent;S=D/'sources'
from fixtures import CASES, first
def separators(text):return ''.join(c for c in text if c not in ALPHABET and not c.isspace())
def hand_tests():
    assert primes(6)==[2,3,5,7,11,13]
    assert decode([0,1,28],'atbash')==[28,27,0]
    assert decode([0,1,28],'atbash_shift3')==[2,1,3]
    assert decode([5,0,8],'keyed',[2,3],[1])==[3,0,5]
    assert decode([5,0,8],'keyed',[2,3],[1],True)==[3,5]
    assert decode([1,0,3,6],'totient',interrupts=[1])==[0,0,1,2]
    assert decode([5,0,8],'keyed',[3,3],[1])!=[3,0,5]
    assert decode([6,0,8],'keyed',[2,3],[1])!=[3,0,5]
hand_tests(); rows=[]
for name,method,key,interrupts,pages in CASES:
    raw=(S/(name+'.txt')).read_text();expected_raw=(S/('solved_'+name+'.txt')).read_text()
    cipher=indices(raw);expected=indices(expected_raw);got=decode(cipher,method,key,interrupts)
    mutated=cipher.copy();mutated[-1]=(mutated[-1]+1)%29
    row=dict(case=name,original_pages=pages,method=method,key=key,interrupt_F_occurrences_one_based=interrupts,input_length=len(cipher),expected_length=len(expected),actual_length=len(got),first_difference=first(got,expected),complete_runes_pass=got==expected,separators_pass=separators(raw)==separators(expected_raw),mutation_detected=decode(mutated,method,key,interrupts)!=expected,expected_indices=expected,actual_indices=got,actual_transliteration=render(got),expected_transliteration=render(expected),cipher_sha256=hashlib.sha256(raw.encode()).hexdigest(),expected_source_sha256=hashlib.sha256(expected_raw.encode()).hexdigest())
    if key:row['key_mutation_detected']=decode(cipher,method,[(k+1)%29 for k in key],interrupts)!=expected
    rows.append(row)
report=dict(run_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),hand_tests='8 passed',cases=rows)
(D/'results.json').write_text(json.dumps(report,indent=2)+'\n')
for r in rows:print({k:v for k,v in r.items() if k not in ('expected_indices','actual_indices','actual_transliteration','expected_transliteration')})
print('complete rune comparisons',sum(r['complete_runes_pass'] for r in rows),'/',len(rows))
sys.exit(0 if all(r['complete_runes_pass'] and r['mutation_detected'] for r in rows) else 1)
