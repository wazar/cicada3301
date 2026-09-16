"""Independent, bounded literal-F model checks. Standard library imports only."""
import argparse
import datetime
import itertools
import json
import math
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[2]
OWNER = pathlib.Path(__file__).resolve().parent
ABC = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
TOK = 'F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()

class Scorer:
    def __init__(self):
        counts = {}
        for line in (ROOT/'liber-primus/data/english_quadgrams.txt').read_text().splitlines():
            gram, value = line.split()
            counts[gram] = int(value)
        total = sum(counts.values())
        self.prob = {g: math.log10(n / total) for g, n in counts.items()}
        self.floor = math.log10(.01 / total)

    def __call__(self, plain):
        text = ''.join(TOK[x] for x in plain)
        return (sum(self.prob.get(text[i:i+4], self.floor) for i in range(len(text)-3)) /
                (len(text)-3)) if len(text) >= 4 else -999.0

def reference_cases():
    specs = [('0_welcome', [23,10,1,10,9,10,16,26], [4,5,6,7,10,11,14,18,20,21,25]),
             ('jpg107-167', [0,10,4,0,1,19,0,18,4,18,9,0,18], [2,3]),
             ('p56_an_end', None, [4])]
    results = []
    for name, cycle, f_labels in specs:
        source = ROOT/'audit/parallel-01/reference/sources'
        c = [ABC.index(r) for r in (source/(name+'.txt')).read_text() if r in ABC]
        expected = [ABC.index(r) for r in (source/('solved_'+name+'.txt')).read_text() if r in ABC]
        if cycle is None:
            # Independent sieve, distinct from reference trial division generator.
            sieve = [True] * 10000
            sieve[0] = sieve[1] = False
            for n in range(2, 100):
                if sieve[n]:
                    for m in range(n*n, 10000, n): sieve[m] = False
            key = [n-1 for n, prime in enumerate(sieve) if prime][:len(c)]
        else:
            key = [cycle[i % len(cycle)] for i in range(len(c))]
        seen = used = 0
        plain, trace = [], []
        for i, rune in enumerate(c):
            seen += rune == 0
            interrupt = rune == 0 and seen in f_labels
            before = used
            emitted = 0 if interrupt else (rune-key[used]) % 29
            used += not interrupt
            plain.append(emitted)
            trace.append(dict(position=i,cipher=rune,f_occurrence=seen if rune==0 else None,
                              action='literal_F' if interrupt else 'normal',key_before=before,
                              key_value=None if interrupt else key[before],key_after=used,plain=emitted))
        assert plain == expected
        assert len(plain) == len(c) and used == len(c)-len(f_labels)
        results.append(dict(name=name,expected=expected,plain=plain,key=key,trace=trace,
                            length=len(c),consumed=used,interruptions=len(f_labels),exact=True))
    return results

def enumerate_masks(cipher, key, score):
    """Independent whole-mask interpreter; never references truth labels."""
    sites = [i for i, c in enumerate(cipher) if c == 0]
    out = []
    for bits in itertools.product((0,1), repeat=len(sites)):
        literals = {i for i, bit in zip(sites, bits) if bit}
        plain = []
        for i, c in enumerate(cipher):
            # Key index is count of earlier nonliteral sites, independently computed.
            j = i - sum(s < i for s in literals)
            plain.append(0 if i in literals else (c-key[j]) % 29)
        out.append(dict(path=sorted(literals),plain=plain,used=len(cipher)-len(literals),score=score(plain)))
    return out

def prefix_search(cipher, key, score, width):
    states = [dict(path=[],plain=[],used=0,score=-999.)]
    retained = []
    for i, c in enumerate(cipher):
        children = []
        for state in states:
            p = state['plain'] + [(c-key[state['used']]) % 29]
            children.append(dict(path=state['path'],plain=p,used=state['used']+1,score=score(p)))
            if c == 0:
                p = state['plain']+[0]
                children.append(dict(path=state['path']+[i],plain=p,used=state['used'],score=score(p)))
        children.sort(key=lambda s:s['score'], reverse=True)
        cutoff = children[min(width,len(children))-1]['score'] if width else -math.inf
        states = [s for s in children if s['score'] >= cutoff]
        retained.append([s['path'] for s in states])
    return states, retained

def encode(name, plain, interrupt, seed, force):
    rng = random.Random(seed)
    key = [rng.randrange(29) for _ in plain]
    cipher, trace = [], []
    j = 0
    for i, p in enumerate(plain):
        before = j
        if i in interrupt:
            assert p == 0
            c = 0
        else:
            if i in force: key[j] = (-p) % 29
            c = (p+key[j]) % 29
            j += 1
        cipher.append(c)
        trace.append(dict(position=i,plain=p,cipher=c,interruption=i in interrupt,key_before=before,key_after=j))
    assert all(cipher[i] == 0 and i not in interrupt for i in force)
    return dict(name=name,plain=plain,cipher=cipher,key=key,interrupt=sorted(interrupt),trace=trace,seed=seed)

def fixtures(tiny):
    if tiny:
        a = encode('tiny_mixed', [0,18,0,4,0,24], [0,4], 330101, [1])
        # Same plaintext from multiple paths when every key is zero.
        b = dict(name='tiny_zero_key_ambiguity',plain=[0,18,0,4],cipher=[0,18,0,4],
                 key=[0]*4,interrupt=[0],seed=None)
        return [a,b]
    prose = [
        'F R O M TH E F I R S T L I GH T'.replace('GH','G H')+' W E L EA R N TH E W A Y O F L I F E A N D TH E W A Y O F W I S D O M',
        'TH E F I R E I S W A R M A N D TH E S T O N E I S C O L D W E W A L C F A R F R O M H O M E I N TH E L I GH T'.replace('GH','G H'),
        'A F R I E N D W I L L F I N D A P A TH O F P EA C E TH R O U GH TH E F O R E S T A N D R E T U R N H O M E'.replace('GH','G H')]
    rng = random.Random(330101)
    plains = [[TOK.index(t) for t in text.split()] for text in prose] + [[rng.randrange(29) for _ in range(80)]]
    plains[-1][5] = plains[-1][30] = plains[-1][60] = 0
    cases = []
    for n, plain in enumerate(plains):
        ints = [i for i,p in enumerate(plain) if p==0][:3]
        force = [i for i,p in enumerate(plain) if p!=0][::20][:3]
        cases.append(encode('prose_'+str(n) if n<3 else 'random_register',plain,ints,330101+n,force))
    return cases

def summarize(case, exhaustive, states, history):
    truth = case['interrupt']
    exactpath = [s for s in states if s['path']==truth]
    best = max(s['score'] for s in states)
    tops = [s for s in states if s['score']==best]
    prune = next((i for i,paths in enumerate(history) if [p for p in truth if p<=i] not in paths),None)
    true_score = next(s['score'] for s in exhaustive if s['path']==truth)
    return dict(true_path_represented=any(s['path']==truth for s in exhaustive),
                first_pruned_position=prune,true_path_survives=bool(exactpath),
                true_path_rank=1+sum(s['score']>true_score for s in states) if exactpath else None,
                true_path_global_rank=1+sum(s['score']>true_score for s in exhaustive),
                true_path_ranks_first=bool(exactpath) and true_score==best,
                true_path_exact_plaintext=bool(exactpath) and exactpath[0]['plain']==case['plain'],
                top_count=len(tops),any_top_plaintext_exact=any(s['plain']==case['plain'] for s in tops),
                all_top_plaintexts_exact=all(s['plain']==case['plain'] for s in tops),
                retained_count=len(states),max_prefix_population=max(map(len,history)))

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('mode',choices=['pilot','main']); args=parser.parse_args()
    score = Scorer()
    output = dict(mode=args.mode,reference=reference_cases() if args.mode=='pilot' else [],cases=[])
    for case in fixtures(args.mode=='pilot'):
        exact = enumerate_masks(case['cipher'],case['key'],score)
        assert len(exact)==2**case['cipher'].count(0)
        assert any(s['path']==case['interrupt'] and s['plain']==case['plain'] for s in exact)
        if args.mode=='pilot':
            unpruned, _ = prefix_search(case['cipher'],case['key'],score,None)
            signature=lambda rows:sorted((tuple(s['path']),tuple(s['plain']),s['used']) for s in rows)
            assert signature(exact)==signature(unpruned)
        beams=[]
        for width in [2,16,128]:
            states,history=prefix_search(case['cipher'],case['key'],score,width)
            beams.append(dict(width=width,summary=summarize(case,exact,states,history),final_states=states,
                              retained_paths_by_position=history))
        output['cases'].append(dict(fixture=case,compatible_paths=len(exact),
                                   distinct_plaintexts=len({tuple(s['plain']) for s in exact}),
                                   exhaustive=exact,beams=beams))
    path=OWNER/'results'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+args.mode+'.json')
    path.parent.mkdir(exist_ok=True)
    with path.open('x') as f: json.dump(output,f,indent=2);f.write('\n')
    print(json.dumps({'result':str(path.relative_to(ROOT)),'references':[(r['name'],r['length'],r['consumed']) for r in output['reference']],
                      'cases':[{'name':r['fixture']['name'],'compatible_paths':r['compatible_paths'],'distinct_plaintexts':r['distinct_plaintexts'],
                                'beams':[{'width':b['width'],**b['summary']} for b in r['beams']]} for r in output['cases']]},indent=2))

if __name__=='__main__': main()
